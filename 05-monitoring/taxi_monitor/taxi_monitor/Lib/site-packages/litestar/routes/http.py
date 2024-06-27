from __future__ import annotations

from itertools import chain
from typing import TYPE_CHECKING, Any, cast

from msgspec.msgpack import decode as _decode_msgpack_plain

from litestar.datastructures.upload_file import UploadFile
from litestar.enums import HttpMethod, MediaType, ScopeType
from litestar.exceptions import ClientException, ImproperlyConfiguredException, SerializationException
from litestar.handlers.http_handlers import HTTPRouteHandler
from litestar.response import Response
from litestar.routes.base import BaseRoute
from litestar.status_codes import HTTP_204_NO_CONTENT
from litestar.types.empty import Empty
from litestar.utils.scope.state import ScopeState

if TYPE_CHECKING:
    from litestar._kwargs import KwargsModel
    from litestar._kwargs.cleanup import DependencyCleanupGroup
    from litestar.connection import Request
    from litestar.types import ASGIApp, HTTPScope, Method, Receive, Scope, Send


class HTTPRoute(BaseRoute):
    """An HTTP route, capable of handling multiple ``HTTPRouteHandler``\\ s."""  # noqa: D301

    __slots__ = (
        "route_handler_map",
        "route_handlers",
    )

    def __init__(
        self,
        *,
        path: str,
        route_handlers: list[HTTPRouteHandler],
    ) -> None:
        """Initialize ``HTTPRoute``.

        Args:
            path: The path for the route.
            route_handlers: A list of :class:`~.handlers.HTTPRouteHandler`.
        """
        methods = list(chain.from_iterable([route_handler.http_methods for route_handler in route_handlers]))
        if "OPTIONS" not in methods:
            methods.append("OPTIONS")
            options_handler = self.create_options_handler(path)
            options_handler.owner = route_handlers[0].owner
            route_handlers.append(options_handler)

        self.route_handlers = route_handlers
        self.route_handler_map: dict[Method, tuple[HTTPRouteHandler, KwargsModel]] = {}

        super().__init__(
            methods=methods,
            path=path,
            scope_type=ScopeType.HTTP,
            handler_names=[route_handler.handler_name for route_handler in self.route_handlers],
        )

    async def handle(self, scope: HTTPScope, receive: Receive, send: Send) -> None:  # type: ignore[override]
        """ASGI app that creates a Request from the passed in args, determines which handler function to call and then
        handles the call.

        Args:
            scope: The ASGI connection scope.
            receive: The ASGI receive function.
            send: The ASGI send function.

        Returns:
            None
        """
        route_handler, parameter_model = self.route_handler_map[scope["method"]]
        request: Request[Any, Any, Any] = route_handler.resolve_request_class()(scope=scope, receive=receive, send=send)

        if route_handler.resolve_guards():
            await route_handler.authorize_connection(connection=request)

        response = await self._get_response_for_request(
            scope=scope, request=request, route_handler=route_handler, parameter_model=parameter_model
        )

        await response(scope, receive, send)

        if after_response_handler := route_handler.resolve_after_response():
            await after_response_handler(request)

        if form_data := scope.get("_form", {}):
            await self._cleanup_temporary_files(form_data=cast("dict[str, Any]", form_data))

    def create_handler_map(self) -> None:
        """Parse the ``router_handlers`` of this route and return a mapping of
        http- methods and route handlers.
        """
        for route_handler in self.route_handlers:
            kwargs_model = route_handler.create_kwargs_model(path_parameters=self.path_parameters)
            for http_method in route_handler.http_methods:
                if self.route_handler_map.get(http_method):
                    raise ImproperlyConfiguredException(
                        f"Handler already registered for path {self.path!r} and http method {http_method}"
                    )
                self.route_handler_map[http_method] = (route_handler, kwargs_model)

    async def _get_response_for_request(
        self,
        scope: Scope,
        request: Request[Any, Any, Any],
        route_handler: HTTPRouteHandler,
        parameter_model: KwargsModel,
    ) -> ASGIApp:
        """Return a response for the request.

        If caching is enabled and a response exist in the cache, the cached response will be returned.
        If caching is enabled and a response does not exist in the cache, the newly created
        response will be cached.

        Args:
            scope: The Request's scope
            request: The Request instance
            route_handler: The HTTPRouteHandler instance
            parameter_model: The Handler's KwargsModel

        Returns:
            An instance of Response or a compatible ASGIApp or a subclass of it
        """
        if route_handler.cache and (
            response := await self._get_cached_response(request=request, route_handler=route_handler)
        ):
            return response

        return await self._call_handler_function(
            scope=scope, request=request, parameter_model=parameter_model, route_handler=route_handler
        )

    async def _call_handler_function(
        self, scope: Scope, request: Request, parameter_model: KwargsModel, route_handler: HTTPRouteHandler
    ) -> ASGIApp:
        """Call the before request handlers, retrieve any data required for the route handler, and call the route
        handler's ``to_response`` method.

        This is wrapped in a try except block - and if an exception is raised,
        it tries to pass it to an appropriate exception handler - if defined.
        """
        response_data: Any = None
        cleanup_group: DependencyCleanupGroup | None = None

        if before_request_handler := route_handler.resolve_before_request():
            response_data = await before_request_handler(request)

        if not response_data:
            response_data, cleanup_group = await self._get_response_data(
                route_handler=route_handler, parameter_model=parameter_model, request=request
            )

        response: ASGIApp = await route_handler.to_response(app=scope["app"], data=response_data, request=request)

        if cleanup_group:
            await cleanup_group.cleanup()

        return response

    @staticmethod
    async def _get_response_data(
        route_handler: HTTPRouteHandler, parameter_model: KwargsModel, request: Request
    ) -> tuple[Any, DependencyCleanupGroup | None]:
        """Determine what kwargs are required for the given route handler's ``fn`` and calls it."""
        parsed_kwargs: dict[str, Any] = {}
        cleanup_group: DependencyCleanupGroup | None = None

        if parameter_model.has_kwargs and route_handler.signature_model:
            kwargs = parameter_model.to_kwargs(connection=request)

            if "data" in kwargs:
                try:
                    data = await kwargs["data"]
                except SerializationException as e:
                    raise ClientException(str(e)) from e

                if data is Empty:
                    del kwargs["data"]
                else:
                    kwargs["data"] = data

            if "body" in kwargs:
                kwargs["body"] = await kwargs["body"]

            if parameter_model.dependency_batches:
                cleanup_group = await parameter_model.resolve_dependencies(request, kwargs)

            parsed_kwargs = route_handler.signature_model.parse_values_from_connection_kwargs(
                connection=request, **kwargs
            )

        if cleanup_group:
            async with cleanup_group:
                data = (
                    route_handler.fn(**parsed_kwargs)
                    if route_handler.has_sync_callable
                    else await route_handler.fn(**parsed_kwargs)
                )
        elif route_handler.has_sync_callable:
            data = route_handler.fn(**parsed_kwargs)
        else:
            data = await route_handler.fn(**parsed_kwargs)

        return data, cleanup_group

    @staticmethod
    async def _get_cached_response(request: Request, route_handler: HTTPRouteHandler) -> ASGIApp | None:
        """Retrieve and un-pickle the cached response, if existing.

        Args:
            request: The :class:`Request <litestar.connection.Request>` instance
            route_handler: The :class:`~.handlers.HTTPRouteHandler` instance

        Returns:
            A cached response instance, if existing.
        """

        cache_config = request.app.response_cache_config
        cache_key = (route_handler.cache_key_builder or cache_config.key_builder)(request)
        store = cache_config.get_store_from_app(request.app)

        if not (cached_response_data := await store.get(key=cache_key)):
            return None

        # we use the regular msgspec.msgpack.decode here since we don't need any of
        # the added decoders
        messages = _decode_msgpack_plain(cached_response_data)

        async def cached_response(scope: Scope, receive: Receive, send: Send) -> None:
            ScopeState.from_scope(scope).is_cached = True
            for message in messages:
                await send(message)

        return cached_response

    def create_options_handler(self, path: str) -> HTTPRouteHandler:
        """Args:
            path: The route path

        Returns:
            An HTTP route handler for OPTIONS requests.
        """

        def options_handler(scope: Scope) -> Response:
            """Handler function for OPTIONS requests.

            Args:
                scope: The ASGI Scope.

            Returns:
                Response
            """
            return Response(
                content=None,
                status_code=HTTP_204_NO_CONTENT,
                headers={"Allow": ", ".join(sorted(self.methods))},  # pyright: ignore
                media_type=MediaType.TEXT,
            )

        return HTTPRouteHandler(
            path=path,
            http_method=[HttpMethod.OPTIONS],
            include_in_schema=False,
            sync_to_thread=False,
        )(options_handler)

    @staticmethod
    async def _cleanup_temporary_files(form_data: dict[str, Any]) -> None:
        for v in form_data.values():
            if isinstance(v, UploadFile) and not v.file.closed:
                await v.close()
