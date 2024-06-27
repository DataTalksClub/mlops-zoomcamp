from __future__ import annotations

import inspect
import logging
import os
import warnings
from contextlib import (
    AbstractAsyncContextManager,
    AsyncExitStack,
    asynccontextmanager,
    suppress,
)
from datetime import date, datetime, time, timedelta
from functools import partial
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncGenerator, Callable, Iterable, Mapping, Sequence, TypedDict, cast

from litestar._asgi import ASGIRouter
from litestar._asgi.utils import get_route_handlers, wrap_in_exception_handler
from litestar._openapi.plugin import OpenAPIPlugin
from litestar._openapi.schema_generation import openapi_schema_plugins
from litestar.config.allowed_hosts import AllowedHostsConfig
from litestar.config.app import AppConfig, ExperimentalFeatures
from litestar.config.response_cache import ResponseCacheConfig
from litestar.connection import Request, WebSocket
from litestar.datastructures.state import State
from litestar.events.emitter import BaseEventEmitterBackend, SimpleEventEmitter
from litestar.exceptions import (
    LitestarWarning,
    MissingDependencyException,
    NoRouteMatchFoundException,
)
from litestar.logging.config import LoggingConfig, get_logger_placeholder
from litestar.middleware._internal.cors import CORSMiddleware
from litestar.openapi.config import OpenAPIConfig
from litestar.plugins import (
    CLIPluginProtocol,
    InitPluginProtocol,
    OpenAPISchemaPluginProtocol,
    PluginProtocol,
    PluginRegistry,
    SerializationPluginProtocol,
)
from litestar.plugins.base import CLIPlugin
from litestar.router import Router
from litestar.routes import ASGIRoute, HTTPRoute, WebSocketRoute
from litestar.static_files.base import StaticFiles
from litestar.stores.registry import StoreRegistry
from litestar.types import Empty, TypeDecodersSequence
from litestar.types.internal_types import PathParameterDefinition, TemplateConfigType
from litestar.utils import deprecated, ensure_async_callable, join_paths, unique
from litestar.utils.dataclass import extract_dataclass_items
from litestar.utils.predicates import is_async_callable
from litestar.utils.warnings import warn_pdb_on_exception

if TYPE_CHECKING:
    from typing_extensions import Self

    from litestar.config.compression import CompressionConfig
    from litestar.config.cors import CORSConfig
    from litestar.config.csrf import CSRFConfig
    from litestar.datastructures import CacheControlHeader, ETag
    from litestar.dto import AbstractDTO
    from litestar.events.listener import EventListener
    from litestar.logging.config import BaseLoggingConfig
    from litestar.openapi.spec import SecurityRequirement
    from litestar.openapi.spec.open_api import OpenAPI
    from litestar.response import Response
    from litestar.static_files.config import StaticFilesConfig
    from litestar.stores.base import Store
    from litestar.types import (
        AfterExceptionHookHandler,
        AfterRequestHookHandler,
        AfterResponseHookHandler,
        AnyCallable,
        ASGIApp,
        BeforeMessageSendHookHandler,
        BeforeRequestHookHandler,
        ControllerRouterHandler,
        Dependencies,
        EmptyType,
        ExceptionHandlersMap,
        GetLogger,
        Guard,
        LifeSpanReceive,
        LifeSpanScope,
        LifeSpanSend,
        Logger,
        Message,
        Middleware,
        OnAppInitHandler,
        ParametersMap,
        Receive,
        ResponseCookies,
        ResponseHeaders,
        RouteHandlerType,
        Scope,
        Send,
        TypeEncodersMap,
    )
    from litestar.types.callable_types import LifespanHook


__all__ = ("HandlerIndex", "Litestar", "DEFAULT_OPENAPI_CONFIG")

DEFAULT_OPENAPI_CONFIG = OpenAPIConfig(title="Litestar API", version="1.0.0")
"""The default OpenAPI config used if not configuration is explicitly passed to the
:class:`Litestar <.app.Litestar>` instance constructor.
"""


class HandlerIndex(TypedDict):
    """Map route handler names to a mapping of paths + route handler.

    It's returned from the 'get_handler_index_by_name' utility method.
    """

    paths: list[str]
    """Full route paths to the route handler."""
    handler: RouteHandlerType
    """Route handler instance."""
    identifier: str
    """Unique identifier of the handler.

    Either equal to :attr`__name__ <obj.__name__>` attribute or ``__str__`` value of the handler.
    """


class Litestar(Router):
    """The Litestar application.

    ``Litestar`` is the root level of the app - it has the base path of ``/`` and all root level Controllers, Routers
    and Route Handlers should be registered on it.
    """

    __slots__ = (
        "_lifespan_managers",
        "_server_lifespan_managers",
        "_debug",
        "_openapi_schema",
        "_static_files_config",
        "plugins",
        "after_exception",
        "allowed_hosts",
        "asgi_handler",
        "asgi_router",
        "before_send",
        "compression_config",
        "cors_config",
        "csrf_config",
        "event_emitter",
        "get_logger",
        "logger",
        "logging_config",
        "multipart_form_part_limit",
        "on_shutdown",
        "on_startup",
        "openapi_config",
        "response_cache_config",
        "route_map",
        "state",
        "stores",
        "template_engine",
        "pdb_on_exception",
        "experimental_features",
    )

    def __init__(
        self,
        route_handlers: Sequence[ControllerRouterHandler] | None = None,
        *,
        after_exception: Sequence[AfterExceptionHookHandler] | None = None,
        after_request: AfterRequestHookHandler | None = None,
        after_response: AfterResponseHookHandler | None = None,
        allowed_hosts: Sequence[str] | AllowedHostsConfig | None = None,
        before_request: BeforeRequestHookHandler | None = None,
        before_send: Sequence[BeforeMessageSendHookHandler] | None = None,
        cache_control: CacheControlHeader | None = None,
        compression_config: CompressionConfig | None = None,
        cors_config: CORSConfig | None = None,
        csrf_config: CSRFConfig | None = None,
        dto: type[AbstractDTO] | None | EmptyType = Empty,
        debug: bool | None = None,
        dependencies: Dependencies | None = None,
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
        request_class: type[Request] | None = None,
        response_cache_config: ResponseCacheConfig | None = None,
        response_class: type[Response] | None = None,
        response_cookies: ResponseCookies | None = None,
        response_headers: ResponseHeaders | None = None,
        return_dto: type[AbstractDTO] | None | EmptyType = Empty,
        security: Sequence[SecurityRequirement] | None = None,
        signature_namespace: Mapping[str, Any] | None = None,
        signature_types: Sequence[Any] | None = None,
        state: State | None = None,
        static_files_config: Sequence[StaticFilesConfig] | None = None,
        stores: StoreRegistry | dict[str, Store] | None = None,
        tags: Sequence[str] | None = None,
        template_config: TemplateConfigType | None = None,
        type_decoders: TypeDecodersSequence | None = None,
        type_encoders: TypeEncodersMap | None = None,
        websocket_class: type[WebSocket] | None = None,
        lifespan: Sequence[Callable[[Litestar], AbstractAsyncContextManager] | AbstractAsyncContextManager]
        | None = None,
        pdb_on_exception: bool | None = None,
        experimental_features: Iterable[ExperimentalFeatures] | None = None,
    ) -> None:
        """Initialize a ``Litestar`` application.

        Args:
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
            type_decoders: A sequence of tuples, each composed of a predicate testing for type identity and a msgspec
                hook for deserialization.
            type_encoders: A mapping of types to callables that transform them into types supported for serialization.
            websocket_class: An optional subclass of :class:`WebSocket <.connection.WebSocket>` to use for websocket
                connections.
            experimental_features: An iterable of experimental features to enable
        """

        if logging_config is Empty:
            logging_config = LoggingConfig()

        if debug is None:
            debug = os.getenv("LITESTAR_DEBUG", "0") == "1"

        if pdb_on_exception is None:
            pdb_on_exception = os.getenv("LITESTAR_PDB", "0") == "1"

        config = AppConfig(
            after_exception=list(after_exception or []),
            after_request=after_request,
            after_response=after_response,
            allowed_hosts=allowed_hosts if isinstance(allowed_hosts, AllowedHostsConfig) else list(allowed_hosts or []),
            before_request=before_request,
            before_send=list(before_send or []),
            cache_control=cache_control,
            compression_config=compression_config,
            cors_config=cors_config,
            csrf_config=csrf_config,
            debug=debug,
            dependencies=dict(dependencies or {}),
            dto=dto,
            etag=etag,
            event_emitter_backend=event_emitter_backend,
            exception_handlers=exception_handlers or {},
            guards=list(guards or []),
            include_in_schema=include_in_schema,
            lifespan=list(lifespan or []),
            listeners=list(listeners or []),
            logging_config=logging_config,
            middleware=list(middleware or []),
            multipart_form_part_limit=multipart_form_part_limit,
            on_shutdown=list(on_shutdown or []),
            on_startup=list(on_startup or []),
            openapi_config=openapi_config,
            opt=dict(opt or {}),
            path=path or "",
            parameters=parameters or {},
            pdb_on_exception=pdb_on_exception,
            plugins=self._get_default_plugins(list(plugins or [])),
            request_class=request_class,
            response_cache_config=response_cache_config or ResponseCacheConfig(),
            response_class=response_class,
            response_cookies=response_cookies or [],
            response_headers=response_headers or [],
            return_dto=return_dto,
            route_handlers=list(route_handlers) if route_handlers is not None else [],
            security=list(security or []),
            signature_namespace=dict(signature_namespace or {}),
            signature_types=list(signature_types or []),
            state=state or State(),
            static_files_config=list(static_files_config or []),
            stores=stores,
            tags=list(tags or []),
            template_config=template_config,
            type_encoders=type_encoders,
            type_decoders=type_decoders,
            websocket_class=websocket_class,
            experimental_features=list(experimental_features or []),
        )

        config.plugins.extend([OpenAPIPlugin(self), *openapi_schema_plugins])

        for handler in chain(
            on_app_init or [],
            (p.on_app_init for p in config.plugins if isinstance(p, InitPluginProtocol)),
        ):
            config = handler(config)  # pyright: ignore
        self.plugins = PluginRegistry(config.plugins)

        self._openapi_schema: OpenAPI | None = None
        self._debug: bool = True
        self.stores: StoreRegistry = (
            config.stores if isinstance(config.stores, StoreRegistry) else StoreRegistry(config.stores)
        )
        self._lifespan_managers = config.lifespan
        for store in self.stores._stores.values():
            self._lifespan_managers.append(store)
        self._server_lifespan_managers = [p.server_lifespan for p in config.plugins or [] if isinstance(p, CLIPlugin)]
        self.experimental_features = frozenset(config.experimental_features or [])
        if ExperimentalFeatures.DTO_CODEGEN in self.experimental_features:
            warnings.warn(
                "Use of redundant experimental feature flag DTO_CODEGEN. "
                "DTO codegen backend is enabled by default since Litestar 2.8. The "
                "DTO_CODEGEN feature flag can be safely removed from the configuration "
                "and will be removed in version 3.0.",
                category=LitestarWarning,
                stacklevel=2,
            )

        self.get_logger: GetLogger = get_logger_placeholder
        self.logger: Logger | None = None
        self.routes: list[HTTPRoute | ASGIRoute | WebSocketRoute] = []

        self.after_exception = [ensure_async_callable(h) for h in config.after_exception]
        self.allowed_hosts = cast("AllowedHostsConfig | None", config.allowed_hosts)
        self.before_send = [ensure_async_callable(h) for h in config.before_send]
        self.compression_config = config.compression_config
        self.cors_config = config.cors_config
        self.csrf_config = config.csrf_config
        self.event_emitter = config.event_emitter_backend(listeners=config.listeners)
        self.logging_config = config.logging_config
        self.multipart_form_part_limit = config.multipart_form_part_limit
        self.on_shutdown = config.on_shutdown
        self.on_startup = config.on_startup
        self.openapi_config = config.openapi_config
        self.request_class: type[Request] = config.request_class or Request
        self.response_cache_config = config.response_cache_config
        self.state = config.state
        self._static_files_config = config.static_files_config
        self.template_engine = config.template_config.engine_instance if config.template_config else None
        self.websocket_class: type[WebSocket] = config.websocket_class or WebSocket
        self.debug = config.debug
        self.pdb_on_exception: bool = config.pdb_on_exception
        self.include_in_schema = include_in_schema

        if self.pdb_on_exception:
            warn_pdb_on_exception()

        try:
            from starlette.exceptions import HTTPException as StarletteHTTPException

            from litestar.middleware._internal.exceptions.middleware import _starlette_exception_handler

            config.exception_handlers.setdefault(StarletteHTTPException, _starlette_exception_handler)
        except ImportError:
            pass

        super().__init__(
            after_request=config.after_request,
            after_response=config.after_response,
            before_request=config.before_request,
            cache_control=config.cache_control,
            dependencies=config.dependencies,
            dto=config.dto,
            etag=config.etag,
            exception_handlers=config.exception_handlers,
            guards=config.guards,
            middleware=config.middleware,
            opt=config.opt,
            parameters=config.parameters,
            path=config.path,
            request_class=self.request_class,
            response_class=config.response_class,
            response_cookies=config.response_cookies,
            response_headers=config.response_headers,
            return_dto=config.return_dto,
            # route handlers are registered below
            route_handlers=[],
            security=config.security,
            signature_namespace=config.signature_namespace,
            signature_types=config.signature_types,
            tags=config.tags,
            type_encoders=config.type_encoders,
            type_decoders=config.type_decoders,
            include_in_schema=config.include_in_schema,
            websocket_class=self.websocket_class,
        )

        self.asgi_router = ASGIRouter(app=self)

        for route_handler in config.route_handlers:
            self.register(route_handler)

        if self.logging_config:
            self.get_logger = self.logging_config.configure()
            self.logger = self.get_logger("litestar")

        for static_config in self._static_files_config:
            self.register(static_config.to_static_files_app())

        self.asgi_handler = self._create_asgi_handler()

    @property
    @deprecated(version="2.6.0", kind="property", info="Use create_static_files router instead")
    def static_files_config(self) -> list[StaticFilesConfig]:
        return self._static_files_config

    @property
    @deprecated(version="2.0", alternative="Litestar.plugins.cli", kind="property")
    def cli_plugins(self) -> list[CLIPluginProtocol]:
        return list(self.plugins.cli)

    @property
    @deprecated(version="2.0", alternative="Litestar.plugins.openapi", kind="property")
    def openapi_schema_plugins(self) -> list[OpenAPISchemaPluginProtocol]:
        return list(self.plugins.openapi)

    @property
    @deprecated(version="2.0", alternative="Litestar.plugins.serialization", kind="property")
    def serialization_plugins(self) -> list[SerializationPluginProtocol]:
        return list(self.plugins.serialization)

    @staticmethod
    def _get_default_plugins(plugins: list[PluginProtocol]) -> list[PluginProtocol]:
        from litestar.plugins.core import MsgspecDIPlugin

        plugins.append(MsgspecDIPlugin())

        with suppress(MissingDependencyException):
            from litestar.contrib.pydantic import (
                PydanticDIPlugin,
                PydanticInitPlugin,
                PydanticPlugin,
                PydanticSchemaPlugin,
            )

            pydantic_plugin_found = any(isinstance(plugin, PydanticPlugin) for plugin in plugins)
            pydantic_init_plugin_found = any(isinstance(plugin, PydanticInitPlugin) for plugin in plugins)
            pydantic_schema_plugin_found = any(isinstance(plugin, PydanticSchemaPlugin) for plugin in plugins)
            pydantic_serialization_plugin_found = any(isinstance(plugin, PydanticDIPlugin) for plugin in plugins)
            if not pydantic_plugin_found and not pydantic_init_plugin_found and not pydantic_schema_plugin_found:
                plugins.append(PydanticPlugin())
            elif not pydantic_plugin_found and pydantic_init_plugin_found and not pydantic_schema_plugin_found:
                plugins.append(PydanticSchemaPlugin())
            elif not pydantic_plugin_found and not pydantic_init_plugin_found:
                plugins.append(PydanticInitPlugin())
            if not pydantic_plugin_found and not pydantic_serialization_plugin_found:
                plugins.append(PydanticDIPlugin())
        with suppress(MissingDependencyException):
            from litestar.contrib.attrs import AttrsSchemaPlugin

            pre_configured = any(isinstance(plugin, AttrsSchemaPlugin) for plugin in plugins)
            if not pre_configured:
                plugins.append(AttrsSchemaPlugin())
        return plugins

    @property
    def debug(self) -> bool:
        return self._debug

    @debug.setter
    def debug(self, value: bool) -> None:
        """Sets the debug logging level for the application.

        When possible, it calls the `self.logging_config.set_level` method.  This allows for implementation specific code and APIs to be called.
        """
        if self.logger and self.logging_config:
            self.logging_config.set_level(self.logger, logging.DEBUG if value else logging.INFO)
        elif self.logger and hasattr(self.logger, "setLevel"):  # pragma: no cover
            self.logger.setLevel(logging.DEBUG if value else logging.INFO)  # pragma: no cover
        if isinstance(self.logging_config, LoggingConfig):
            self.logging_config.loggers["litestar"]["level"] = "DEBUG" if value else "INFO"
        self._debug = value

    async def __call__(
        self,
        scope: Scope | LifeSpanScope,
        receive: Receive | LifeSpanReceive,
        send: Send | LifeSpanSend,
    ) -> None:
        """Application entry point.

        Lifespan events (startup / shutdown) are sent to the lifespan handler, otherwise the ASGI handler is used

        Args:
            scope: The ASGI connection scope.
            receive: The ASGI receive function.
            send: The ASGI send function.

        Returns:
            None
        """
        if scope["type"] == "lifespan":
            await self.asgi_router.lifespan(receive=receive, send=send)  # type: ignore[arg-type]
            return

        scope["app"] = self
        scope.setdefault("state", {})
        await self.asgi_handler(scope, receive, self._wrap_send(send=send, scope=scope))  # type: ignore[arg-type]

    async def _call_lifespan_hook(self, hook: LifespanHook) -> None:
        ret = hook(self) if inspect.signature(hook).parameters else hook()  # type: ignore[call-arg]

        if is_async_callable(hook):  # pyright: ignore[reportGeneralTypeIssues]
            await ret

    @asynccontextmanager
    async def lifespan(self) -> AsyncGenerator[None, None]:
        """Context manager handling the ASGI lifespan.

        It will be entered when the ``lifespan`` message has been received from the
        server, and exit after the ``asgi.shutdown`` message. During this period, it is
        responsible for calling the ``on_startup``, ``on_shutdown`` hooks, as well as
        custom lifespan managers.
        """
        async with AsyncExitStack() as exit_stack:
            for hook in self.on_shutdown[::-1]:
                exit_stack.push_async_callback(partial(self._call_lifespan_hook, hook))

            await exit_stack.enter_async_context(self.event_emitter)

            for manager in self._lifespan_managers:
                if not isinstance(manager, AbstractAsyncContextManager):
                    manager = manager(self)
                await exit_stack.enter_async_context(manager)

            for hook in self.on_startup:
                await self._call_lifespan_hook(hook)

            yield

    @property
    def openapi_schema(self) -> OpenAPI:
        """Access  the OpenAPI schema of the application.

        Returns:
            The :class:`OpenAPI`
            <pydantic_openapi_schema.open_api.OpenAPI> instance of the
            application.

        Raises:
            ImproperlyConfiguredException: If the application ``openapi_config`` attribute is ``None``.
        """
        return self.plugins.get(OpenAPIPlugin).provide_openapi()

    @classmethod
    def from_config(cls, config: AppConfig) -> Self:
        """Initialize a ``Litestar`` application from a configuration instance.

        Args:
            config: An instance of :class:`AppConfig` <.config.AppConfig>

        Returns:
            An instance of ``Litestar`` application.
        """
        return cls(**dict(extract_dataclass_items(config)))

    def register(self, value: ControllerRouterHandler) -> None:  # type: ignore[override]
        """Register a route handler on the app.

        This method can be used to dynamically add endpoints to an application.

        Args:
            value: An instance of :class:`Router <.router.Router>`, a subclass of
                :class:`Controller <.controller.Controller>` or any function decorated by the route handler decorators.

        Returns:
            None
        """
        routes = super().register(value=value)

        for route in routes:
            route_handlers = get_route_handlers(route)

            for route_handler in route_handlers:
                route_handler.on_registration(self)

            if isinstance(route, HTTPRoute):
                route.create_handler_map()

            elif isinstance(route, WebSocketRoute):
                handler = route.route_handler
                route.handler_parameter_model = handler.create_kwargs_model(path_parameters=route.path_parameters)

            for plugin in self.plugins.receive_route:
                plugin.receive_route(route)

        self.asgi_router.construct_routing_trie()

    def get_handler_index_by_name(self, name: str) -> HandlerIndex | None:
        """Receives a route handler name and returns an optional dictionary containing the route handler instance and
        list of paths sorted lexically.

        Examples:
            .. code-block:: python

                from litestar import Litestar, get


                @get("/", name="my-handler")
                def handler() -> None:
                    pass


                app = Litestar(route_handlers=[handler])

                handler_index = app.get_handler_index_by_name("my-handler")

                # { "paths": ["/"], "handler" ... }

        Args:
            name: A route handler unique name.

        Returns:
            A :class:`HandlerIndex <.app.HandlerIndex>` instance or ``None``.
        """
        handler = self.asgi_router.route_handler_index.get(name)
        if not handler:
            return None

        identifier = handler.name or str(handler)
        routes = self.asgi_router.route_mapping[identifier]
        paths = sorted(unique([route.path for route in routes]))

        return HandlerIndex(handler=handler, paths=paths, identifier=identifier)

    def route_reverse(self, name: str, **path_parameters: Any) -> str:
        """Receives a route handler name, path parameter values and returns url path to the handler with filled path
        parameters.

        Examples:
            .. code-block:: python

                from litestar import Litestar, get


                @get("/group/{group_id:int}/user/{user_id:int}", name="get_membership_details")
                def get_membership_details(group_id: int, user_id: int) -> None:
                    pass


                app = Litestar(route_handlers=[get_membership_details])

                path = app.route_reverse("get_membership_details", user_id=100, group_id=10)

                # /group/10/user/100

        Args:
            name: A route handler unique name.
            **path_parameters: Actual values for path parameters in the route.

        Raises:
            NoRouteMatchFoundException: If route with 'name' does not exist, path parameters are missing in
                ``**path_parameters or have wrong type``.

        Returns:
            A fully formatted url path.
        """
        handler_index = self.get_handler_index_by_name(name)
        if handler_index is None:
            raise NoRouteMatchFoundException(f"Route {name} can not be found")

        allow_str_instead = {datetime, date, time, timedelta, float, Path}
        routes = sorted(
            self.asgi_router.route_mapping[handler_index["identifier"]],
            key=lambda r: len(r.path_parameters),
            reverse=True,
        )
        passed_parameters = set(path_parameters.keys())

        selected_route = next(
            (route for route in routes if passed_parameters.issuperset(route.path_parameters)),
            routes[-1],
        )
        output: list[str] = []
        for component in selected_route.path_components:
            if isinstance(component, PathParameterDefinition):
                val = path_parameters.get(component.name)
                if not isinstance(val, component.type) and (
                    component.type not in allow_str_instead or not isinstance(val, str)
                ):
                    raise NoRouteMatchFoundException(
                        f"Received type for path parameter {component.name} doesn't match declared type {component.type}"
                    )
                output.append(str(val))
            else:
                output.append(component)

        return join_paths(output)

    @deprecated(
        "2.6.0", info="Use create_static_files router instead of StaticFilesConfig, which works with route_reverse"
    )
    def url_for_static_asset(self, name: str, file_path: str) -> str:
        """Receives a static files handler name, an asset file path and returns resolved url path to the asset.

        Examples:
            .. code-block:: python

                from litestar import Litestar
                from litestar.static_files.config import StaticFilesConfig

                app = Litestar(
                    static_files_config=[
                        StaticFilesConfig(directories=["css"], path="/static/css", name="css")
                    ]
                )

                path = app.url_for_static_asset("css", "main.css")

                # /static/css/main.css

        Args:
            name: A static handler unique name.
            file_path: a string containing path to an asset.

        Raises:
            NoRouteMatchFoundException: If static files handler with ``name`` does not exist.

        Returns:
            A url path to the asset.
        """

        handler_index = self.get_handler_index_by_name(name)
        if handler_index is None:
            raise NoRouteMatchFoundException(f"Static handler {name} can not be found")

        handler_fn = cast("AnyCallable", handler_index["handler"].fn)
        if not isinstance(handler_fn, StaticFiles):
            raise NoRouteMatchFoundException(f"Handler with name {name} is not a static files handler")

        return join_paths([handler_index["paths"][0], file_path])  # type: ignore[unreachable]

    @property
    def route_handler_method_view(self) -> dict[str, list[str]]:
        """Map route handlers to paths.

        Returns:
            A dictionary of router handlers and lists of paths as strings
        """
        route_map: dict[str, list[str]] = {
            handler: [route.path for route in routes] for handler, routes in self.asgi_router.route_mapping.items()
        }
        return route_map

    def _create_asgi_handler(self) -> ASGIApp:
        """Create an ASGIApp that wraps the ASGI router inside an exception handler.

        If CORS or TrustedHost configs are provided to the constructor, they will wrap the router as well.
        """
        asgi_handler = wrap_in_exception_handler(app=self.asgi_router)

        if self.cors_config:
            return CORSMiddleware(app=asgi_handler, config=self.cors_config)

        return asgi_handler

    def _wrap_send(self, send: Send, scope: Scope) -> Send:
        """Wrap the ASGI send and handles any 'before send' hooks.

        Args:
            send: The ASGI send function.
            scope: The ASGI scope.

        Returns:
            An ASGI send function.
        """
        if self.before_send:

            async def wrapped_send(message: Message) -> None:
                for hook in self.before_send:
                    await hook(message, scope)
                await send(message)

            return wrapped_send
        return send

    def update_openapi_schema(self) -> None:
        """Update the OpenAPI schema to reflect the route handlers registered on the app.

        Returns:
            None
        """
        self.plugins.get(OpenAPIPlugin)._build_openapi()

    def emit(self, event_id: str, *args: Any, **kwargs: Any) -> None:
        """Emit an event to all attached listeners.

        Args:
            event_id: The ID of the event to emit, e.g ``my_event``.
            args: args to pass to the listener(s).
            kwargs: kwargs to pass to the listener(s)

        Returns:
            None
        """
        self.event_emitter.emit(event_id, *args, **kwargs)
