from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any, Callable, Final, Literal
from uuid import uuid4

from litestar.constants import OPENAPI_NOT_INITIALIZED
from litestar.controller import Controller
from litestar.enums import MediaType, OpenAPIMediaType
from litestar.exceptions import ImproperlyConfiguredException
from litestar.handlers import get
from litestar.openapi.config import _DEFAULT_SCHEMA_SITE
from litestar.response.base import ASGIResponse
from litestar.serialization import encode_json
from litestar.serialization.msgspec_hooks import decode_json
from litestar.status_codes import HTTP_404_NOT_FOUND

if TYPE_CHECKING:
    from litestar.connection.request import Request
    from litestar.openapi.spec.open_api import OpenAPI

__all__ = ("OpenAPIController",)

# NOTE: We are explicitly using a different name to the one defined in litestar.constants so that an openapi
#   controller can be added to a router on the same application as the openapi router.
#   See: https://github.com/litestar-org/litestar/issues/3337
OPENAPI_JSON_HANDLER_NAME: Final = f"{uuid4().hex}_litestar_openapi_json"


class OpenAPIController(Controller):
    """Controller for OpenAPI endpoints."""

    path: str = "/schema"
    """Base path for the OpenAPI documentation endpoints."""
    style: str = "body { margin: 0; padding: 0 }"
    """Base styling of the html body."""
    redoc_version: str = "next"
    """Redoc version to download from the CDN."""
    swagger_ui_version: str = "5.1.3"
    """SwaggerUI version to download from the CDN."""
    stoplight_elements_version: str = "7.7.18"
    """StopLight Elements version to download from the CDN."""
    rapidoc_version: str = "9.3.4"
    """RapiDoc version to download from the CDN."""
    favicon_url: str = ""
    """URL to download a favicon from."""
    redoc_google_fonts: bool = True
    """Download google fonts via CDN.

    Should be set to ``False`` when not using a CDN.
    """
    redoc_js_url: str = f"https://cdn.jsdelivr.net/npm/redoc@{redoc_version}/bundles/redoc.standalone.js"
    """Download url for the Redoc JS bundle."""
    swagger_css_url: str = f"https://cdn.jsdelivr.net/npm/swagger-ui-dist@{swagger_ui_version}/swagger-ui.css"
    """Download url for the Swagger UI CSS bundle."""
    swagger_ui_bundle_js_url: str = (
        f"https://cdn.jsdelivr.net/npm/swagger-ui-dist@{swagger_ui_version}/swagger-ui-bundle.js"
    )
    """Download url for the Swagger UI JS bundle."""
    swagger_ui_standalone_preset_js_url: str = (
        f"https://cdn.jsdelivr.net/npm/swagger-ui-dist@{swagger_ui_version}/swagger-ui-standalone-preset.js"
    )
    """Download url for the Swagger Standalone Preset JS bundle."""
    swagger_ui_init_oauth: dict[Any, Any] | bytes = {}
    """
    JSON to initialize Swagger UI OAuth2 by calling the `initOAuth` method.

    Refer to the following URL for details:
    `Swagger-UI <https://swagger.io/docs/open-source-tools/swagger-ui/usage/oauth2/>`_.
    """
    stoplight_elements_css_url: str = (
        f"https://unpkg.com/@stoplight/elements@{stoplight_elements_version}/styles.min.css"
    )
    """Download url for the Stoplight Elements CSS bundle."""
    stoplight_elements_js_url: str = (
        f"https://unpkg.com/@stoplight/elements@{stoplight_elements_version}/web-components.min.js"
    )
    """Download url for the Stoplight Elements JS bundle."""
    rapidoc_js_url: str = f"https://unpkg.com/rapidoc@{rapidoc_version}/dist/rapidoc-min.js"
    """Download url for the RapiDoc JS bundle."""

    # internal
    _dumped_json_schema: str = ""
    _dumped_yaml_schema: bytes = b""
    # until swagger-ui supports v3.1.* of OpenAPI officially, we need to modify the schema for it and keep it
    # separate from the redoc version of the schema, which is unmodified.
    dto = None
    return_dto = None

    @staticmethod
    def get_schema_from_request(request: Request[Any, Any, Any]) -> OpenAPI:
        """Return the OpenAPI pydantic model from the request instance.

        Args:
            request: A :class:`Litestar <.connection.Request>` instance.

        Returns:
            An :class:`OpenAPI <litestar.openapi.spec.open_api.OpenAPI>` instance.
        """
        return request.app.openapi_schema

    def should_serve_endpoint(self, request: Request[Any, Any, Any]) -> bool:
        """Verify that the requested path is within the enabled endpoints in the openapi_config.

        Args:
            request: To be tested if endpoint enabled.

        Returns:
            A boolean.

        Raises:
            ImproperlyConfiguredException: If the application ``openapi_config`` attribute is ``None``.
        """
        if not request.app.openapi_config:  # pragma: no cover
            raise ImproperlyConfiguredException("Litestar has not been instantiated with an OpenAPIConfig")

        asgi_root_path = set(filter(None, request.scope.get("root_path", "").split("/")))
        full_request_path = set(filter(None, request.url.path.split("/")))
        request_path = full_request_path.difference(asgi_root_path)
        root_path = set(filter(None, self.path.split("/")))

        config = request.app.openapi_config
        enabled_endpoints = config.enabled_endpoints or set()
        root_schema_site = config.root_schema_site or _DEFAULT_SCHEMA_SITE

        if request_path == root_path and root_schema_site in enabled_endpoints:
            return True

        return bool(request_path & enabled_endpoints)

    @property
    def favicon(self) -> str:
        """Return favicon ``<link>`` tag, if applicable.

        Returns:
            A ``<link>`` tag if ``self.favicon_url`` is not empty, otherwise returns a placeholder meta tag.
        """
        return f"<link rel='icon' type='image/x-icon' href='{self.favicon_url}'>" if self.favicon_url else "<meta/>"

    @cached_property
    def render_methods_map(
        self,
    ) -> dict[Literal["redoc", "swagger", "elements", "rapidoc"], Callable[[Request], bytes]]:
        """Map render method names to render methods.

        Returns:
            A mapping of string keys to render methods.
        """
        return {
            "redoc": self.render_redoc,
            "swagger": self.render_swagger_ui,
            "elements": self.render_stoplight_elements,
            "rapidoc": self.render_rapidoc,
        }

    @get(
        path=["/openapi.yaml", "openapi.yml"],
        media_type=OpenAPIMediaType.OPENAPI_YAML,
        include_in_schema=False,
        sync_to_thread=False,
    )
    def retrieve_schema_yaml(self, request: Request[Any, Any, Any]) -> ASGIResponse:
        """Return the OpenAPI schema as YAML with an ``application/vnd.oai.openapi`` Content-Type header.

        Args:
            request:
                A :class:`Request <.connection.Request>` instance.

        Returns:
            A Response instance with the YAML object rendered into a string.
        """
        from yaml import dump as dump_yaml

        if self.should_serve_endpoint(request):
            if not self._dumped_yaml_schema:
                schema_json = decode_json(self._get_schema_as_json(request))
                schema_yaml = dump_yaml(schema_json, default_flow_style=False)
                self._dumped_yaml_schema = schema_yaml.encode("utf-8")
            return ASGIResponse(body=self._dumped_yaml_schema, media_type=OpenAPIMediaType.OPENAPI_YAML)
        return ASGIResponse(body=b"", status_code=HTTP_404_NOT_FOUND, media_type=MediaType.HTML)

    @get(
        path="/openapi.json",
        media_type=OpenAPIMediaType.OPENAPI_JSON,
        include_in_schema=False,
        sync_to_thread=False,
        name=OPENAPI_JSON_HANDLER_NAME,
    )
    def retrieve_schema_json(self, request: Request[Any, Any, Any]) -> ASGIResponse:
        """Return the OpenAPI schema as JSON with an ``application/vnd.oai.openapi+json`` Content-Type header.

        Args:
            request:
                A :class:`Request <.connection.Request>` instance.

        Returns:
            A Response instance with the JSON object rendered into a string.
        """
        if self.should_serve_endpoint(request):
            return ASGIResponse(
                body=self._get_schema_as_json(request),
                media_type=OpenAPIMediaType.OPENAPI_JSON,
            )
        return ASGIResponse(body=b"", status_code=HTTP_404_NOT_FOUND, media_type=MediaType.HTML)

    @get(path="/", include_in_schema=False, sync_to_thread=False)
    def root(self, request: Request[Any, Any, Any]) -> ASGIResponse:
        """Render a static documentation site.

         The site to be rendered is based on the ``root_schema_site`` value set in the application's
         :class:`OpenAPIConfig <.openapi.OpenAPIConfig>`. Defaults to ``redoc``.

        Args:
            request:
                A :class:`Request <.connection.Request>` instance.

        Returns:
            A response with the rendered site defined in root_schema_site.

        Raises:
            ImproperlyConfiguredException: If the application ``openapi_config`` attribute is ``None``.
        """
        config = request.app.openapi_config
        if not config:  # pragma: no cover
            raise ImproperlyConfiguredException(OPENAPI_NOT_INITIALIZED)

        render_method = self.render_methods_map[config.root_schema_site or _DEFAULT_SCHEMA_SITE]

        if self.should_serve_endpoint(request):
            return ASGIResponse(body=render_method(request), media_type=MediaType.HTML)
        return ASGIResponse(body=self.render_404_page(), status_code=HTTP_404_NOT_FOUND, media_type=MediaType.HTML)

    @get(path="/swagger", include_in_schema=False, sync_to_thread=False)
    def swagger_ui(self, request: Request[Any, Any, Any]) -> ASGIResponse:
        """Route handler responsible for rendering Swagger-UI.

        Args:
            request:
                A :class:`Request <.connection.Request>` instance.

        Returns:
            A response with a rendered swagger documentation site
        """
        if self.should_serve_endpoint(request):
            return ASGIResponse(body=self.render_swagger_ui(request), media_type=MediaType.HTML)
        return ASGIResponse(body=self.render_404_page(), status_code=HTTP_404_NOT_FOUND, media_type=MediaType.HTML)

    @get(path="/elements", media_type=MediaType.HTML, include_in_schema=False, sync_to_thread=False)
    def stoplight_elements(self, request: Request[Any, Any, Any]) -> ASGIResponse:
        """Route handler responsible for rendering StopLight Elements.

        Args:
            request:
                A :class:`Request <.connection.Request>` instance.

        Returns:
            A response with a rendered stoplight elements documentation site
        """
        if self.should_serve_endpoint(request):
            return ASGIResponse(body=self.render_stoplight_elements(request), media_type=MediaType.HTML)
        return ASGIResponse(body=self.render_404_page(), status_code=HTTP_404_NOT_FOUND, media_type=MediaType.HTML)

    @get(path="/redoc", media_type=MediaType.HTML, include_in_schema=False, sync_to_thread=False)
    def redoc(self, request: Request[Any, Any, Any]) -> ASGIResponse:  # pragma: no cover
        """Route handler responsible for rendering Redoc.

        Args:
            request:
                A :class:`Request <.connection.Request>` instance.

        Returns:
            A response with a rendered redoc documentation site
        """
        if self.should_serve_endpoint(request):
            return ASGIResponse(body=self.render_redoc(request), media_type=MediaType.HTML)
        return ASGIResponse(body=self.render_404_page(), status_code=HTTP_404_NOT_FOUND, media_type=MediaType.HTML)

    @get(path="/rapidoc", media_type=MediaType.HTML, include_in_schema=False, sync_to_thread=False)
    def rapidoc(self, request: Request[Any, Any, Any]) -> ASGIResponse:
        if self.should_serve_endpoint(request):
            return ASGIResponse(body=self.render_rapidoc(request), media_type=MediaType.HTML)
        return ASGIResponse(body=self.render_404_page(), status_code=HTTP_404_NOT_FOUND, media_type=MediaType.HTML)

    @get(path="/oauth2-redirect.html", media_type=MediaType.HTML, include_in_schema=False, sync_to_thread=False)
    def swagger_ui_oauth2_redirect(self, request: Request[Any, Any, Any]) -> ASGIResponse:  # pragma: no cover
        """Route handler responsible for rendering oauth2-redirect.html page for Swagger-UI.

        Args:
            request:
                A :class:`Request <.connection.Request>` instance.

        Returns:
            A response with a rendered oauth2-redirect.html page for Swagger-UI.
        """
        if self.should_serve_endpoint(request):
            return ASGIResponse(body=self.render_swagger_ui_oauth2_redirect(request), media_type=MediaType.HTML)
        return ASGIResponse(body=self.render_404_page(), status_code=HTTP_404_NOT_FOUND, media_type=MediaType.HTML)

    def render_swagger_ui_oauth2_redirect(self, request: Request[Any, Any, Any]) -> bytes:
        """Render an HTML oauth2-redirect.html page for Swagger-UI.

        Notes:
            - override this method to customize the template.

        Args:
            request:
                A :class:`Request <.connection.Request>` instance.

        Returns:
            A rendered html string.
        """
        return rb"""<!doctype html>
        <html lang="en-US">
        <head>
            <title>Swagger UI: OAuth2 Redirect</title>
        </head>
        <body>
        <script>
            'use strict';
            function run () {
                var oauth2 = window.opener.swaggerUIRedirectOauth2;
                var sentState = oauth2.state;
                var redirectUrl = oauth2.redirectUrl;
                var isValid, qp, arr;

                if (/code|token|error/.test(window.location.hash)) {
                    qp = window.location.hash.substring(1).replace('?', '&');
                } else {
                    qp = location.search.substring(1);
                }

                arr = qp.split("&");
                arr.forEach(function (v,i,_arr) { _arr[i] = '"' + v.replace('=', '":"') + '"';});
                qp = qp ? JSON.parse('{' + arr.join() + '}',
                        function (key, value) {
                            return key === "" ? value : decodeURIComponent(value);
                        }
                ) : {};

                isValid = qp.state === sentState;

                if ((
                oauth2.auth.schema.get("flow") === "accessCode" ||
                oauth2.auth.schema.get("flow") === "authorizationCode" ||
                oauth2.auth.schema.get("flow") === "authorization_code"
                ) && !oauth2.auth.code) {
                    if (!isValid) {
                        oauth2.errCb({
                            authId: oauth2.auth.name,
                            source: "auth",
                            level: "warning",
                            message: "Authorization may be unsafe, passed state was changed in server. The passed state wasn't returned from auth server."
                        });
                    }

                    if (qp.code) {
                        delete oauth2.state;
                        oauth2.auth.code = qp.code;
                        oauth2.callback({auth: oauth2.auth, redirectUrl: redirectUrl});
                    } else {
                        let oauthErrorMsg;
                        if (qp.error) {
                            oauthErrorMsg = "["+qp.error+"]: " +
                                (qp.error_description ? qp.error_description+ ". " : "no accessCode received from the server. ") +
                                (qp.error_uri ? "More info: "+qp.error_uri : "");
                        }

                        oauth2.errCb({
                            authId: oauth2.auth.name,
                            source: "auth",
                            level: "error",
                            message: oauthErrorMsg || "[Authorization failed]: no accessCode received from the server."
                        });
                    }
                } else {
                    oauth2.callback({auth: oauth2.auth, token: qp, isValid: isValid, redirectUrl: redirectUrl});
                }
                window.close();
            }

            if (document.readyState !== 'loading') {
                run();
            } else {
                document.addEventListener('DOMContentLoaded', function () {
                    run();
                });
            }
        </script>
        </body>
        </html>"""

    def render_swagger_ui(self, request: Request[Any, Any, Any]) -> bytes:
        """Render an HTML page for Swagger-UI.

        Notes:
            - override this method to customize the template.

        Args:
            request:
                A :class:`Request <.connection.Request>` instance.

        Returns:
            A rendered html string.
        """
        schema = self.get_schema_from_request(request)

        head = f"""
          <head>
            <title>{schema.info.title}</title>
            {self.favicon}
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="{self.swagger_css_url}" rel="stylesheet">
            <script src="{self.swagger_ui_bundle_js_url}" crossorigin></script>
            <script src="{self.swagger_ui_standalone_preset_js_url}" crossorigin></script>
            <style>{self.style}</style>
          </head>
        """

        body = f"""
          <body>
            <div id='swagger-container'/>
            <script type="text/javascript">
            const ui = SwaggerUIBundle({{
                spec: {self._get_schema_as_json(request)},
                dom_id: '#swagger-container',
                deepLinking: true,
                showExtensions: true,
                showCommonExtensions: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
            }})
            ui.initOAuth({encode_json(self.swagger_ui_init_oauth).decode('utf-8')})
            </script>
          </body>
        """

        return f"""
        <!DOCTYPE html>
            <html>
                {head}
                {body}
            </html>
        """.encode()

    def render_stoplight_elements(self, request: Request[Any, Any, Any]) -> bytes:
        """Render an HTML page for StopLight Elements.

        Notes:
            - override this method to customize the template.

        Args:
            request:
                A :class:`Request <.connection.Request>` instance.

        Returns:
            A rendered html string.
        """
        schema = self.get_schema_from_request(request)
        head = f"""
          <head>
            <title>{schema.info.title}</title>
            {self.favicon}
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <link rel="stylesheet" href="{self.stoplight_elements_css_url}">
            <script src="{self.stoplight_elements_js_url}" crossorigin></script>
            <style>{self.style}</style>
          </head>
        """

        body = f"""
          <body>
            <elements-api
                apiDescriptionUrl="{request.app.route_reverse(OPENAPI_JSON_HANDLER_NAME)}"
                router="hash"
                layout="sidebar"
            />
          </body>
        """

        return f"""
        <!DOCTYPE html>
            <html>
                {head}
                {body}
            </html>
        """.encode()

    def render_rapidoc(self, request: Request[Any, Any, Any]) -> bytes:  # pragma: no cover
        schema = self.get_schema_from_request(request)

        head = f"""
          <head>
            <title>{schema.info.title}</title>
            {self.favicon}
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <script src="{self.rapidoc_js_url}" crossorigin></script>
            <style>{self.style}</style>
          </head>
        """

        body = f"""
          <body>
            <rapi-doc spec-url="{request.app.route_reverse(OPENAPI_JSON_HANDLER_NAME)}" />
          </body>
        """

        return f"""
        <!DOCTYPE html>
            <html>
                {head}
                {body}
            </html>
        """.encode()

    def render_redoc(self, request: Request[Any, Any, Any]) -> bytes:  # pragma: no cover
        """Render an HTML page for Redoc.

        Notes:
            - override this method to customize the template.

        Args:
            request:
                A :class:`Request <.connection.Request>` instance.

        Returns:
            A rendered html string.
        """
        schema = self.get_schema_from_request(request)

        head = f"""
          <head>
            <title>{schema.info.title}</title>
            {self.favicon}
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            """

        if self.redoc_google_fonts:
            head += """
            <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
            """

        head += f"""
            <script src="{self.redoc_js_url}" crossorigin></script>
            <style>
                {self.style}
            </style>
          </head>
        """

        body = f"""
          <body>
            <div id='redoc-container'/>
            <script type="text/javascript">
                Redoc.init(
                    {self._get_schema_as_json(request)},
                    undefined,
                    document.getElementById('redoc-container')
                )
            </script>
          </body>
        """

        return f"""
        <!DOCTYPE html>
            <html>
                {head}
                {body}
            </html>
        """.encode()

    def render_404_page(self) -> bytes:
        """Render an HTML 404 page.

        Returns:
            A rendered html string.
        """

        return f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>404 Not found</title>
                {self.favicon}
                <meta charset="utf-8"/>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    {self.style}
                </style>
            </head>
            <body>
                <h1>Error 404</h1>
            </body>
        </html>
        """.encode()

    def _get_schema_as_json(self, request: Request) -> str:
        """Get the schema encoded as a JSON string."""

        if not self._dumped_json_schema:
            schema = self.get_schema_from_request(request).to_schema()
            json_encoded_schema = encode_json(schema, request.route_handler.default_serializer)
            self._dumped_json_schema = json_encoded_schema.decode("utf-8")

        return self._dumped_json_schema
