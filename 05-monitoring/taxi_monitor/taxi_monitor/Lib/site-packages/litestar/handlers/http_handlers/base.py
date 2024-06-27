from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, AnyStr, Mapping, Sequence, TypedDict, cast

from litestar._layers.utils import narrow_response_cookies, narrow_response_headers
from litestar.connection import Request
from litestar.datastructures.cookie import Cookie
from litestar.datastructures.response_header import ResponseHeader
from litestar.enums import HttpMethod, MediaType
from litestar.exceptions import (
    HTTPException,
    ImproperlyConfiguredException,
)
from litestar.handlers.base import BaseRouteHandler
from litestar.handlers.http_handlers._utils import (
    create_data_handler,
    create_generic_asgi_response_handler,
    create_response_handler,
    get_default_status_code,
    is_empty_response_annotation,
    normalize_http_method,
)
from litestar.openapi.spec import Operation
from litestar.response import Response
from litestar.status_codes import HTTP_204_NO_CONTENT, HTTP_304_NOT_MODIFIED
from litestar.types import (
    AfterRequestHookHandler,
    AfterResponseHookHandler,
    AnyCallable,
    ASGIApp,
    BeforeRequestHookHandler,
    CacheKeyBuilder,
    Dependencies,
    Empty,
    EmptyType,
    ExceptionHandlersMap,
    Guard,
    Method,
    Middleware,
    ResponseCookies,
    ResponseHeaders,
    TypeEncodersMap,
)
from litestar.utils import ensure_async_callable
from litestar.utils.predicates import is_async_callable
from litestar.utils.warnings import warn_implicit_sync_to_thread, warn_sync_to_thread_with_async_callable

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable

    from litestar.app import Litestar
    from litestar.background_tasks import BackgroundTask, BackgroundTasks
    from litestar.config.response_cache import CACHE_FOREVER
    from litestar.datastructures import CacheControlHeader, ETag
    from litestar.dto import AbstractDTO
    from litestar.openapi.datastructures import ResponseSpec
    from litestar.openapi.spec import SecurityRequirement
    from litestar.types.callable_types import AsyncAnyCallable, OperationIDCreator
    from litestar.types.composite_types import TypeDecodersSequence

__all__ = ("HTTPRouteHandler", "route")


class ResponseHandlerMap(TypedDict):
    default_handler: Callable[[Any], Awaitable[ASGIApp]] | EmptyType
    response_type_handler: Callable[[Any], Awaitable[ASGIApp]] | EmptyType


class HTTPRouteHandler(BaseRouteHandler):
    """HTTP Route Decorator.

    Use this decorator to decorate an HTTP handler with multiple methods.
    """

    __slots__ = (
        "_resolved_after_response",
        "_resolved_before_request",
        "_response_handler_mapping",
        "_resolved_include_in_schema",
        "_resolved_response_class",
        "_resolved_request_class",
        "_resolved_tags",
        "_resolved_security",
        "after_request",
        "after_response",
        "background",
        "before_request",
        "cache",
        "cache_control",
        "cache_key_builder",
        "content_encoding",
        "content_media_type",
        "deprecated",
        "description",
        "etag",
        "has_sync_callable",
        "http_methods",
        "include_in_schema",
        "media_type",
        "operation_class",
        "operation_id",
        "raises",
        "request_class",
        "response_class",
        "response_cookies",
        "response_description",
        "response_headers",
        "responses",
        "security",
        "status_code",
        "summary",
        "sync_to_thread",
        "tags",
        "template_name",
    )

    has_sync_callable: bool

    def __init__(
        self,
        path: str | Sequence[str] | None = None,
        *,
        after_request: AfterRequestHookHandler | None = None,
        after_response: AfterResponseHookHandler | None = None,
        background: BackgroundTask | BackgroundTasks | None = None,
        before_request: BeforeRequestHookHandler | None = None,
        cache: bool | int | type[CACHE_FOREVER] = False,
        cache_control: CacheControlHeader | None = None,
        cache_key_builder: CacheKeyBuilder | None = None,
        dependencies: Dependencies | None = None,
        dto: type[AbstractDTO] | None | EmptyType = Empty,
        etag: ETag | None = None,
        exception_handlers: ExceptionHandlersMap | None = None,
        guards: Sequence[Guard] | None = None,
        http_method: HttpMethod | Method | Sequence[HttpMethod | Method],
        media_type: MediaType | str | None = None,
        middleware: Sequence[Middleware] | None = None,
        name: str | None = None,
        opt: Mapping[str, Any] | None = None,
        request_class: type[Request] | None = None,
        response_class: type[Response] | None = None,
        response_cookies: ResponseCookies | None = None,
        response_headers: ResponseHeaders | None = None,
        return_dto: type[AbstractDTO] | None | EmptyType = Empty,
        status_code: int | None = None,
        sync_to_thread: bool | None = None,
        # OpenAPI related attributes
        content_encoding: str | None = None,
        content_media_type: str | None = None,
        deprecated: bool = False,
        description: str | None = None,
        include_in_schema: bool | EmptyType = Empty,
        operation_class: type[Operation] = Operation,
        operation_id: str | OperationIDCreator | None = None,
        raises: Sequence[type[HTTPException]] | None = None,
        response_description: str | None = None,
        responses: Mapping[int, ResponseSpec] | None = None,
        signature_namespace: Mapping[str, Any] | None = None,
        security: Sequence[SecurityRequirement] | None = None,
        summary: str | None = None,
        tags: Sequence[str] | None = None,
        type_decoders: TypeDecodersSequence | None = None,
        type_encoders: TypeEncodersMap | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize ``HTTPRouteHandler``.

        Args:
            path: A path fragment for the route handler function or a sequence of path fragments.
                If not given defaults to ``/``
            after_request: A sync or async function executed before a :class:`Request <.connection.Request>` is passed
                to any route handler. If this function returns a value, the request will not reach the route handler,
                and instead this value will be used.
            after_response: A sync or async function called after the response has been awaited. It receives the
                :class:`Request <.connection.Request>` object and should not return any values.
            background: A :class:`BackgroundTask <.background_tasks.BackgroundTask>` instance or
                :class:`BackgroundTasks <.background_tasks.BackgroundTasks>` to execute after the response is finished.
                Defaults to ``None``.
            before_request: A sync or async function called immediately before calling the route handler. Receives
                the :class:`Request <.connection.Request>` instance and any non-``None`` return value is used for the
                response, bypassing the route handler.
            cache: Enables response caching if configured on the application level. Valid values are ``True`` or a
                number of seconds (e.g. ``120``) to cache the response.
            cache_control: A ``cache-control`` header of type
                :class:`CacheControlHeader <.datastructures.CacheControlHeader>` that will be added to the response.
            cache_key_builder: A :class:`cache-key builder function <.types.CacheKeyBuilder>`. Allows for customization
                of the cache key if caching is configured on the application level.
            dependencies: A string keyed mapping of dependency :class:`Provider <.di.Provide>` instances.
            dto: :class:`AbstractDTO <.dto.base_dto.AbstractDTO>` to use for (de)serializing and
                validation of request data.
            etag: An ``etag`` header of type :class:`ETag <.datastructures.ETag>` that will be added to the response.
            exception_handlers: A mapping of status codes and/or exception types to handler functions.
            guards: A sequence of :class:`Guard <.types.Guard>` callables.
            http_method: An :class:`http method string <.types.Method>`, a member of the enum
                :class:`HttpMethod <.enums.HttpMethod>` or a list of these that correlates to the methods the route
                handler function should handle.
            media_type: A member of the :class:`MediaType <.enums.MediaType>` enum or a string with a valid IANA
                Media-Type.
            middleware: A sequence of :class:`Middleware <.types.Middleware>`.
            name: A string identifying the route handler.
            opt: A string keyed mapping of arbitrary values that can be accessed in :class:`Guards <.types.Guard>` or
                wherever you have access to :class:`Request <.connection.Request>` or
                :class:`ASGI Scope <.types.Scope>`.
            request_class: A custom subclass of :class:`Request <.connection.Request>` to be used as route handler's
                default request.
            response_class: A custom subclass of :class:`Response <.response.Response>` to be used as route handler's
                default response.
            response_cookies: A sequence of :class:`Cookie <.datastructures.Cookie>` instances.
            response_headers: A string keyed mapping of :class:`ResponseHeader <.datastructures.ResponseHeader>`
                instances.
            responses: A mapping of additional status codes and a description of their expected content.
                This information will be included in the OpenAPI schema
            return_dto: :class:`AbstractDTO <.dto.base_dto.AbstractDTO>` to use for serializing
                outbound response data.
            signature_namespace: A mapping of names to types for use in forward reference resolution during signature modelling.
            status_code: An http status code for the response. Defaults to ``200`` for mixed method or ``GET``, ``PUT`` and
                ``PATCH``, ``201`` for ``POST`` and ``204`` for ``DELETE``.
            sync_to_thread: A boolean dictating whether the handler function will be executed in a worker thread or the
                main event loop. This has an effect only for sync handler functions. See using sync handler functions.
            content_encoding: A string describing the encoding of the content, e.g. ``"base64"``.
            content_media_type: A string designating the media-type of the content, e.g. ``"image/png"``.
            deprecated:  A boolean dictating whether this route should be marked as deprecated in the OpenAPI schema.
            description: Text used for the route's schema description section.
            include_in_schema: A boolean flag dictating whether  the route handler should be documented in the OpenAPI schema.
            operation_class: :class:`Operation <.openapi.spec.operation.Operation>` to be used with the route's OpenAPI schema.
            operation_id: Either a string or a callable returning a string. An identifier used for the route's schema operationId.
            raises:  A list of exception classes extending from litestar.HttpException that is used for the OpenAPI documentation.
                This list should describe all exceptions raised within the route handler's function/method. The Litestar
                ValidationException will be added automatically for the schema if any validation is involved.
            response_description: Text used for the route's response schema description section.
            security: A sequence of dictionaries that contain information about which security scheme can be used on the endpoint.
            summary: Text used for the route's schema summary section.
            tags: A sequence of string tags that will be appended to the OpenAPI schema.
            type_decoders: A sequence of tuples, each composed of a predicate testing for type identity and a msgspec hook for deserialization.
            type_encoders: A mapping of types to callables that transform them into types supported for serialization.
            **kwargs: Any additional kwarg - will be set in the opt dictionary.
        """
        if not http_method:
            raise ImproperlyConfiguredException("An http_method kwarg is required")

        self.http_methods = normalize_http_method(http_methods=http_method)
        self.status_code = status_code or get_default_status_code(http_methods=self.http_methods)

        super().__init__(
            path=path,
            dependencies=dependencies,
            dto=dto,
            exception_handlers=exception_handlers,
            guards=guards,
            middleware=middleware,
            name=name,
            opt=opt,
            return_dto=return_dto,
            signature_namespace=signature_namespace,
            type_decoders=type_decoders,
            type_encoders=type_encoders,
            **kwargs,
        )

        self.after_request = ensure_async_callable(after_request) if after_request else None  # pyright: ignore
        self.after_response = ensure_async_callable(after_response) if after_response else None
        self.background = background
        self.before_request = ensure_async_callable(before_request) if before_request else None
        self.cache = cache
        self.cache_control = cache_control
        self.cache_key_builder = cache_key_builder
        self.etag = etag
        self.media_type: MediaType | str = media_type or ""
        self.request_class = request_class
        self.response_class = response_class
        self.response_cookies: Sequence[Cookie] | None = narrow_response_cookies(response_cookies)
        self.response_headers: Sequence[ResponseHeader] | None = narrow_response_headers(response_headers)

        self.sync_to_thread = sync_to_thread
        # OpenAPI related attributes
        self.content_encoding = content_encoding
        self.content_media_type = content_media_type
        self.deprecated = deprecated
        self.description = description
        self.include_in_schema = include_in_schema
        self.operation_class = operation_class
        self.operation_id = operation_id
        self.raises = raises
        self.response_description = response_description
        self.summary = summary
        self.tags = tags
        self.security = security
        self.responses = responses
        # memoized attributes, defaulted to Empty
        self._resolved_after_response: AsyncAnyCallable | None | EmptyType = Empty
        self._resolved_before_request: AsyncAnyCallable | None | EmptyType = Empty
        self._response_handler_mapping: ResponseHandlerMap = {"default_handler": Empty, "response_type_handler": Empty}
        self._resolved_include_in_schema: bool | EmptyType = Empty
        self._resolved_response_class: type[Response] | EmptyType = Empty
        self._resolved_request_class: type[Request] | EmptyType = Empty
        self._resolved_security: list[SecurityRequirement] | EmptyType = Empty
        self._resolved_tags: list[str] | EmptyType = Empty

    def __call__(self, fn: AnyCallable) -> HTTPRouteHandler:
        """Replace a function with itself."""
        if not is_async_callable(fn):
            if self.sync_to_thread is None:
                warn_implicit_sync_to_thread(fn, stacklevel=3)
        elif self.sync_to_thread is not None:
            warn_sync_to_thread_with_async_callable(fn, stacklevel=3)

        super().__call__(fn)
        return self

    def resolve_request_class(self) -> type[Request]:
        """Return the closest custom Request class in the owner graph or the default Request class.

        This method is memoized so the computation occurs only once.

        Returns:
            The default :class:`Request <.connection.Request>` class for the route handler.
        """

        if self._resolved_request_class is Empty:
            self._resolved_request_class = next(
                (layer.request_class for layer in reversed(self.ownership_layers) if layer.request_class is not None),
                Request,
            )

        return cast("type[Request]", self._resolved_request_class)

    def resolve_response_class(self) -> type[Response]:
        """Return the closest custom Response class in the owner graph or the default Response class.

        This method is memoized so the computation occurs only once.

        Returns:
            The default :class:`Response <.response.Response>` class for the route handler.
        """
        if self._resolved_response_class is Empty:
            self._resolved_response_class = next(
                (layer.response_class for layer in reversed(self.ownership_layers) if layer.response_class is not None),
                Response,
            )

        return cast("type[Response]", self._resolved_response_class)

    def resolve_response_headers(self) -> frozenset[ResponseHeader]:
        """Return all header parameters in the scope of the handler function.

        Returns:
            A dictionary mapping keys to :class:`ResponseHeader <.datastructures.ResponseHeader>` instances.
        """
        resolved_response_headers: dict[str, ResponseHeader] = {}

        for layer in self.ownership_layers:
            if layer_response_headers := layer.response_headers:
                if isinstance(layer_response_headers, Mapping):
                    # this can't happen unless you manually set response_headers on an instance, which would result in a
                    # type-checking error on everything but the controller. We cover this case nevertheless
                    resolved_response_headers.update(
                        {name: ResponseHeader(name=name, value=value) for name, value in layer_response_headers.items()}
                    )
                else:
                    resolved_response_headers.update({h.name: h for h in layer_response_headers})
            for extra_header in ("cache_control", "etag"):
                if header_model := getattr(layer, extra_header, None):
                    resolved_response_headers[header_model.HEADER_NAME] = ResponseHeader(
                        name=header_model.HEADER_NAME,
                        value=header_model.to_header(),
                        documentation_only=header_model.documentation_only,
                    )

        return frozenset(resolved_response_headers.values())

    def resolve_response_cookies(self) -> frozenset[Cookie]:
        """Return a list of Cookie instances. Filters the list to ensure each cookie key is unique.

        Returns:
            A list of :class:`Cookie <.datastructures.Cookie>` instances.
        """
        response_cookies: set[Cookie] = set()
        for layer in reversed(self.ownership_layers):
            if layer_response_cookies := layer.response_cookies:
                if isinstance(layer_response_cookies, Mapping):
                    # this can't happen unless you manually set response_cookies on an instance, which would result in a
                    # type-checking error on everything but the controller. We cover this case nevertheless
                    response_cookies.update(
                        {Cookie(key=key, value=value) for key, value in layer_response_cookies.items()}
                    )
                else:
                    response_cookies.update(cast("set[Cookie]", layer_response_cookies))
        return frozenset(response_cookies)

    def resolve_before_request(self) -> AsyncAnyCallable | None:
        """Resolve the before_handler handler by starting from the route handler and moving up.

        If a handler is found it is returned, otherwise None is set.
        This method is memoized so the computation occurs only once.

        Returns:
            An optional :class:`before request lifecycle hook handler <.types.BeforeRequestHookHandler>`
        """
        if self._resolved_before_request is Empty:
            before_request_handlers = [layer.before_request for layer in self.ownership_layers if layer.before_request]
            self._resolved_before_request = before_request_handlers[-1] if before_request_handlers else None
        return cast("AsyncAnyCallable | None", self._resolved_before_request)

    def resolve_after_response(self) -> AsyncAnyCallable | None:
        """Resolve the after_response handler by starting from the route handler and moving up.

        If a handler is found it is returned, otherwise None is set.
        This method is memoized so the computation occurs only once.

        Returns:
            An optional :class:`after response lifecycle hook handler <.types.AfterResponseHookHandler>`
        """
        if self._resolved_after_response is Empty:
            after_response_handlers: list[AsyncAnyCallable] = [
                layer.after_response  # type: ignore[misc]
                for layer in self.ownership_layers
                if layer.after_response
            ]
            self._resolved_after_response = after_response_handlers[-1] if after_response_handlers else None

        return cast("AsyncAnyCallable | None", self._resolved_after_response)

    def resolve_include_in_schema(self) -> bool:
        """Resolve the 'include_in_schema' property by starting from the route handler and moving up.

        If 'include_in_schema' is found in any of the ownership layers, the last value found is returned.
        If not found in any layer, the default value ``True`` is returned.

        Returns:
            bool: The resolved 'include_in_schema' property.
        """
        if self._resolved_include_in_schema is Empty:
            include_in_schemas = [
                i.include_in_schema for i in self.ownership_layers if isinstance(i.include_in_schema, bool)
            ]
            self._resolved_include_in_schema = include_in_schemas[-1] if include_in_schemas else True

        return self._resolved_include_in_schema

    def resolve_security(self) -> list[SecurityRequirement]:
        """Resolve the security property by starting from the route handler and moving up.

        Security requirements are additive, so the security requirements of the route handler are the sum of all
        security requirements of the ownership layers.

        Returns:
            list[SecurityRequirement]: The resolved security property.
        """
        if self._resolved_security is Empty:
            self._resolved_security = []
            for layer in self.ownership_layers:
                if isinstance(layer.security, Sequence):
                    self._resolved_security.extend(layer.security)

        return self._resolved_security

    def resolve_tags(self) -> list[str]:
        """Resolve the tags property by starting from the route handler and moving up.

        Tags are additive, so the tags of the route handler are the sum of all tags of the ownership layers.

        Returns:
            list[str]: A sorted list of unique tags.
        """
        if self._resolved_tags is Empty:
            tag_set = set()
            for layer in self.ownership_layers:
                for tag in layer.tags or []:
                    tag_set.add(tag)
            self._resolved_tags = sorted(tag_set)

        return self._resolved_tags

    def get_response_handler(self, is_response_type_data: bool = False) -> Callable[[Any], Awaitable[ASGIApp]]:
        """Resolve the response_handler function for the route handler.

        This method is memoized so the computation occurs only once.

        Args:
            is_response_type_data: Whether to return a handler for 'Response' instances.

        Returns:
            Async Callable to handle an HTTP Request
        """
        if self._response_handler_mapping["default_handler"] is Empty:
            after_request_handlers: list[AsyncAnyCallable] = [
                layer.after_request  # type: ignore[misc]
                for layer in self.ownership_layers
                if layer.after_request
            ]
            after_request = cast(
                "AfterRequestHookHandler | None",
                after_request_handlers[-1] if after_request_handlers else None,
            )

            media_type = self.media_type.value if isinstance(self.media_type, Enum) else self.media_type
            response_class = self.resolve_response_class()
            headers = self.resolve_response_headers()
            cookies = self.resolve_response_cookies()
            type_encoders = self.resolve_type_encoders()

            return_type = self.parsed_fn_signature.return_type
            return_annotation = return_type.annotation

            self._response_handler_mapping["response_type_handler"] = response_type_handler = create_response_handler(
                after_request=after_request,
                background=self.background,
                cookies=cookies,
                headers=headers,
                media_type=media_type,
                status_code=self.status_code,
                type_encoders=type_encoders,
            )

            if return_type.is_subclass_of(Response):
                self._response_handler_mapping["default_handler"] = response_type_handler
            elif is_async_callable(return_annotation) or return_annotation is ASGIApp:
                self._response_handler_mapping["default_handler"] = create_generic_asgi_response_handler(
                    after_request=after_request
                )
            else:
                self._response_handler_mapping["default_handler"] = create_data_handler(
                    after_request=after_request,
                    background=self.background,
                    cookies=cookies,
                    headers=headers,
                    media_type=media_type,
                    response_class=response_class,
                    status_code=self.status_code,
                    type_encoders=type_encoders,
                )

        return cast(
            "Callable[[Any], Awaitable[ASGIApp]]",
            self._response_handler_mapping["response_type_handler"]
            if is_response_type_data
            else self._response_handler_mapping["default_handler"],
        )

    async def to_response(self, app: Litestar, data: Any, request: Request) -> ASGIApp:
        """Return a :class:`Response <.response.Response>` from the handler by resolving and calling it.

        Args:
            app: The :class:`Litestar <litestar.app.Litestar>` app instance
            data: Either an instance of a :class:`Response <.response.Response>`,
                a Response instance or an arbitrary value.
            request: A :class:`Request <.connection.Request>` instance

        Returns:
            A Response instance
        """
        if return_dto_type := self.resolve_return_dto():
            data = return_dto_type(request).data_to_encodable_type(data)

        response_handler = self.get_response_handler(is_response_type_data=isinstance(data, Response))
        return await response_handler(app=app, data=data, request=request)  # type: ignore[call-arg]

    def on_registration(self, app: Litestar) -> None:
        super().on_registration(app)
        self.resolve_after_response()
        self.resolve_include_in_schema()
        self.has_sync_callable = not is_async_callable(self.fn)

        if self.has_sync_callable and self.sync_to_thread:
            self._fn = ensure_async_callable(self.fn)
            self.has_sync_callable = False

    def _validate_handler_function(self) -> None:
        """Validate the route handler function once it is set by inspecting its return annotations."""
        super()._validate_handler_function()

        return_type = self.parsed_fn_signature.return_type

        if return_type.annotation is Empty:
            raise ImproperlyConfiguredException(
                "A return value of a route handler function should be type annotated. "
                "If your function doesn't return a value, annotate it as returning 'None'."
            )

        if (
            self.status_code < 200 or self.status_code in {HTTP_204_NO_CONTENT, HTTP_304_NOT_MODIFIED}
        ) and not is_empty_response_annotation(return_type):
            raise ImproperlyConfiguredException(
                "A status code 204, 304 or in the range below 200 does not support a response body. "
                "If the function should return a value, change the route handler status code to an appropriate value.",
            )

        if not self.media_type:
            if return_type.is_subclass_of((str, bytes)) or return_type.annotation is AnyStr:
                self.media_type = MediaType.TEXT
            elif not return_type.is_subclass_of(Response):
                self.media_type = MediaType.JSON

        if "socket" in self.parsed_fn_signature.parameters:
            raise ImproperlyConfiguredException("The 'socket' kwarg is not supported with http handlers")

        if "data" in self.parsed_fn_signature.parameters and "GET" in self.http_methods:
            raise ImproperlyConfiguredException("'data' kwarg is unsupported for 'GET' request handlers")


route = HTTPRouteHandler
