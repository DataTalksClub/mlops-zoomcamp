from __future__ import annotations

import json
from functools import partial
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import urlencode

from httpx._content import encode_json as httpx_encode_json
from httpx._content import encode_multipart_data, encode_urlencoded_data

from litestar import delete, patch, post, put
from litestar.app import Litestar
from litestar.connection import Request
from litestar.enums import HttpMethod, ParamType, RequestEncodingType, ScopeType
from litestar.handlers.http_handlers import get
from litestar.serialization import decode_json, default_serializer, encode_json
from litestar.types import DataContainerType, HTTPScope, RouteHandlerType
from litestar.types.asgi_types import ASGIVersion
from litestar.utils import get_serializer_from_scope
from litestar.utils.scope.state import ScopeState

if TYPE_CHECKING:
    from httpx._types import FileTypes

    from litestar.datastructures.cookie import Cookie
    from litestar.handlers.http_handlers import HTTPRouteHandler

_decorator_http_method_map: dict[HttpMethod, type[HTTPRouteHandler]] = {
    HttpMethod.GET: get,
    HttpMethod.POST: post,
    HttpMethod.DELETE: delete,
    HttpMethod.PATCH: patch,
    HttpMethod.PUT: put,
}


def _create_default_route_handler(
    http_method: HttpMethod, handler_kwargs: dict[str, Any] | None, app: Litestar
) -> HTTPRouteHandler:
    handler_decorator = _decorator_http_method_map[http_method]

    def _default_route_handler() -> None: ...

    handler = handler_decorator("/", sync_to_thread=False, **(handler_kwargs or {}))(_default_route_handler)
    handler.owner = app
    return handler


def _create_default_app() -> Litestar:
    return Litestar(route_handlers=[])


class RequestFactory:
    """Factory to create :class:`Request <litestar.connection.Request>` instances."""

    __slots__ = (
        "app",
        "server",
        "port",
        "root_path",
        "scheme",
        "handler_kwargs",
        "serializer",
    )

    def __init__(
        self,
        app: Litestar | None = None,
        server: str = "test.org",
        port: int = 3000,
        root_path: str = "",
        scheme: str = "http",
        handler_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """Initialize ``RequestFactory``

        Args:
             app: An instance of :class:`Litestar <litestar.app.Litestar>` to set as ``request.scope["app"]``.
             server: The server's domain.
             port: The server's port.
             root_path: Root path for the server.
             scheme: Scheme for the server.
             handler_kwargs: Kwargs to pass to the route handler created for the request

        Examples:
            .. code-block:: python

                from litestar import Litestar
                from litestar.enums import RequestEncodingType
                from litestar.testing import RequestFactory

                from tests import PersonFactory

                my_app = Litestar(route_handlers=[])
                my_server = "litestar.org"

                # Create a GET request
                query_params = {"id": 1}
                get_user_request = RequestFactory(app=my_app, server=my_server).get(
                    "/person", query_params=query_params
                )

                # Create a POST request
                new_person = PersonFactory.build()
                create_user_request = RequestFactory(app=my_app, server=my_server).post(
                    "/person", data=person
                )

                # Create a request with a special header
                headers = {"header1": "value1"}
                request_with_header = RequestFactory(app=my_app, server=my_server).get(
                    "/person", query_params=query_params, headers=headers
                )

                # Create a request with a media type
                request_with_media_type = RequestFactory(app=my_app, server=my_server).post(
                    "/person", data=person, request_media_type=RequestEncodingType.MULTI_PART
                )

        """

        self.app = app if app is not None else _create_default_app()
        self.server = server
        self.port = port
        self.root_path = root_path
        self.scheme = scheme
        self.handler_kwargs = handler_kwargs
        self.serializer = partial(default_serializer, type_encoders=self.app.type_encoders)

    def _create_scope(
        self,
        path: str,
        http_method: HttpMethod,
        session: dict[str, Any] | None = None,
        user: Any = None,
        auth: Any = None,
        query_params: dict[str, str | list[str]] | None = None,
        state: dict[str, Any] | None = None,
        path_params: dict[str, str] | None = None,
        http_version: str | None = "1.1",
        route_handler: RouteHandlerType | None = None,
    ) -> HTTPScope:
        """Create the scope for the :class:`Request <litestar.connection.Request>`.

        Args:
            path: The request's path.
            http_method: The request's HTTP method.
            session: A dictionary of session data.
            user: A value for `request.scope["user"]`.
            auth: A value for `request.scope["auth"]`.
            query_params: A dictionary of values from which the request's query will be generated.
            state: Arbitrary request state.
            path_params: A string keyed dictionary of path parameter values.
            http_version: HTTP version. Defaults to "1.1".
            route_handler: A route handler instance or method. If not provided a default handler is set.

        Returns:
            A dictionary that can be passed as a scope to the :class:`Request <litestar.connection.Request>` ctor.
        """
        if session is None:
            session = {}

        if state is None:
            state = {}

        if path_params is None:
            path_params = {}

        return HTTPScope(
            type=ScopeType.HTTP,
            method=http_method.value,
            scheme=self.scheme,
            server=(self.server, self.port),
            root_path=self.root_path.rstrip("/"),
            path=path,
            headers=[],
            app=self.app,
            session=session,
            user=user,
            auth=auth,
            query_string=urlencode(query_params, doseq=True).encode() if query_params else b"",
            path_params=path_params,
            client=(self.server, self.port),
            state=state,
            asgi=ASGIVersion(spec_version="3.0", version="3.0"),
            http_version=http_version or "1.1",
            raw_path=path.encode("ascii"),
            route_handler=route_handler
            or _create_default_route_handler(http_method, self.handler_kwargs, app=self.app),
            extensions={},
        )

    @classmethod
    def _create_cookie_header(cls, headers: dict[str, str], cookies: list[Cookie] | str | None = None) -> None:
        """Create the cookie header and add it to the ``headers`` dictionary.

        Args:
            headers: A dictionary of headers, the cookie header will be added to it.
            cookies: A string representing the cookie header or a list of "Cookie" instances.
                This value can include multiple cookies.
        """
        if not cookies:
            return

        if isinstance(cookies, list):
            cookie_header = "; ".join(cookie.to_header(header="") for cookie in cookies)
            headers[ParamType.COOKIE] = cookie_header
        elif isinstance(cookies, str):
            headers[ParamType.COOKIE] = cookies

    def _build_headers(
        self,
        headers: dict[str, str] | None = None,
        cookies: list[Cookie] | str | None = None,
    ) -> list[tuple[bytes, bytes]]:
        """Build a list of encoded headers that can be passed to the request scope.

        Args:
            headers: A dictionary of headers.
            cookies: A string representing the cookie header or a list of "Cookie" instances.
                This value can include multiple cookies.

        Returns:
            A list of encoded headers that can be passed to the request scope.
        """
        headers = headers or {}
        self._create_cookie_header(headers, cookies)
        return [
            ((key.lower()).encode("latin-1", errors="ignore"), value.encode("latin-1", errors="ignore"))
            for key, value in headers.items()
        ]

    def _create_request_with_data(
        self,
        http_method: HttpMethod,
        path: str,
        headers: dict[str, str] | None = None,
        cookies: list[Cookie] | str | None = None,
        session: dict[str, Any] | None = None,
        user: Any = None,
        auth: Any = None,
        request_media_type: RequestEncodingType = RequestEncodingType.JSON,
        data: dict[str, Any] | DataContainerType | None = None,  # pyright: ignore
        files: dict[str, FileTypes] | list[tuple[str, FileTypes]] | None = None,
        query_params: dict[str, str | list[str]] | None = None,
        state: dict[str, Any] | None = None,
        path_params: dict[str, str] | None = None,
        http_version: str | None = "1.1",
        route_handler: RouteHandlerType | None = None,
    ) -> Request[Any, Any, Any]:
        """Create a :class:`Request <litestar.connection.Request>` instance that has body (data)

        Args:
            http_method: The request's HTTP method.
            path: The request's path.
            headers: A dictionary of headers.
            cookies: A string representing the cookie header or a list of "Cookie" instances.
                This value can include multiple cookies.
            session: A dictionary of session data.
            user: A value for `request.scope["user"]`
            auth: A value for `request.scope["auth"]`
            request_media_type: The 'Content-Type' header of the request.
            data: A value for the request's body. Can be any supported serializable type.
            files: A dictionary of files to be sent with the request.
            query_params: A dictionary of values from which the request's query will be generated.
            state: Arbitrary request state.
            path_params: A string keyed dictionary of path parameter values.
            http_version: HTTP version. Defaults to "1.1".
            route_handler: A route handler instance or method. If not provided a default handler is set.

        Returns:
            A :class:`Request <litestar.connection.Request>` instance
        """
        scope = self._create_scope(
            path=path,
            http_method=http_method,
            session=session,
            user=user,
            auth=auth,
            query_params=query_params,
            state=state,
            path_params=path_params,
            http_version=http_version,
            route_handler=route_handler,
        )

        headers = headers or {}
        body = b""
        if data:
            data = json.loads(encode_json(data, serializer=get_serializer_from_scope(scope)))

            if request_media_type == RequestEncodingType.JSON:
                encoding_headers, stream = httpx_encode_json(data)
            elif request_media_type == RequestEncodingType.MULTI_PART:
                encoding_headers, stream = encode_multipart_data(  # type: ignore[assignment]
                    cast("dict[str, Any]", data), files=files or [], boundary=None
                )
            else:
                encoding_headers, stream = encode_urlencoded_data(decode_json(value=encode_json(data)))
            headers.update(encoding_headers)
            for chunk in stream:
                body += chunk
        scope_state = ScopeState.from_scope(scope)
        scope_state.body = body
        scope_state.exception_handlers = scope["route_handler"].resolve_exception_handlers()
        self._create_cookie_header(headers, cookies)
        scope["headers"] = self._build_headers(headers)
        return Request(scope=scope)

    def get(
        self,
        path: str = "/",
        headers: dict[str, str] | None = None,
        cookies: list[Cookie] | str | None = None,
        session: dict[str, Any] | None = None,
        user: Any = None,
        auth: Any = None,
        query_params: dict[str, str | list[str]] | None = None,
        state: dict[str, Any] | None = None,
        path_params: dict[str, str] | None = None,
        http_version: str | None = "1.1",
        route_handler: RouteHandlerType | None = None,
    ) -> Request[Any, Any, Any]:
        """Create a GET :class:`Request <litestar.connection.Request>` instance.

        Args:
            path: The request's path.
            headers: A dictionary of headers.
            cookies: A string representing the cookie header or a list of "Cookie" instances.
                This value can include multiple cookies.
            session: A dictionary of session data.
            user: A value for `request.scope["user"]`.
            auth: A value for `request.scope["auth"]`.
            query_params: A dictionary of values from which the request's query will be generated.
            state: Arbitrary request state.
            path_params: A string keyed dictionary of path parameter values.
            http_version: HTTP version. Defaults to "1.1".
            route_handler: A route handler instance or method. If not provided a default handler is set.

        Returns:
            A :class:`Request <litestar.connection.Request>` instance
        """
        scope = self._create_scope(
            path=path,
            http_method=HttpMethod.GET,
            session=session,
            user=user,
            auth=auth,
            query_params=query_params,
            state=state,
            path_params=path_params,
            http_version=http_version,
            route_handler=route_handler,
        )

        scope["headers"] = self._build_headers(headers, cookies)
        return Request(scope=scope)

    def post(
        self,
        path: str = "/",
        headers: dict[str, str] | None = None,
        cookies: list[Cookie] | str | None = None,
        session: dict[str, Any] | None = None,
        user: Any = None,
        auth: Any = None,
        request_media_type: RequestEncodingType = RequestEncodingType.JSON,
        data: dict[str, Any] | DataContainerType | None = None,  # pyright: ignore
        query_params: dict[str, str | list[str]] | None = None,
        state: dict[str, Any] | None = None,
        path_params: dict[str, str] | None = None,
        http_version: str | None = "1.1",
        route_handler: RouteHandlerType | None = None,
    ) -> Request[Any, Any, Any]:
        """Create a POST :class:`Request <litestar.connection.Request>` instance.

        Args:
            path: The request's path.
            headers: A dictionary of headers.
            cookies: A string representing the cookie header or a list of "Cookie" instances.
                This value can include multiple cookies.
            session: A dictionary of session data.
            user: A value for `request.scope["user"]`.
            auth: A value for `request.scope["auth"]`.
            request_media_type: The 'Content-Type' header of the request.
            data: A value for the request's body. Can be any supported serializable type.
            query_params: A dictionary of values from which the request's query will be generated.
            state: Arbitrary request state.
            path_params: A string keyed dictionary of path parameter values.
            http_version: HTTP version. Defaults to "1.1".
            route_handler: A route handler instance or method. If not provided a default handler is set.

        Returns:
            A :class:`Request <litestar.connection.Request>` instance
        """
        return self._create_request_with_data(
            auth=auth,
            cookies=cookies,
            data=data,
            headers=headers,
            http_method=HttpMethod.POST,
            path=path,
            query_params=query_params,
            request_media_type=request_media_type,
            session=session,
            user=user,
            state=state,
            path_params=path_params,
            http_version=http_version,
            route_handler=route_handler,
        )

    def put(
        self,
        path: str = "/",
        headers: dict[str, str] | None = None,
        cookies: list[Cookie] | str | None = None,
        session: dict[str, Any] | None = None,
        user: Any = None,
        auth: Any = None,
        request_media_type: RequestEncodingType = RequestEncodingType.JSON,
        data: dict[str, Any] | DataContainerType | None = None,  # pyright: ignore
        query_params: dict[str, str | list[str]] | None = None,
        state: dict[str, Any] | None = None,
        path_params: dict[str, str] | None = None,
        http_version: str | None = "1.1",
        route_handler: RouteHandlerType | None = None,
    ) -> Request[Any, Any, Any]:
        """Create a PUT :class:`Request <litestar.connection.Request>` instance.

        Args:
            path: The request's path.
            headers: A dictionary of headers.
            cookies: A string representing the cookie header or a list of "Cookie" instances.
                This value can include multiple cookies.
            session: A dictionary of session data.
            user: A value for `request.scope["user"]`.
            auth: A value for `request.scope["auth"]`.
            request_media_type: The 'Content-Type' header of the request.
            data: A value for the request's body. Can be any supported serializable type.
            query_params: A dictionary of values from which the request's query will be generated.
            state: Arbitrary request state.
            path_params: A string keyed dictionary of path parameter values.
            http_version: HTTP version. Defaults to "1.1".
            route_handler: A route handler instance or method. If not provided a default handler is set.

        Returns:
            A :class:`Request <litestar.connection.Request>` instance
        """
        return self._create_request_with_data(
            auth=auth,
            cookies=cookies,
            data=data,
            headers=headers,
            http_method=HttpMethod.PUT,
            path=path,
            query_params=query_params,
            request_media_type=request_media_type,
            session=session,
            user=user,
            state=state,
            path_params=path_params,
            http_version=http_version,
            route_handler=route_handler,
        )

    def patch(
        self,
        path: str = "/",
        headers: dict[str, str] | None = None,
        cookies: list[Cookie] | str | None = None,
        session: dict[str, Any] | None = None,
        user: Any = None,
        auth: Any = None,
        request_media_type: RequestEncodingType = RequestEncodingType.JSON,
        data: dict[str, Any] | DataContainerType | None = None,  # pyright: ignore
        query_params: dict[str, str | list[str]] | None = None,
        state: dict[str, Any] | None = None,
        path_params: dict[str, str] | None = None,
        http_version: str | None = "1.1",
        route_handler: RouteHandlerType | None = None,
    ) -> Request[Any, Any, Any]:
        """Create a PATCH :class:`Request <litestar.connection.Request>` instance.

        Args:
            path: The request's path.
            headers: A dictionary of headers.
            cookies: A string representing the cookie header or a list of "Cookie" instances.
                This value can include multiple cookies.
            session: A dictionary of session data.
            user: A value for `request.scope["user"]`.
            auth: A value for `request.scope["auth"]`.
            request_media_type: The 'Content-Type' header of the request.
            data: A value for the request's body. Can be any supported serializable type.
            query_params: A dictionary of values from which the request's query will be generated.
            state: Arbitrary request state.
            path_params: A string keyed dictionary of path parameter values.
            http_version: HTTP version. Defaults to "1.1".
            route_handler: A route handler instance or method. If not provided a default handler is set.

        Returns:
            A :class:`Request <litestar.connection.Request>` instance
        """
        return self._create_request_with_data(
            auth=auth,
            cookies=cookies,
            data=data,
            headers=headers,
            http_method=HttpMethod.PATCH,
            path=path,
            query_params=query_params,
            request_media_type=request_media_type,
            session=session,
            user=user,
            state=state,
            path_params=path_params,
            http_version=http_version,
            route_handler=route_handler,
        )

    def delete(
        self,
        path: str = "/",
        headers: dict[str, str] | None = None,
        cookies: list[Cookie] | str | None = None,
        session: dict[str, Any] | None = None,
        user: Any = None,
        auth: Any = None,
        query_params: dict[str, str | list[str]] | None = None,
        state: dict[str, Any] | None = None,
        path_params: dict[str, str] | None = None,
        http_version: str | None = "1.1",
        route_handler: RouteHandlerType | None = None,
    ) -> Request[Any, Any, Any]:
        """Create a POST :class:`Request <litestar.connection.Request>` instance.

        Args:
            path: The request's path.
            headers: A dictionary of headers.
            cookies: A string representing the cookie header or a list of "Cookie" instances.
                This value can include multiple cookies.
            session: A dictionary of session data.
            user: A value for `request.scope["user"]`.
            auth: A value for `request.scope["auth"]`.
            query_params: A dictionary of values from which the request's query will be generated.
            state: Arbitrary request state.
            path_params: A string keyed dictionary of path parameter values.
            http_version: HTTP version. Defaults to "1.1".
            route_handler: A route handler instance or method. If not provided a default handler is set.

        Returns:
            A :class:`Request <litestar.connection.Request>` instance
        """
        scope = self._create_scope(
            path=path,
            http_method=HttpMethod.DELETE,
            session=session,
            user=user,
            auth=auth,
            query_params=query_params,
            state=state,
            path_params=path_params,
            http_version=http_version,
            route_handler=route_handler,
        )
        scope["headers"] = self._build_headers(headers, cookies)
        return Request(scope=scope)
