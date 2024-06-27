from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Literal, Mapping, Sequence

from litestar.app import DEFAULT_OPENAPI_CONFIG, Litestar
from litestar.controller import Controller
from litestar.events import SimpleEventEmitter
from litestar.testing.client import AsyncTestClient, TestClient
from litestar.types import Empty
from litestar.utils.predicates import is_class_and_subclass

if TYPE_CHECKING:
    from contextlib import AbstractAsyncContextManager

    from litestar import Request, Response, WebSocket
    from litestar.config.allowed_hosts import AllowedHostsConfig
    from litestar.config.app import ExperimentalFeatures
    from litestar.config.compression import CompressionConfig
    from litestar.config.cors import CORSConfig
    from litestar.config.csrf import CSRFConfig
    from litestar.config.response_cache import ResponseCacheConfig
    from litestar.datastructures import CacheControlHeader, ETag, State
    from litestar.dto import AbstractDTO
    from litestar.events import BaseEventEmitterBackend, EventListener
    from litestar.logging.config import BaseLoggingConfig
    from litestar.middleware.session.base import BaseBackendConfig
    from litestar.openapi.config import OpenAPIConfig
    from litestar.openapi.spec import SecurityRequirement
    from litestar.plugins import PluginProtocol
    from litestar.static_files.config import StaticFilesConfig
    from litestar.stores.base import Store
    from litestar.stores.registry import StoreRegistry
    from litestar.template.config import TemplateConfig
    from litestar.types import (
        AfterExceptionHookHandler,
        AfterRequestHookHandler,
        AfterResponseHookHandler,
        BeforeMessageSendHookHandler,
        BeforeRequestHookHandler,
        ControllerRouterHandler,
        Dependencies,
        EmptyType,
        ExceptionHandlersMap,
        Guard,
        LifespanHook,
        Middleware,
        OnAppInitHandler,
        ParametersMap,
        ResponseCookies,
        ResponseHeaders,
        TypeEncodersMap,
    )


def create_test_client(
    route_handlers: ControllerRouterHandler | Sequence[ControllerRouterHandler] | None = None,
    *,
    after_exception: Sequence[AfterExceptionHookHandler] | None = None,
    after_request: AfterRequestHookHandler | None = None,
    after_response: AfterResponseHookHandler | None = None,
    allowed_hosts: Sequence[str] | AllowedHostsConfig | None = None,
    backend: Literal["asyncio", "trio"] = "asyncio",
    backend_options: Mapping[str, Any] | None = None,
    base_url: str = "http://testserver.local",
    before_request: BeforeRequestHookHandler | None = None,
    before_send: Sequence[BeforeMessageSendHookHandler] | None = None,
    cache_control: CacheControlHeader | None = None,
    compression_config: CompressionConfig | None = None,
    cors_config: CORSConfig | None = None,
    csrf_config: CSRFConfig | None = None,
    debug: bool = True,
    dependencies: Dependencies | None = None,
    dto: type[AbstractDTO] | None | EmptyType = Empty,
    etag: ETag | None = None,
    event_emitter_backend: type[BaseEventEmitterBackend] = SimpleEventEmitter,
    exception_handlers: ExceptionHandlersMap | None = None,
    guards: Sequence[Guard] | None = None,
    include_in_schema: bool | EmptyType = Empty,
    listeners: Sequence[EventListener] | None = None,
    logging_config: BaseLoggingConfig | EmptyType | None = Empty,
    middleware: Sequence[Middleware] | None = None,
    multipart_form_part_limit: int = 1000,
    on_app_init: Sequence[OnAppInitHandler] | None = None,
    on_shutdown: Sequence[LifespanHook] | None = None,
    on_startup: Sequence[LifespanHook] | None = None,
    openapi_config: OpenAPIConfig | None = DEFAULT_OPENAPI_CONFIG,
    opt: Mapping[str, Any] | None = None,
    parameters: ParametersMap | None = None,
    path: str | None = None,
    plugins: Sequence[PluginProtocol] | None = None,
    lifespan: list[Callable[[Litestar], AbstractAsyncContextManager] | AbstractAsyncContextManager] | None = None,
    raise_server_exceptions: bool = True,
    pdb_on_exception: bool | None = None,
    request_class: type[Request] | None = None,
    response_cache_config: ResponseCacheConfig | None = None,
    response_class: type[Response] | None = None,
    response_cookies: ResponseCookies | None = None,
    response_headers: ResponseHeaders | None = None,
    return_dto: type[AbstractDTO] | None | EmptyType = Empty,
    root_path: str = "",
    security: Sequence[SecurityRequirement] | None = None,
    session_config: BaseBackendConfig | None = None,
    signature_namespace: Mapping[str, Any] | None = None,
    signature_types: Sequence[Any] | None = None,
    state: State | None = None,
    static_files_config: Sequence[StaticFilesConfig] | None = None,
    stores: StoreRegistry | dict[str, Store] | None = None,
    tags: Sequence[str] | None = None,
    template_config: TemplateConfig | None = None,
    timeout: float | None = None,
    type_encoders: TypeEncodersMap | None = None,
    websocket_class: type[WebSocket] | None = None,
    experimental_features: list[ExperimentalFeatures] | None = None,
) -> TestClient[Litestar]:
    """Create a Litestar app instance and initializes it.

    :class:`TestClient <litestar.testing.TestClient>` with it.

    Notes:
        - This function should be called as a context manager to ensure async startup and shutdown are
            handled correctly.

    Examples:
        .. code-block:: python

            from litestar import get
            from litestar.testing import create_test_client


            @get("/some-path")
            def my_handler() -> dict[str, str]:
                return {"hello": "world"}


            def test_my_handler() -> None:
                with create_test_client(my_handler) as client:
                    response = client.get("/some-path")
                    assert response.json() == {"hello": "world"}

    Args:
        route_handlers: A single handler or a sequence of route handlers, which can include instances of
            :class:`Router <litestar.router.Router>`, subclasses of :class:`Controller <.controller.Controller>` or
            any function decorated by the route handler decorators.
        backend: The async backend to use, options are "asyncio" or "trio".
        backend_options: ``anyio`` options.
        base_url: URL scheme and domain for test request paths, e.g. ``http://testserver``.
        raise_server_exceptions: Flag for underlying the test client to raise server exceptions instead of wrapping them
            in an HTTP response.
        root_path: Path prefix for requests.
        session_config: Configuration for Session Middleware class to create raw session cookies for request to the
            route handlers.
        after_exception: A sequence of :class:`exception hook handlers <.types.AfterExceptionHookHandler>`. This
            hook is called after an exception occurs. In difference to exception handlers, it is not meant to
            return a response - only to process the exception (e.g. log it, send it to Sentry etc.).
        after_request: A sync or async function executed after the route handler function returned and the response
            object has been resolved. Receives the response object.
        after_response: A sync or async function called after the response has been awaited. It receives the
            :class:`Request <.connection.Request>` object and should not return any values.
        allowed_hosts: A sequence of allowed hosts, or an
            :class:`AllowedHostsConfig <.config.allowed_hosts.AllowedHostsConfig>` instance. Enables the builtin
            allowed hosts middleware.
        before_request: A sync or async function called immediately before calling the route handler. Receives the
            :class:`Request <.connection.Request>` instance and any non-``None`` return value is used for the
            response, bypassing the route handler.
        before_send: A sequence of :class:`before send hook handlers <.types.BeforeMessageSendHookHandler>`. Called
            when the ASGI send function is called.
        cache_control: A ``cache-control`` header of type
            :class:`CacheControlHeader <litestar.datastructures.CacheControlHeader>` to add to route handlers of
            this app. Can be overridden by route handlers.
        compression_config: Configures compression behaviour of the application, this enabled a builtin or user
            defined Compression middleware.
        cors_config: If set, configures CORS handling for the application.
        csrf_config: If set, configures :class:`CSRFMiddleware <.middleware.csrf.CSRFMiddleware>`.
        debug: If ``True``, app errors rendered as HTML with a stack trace.
        dependencies: A string keyed mapping of dependency :class:`Providers <.di.Provide>`.
        dto: :class:`AbstractDTO <.dto.base_dto.AbstractDTO>` to use for (de)serializing and
            validation of request data.
        etag: An ``etag`` header of type :class:`ETag <.datastructures.ETag>` to add to route handlers of this app.
            Can be overridden by route handlers.
        event_emitter_backend: A subclass of
            :class:`BaseEventEmitterBackend <.events.emitter.BaseEventEmitterBackend>`.
        exception_handlers: A mapping of status codes and/or exception types to handler functions.
        guards: A sequence of :class:`Guard <.types.Guard>` callables.
        include_in_schema: A boolean flag dictating whether  the route handler should be documented in the OpenAPI schema.
        lifespan: A list of callables returning async context managers, wrapping the lifespan of the ASGI application
        listeners: A sequence of :class:`EventListener <.events.listener.EventListener>`.
        logging_config: A subclass of :class:`BaseLoggingConfig <.logging.config.BaseLoggingConfig>`.
        middleware: A sequence of :class:`Middleware <.types.Middleware>`.
        multipart_form_part_limit: The maximal number of allowed parts in a multipart/formdata request. This limit
            is intended to protect from DoS attacks.
        on_app_init: A sequence of :class:`OnAppInitHandler <.types.OnAppInitHandler>` instances. Handlers receive
            an instance of :class:`AppConfig <.config.app.AppConfig>` that will have been initially populated with
            the parameters passed to :class:`Litestar <litestar.app.Litestar>`, and must return an instance of same.
            If more than one handler is registered they are called in the order they are provided.
        on_shutdown: A sequence of :class:`LifespanHook <.types.LifespanHook>` called during application
            shutdown.
        on_startup: A sequence of :class:`LifespanHook <litestar.types.LifespanHook>` called during
            application startup.
        openapi_config: Defaults to :attr:`DEFAULT_OPENAPI_CONFIG`
        opt: A string keyed mapping of arbitrary values that can be accessed in :class:`Guards <.types.Guard>` or
            wherever you have access to :class:`Request <litestar.connection.request.Request>` or
            :class:`ASGI Scope <.types.Scope>`.
        parameters: A mapping of :class:`Parameter <.params.Parameter>` definitions available to all application
            paths.
        path: A path fragment that is prefixed to all route handlers, controllers and routers associated
            with the application instance.

            .. versionadded:: 2.8.0
        pdb_on_exception: Drop into the PDB when an exception occurs.
        plugins: Sequence of plugins.
        request_class: An optional subclass of :class:`Request <.connection.Request>` to use for http connections.
        response_class: A custom subclass of :class:`Response <.response.Response>` to be used as the app's default
            response.
        response_cookies: A sequence of :class:`Cookie <.datastructures.Cookie>`.
        response_headers: A string keyed mapping of :class:`ResponseHeader <.datastructures.ResponseHeader>`
        response_cache_config: Configures caching behavior of the application.
        return_dto: :class:`AbstractDTO <.dto.base_dto.AbstractDTO>` to use for serializing
            outbound response data.
        route_handlers: A sequence of route handlers, which can include instances of
            :class:`Router <.router.Router>`, subclasses of :class:`Controller <.controller.Controller>` or any
            callable decorated by the route handler decorators.
        security: A sequence of dicts that will be added to the schema of all route handlers in the application.
            See
            :data:`SecurityRequirement <.openapi.spec.SecurityRequirement>` for details.
        signature_namespace: A mapping of names to types for use in forward reference resolution during signature modeling.
        signature_types: A sequence of types for use in forward reference resolution during signature modeling.
            These types will be added to the signature namespace using their ``__name__`` attribute.
        state: An optional :class:`State <.datastructures.State>` for application state.
        static_files_config: A sequence of :class:`StaticFilesConfig <.static_files.StaticFilesConfig>`
        stores: Central registry of :class:`Store <.stores.base.Store>` that will be available throughout the
            application. If this is a dictionary to it will be passed to a
            :class:`StoreRegistry <.stores.registry.StoreRegistry>`. If it is a
            :class:`StoreRegistry <.stores.registry.StoreRegistry>`, this instance will be used directly.
        tags: A sequence of string tags that will be appended to the schema of all route handlers under the
            application.
        template_config: An instance of :class:`TemplateConfig <.template.TemplateConfig>`
        timeout: Request timeout
        type_encoders: A mapping of types to callables that transform them into types supported for serialization.
        websocket_class: An optional subclass of :class:`WebSocket <.connection.WebSocket>` to use for websocket
            connections.
        experimental_features: An iterable of experimental features to enable


    Returns:
        An instance of :class:`TestClient <.testing.TestClient>` with a created app instance.
    """
    route_handlers = () if route_handlers is None else route_handlers
    if is_class_and_subclass(route_handlers, Controller) or not isinstance(route_handlers, Sequence):
        route_handlers = (route_handlers,)

    app = Litestar(
        after_exception=after_exception,
        after_request=after_request,
        after_response=after_response,
        allowed_hosts=allowed_hosts,
        before_request=before_request,
        before_send=before_send,
        cache_control=cache_control,
        compression_config=compression_config,
        cors_config=cors_config,
        csrf_config=csrf_config,
        debug=debug,
        dependencies=dependencies,
        dto=dto,
        etag=etag,
        lifespan=lifespan,
        event_emitter_backend=event_emitter_backend,
        exception_handlers=exception_handlers,
        guards=guards,
        include_in_schema=include_in_schema,
        listeners=listeners,
        logging_config=logging_config,
        middleware=middleware,
        multipart_form_part_limit=multipart_form_part_limit,
        on_app_init=on_app_init,
        on_shutdown=on_shutdown,
        on_startup=on_startup,
        openapi_config=openapi_config,
        opt=opt,
        parameters=parameters,
        path=path,
        pdb_on_exception=pdb_on_exception,
        plugins=plugins,
        request_class=request_class,
        response_cache_config=response_cache_config,
        response_class=response_class,
        response_cookies=response_cookies,
        response_headers=response_headers,
        return_dto=return_dto,
        route_handlers=route_handlers,
        security=security,
        signature_namespace=signature_namespace,
        signature_types=signature_types,
        state=state,
        static_files_config=static_files_config,
        stores=stores,
        tags=tags,
        template_config=template_config,
        type_encoders=type_encoders,
        websocket_class=websocket_class,
        experimental_features=experimental_features,
    )

    return TestClient[Litestar](
        app=app,
        backend=backend,
        backend_options=backend_options,
        base_url=base_url,
        raise_server_exceptions=raise_server_exceptions,
        root_path=root_path,
        session_config=session_config,
        timeout=timeout,
    )


def create_async_test_client(
    route_handlers: ControllerRouterHandler | Sequence[ControllerRouterHandler] | None = None,
    *,
    after_exception: Sequence[AfterExceptionHookHandler] | None = None,
    after_request: AfterRequestHookHandler | None = None,
    after_response: AfterResponseHookHandler | None = None,
    allowed_hosts: Sequence[str] | AllowedHostsConfig | None = None,
    backend: Literal["asyncio", "trio"] = "asyncio",
    backend_options: Mapping[str, Any] | None = None,
    base_url: str = "http://testserver.local",
    before_request: BeforeRequestHookHandler | None = None,
    before_send: Sequence[BeforeMessageSendHookHandler] | None = None,
    cache_control: CacheControlHeader | None = None,
    compression_config: CompressionConfig | None = None,
    cors_config: CORSConfig | None = None,
    csrf_config: CSRFConfig | None = None,
    debug: bool = True,
    dependencies: Dependencies | None = None,
    dto: type[AbstractDTO] | None | EmptyType = Empty,
    etag: ETag | None = None,
    event_emitter_backend: type[BaseEventEmitterBackend] = SimpleEventEmitter,
    exception_handlers: ExceptionHandlersMap | None = None,
    guards: Sequence[Guard] | None = None,
    include_in_schema: bool | EmptyType = Empty,
    lifespan: list[Callable[[Litestar], AbstractAsyncContextManager] | AbstractAsyncContextManager] | None = None,
    listeners: Sequence[EventListener] | None = None,
    logging_config: BaseLoggingConfig | EmptyType | None = Empty,
    middleware: Sequence[Middleware] | None = None,
    multipart_form_part_limit: int = 1000,
    on_app_init: Sequence[OnAppInitHandler] | None = None,
    on_shutdown: Sequence[LifespanHook] | None = None,
    on_startup: Sequence[LifespanHook] | None = None,
    openapi_config: OpenAPIConfig | None = DEFAULT_OPENAPI_CONFIG,
    opt: Mapping[str, Any] | None = None,
    parameters: ParametersMap | None = None,
    pdb_on_exception: bool | None = None,
    path: str | None = None,
    plugins: Sequence[PluginProtocol] | None = None,
    raise_server_exceptions: bool = True,
    request_class: type[Request] | None = None,
    response_cache_config: ResponseCacheConfig | None = None,
    response_class: type[Response] | None = None,
    response_cookies: ResponseCookies | None = None,
    response_headers: ResponseHeaders | None = None,
    return_dto: type[AbstractDTO] | None | EmptyType = Empty,
    root_path: str = "",
    security: Sequence[SecurityRequirement] | None = None,
    session_config: BaseBackendConfig | None = None,
    signature_namespace: Mapping[str, Any] | None = None,
    signature_types: Sequence[Any] | None = None,
    state: State | None = None,
    static_files_config: Sequence[StaticFilesConfig] | None = None,
    stores: StoreRegistry | dict[str, Store] | None = None,
    tags: Sequence[str] | None = None,
    template_config: TemplateConfig | None = None,
    timeout: float | None = None,
    type_encoders: TypeEncodersMap | None = None,
    websocket_class: type[WebSocket] | None = None,
    experimental_features: list[ExperimentalFeatures] | None = None,
) -> AsyncTestClient[Litestar]:
    """Create a Litestar app instance and initializes it.

    :class:`AsyncTestClient <litestar.testing.AsyncTestClient>` with it.

    Notes:
        - This function should be called as a context manager to ensure async startup and shutdown are
            handled correctly.

    Examples:
        .. code-block:: python

            from litestar import get
            from litestar.testing import create_async_test_client


            @get("/some-path")
            def my_handler() -> dict[str, str]:
                return {"hello": "world"}


            async def test_my_handler() -> None:
                async with create_async_test_client(my_handler) as client:
                    response = await client.get("/some-path")
                    assert response.json() == {"hello": "world"}

    Args:
        route_handlers: A single handler or a sequence of route handlers, which can include instances of
            :class:`Router <litestar.router.Router>`, subclasses of :class:`Controller <.controller.Controller>` or
            any function decorated by the route handler decorators.
        backend: The async backend to use, options are "asyncio" or "trio".
        backend_options: ``anyio`` options.
        base_url: URL scheme and domain for test request paths, e.g. ``http://testserver``.
        raise_server_exceptions: Flag for underlying the test client to raise server exceptions instead of wrapping them
            in an HTTP response.
        root_path: Path prefix for requests.
        session_config: Configuration for Session Middleware class to create raw session cookies for request to the
            route handlers.
        after_exception: A sequence of :class:`exception hook handlers <.types.AfterExceptionHookHandler>`. This
            hook is called after an exception occurs. In difference to exception handlers, it is not meant to
            return a response - only to process the exception (e.g. log it, send it to Sentry etc.).
        after_request: A sync or async function executed after the route handler function returned and the response
            object has been resolved. Receives the response object.
        after_response: A sync or async function called after the response has been awaited. It receives the
            :class:`Request <.connection.Request>` object and should not return any values.
        allowed_hosts: A sequence of allowed hosts, or an
            :class:`AllowedHostsConfig <.config.allowed_hosts.AllowedHostsConfig>` instance. Enables the builtin
            allowed hosts middleware.
        before_request: A sync or async function called immediately before calling the route handler. Receives the
            :class:`Request <.connection.Request>` instance and any non-``None`` return value is used for the
            response, bypassing the route handler.
        before_send: A sequence of :class:`before send hook handlers <.types.BeforeMessageSendHookHandler>`. Called
            when the ASGI send function is called.
        cache_control: A ``cache-control`` header of type
            :class:`CacheControlHeader <litestar.datastructures.CacheControlHeader>` to add to route handlers of
            this app. Can be overridden by route handlers.
        compression_config: Configures compression behaviour of the application, this enabled a builtin or user
            defined Compression middleware.
        cors_config: If set, configures CORS handling for the application.
        csrf_config: If set, configures :class:`CSRFMiddleware <.middleware.csrf.CSRFMiddleware>`.
        debug: If ``True``, app errors rendered as HTML with a stack trace.
        dependencies: A string keyed mapping of dependency :class:`Providers <.di.Provide>`.
        dto: :class:`AbstractDTO <.dto.base_dto.AbstractDTO>` to use for (de)serializing and
            validation of request data.
        etag: An ``etag`` header of type :class:`ETag <.datastructures.ETag>` to add to route handlers of this app.
            Can be overridden by route handlers.
        event_emitter_backend: A subclass of
            :class:`BaseEventEmitterBackend <.events.emitter.BaseEventEmitterBackend>`.
        exception_handlers: A mapping of status codes and/or exception types to handler functions.
        guards: A sequence of :class:`Guard <.types.Guard>` callables.
        include_in_schema: A boolean flag dictating whether  the route handler should be documented in the OpenAPI schema.
        lifespan: A list of callables returning async context managers, wrapping the lifespan of the ASGI application
        listeners: A sequence of :class:`EventListener <.events.listener.EventListener>`.
        logging_config: A subclass of :class:`BaseLoggingConfig <.logging.config.BaseLoggingConfig>`.
        middleware: A sequence of :class:`Middleware <.types.Middleware>`.
        multipart_form_part_limit: The maximal number of allowed parts in a multipart/formdata request. This limit
            is intended to protect from DoS attacks.
        on_app_init: A sequence of :class:`OnAppInitHandler <.types.OnAppInitHandler>` instances. Handlers receive
            an instance of :class:`AppConfig <.config.app.AppConfig>` that will have been initially populated with
            the parameters passed to :class:`Litestar <litestar.app.Litestar>`, and must return an instance of same.
            If more than one handler is registered they are called in the order they are provided.
        on_shutdown: A sequence of :class:`LifespanHook <.types.LifespanHook>` called during application
            shutdown.
        on_startup: A sequence of :class:`LifespanHook <litestar.types.LifespanHook>` called during
            application startup.
        openapi_config: Defaults to :attr:`DEFAULT_OPENAPI_CONFIG`
        opt: A string keyed mapping of arbitrary values that can be accessed in :class:`Guards <.types.Guard>` or
            wherever you have access to :class:`Request <litestar.connection.request.Request>` or
            :class:`ASGI Scope <.types.Scope>`.
        parameters: A mapping of :class:`Parameter <.params.Parameter>` definitions available to all application
            paths.
        path: A path fragment that is prefixed to all route handlers, controllers and routers associated
            with the application instance.

            .. versionadded:: 2.8.0
        pdb_on_exception: Drop into the PDB when an exception occurs.
        plugins: Sequence of plugins.
        request_class: An optional subclass of :class:`Request <.connection.Request>` to use for http connections.
        response_class: A custom subclass of :class:`Response <.response.Response>` to be used as the app's default
            response.
        response_cookies: A sequence of :class:`Cookie <.datastructures.Cookie>`.
        response_headers: A string keyed mapping of :class:`ResponseHeader <.datastructures.ResponseHeader>`
        response_cache_config: Configures caching behavior of the application.
        return_dto: :class:`AbstractDTO <.dto.base_dto.AbstractDTO>` to use for serializing
            outbound response data.
        route_handlers: A sequence of route handlers, which can include instances of
            :class:`Router <.router.Router>`, subclasses of :class:`Controller <.controller.Controller>` or any
            callable decorated by the route handler decorators.
        security: A sequence of dicts that will be added to the schema of all route handlers in the application.
            See
            :data:`SecurityRequirement <.openapi.spec.SecurityRequirement>` for details.
        signature_namespace: A mapping of names to types for use in forward reference resolution during signature modeling.
        signature_types: A sequence of types for use in forward reference resolution during signature modeling.
            These types will be added to the signature namespace using their ``__name__`` attribute.
        state: An optional :class:`State <.datastructures.State>` for application state.
        static_files_config: A sequence of :class:`StaticFilesConfig <.static_files.StaticFilesConfig>`
        stores: Central registry of :class:`Store <.stores.base.Store>` that will be available throughout the
            application. If this is a dictionary to it will be passed to a
            :class:`StoreRegistry <.stores.registry.StoreRegistry>`. If it is a
            :class:`StoreRegistry <.stores.registry.StoreRegistry>`, this instance will be used directly.
        tags: A sequence of string tags that will be appended to the schema of all route handlers under the
            application.
        template_config: An instance of :class:`TemplateConfig <.template.TemplateConfig>`
        timeout: Request timeout
        type_encoders: A mapping of types to callables that transform them into types supported for serialization.
        websocket_class: An optional subclass of :class:`WebSocket <.connection.WebSocket>` to use for websocket
            connections.
        experimental_features: An iterable of experimental features to enable

    Returns:
        An instance of :class:`AsyncTestClient <litestar.testing.AsyncTestClient>` with a created app instance.
    """
    route_handlers = () if route_handlers is None else route_handlers
    if is_class_and_subclass(route_handlers, Controller) or not isinstance(route_handlers, Sequence):
        route_handlers = (route_handlers,)

    app = Litestar(
        after_exception=after_exception,
        after_request=after_request,
        after_response=after_response,
        allowed_hosts=allowed_hosts,
        before_request=before_request,
        before_send=before_send,
        cache_control=cache_control,
        compression_config=compression_config,
        cors_config=cors_config,
        csrf_config=csrf_config,
        debug=debug,
        dependencies=dependencies,
        dto=dto,
        etag=etag,
        event_emitter_backend=event_emitter_backend,
        exception_handlers=exception_handlers,
        guards=guards,
        include_in_schema=include_in_schema,
        lifespan=lifespan,
        listeners=listeners,
        logging_config=logging_config,
        middleware=middleware,
        multipart_form_part_limit=multipart_form_part_limit,
        on_app_init=on_app_init,
        on_shutdown=on_shutdown,
        on_startup=on_startup,
        openapi_config=openapi_config,
        opt=opt,
        parameters=parameters,
        path=path,
        pdb_on_exception=pdb_on_exception,
        plugins=plugins,
        request_class=request_class,
        response_cache_config=response_cache_config,
        response_class=response_class,
        response_cookies=response_cookies,
        response_headers=response_headers,
        return_dto=return_dto,
        route_handlers=route_handlers,
        security=security,
        signature_namespace=signature_namespace,
        signature_types=signature_types,
        state=state,
        static_files_config=static_files_config,
        stores=stores,
        tags=tags,
        template_config=template_config,
        type_encoders=type_encoders,
        websocket_class=websocket_class,
        experimental_features=experimental_features,
    )

    return AsyncTestClient[Litestar](
        app=app,
        backend=backend,
        backend_options=backend_options,
        base_url=base_url,
        raise_server_exceptions=raise_server_exceptions,
        root_path=root_path,
        session_config=session_config,
        timeout=timeout,
    )
