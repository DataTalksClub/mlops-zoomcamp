from __future__ import annotations

import types
from collections import defaultdict
from copy import deepcopy
from operator import attrgetter
from typing import TYPE_CHECKING, Any, Mapping, Sequence, cast

from litestar._layers.utils import narrow_response_cookies, narrow_response_headers
from litestar.exceptions import ImproperlyConfiguredException
from litestar.handlers.base import BaseRouteHandler
from litestar.handlers.http_handlers import HTTPRouteHandler
from litestar.handlers.websocket_handlers import WebsocketRouteHandler
from litestar.types.empty import Empty
from litestar.utils import normalize_path
from litestar.utils.signature import add_types_to_signature_namespace

__all__ = ("Controller",)


if TYPE_CHECKING:
    from litestar.connection import Request, WebSocket
    from litestar.datastructures import CacheControlHeader, ETag
    from litestar.dto import AbstractDTO
    from litestar.openapi.spec import SecurityRequirement
    from litestar.response import Response
    from litestar.router import Router
    from litestar.types import (
        AfterRequestHookHandler,
        AfterResponseHookHandler,
        BeforeRequestHookHandler,
        Dependencies,
        ExceptionHandlersMap,
        Guard,
        Middleware,
        ParametersMap,
        ResponseCookies,
        TypeEncodersMap,
    )
    from litestar.types.composite_types import ResponseHeaders, TypeDecodersSequence
    from litestar.types.empty import EmptyType


class Controller:
    """The Litestar Controller class.

    Subclass this class to create 'view' like components and utilize OOP.
    """

    __slots__ = (
        "after_request",
        "after_response",
        "before_request",
        "cache_control",
        "dependencies",
        "dto",
        "etag",
        "exception_handlers",
        "guards",
        "include_in_schema",
        "middleware",
        "opt",
        "owner",
        "parameters",
        "path",
        "request_class",
        "response_class",
        "response_cookies",
        "response_headers",
        "return_dto",
        "security",
        "signature_namespace",
        "signature_types",
        "tags",
        "type_encoders",
        "type_decoders",
        "websocket_class",
    )

    after_request: AfterRequestHookHandler | None
    """A sync or async function executed before a :class:`Request <.connection.Request>` is passed to any route handler.

    If this function returns a value, the request will not reach the route handler, and instead this value will be used.
    """
    after_response: AfterResponseHookHandler | None
    """A sync or async function called after the response has been awaited.

    It receives the :class:`Request <.connection.Request>` instance and should not return any values.
    """
    before_request: BeforeRequestHookHandler | None
    """A sync or async function called immediately before calling the route handler.

    It receives the :class:`Request <.connection.Request>` instance and any non-``None`` return value is used for the
    response, bypassing the route handler.
    """
    cache_control: CacheControlHeader | None
    """A :class:`CacheControlHeader <.datastructures.CacheControlHeader>` header to add to route handlers of this
    controller.

    Can be overridden by route handlers.
    """
    dependencies: Dependencies | None
    """A string keyed dictionary of dependency :class:`Provider <.di.Provide>` instances."""
    dto: type[AbstractDTO] | None | EmptyType
    """:class:`AbstractDTO <.dto.base_dto.AbstractDTO>` to use for (de)serializing and validation of request data."""
    etag: ETag | None
    """An ``etag`` header of type :class:`ETag <.datastructures.ETag>` to add to route handlers of this controller.

    Can be overridden by route handlers.
    """
    exception_handlers: ExceptionHandlersMap | None
    """A map of handler functions to status codes and/or exception types."""
    guards: Sequence[Guard] | None
    """A sequence of :class:`Guard <.types.Guard>` callables."""
    include_in_schema: bool | EmptyType
    """A boolean flag dictating whether  the route handler should be documented in the OpenAPI schema"""
    middleware: Sequence[Middleware] | None
    """A sequence of :class:`Middleware <.types.Middleware>`."""
    opt: Mapping[str, Any] | None
    """A string key mapping of arbitrary values that can be accessed in :class:`Guards <.types.Guard>` or wherever you
    have access to :class:`Request <.connection.Request>` or :class:`ASGI Scope <.types.Scope>`.
    """
    owner: Router
    """The :class:`Router <.router.Router>` or :class:`Litestar <litestar.app.Litestar>` app that owns the controller.

    This value is set internally by Litestar and it should not be set when subclassing the controller.
    """
    parameters: ParametersMap | None
    """A mapping of :class:`Parameter <.params.Parameter>` definitions available to all application paths."""
    path: str
    """A path fragment for the controller.

    All route handlers under the controller will have the fragment appended to them. If not set it defaults to ``/``.
    """
    request_class: type[Request] | None
    """A custom subclass of :class:`Request <.connection.Request>` to be used as the default request for all route
    handlers under the controller.
    """
    response_class: type[Response] | None
    """A custom subclass of :class:`Response <.response.Response>` to be used as the default response for all route
    handlers under the controller.
    """
    response_cookies: ResponseCookies | None
    """A list of :class:`Cookie <.datastructures.Cookie>` instances."""
    response_headers: ResponseHeaders | None
    """A string keyed dictionary mapping :class:`ResponseHeader <.datastructures.ResponseHeader>` instances."""
    return_dto: type[AbstractDTO] | None | EmptyType
    """:class:`AbstractDTO <.dto.base_dto.AbstractDTO>` to use for serializing outbound response
    data.
    """
    tags: Sequence[str] | None
    """A sequence of string tags that will be appended to the schema of all route handlers under the controller."""
    security: Sequence[SecurityRequirement] | None
    """A sequence of dictionaries that to the schema of all route handlers under the controller."""
    signature_namespace: dict[str, Any]
    """A mapping of names to types for use in forward reference resolution during signature modeling."""
    signature_types: Sequence[Any]
    """A sequence of types for use in forward reference resolution during signature modeling.

    These types will be added to the signature namespace using their ``__name__`` attribute.
    """
    type_decoders: TypeDecodersSequence | None
    """A sequence of tuples, each composed of a predicate testing for type identity and a msgspec hook for deserialization."""
    type_encoders: TypeEncodersMap | None
    """A mapping of types to callables that transform them into types supported for serialization."""
    websocket_class: type[WebSocket] | None
    """A custom subclass of :class:`WebSocket <.connection.WebSocket>` to be used as the default websocket for all route
    handlers under the controller.
    """

    def __init__(self, owner: Router) -> None:
        """Initialize a controller.

        Should only be called by routers as part of controller registration.

        Args:
            owner: An instance of :class:`Router <.router.Router>`
        """
        # Since functions set on classes are bound, we need replace the bound instance with the class version
        for key in ("after_request", "after_response", "before_request"):
            cls_value = getattr(type(self), key, None)
            if callable(cls_value):
                setattr(self, key, cls_value)

        if not hasattr(self, "dto"):
            self.dto = Empty

        if not hasattr(self, "return_dto"):
            self.return_dto = Empty

        if not hasattr(self, "include_in_schema"):
            self.include_in_schema = Empty

        self.signature_namespace = add_types_to_signature_namespace(
            getattr(self, "signature_types", []), getattr(self, "signature_namespace", {})
        )

        for key in self.__slots__:
            if not hasattr(self, key):
                setattr(self, key, None)

        self.response_cookies = narrow_response_cookies(self.response_cookies)
        self.response_headers = narrow_response_headers(self.response_headers)
        self.path = normalize_path(self.path or "/")
        self.owner = owner

    def as_router(self) -> Router:
        from litestar.router import Router

        router = Router(
            path=self.path,
            route_handlers=self.get_route_handlers(),
            after_request=self.after_request,
            after_response=self.after_response,
            before_request=self.before_request,
            cache_control=self.cache_control,
            dependencies=self.dependencies,
            dto=self.dto,
            etag=self.etag,
            exception_handlers=self.exception_handlers,
            guards=self.guards,
            include_in_schema=self.include_in_schema,
            middleware=self.middleware,
            opt=self.opt,
            parameters=self.parameters,
            request_class=self.request_class,
            response_class=self.response_class,
            response_cookies=self.response_cookies,
            response_headers=self.response_headers,
            return_dto=self.return_dto,
            security=self.security,
            signature_types=self.signature_types,
            signature_namespace=self.signature_namespace,
            tags=self.tags,
            type_encoders=self.type_encoders,
            type_decoders=self.type_decoders,
            websocket_class=self.websocket_class,
        )
        router.owner = self.owner
        return router

    def get_route_handlers(self) -> list[BaseRouteHandler]:
        """Get a controller's route handlers and set the controller as the handlers' owner.

        Returns:
            A list containing a copy of the route handlers defined on the controller
        """

        route_handlers: list[BaseRouteHandler] = []
        controller_names = set(dir(Controller))
        self_handlers = [
            getattr(self, name)
            for name in dir(self)
            if name not in controller_names and isinstance(getattr(self, name), BaseRouteHandler)
        ]
        self_handlers.sort(key=attrgetter("handler_id"))
        for self_handler in self_handlers:
            route_handler = deepcopy(self_handler)
            # at the point we get a reference to the handler function, it's unbound, so
            # we replace it with a regular bound method here
            route_handler._fn = types.MethodType(route_handler._fn, self)
            route_handler.owner = self
            route_handlers.append(route_handler)

        self.validate_route_handlers(route_handlers=route_handlers)

        return route_handlers

    def validate_route_handlers(self, route_handlers: list[BaseRouteHandler]) -> None:
        """Validate that the combination of path and decorator method or type are unique on the controller.

        Args:
            route_handlers: The controller's route handlers.

        Raises:
            ImproperlyConfiguredException

        Returns:
            None
        """
        paths: defaultdict[str, set[str]] = defaultdict(set)

        for route_handler in route_handlers:
            if isinstance(route_handler, HTTPRouteHandler):
                methods: set[str] = cast("set[str]", route_handler.http_methods)
            elif isinstance(route_handler, WebsocketRouteHandler):
                methods = {"websocket"}
            else:
                methods = {"asgi"}

            for path in route_handler.paths:
                if (entry := paths[path]) and (intersection := entry.intersection(methods)):
                    raise ImproperlyConfiguredException(
                        f"the combination of path and method must be unique in a controller - "
                        f"the following methods {''.join(m.lower() for m in intersection)} for {type(self).__name__} "
                        f"controller path {path} are not unique"
                    )
                paths[path].update(methods)
