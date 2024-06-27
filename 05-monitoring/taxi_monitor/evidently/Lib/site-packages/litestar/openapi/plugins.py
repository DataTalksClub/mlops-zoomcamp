from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Sequence

import msgspec
import yaml

from litestar.constants import OPENAPI_JSON_HANDLER_NAME
from litestar.enums import MediaType, OpenAPIMediaType
from litestar.handlers import get
from litestar.serialization import encode_json, get_serializer

if TYPE_CHECKING:
    from litestar.connection import Request
    from litestar.router import Router

__all__ = (
    "OpenAPIRenderPlugin",
    "RapidocRenderPlugin",
    "RedocRenderPlugin",
    "ScalarRenderPlugin",
    "StoplightRenderPlugin",
    "SwaggerRenderPlugin",
    "YamlRenderPlugin",
)

_favicon_url = "https://cdn.jsdelivr.net/gh/litestar-org/branding@main/assets/Branding%20-%20PNG%20-%20Transparent/Badge%20-%20Blue%20and%20Yellow.png"
_default_favicon = f"<link rel='icon' type='image/png' href='{_favicon_url}'>"
_default_style = "<style>body { margin: 0; padding: 0 }</style>"


class OpenAPIRenderPlugin(ABC):
    """Base class for OpenAPI UI render plugins."""

    paths: list[str]

    def __init__(
        self,
        *,
        path: str | Sequence[str],
        media_type: MediaType | OpenAPIMediaType = MediaType.HTML,
        favicon: str = _default_favicon,
        style: str = _default_style,
    ) -> None:
        """Initialize the OpenAPI UI render plugin.

        Args:
            path: Path to serve the OpenAPI UI at.
            media_type: Media type for the handler.
            favicon: Html <link> tag for the favicon.
            style: Base styling of the html body.
        """
        self.paths = [path] if isinstance(path, str) else list(path)
        self.media_type = media_type
        self.favicon = favicon
        self.style = style

    @staticmethod
    def render_json(request: Request, openapi_schema: dict[str, Any]) -> bytes:
        """Render the OpenAPI schema as JSON.

        Args:
            request: The request that triggered the render.
            openapi_schema: The OpenAPI schema as a dictionary.

        Returns:
            The rendered JSON.
        """
        return encode_json(openapi_schema, serializer=get_serializer(request.route_handler.resolve_type_encoders()))

    @abstractmethod
    def render(self, request: Request, openapi_schema: dict[str, Any]) -> bytes:
        """Render the OpenAPI UI.

        Args:
            request: The request that triggered the render.
            openapi_schema: The OpenAPI schema as a dictionary.

        Returns:
            The rendered HTML.
        """
        raise NotImplementedError

    @staticmethod
    def get_openapi_json_route(request: Request) -> str:
        """Get the route for the OpenAPI JSON schema.

        Returns:
            The route for the OpenAPI JSON schema.
        """
        return request.app.route_reverse(OPENAPI_JSON_HANDLER_NAME)

    def receive_router(self, router: Router) -> None:
        """Receive the router that serves the OpenAPI UI.

        Can be used by plugins to additionally configure the router, e.g. to add
        additional routes.

        Args:
            router: The router that serves the OpenAPI UI.
        """
        return

    def has_path(self, path: str) -> bool:
        """Check if the plugin has a path.

        Args:
            path: The path to check.

        Returns:
            True if the plugin has the path, False otherwise.
        """
        return path in self.paths


class JsonRenderPlugin(OpenAPIRenderPlugin):
    """Render the OpenAPI schema as JSON."""

    def __init__(
        self,
        *,
        path: str | Sequence[str] = "/openapi.json",
        media_type: MediaType | OpenAPIMediaType = OpenAPIMediaType.OPENAPI_JSON,
        **kwargs: Any,
    ) -> None:
        """Initialize the OpenAPI UI render plugin.

        Args:
            path: Path to serve the OpenAPI UI at.
            media_type: Media type for the handler.
            **kwargs: Additional arguments to pass to the base class.

        """
        super().__init__(path=path, media_type=media_type, **kwargs)

    def render(self, request: Request, openapi_schema: dict[str, Any]) -> bytes:
        """Render an OpenAPI schema as JSON.

        Args:
            request: The request.
            openapi_schema: The OpenAPI schema as a dictionary.

        Returns:
            The rendered OpenAPI schema as JSON.
        """
        return self.render_json(request, openapi_schema)


class YamlRenderPlugin(OpenAPIRenderPlugin):
    """Render an OpenAPI schema as YAML."""

    def __init__(
        self,
        *,
        path: str | Sequence[str] = ("/openapi.yaml", "/openapi.yml"),
        media_type: MediaType | OpenAPIMediaType = OpenAPIMediaType.OPENAPI_YAML,
        **kwargs: Any,
    ) -> None:
        """Initialize the OpenAPI UI render plugin.

        Args:
            path: Path to serve the OpenAPI UI at.
            media_type: Media type for the handler.
            **kwargs: Additional arguments to pass to the base class.
        """
        super().__init__(path=path, media_type=media_type, **kwargs)

    def render(self, request: Request, openapi_schema: dict[str, Any]) -> bytes:
        """Render an OpenAPI schema as YAML.

        Args:
            request: The request.
            openapi_schema: The OpenAPI schema as a dictionary.

        Returns:
            The rendered OpenAPI schema as YAML.
        """
        # using msgspec.to_builtins() ensures that any examples generated by polyfactory that have the
        # UNSET value (possible if the examples are being generated for a partial DTO model which makes
        # every type a union with UNSET) are stripped out.
        openapi_schema = msgspec.to_builtins(
            openapi_schema, enc_hook=get_serializer(request.route_handler.resolve_type_encoders())
        )
        return yaml.dump(openapi_schema, default_flow_style=False).encode("utf-8")


class RapidocRenderPlugin(OpenAPIRenderPlugin):
    """Render an OpenAPI schema using Rapidoc."""

    def __init__(
        self,
        *,
        version: str = "9.3.4",
        js_url: str | None = None,
        path: str | Sequence[str] = "/rapidoc",
        **kwargs: Any,
    ) -> None:
        """Initialize the OpenAPI UI render plugin.

        Args:
            version: Rapidoc version to download from the CDN. If js_url is provided, this is ignored.
            js_url: Download url for the RapiDoc JS bundle. If not provided, the version will be used to construct the
                url.
            path: Path to serve the OpenAPI UI at.
            **kwargs: Additional arguments to pass to the base class.
        """
        self.js_url = js_url or f"https://unpkg.com/rapidoc@{version}/dist/rapidoc-min.js"
        super().__init__(path=path, **kwargs)

    def render(self, request: Request, openapi_schema: dict[str, Any]) -> bytes:
        """Render an HTML page for Rapidoc.

        .. note:: Override this method to customize the template.

        Args:
            request: The request.
            openapi_schema: The OpenAPI schema as a dictionary.

        Returns:
            A rendered html string.
        """

        head = f"""
          <head>
            <title>{openapi_schema["info"]["title"]}</title>
            {self.favicon}
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <script src="{self.js_url}" crossorigin></script>
            {self.style}
          </head>
        """

        body = f"""
          <body>
            <rapi-doc spec-url="{self.get_openapi_json_route(request)}" />
          </body>
        """

        return f"""
        <!DOCTYPE html>
            <html>
                {head}
                {body}
            </html>
        """.encode()


class RedocRenderPlugin(OpenAPIRenderPlugin):
    """Render an OpenAPI schema using Redoc."""

    def __init__(
        self,
        *,
        version: str = "next",
        js_url: str | None = None,
        google_fonts: bool = True,
        path: str | Sequence[str] = "/redoc",
        **kwargs: Any,
    ) -> None:
        """Initialize the OpenAPI UI render plugin.

        Args:
            version: Redoc version to download from the CDN. If js_url is provided, this is ignored.
            js_url: Download url for the Redoc JS bundle. If not provided, the version will be used to construct the url.
            google_fonts: Download google fonts via CDN. Should be set to False when not using a CDN.
            path: Path to serve the OpenAPI UI at.
            **kwargs: Additional arguments to pass to the base class.
        """
        self.js_url = js_url or f"https://cdn.jsdelivr.net/npm/redoc@{version}/bundles/redoc.standalone.js"
        self.google_fonts = google_fonts
        super().__init__(path=path, **kwargs)

    def render(self, request: Request, openapi_schema: dict[str, Any]) -> bytes:
        """Render an HTML page for Redoc.

        .. note:: override this method to customize the template.

        Args:
            request: The request.
            openapi_schema: The OpenAPI schema as a dictionary.

        Returns:
            A rendered html string.
        """

        head = f"""
          <head>
            <title>{openapi_schema["info"]["title"]}</title>
            {self.favicon}
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            """

        if self.google_fonts:
            head += """
            <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
            """

        head += f"""
            <script src="{self.js_url}" crossorigin></script>
            {self.style}
          </head>
        """

        body = b"".join(
            [
                b"<body><div id='redoc-container'/><script type='text/javascript'>Redoc.init(",
                self.render_json(request, openapi_schema),
                b",undefined,document.getElementById('redoc-container'))</script></body>",
            ]
        )

        return b"".join(
            [
                b"<!DOCTYPE html><html>",
                head.encode(),
                body,
                b"</html>",
            ]
        )


class ScalarRenderPlugin(OpenAPIRenderPlugin):
    """Plugin to render an OpenAPI schema using Scalar.

    .. versionadded:: 2.8.0
    """

    _default_css_url = "https://cdn.jsdelivr.net/gh/litestar-org/branding@main/assets/openapi/scalar.css"

    def __init__(
        self,
        *,
        version: str = "1.19.5",
        js_url: str | None = None,
        css_url: str | None = None,
        path: str | Sequence[str] = "/scalar",
        **kwargs: Any,
    ) -> None:
        """Initialize the Scalar OpenAPI UI render plugin.

        Args:
            version: Scalar version to download from the CDN.
                If js_url is provided, this is ignored.
            js_url: Download url for the Scalar JS bundle.
                If not provided, the version will be used to construct the url.
            css_url: Download url for the Scalar CSS bundle.
                If not provided, the Litestar-provided CSS will be used.
            path: Path to serve the OpenAPI UI at.
            **kwargs: Additional arguments to pass to the base class.
        """
        self.js_url = js_url or f"https://cdn.jsdelivr.net/npm/@scalar/api-reference@{version}"
        self.css_url = css_url or self._default_css_url
        super().__init__(path=path, **kwargs)

    def render(self, request: Request, openapi_schema: dict[str, Any]) -> bytes:
        """Render an HTMl page for Scalar.

        .. note:: Override this method to customize the template.

        Args:
            request: The request.
            openapi_schema: The OpenAPI schema as a dictionary.

        Returns:
            A rendered html string.
        """
        head = f"""
                  <head>
                    <title>{openapi_schema["info"]["title"]}</title>
                    {self.style}
                    <meta charset="utf-8"/>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    {self.favicon}
                    <link rel="stylesheet" type="text/css" href="{self.css_url}">
                  </head>
                """

        body = f"""
                <noscript>
                    Scalar requires Javascript to function. Please enable it to browse the documentation.
                </noscript>
                <script
                  id="api-reference"
                  data-url="{self.get_openapi_json_route(request)}">
                </script>
                <script src="{self.js_url}" crossorigin></script>
                """

        return f"""
                <!DOCTYPE html>
                    <html>
                        {head}
                        {body}
                    </html>
                """.encode()


class StoplightRenderPlugin(OpenAPIRenderPlugin):
    """Render an OpenAPI schema using StopLight Elements."""

    def __init__(
        self,
        *,
        version: str = "7.7.18",
        js_url: str | None = None,
        css_url: str | None = None,
        path: str | Sequence[str] = "/elements",
        **kwargs: Any,
    ) -> None:
        """Initialize the OpenAPI UI render plugin.

        Args:
            version: StopLight Elements version to download from the CDN. If js_url is provided, this is ignored.
            js_url: Download url for the StopLight Elements JS bundle. If not provided, the version will be used to
                construct the url.
            css_url: Download url for the StopLight Elements CSS bundle. If not provided, the version will be used to
                construct the url.
            path: Path to serve the OpenAPI UI at.
            **kwargs: Additional arguments to pass to the base class.
        """
        self.js_url = js_url or f"https://unpkg.com/@stoplight/elements@{version}/web-components.min.js"
        self.css_url = css_url or f"https://unpkg.com/@stoplight/elements@{version}/styles.min.css"
        super().__init__(path=path, **kwargs)

    def render(self, request: Request, openapi_schema: dict[str, Any]) -> bytes:
        """Render an HTML page for StopLight Elements.

        .. note:: Override this method to customize the template.

        Args:
            request: The request.
            openapi_schema: The OpenAPI schema as a dictionary.

        Returns:
            A rendered html string.
        """
        head = f"""
          <head>
            <title>{openapi_schema["info"]["title"]}</title>
            {self.favicon}
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <link rel="stylesheet" href="{self.css_url}">
            <script src="{self.js_url}" crossorigin></script>
            {self.style}
          </head>
        """

        body = f"""
          <body>
            <elements-api
                apiDescriptionUrl="{self.get_openapi_json_route(request)}"
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


class SwaggerRenderPlugin(OpenAPIRenderPlugin):
    """Render an OpenAPI schema using Swagger-UI."""

    def __init__(
        self,
        version: str = "5.1.3",
        js_url: str | None = None,
        css_url: str | None = None,
        standalone_preset_js_url: str | None = None,
        init_oauth: dict[str, Any] | bytes | None = None,
        path: str | Sequence[str] = "/swagger",
        **kwargs: Any,
    ) -> None:
        """Initialize the OpenAPI UI render plugin.

        Args:
            version: SwaggerUI version to download from the CDN. If js_url is provided, this is ignored.
            js_url: Download url for the Swagger UI JS bundle. If not provided, the version will be used to construct
                the url.
            css_url: Download url for the Swagger UI CSS bundle. If not provided, the version will be used to construct
                the url.
            standalone_preset_js_url: Download url for the Swagger Standalone Preset JS bundle. If not provided, the
                version will be used to construct the url.
            init_oauth: JSON to initialize Swagger UI OAuth2 by calling the ``initOAuth`` method.
                Refer to the following URL for details:
                `Swagger-UI <https://swagger.io/docs/open-source-tools/swagger-ui/usage/oauth2/>`_.
            path: Path to serve the OpenAPI UI at.
            **kwargs: Additional arguments to pass to the base class.
        """
        self.js_url = js_url or f"https://cdn.jsdelivr.net/npm/swagger-ui-dist@{version}/swagger-ui-bundle.js"
        self.css_url = css_url or f"https://cdn.jsdelivr.net/npm/swagger-ui-dist@{version}/swagger-ui.css"
        self.standalone_preset_js_url = (
            standalone_preset_js_url
            or f"https://cdn.jsdelivr.net/npm/swagger-ui-dist@{version}/swagger-ui-standalone-preset.js"
        )
        self.init_oauth = init_oauth or {}
        super().__init__(path=path, **kwargs)

    def render(self, request: Request, openapi_schema: dict[str, Any]) -> bytes:
        """Render an HTML page for Swagger-UI.

        Notes:
            - override this method to customize the template.

        Args:
            request: The request.
            openapi_schema: The OpenAPI schema as a dictionary.

        Returns:
            A rendered html string.
        """

        head = f"""
          <head>
            <title>{openapi_schema["info"]["title"]}</title>
            {self.favicon}
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="{self.css_url}" rel="stylesheet">
            <script src="{self.js_url}" crossorigin></script>
            <script src="{self.standalone_preset_js_url}" crossorigin></script>
            {self.style}
          </head>
        """

        body = b"".join(
            [
                b"""
            <body>
              <div id='swagger-container'/>
                <script type='text/javascript'>
                const ui = SwaggerUIBundle({
                  spec: """,
                self.render_json(request, openapi_schema),
                b""",
                  dom_id: '#swagger-container',
                  deepLinking: true,
                  showExtensions: true,
                  showCommonExtensions: true,
                  presets: [
                      SwaggerUIBundle.presets.apis,
                      SwaggerUIBundle.SwaggerUIStandalonePreset
                  ],
                })
            ui.initOAuth(""",
                encode_json(self.init_oauth),
                b""")
            </script>
          </body>
        """,
            ]
        )

        return b"".join([b"<!DOCTYPE html><html>", head.encode(), body, b"</html>"])

    def receive_router(self, router: Router) -> None:
        """Receive the router that serves the OpenAPI UI.

        Adds a route to serve the OAuth2 redirect page.

        Args:
            router: The router that serves the OpenAPI UI.
        """
        router.register(
            get("/oauth2-redirect.html", media_type=MediaType.HTML, sync_to_thread=False)(self.render_oauth2_redirect),
        )

    @staticmethod
    def render_oauth2_redirect() -> bytes:
        """Render an HTML oauth2-redirect.html page for Swagger-UI.

        .. note:: Override this method to customize the template.

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
