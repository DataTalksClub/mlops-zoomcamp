from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from litestar.enums import HttpMethod, MediaType
from litestar.exceptions import HTTPException, ImproperlyConfiguredException
from litestar.openapi.spec import Operation
from litestar.response.file import ASGIFileResponse, File
from litestar.types import Empty, TypeDecodersSequence
from litestar.types.builtin_types import NoneType
from litestar.utils import is_class_and_subclass

from .base import HTTPRouteHandler

if TYPE_CHECKING:
    from typing import Any, Mapping, Sequence

    from litestar.background_tasks import BackgroundTask, BackgroundTasks
    from litestar.config.response_cache import CACHE_FOREVER
    from litestar.connection import Request
    from litestar.datastructures import CacheControlHeader, ETag
    from litestar.dto import AbstractDTO
    from litestar.openapi.datastructures import ResponseSpec
    from litestar.openapi.spec import SecurityRequirement
    from litestar.response import Response
    from litestar.types import (
        AfterRequestHookHandler,
        AfterResponseHookHandler,
        BeforeRequestHookHandler,
        CacheKeyBuilder,
        Dependencies,
        EmptyType,
        ExceptionHandlersMap,
        Guard,
        Middleware,
        ResponseCookies,
        ResponseHeaders,
        TypeEncodersMap,
    )
    from litestar.types.callable_types import OperationIDCreator


__all__ = ("get", "head", "post", "put", "patch", "delete")

MSG_SEMANTIC_ROUTE_HANDLER_WITH_HTTP = "semantic route handlers cannot define http_method"


def _subclass_warning() -> None:
    warnings.warn(
        "Semantic HTTP route handler classes are deprecated and will be replaced by "
        "functional decorators in Litestar 3.0.",
        category=DeprecationWarning,
        stacklevel=2,
    )


class delete(HTTPRouteHandler):
    """DELETE Route Decorator.

    Use this decorator to decorate an HTTP handler for DELETE requests.
    """

    def __init__(
        self,
        path: str | None | Sequence[str] = None,
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
        media_type: MediaType | str | None = None,
        middleware: Sequence[Middleware] | None = None,
        name: str | None = None,
        opt: Mapping[str, Any] | None = None,
        request_class: type[Request] | None = None,
        response_class: type[Response] | None = None,
        response_cookies: ResponseCookies | None = None,
        response_headers: ResponseHeaders | None = None,
        return_dto: type[AbstractDTO] | None | EmptyType = Empty,
        signature_namespace: Mapping[str, Any] | None = None,
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
        security: Sequence[SecurityRequirement] | None = None,
        summary: str | None = None,
        tags: Sequence[str] | None = None,
        type_decoders: TypeDecodersSequence | None = None,
        type_encoders: TypeEncodersMap | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize ``delete``

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
                the :class:`.connection.Request` instance and any non-``None`` return value is used for the response,
                bypassing the route handler.
            cache: Enables response caching if configured on the application level. Valid values are ``True`` or a number
                of seconds (e.g. ``120``) to cache the response.
            cache_control: A ``cache-control`` header of type
                :class:`CacheControlHeader <.datastructures.CacheControlHeader>` that will be added to the response.
            cache_key_builder: A :class:`cache-key builder function <.types.CacheKeyBuilder>`. Allows for customization
                of the cache key if caching is configured on the application level.
            dto: :class:`AbstractDTO <.dto.base_dto.AbstractDTO>` to use for (de)serializing and
                validation of request data.
            dependencies: A string keyed mapping of dependency :class:`Provider <.di.Provide>` instances.
            etag: An ``etag`` header of type :class:`ETag <.datastructures.ETag>` that will be added to the response.
            exception_handlers: A mapping of status codes and/or exception types to handler functions.
            guards: A sequence of :class:`Guard <.types.Guard>` callables.
            http_method: An :class:`http method string <.types.Method>`, a member of the enum
                :class:`HttpMethod <litestar.enums.HttpMethod>` or a list of these that correlates to the methods the
                route handler function should handle.
            media_type: A member of the :class:`MediaType <.enums.MediaType>` enum or a string with a
                valid IANA Media-Type.
            middleware: A sequence of :class:`Middleware <.types.Middleware>`.
            name: A string identifying the route handler.
            opt: A string keyed mapping of arbitrary values that can be accessed in :class:`Guards <.types.Guard>` or
                wherever you have access to :class:`Request <.connection.Request>` or :class:`ASGI Scope <.types.Scope>`.
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
            status_code: An http status code for the response. Defaults to ``200`` for mixed method or ``GET``, ``PUT``
                and ``PATCH``, ``201`` for ``POST`` and ``204`` for ``DELETE``.
            sync_to_thread: A boolean dictating whether the handler function will be executed in a worker thread or the
                main event loop. This has an effect only for sync handler functions. See using sync handler functions.
            content_encoding: A string describing the encoding of the content, e.g. ``base64``.
            content_media_type: A string designating the media-type of the content, e.g. ``image/png``.
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
            type_decoders: A sequence of tuples, each composed of a predicate testing for type identity and a msgspec
                hook for deserialization.
            type_encoders: A mapping of types to callables that transform them into types supported for serialization.
            **kwargs: Any additional kwarg - will be set in the opt dictionary.
        """
        if "http_method" in kwargs:
            raise ImproperlyConfiguredException(MSG_SEMANTIC_ROUTE_HANDLER_WITH_HTTP)
        super().__init__(
            after_request=after_request,
            after_response=after_response,
            background=background,
            before_request=before_request,
            cache=cache,
            cache_control=cache_control,
            cache_key_builder=cache_key_builder,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            dependencies=dependencies,
            deprecated=deprecated,
            description=description,
            dto=dto,
            etag=etag,
            exception_handlers=exception_handlers,
            guards=guards,
            http_method=HttpMethod.DELETE,
            include_in_schema=include_in_schema,
            media_type=media_type,
            middleware=middleware,
            name=name,
            operation_class=operation_class,
            operation_id=operation_id,
            opt=opt,
            path=path,
            raises=raises,
            request_class=request_class,
            response_class=response_class,
            response_cookies=response_cookies,
            response_description=response_description,
            response_headers=response_headers,
            responses=responses,
            return_dto=return_dto,
            security=security,
            signature_namespace=signature_namespace,
            status_code=status_code,
            summary=summary,
            sync_to_thread=sync_to_thread,
            tags=tags,
            type_decoders=type_decoders,
            type_encoders=type_encoders,
            **kwargs,
        )

    def __init_subclass__(cls, **kwargs: Any) -> None:
        _subclass_warning()


class get(HTTPRouteHandler):
    """GET Route Decorator.

    Use this decorator to decorate an HTTP handler for GET requests.
    """

    def __init__(
        self,
        path: str | None | Sequence[str] = None,
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
        media_type: MediaType | str | None = None,
        middleware: Sequence[Middleware] | None = None,
        name: str | None = None,
        opt: Mapping[str, Any] | None = None,
        request_class: type[Request] | None = None,
        response_class: type[Response] | None = None,
        response_cookies: ResponseCookies | None = None,
        response_headers: ResponseHeaders | None = None,
        return_dto: type[AbstractDTO] | None | EmptyType = Empty,
        signature_namespace: Mapping[str, Any] | None = None,
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
        security: Sequence[SecurityRequirement] | None = None,
        summary: str | None = None,
        tags: Sequence[str] | None = None,
        type_decoders: TypeDecodersSequence | None = None,
        type_encoders: TypeEncodersMap | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize ``get``.

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
                the :class:`.connection.Request` instance and any non-``None`` return value is used for the response,
                bypassing the route handler.
            cache: Enables response caching if configured on the application level. Valid values are ``True`` or a number
                of seconds (e.g. ``120``) to cache the response.
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
                :class:`HttpMethod <litestar.enums.HttpMethod>` or a list of these that correlates to the methods the
                route handler function should handle.
            media_type: A member of the :class:`MediaType <.enums.MediaType>` enum or a string with a
                valid IANA Media-Type.
            middleware: A sequence of :class:`Middleware <.types.Middleware>`.
            name: A string identifying the route handler.
            opt: A string keyed mapping of arbitrary values that can be accessed in :class:`Guards <.types.Guard>` or
                wherever you have access to :class:`Request <.connection.Request>` or :class:`ASGI Scope <.types.Scope>`.
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
            content_encoding: A string describing the encoding of the content, e.g. ``base64``.
            content_media_type: A string designating the media-type of the content, e.g. ``image/png``.
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
            type_decoders: A sequence of tuples, each composed of a predicate testing for type identity and a msgspec
                hook for deserialization.
            type_encoders: A mapping of types to callables that transform them into types supported for serialization.
            **kwargs: Any additional kwarg - will be set in the opt dictionary.
        """
        if "http_method" in kwargs:
            raise ImproperlyConfiguredException(MSG_SEMANTIC_ROUTE_HANDLER_WITH_HTTP)

        super().__init__(
            after_request=after_request,
            after_response=after_response,
            background=background,
            before_request=before_request,
            cache=cache,
            cache_control=cache_control,
            cache_key_builder=cache_key_builder,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            dependencies=dependencies,
            deprecated=deprecated,
            description=description,
            dto=dto,
            etag=etag,
            exception_handlers=exception_handlers,
            guards=guards,
            http_method=HttpMethod.GET,
            include_in_schema=include_in_schema,
            media_type=media_type,
            middleware=middleware,
            name=name,
            operation_class=operation_class,
            operation_id=operation_id,
            opt=opt,
            path=path,
            raises=raises,
            request_class=request_class,
            response_class=response_class,
            response_cookies=response_cookies,
            response_description=response_description,
            response_headers=response_headers,
            responses=responses,
            return_dto=return_dto,
            security=security,
            signature_namespace=signature_namespace,
            status_code=status_code,
            summary=summary,
            sync_to_thread=sync_to_thread,
            tags=tags,
            type_decoders=type_decoders,
            type_encoders=type_encoders,
            **kwargs,
        )

    def __init_subclass__(cls, **kwargs: Any) -> None:
        _subclass_warning()


class head(HTTPRouteHandler):
    """HEAD Route Decorator.

    Use this decorator to decorate an HTTP handler for HEAD requests.
    """

    def __init__(
        self,
        path: str | None | Sequence[str] = None,
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
        media_type: MediaType | str | None = None,
        middleware: Sequence[Middleware] | None = None,
        name: str | None = None,
        opt: Mapping[str, Any] | None = None,
        request_class: type[Request] | None = None,
        response_class: type[Response] | None = None,
        response_cookies: ResponseCookies | None = None,
        response_headers: ResponseHeaders | None = None,
        signature_namespace: Mapping[str, Any] | None = None,
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
        return_dto: type[AbstractDTO] | None | EmptyType = Empty,
        security: Sequence[SecurityRequirement] | None = None,
        summary: str | None = None,
        tags: Sequence[str] | None = None,
        type_decoders: TypeDecodersSequence | None = None,
        type_encoders: TypeEncodersMap | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize ``head``.

        Notes:
            - A response to a head request cannot include a body.
                See: [MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/HEAD).

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
                the :class:`.connection.Request` instance and any non-``None`` return value is used for the response,
                bypassing the route handler.
            cache: Enables response caching if configured on the application level. Valid values are ``True`` or a number
                of seconds (e.g. ``120``) to cache the response.
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
                :class:`HttpMethod <litestar.enums.HttpMethod>` or a list of these that correlates to the methods the
                route handler function should handle.
            media_type: A member of the :class:`MediaType <.enums.MediaType>` enum or a string with a
                valid IANA Media-Type.
            middleware: A sequence of :class:`Middleware <.types.Middleware>`.
            name: A string identifying the route handler.
            opt: A string keyed mapping of arbitrary values that can be accessed in :class:`Guards <.types.Guard>` or
                wherever you have access to :class:`Request <.connection.Request>` or :class:`ASGI Scope <.types.Scope>`.
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
            content_encoding: A string describing the encoding of the content, e.g. ``base64``.
            content_media_type: A string designating the media-type of the content, e.g. ``image/png``.
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
            type_decoders: A sequence of tuples, each composed of a predicate testing for type identity and a msgspec
                hook for deserialization.
            type_encoders: A mapping of types to callables that transform them into types supported for serialization.
            **kwargs: Any additional kwarg - will be set in the opt dictionary.
        """
        if "http_method" in kwargs:
            raise ImproperlyConfiguredException(MSG_SEMANTIC_ROUTE_HANDLER_WITH_HTTP)

        super().__init__(
            after_request=after_request,
            after_response=after_response,
            background=background,
            before_request=before_request,
            cache=cache,
            cache_control=cache_control,
            cache_key_builder=cache_key_builder,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            dependencies=dependencies,
            deprecated=deprecated,
            description=description,
            dto=dto,
            etag=etag,
            exception_handlers=exception_handlers,
            guards=guards,
            http_method=HttpMethod.HEAD,
            include_in_schema=include_in_schema,
            media_type=media_type,
            middleware=middleware,
            name=name,
            operation_class=operation_class,
            operation_id=operation_id,
            opt=opt,
            path=path,
            raises=raises,
            request_class=request_class,
            response_class=response_class,
            response_cookies=response_cookies,
            response_description=response_description,
            response_headers=response_headers,
            responses=responses,
            return_dto=return_dto,
            security=security,
            signature_namespace=signature_namespace,
            status_code=status_code,
            summary=summary,
            sync_to_thread=sync_to_thread,
            tags=tags,
            type_decoders=type_decoders,
            type_encoders=type_encoders,
            **kwargs,
        )

    def __init_subclass__(cls, **kwargs: Any) -> None:
        _subclass_warning()

    def _validate_handler_function(self) -> None:
        """Validate the route handler function once it is set by inspecting its return annotations."""
        super()._validate_handler_function()

        # we allow here File and File because these have special setting for head responses
        return_annotation = self.parsed_fn_signature.return_type.annotation
        if not (
            return_annotation in {NoneType, None}
            or is_class_and_subclass(return_annotation, File)
            or is_class_and_subclass(return_annotation, ASGIFileResponse)
        ):
            raise ImproperlyConfiguredException("A response to a head request should not have a body")


class patch(HTTPRouteHandler):
    """PATCH Route Decorator.

    Use this decorator to decorate an HTTP handler for PATCH requests.
    """

    def __init__(
        self,
        path: str | None | Sequence[str] = None,
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
        media_type: MediaType | str | None = None,
        middleware: Sequence[Middleware] | None = None,
        name: str | None = None,
        opt: Mapping[str, Any] | None = None,
        request_class: type[Request] | None = None,
        response_class: type[Response] | None = None,
        response_cookies: ResponseCookies | None = None,
        response_headers: ResponseHeaders | None = None,
        return_dto: type[AbstractDTO] | None | EmptyType = Empty,
        signature_namespace: Mapping[str, Any] | None = None,
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
        security: Sequence[SecurityRequirement] | None = None,
        summary: str | None = None,
        tags: Sequence[str] | None = None,
        type_decoders: TypeDecodersSequence | None = None,
        type_encoders: TypeEncodersMap | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize ``patch``.

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
                the :class:`.connection.Request` instance and any non-``None`` return value is used for the response,
                bypassing the route handler.
            cache: Enables response caching if configured on the application level. Valid values are ``True`` or a number
                of seconds (e.g. ``120``) to cache the response.
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
                :class:`HttpMethod <litestar.enums.HttpMethod>` or a list of these that correlates to the methods the
                route handler function should handle.
            media_type: A member of the :class:`MediaType <.enums.MediaType>` enum or a string with a
                valid IANA Media-Type.
            middleware: A sequence of :class:`Middleware <.types.Middleware>`.
            name: A string identifying the route handler.
            opt: A string keyed mapping of arbitrary values that can be accessed in :class:`Guards <.types.Guard>` or
                wherever you have access to :class:`Request <.connection.Request>` or :class:`ASGI Scope <.types.Scope>`.
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
            content_encoding: A string describing the encoding of the content, e.g. ``base64``.
            content_media_type: A string designating the media-type of the content, e.g. ``image/png``.
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
            type_decoders: A sequence of tuples, each composed of a predicate testing for type identity and a msgspec
                hook for deserialization.
            type_encoders: A mapping of types to callables that transform them into types supported for serialization.
            **kwargs: Any additional kwarg - will be set in the opt dictionary.
        """
        if "http_method" in kwargs:
            raise ImproperlyConfiguredException(MSG_SEMANTIC_ROUTE_HANDLER_WITH_HTTP)
        super().__init__(
            after_request=after_request,
            after_response=after_response,
            background=background,
            before_request=before_request,
            cache=cache,
            cache_control=cache_control,
            cache_key_builder=cache_key_builder,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            dependencies=dependencies,
            deprecated=deprecated,
            description=description,
            dto=dto,
            etag=etag,
            exception_handlers=exception_handlers,
            guards=guards,
            http_method=HttpMethod.PATCH,
            include_in_schema=include_in_schema,
            media_type=media_type,
            middleware=middleware,
            name=name,
            operation_class=operation_class,
            operation_id=operation_id,
            opt=opt,
            path=path,
            raises=raises,
            request_class=request_class,
            response_class=response_class,
            response_cookies=response_cookies,
            response_description=response_description,
            response_headers=response_headers,
            responses=responses,
            return_dto=return_dto,
            security=security,
            signature_namespace=signature_namespace,
            status_code=status_code,
            summary=summary,
            sync_to_thread=sync_to_thread,
            tags=tags,
            type_decoders=type_decoders,
            type_encoders=type_encoders,
            **kwargs,
        )

    def __init_subclass__(cls, **kwargs: Any) -> None:
        _subclass_warning()


class post(HTTPRouteHandler):
    """POST Route Decorator.

    Use this decorator to decorate an HTTP handler for POST requests.
    """

    def __init__(
        self,
        path: str | None | Sequence[str] = None,
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
        media_type: MediaType | str | None = None,
        middleware: Sequence[Middleware] | None = None,
        name: str | None = None,
        opt: Mapping[str, Any] | None = None,
        request_class: type[Request] | None = None,
        response_class: type[Response] | None = None,
        response_cookies: ResponseCookies | None = None,
        response_headers: ResponseHeaders | None = None,
        return_dto: type[AbstractDTO] | None | EmptyType = Empty,
        signature_namespace: Mapping[str, Any] | None = None,
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
        security: Sequence[SecurityRequirement] | None = None,
        summary: str | None = None,
        tags: Sequence[str] | None = None,
        type_decoders: TypeDecodersSequence | None = None,
        type_encoders: TypeEncodersMap | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize ``post``

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
                the :class:`.connection.Request` instance and any non-``None`` return value is used for the response,
                bypassing the route handler.
            cache: Enables response caching if configured on the application level. Valid values are ``True`` or a number
                of seconds (e.g. ``120``) to cache the response.
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
                :class:`HttpMethod <litestar.enums.HttpMethod>` or a list of these that correlates to the methods the
                route handler function should handle.
            media_type: A member of the :class:`MediaType <.enums.MediaType>` enum or a string with a
                valid IANA Media-Type.
            middleware: A sequence of :class:`Middleware <.types.Middleware>`.
            name: A string identifying the route handler.
            opt: A string keyed mapping of arbitrary values that can be accessed in :class:`Guards <.types.Guard>` or
                wherever you have access to :class:`Request <.connection.Request>` or :class:`ASGI Scope <.types.Scope>`.
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
            content_encoding: A string describing the encoding of the content, e.g. ``base64``.
            content_media_type: A string designating the media-type of the content, e.g. ``image/png``.
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
            type_decoders: A sequence of tuples, each composed of a predicate testing for type identity and a msgspec
                hook for deserialization.
            type_encoders: A mapping of types to callables that transform them into types supported for serialization.
            **kwargs: Any additional kwarg - will be set in the opt dictionary.
        """
        if "http_method" in kwargs:
            raise ImproperlyConfiguredException(MSG_SEMANTIC_ROUTE_HANDLER_WITH_HTTP)
        super().__init__(
            after_request=after_request,
            after_response=after_response,
            background=background,
            before_request=before_request,
            cache=cache,
            cache_control=cache_control,
            cache_key_builder=cache_key_builder,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            dependencies=dependencies,
            deprecated=deprecated,
            description=description,
            dto=dto,
            exception_handlers=exception_handlers,
            etag=etag,
            guards=guards,
            http_method=HttpMethod.POST,
            include_in_schema=include_in_schema,
            media_type=media_type,
            middleware=middleware,
            name=name,
            operation_class=operation_class,
            operation_id=operation_id,
            opt=opt,
            path=path,
            raises=raises,
            request_class=request_class,
            response_class=response_class,
            response_cookies=response_cookies,
            response_description=response_description,
            response_headers=response_headers,
            responses=responses,
            return_dto=return_dto,
            signature_namespace=signature_namespace,
            security=security,
            status_code=status_code,
            summary=summary,
            sync_to_thread=sync_to_thread,
            tags=tags,
            type_decoders=type_decoders,
            type_encoders=type_encoders,
            **kwargs,
        )

    def __init_subclass__(cls, **kwargs: Any) -> None:
        _subclass_warning()


class put(HTTPRouteHandler):
    """PUT Route Decorator.

    Use this decorator to decorate an HTTP handler for PUT requests.
    """

    def __init__(
        self,
        path: str | None | Sequence[str] = None,
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
        media_type: MediaType | str | None = None,
        middleware: Sequence[Middleware] | None = None,
        name: str | None = None,
        opt: Mapping[str, Any] | None = None,
        request_class: type[Request] | None = None,
        response_class: type[Response] | None = None,
        response_cookies: ResponseCookies | None = None,
        response_headers: ResponseHeaders | None = None,
        return_dto: type[AbstractDTO] | None | EmptyType = Empty,
        signature_namespace: Mapping[str, Any] | None = None,
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
        security: Sequence[SecurityRequirement] | None = None,
        summary: str | None = None,
        tags: Sequence[str] | None = None,
        type_decoders: TypeDecodersSequence | None = None,
        type_encoders: TypeEncodersMap | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize ``put``

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
                the :class:`.connection.Request` instance and any non-``None`` return value is used for the response,
                bypassing the route handler.
            cache: Enables response caching if configured on the application level. Valid values are ``True`` or a number
                of seconds (e.g. ``120``) to cache the response.
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
                :class:`HttpMethod <litestar.enums.HttpMethod>` or a list of these that correlates to the methods the
                route handler function should handle.
            media_type: A member of the :class:`MediaType <.enums.MediaType>` enum or a string with a
                valid IANA Media-Type.
            middleware: A sequence of :class:`Middleware <.types.Middleware>`.
            name: A string identifying the route handler.
            opt: A string keyed mapping of arbitrary values that can be accessed in :class:`Guards <.types.Guard>` or
                wherever you have access to :class:`Request <.connection.Request>` or :class:`ASGI Scope <.types.Scope>`.
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
            content_encoding: A string describing the encoding of the content, e.g. ``base64``.
            content_media_type: A string designating the media-type of the content, e.g. ``image/png``.
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
            type_decoders: A sequence of tuples, each composed of a predicate testing for type identity and a msgspec
                hook for deserialization.
            type_encoders: A mapping of types to callables that transform them into types supported for serialization.
            **kwargs: Any additional kwarg - will be set in the opt dictionary.
        """
        if "http_method" in kwargs:
            raise ImproperlyConfiguredException(MSG_SEMANTIC_ROUTE_HANDLER_WITH_HTTP)
        super().__init__(
            after_request=after_request,
            after_response=after_response,
            background=background,
            before_request=before_request,
            cache=cache,
            cache_control=cache_control,
            cache_key_builder=cache_key_builder,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            dependencies=dependencies,
            deprecated=deprecated,
            description=description,
            dto=dto,
            exception_handlers=exception_handlers,
            etag=etag,
            guards=guards,
            http_method=HttpMethod.PUT,
            include_in_schema=include_in_schema,
            media_type=media_type,
            middleware=middleware,
            name=name,
            operation_class=operation_class,
            operation_id=operation_id,
            opt=opt,
            path=path,
            raises=raises,
            request_class=request_class,
            response_class=response_class,
            response_cookies=response_cookies,
            response_description=response_description,
            response_headers=response_headers,
            responses=responses,
            return_dto=return_dto,
            security=security,
            signature_namespace=signature_namespace,
            status_code=status_code,
            summary=summary,
            sync_to_thread=sync_to_thread,
            tags=tags,
            type_decoders=type_decoders,
            type_encoders=type_encoders,
            **kwargs,
        )

    def __init_subclass__(cls, **kwargs: Any) -> None:
        _subclass_warning()
