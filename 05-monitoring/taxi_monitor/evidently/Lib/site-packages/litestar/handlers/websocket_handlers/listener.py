from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    Mapping,
    Optional,
    cast,
    overload,
)

from litestar._signature import SignatureModel
from litestar.connection import WebSocket
from litestar.exceptions import ImproperlyConfiguredException, WebSocketDisconnect
from litestar.types import (
    AnyCallable,
    Dependencies,
    Empty,
    EmptyType,
    ExceptionHandler,
    Guard,
    Middleware,
    TypeEncodersMap,
)
from litestar.utils import ensure_async_callable
from litestar.utils.signature import ParsedSignature, get_fn_type_hints

from ._utils import (
    ListenerHandler,
    create_handle_receive,
    create_handle_send,
    create_handler_signature,
    create_stub_dependency,
)
from .route_handler import WebsocketRouteHandler

if TYPE_CHECKING:
    from typing import Coroutine

    from typing_extensions import Self

    from litestar import Router
    from litestar.dto import AbstractDTO
    from litestar.types.asgi_types import WebSocketMode
    from litestar.types.composite_types import TypeDecodersSequence

__all__ = ("WebsocketListener", "WebsocketListenerRouteHandler", "websocket_listener")


class WebsocketListenerRouteHandler(WebsocketRouteHandler):
    """A websocket listener that automatically accepts a connection, handles disconnects,
    invokes a callback function every time new data is received and sends any data
    returned
    """

    __slots__ = {
        "connection_accept_handler": "Callback to accept a WebSocket connection. By default, calls WebSocket.accept",
        "on_accept": "Callback invoked after a WebSocket connection has been accepted",
        "on_disconnect": "Callback invoked after a WebSocket connection has been closed",
        "_connection_lifespan": None,
        "_receive_handler": None,
        "_receive_mode": None,
        "_send_handler": None,
        "_send_mode": None,
    }

    @overload
    def __init__(
        self,
        path: str | list[str] | None = None,
        *,
        connection_lifespan: Callable[..., AbstractAsyncContextManager[Any]] | None = None,
        dependencies: Dependencies | None = None,
        dto: type[AbstractDTO] | None | EmptyType = Empty,
        exception_handlers: dict[int | type[Exception], ExceptionHandler] | None = None,
        guards: list[Guard] | None = None,
        middleware: list[Middleware] | None = None,
        receive_mode: WebSocketMode = "text",
        send_mode: WebSocketMode = "text",
        name: str | None = None,
        opt: dict[str, Any] | None = None,
        return_dto: type[AbstractDTO] | None | EmptyType = Empty,
        signature_namespace: Mapping[str, Any] | None = None,
        type_decoders: TypeDecodersSequence | None = None,
        type_encoders: TypeEncodersMap | None = None,
        websocket_class: type[WebSocket] | None = None,
        **kwargs: Any,
    ) -> None: ...

    @overload
    def __init__(
        self,
        path: str | list[str] | None = None,
        *,
        connection_accept_handler: Callable[[WebSocket], Coroutine[Any, Any, None]] = WebSocket.accept,
        dependencies: Dependencies | None = None,
        dto: type[AbstractDTO] | None | EmptyType = Empty,
        exception_handlers: dict[int | type[Exception], ExceptionHandler] | None = None,
        guards: list[Guard] | None = None,
        middleware: list[Middleware] | None = None,
        receive_mode: WebSocketMode = "text",
        send_mode: WebSocketMode = "text",
        name: str | None = None,
        on_accept: AnyCallable | None = None,
        on_disconnect: AnyCallable | None = None,
        opt: dict[str, Any] | None = None,
        return_dto: type[AbstractDTO] | None | EmptyType = Empty,
        signature_namespace: Mapping[str, Any] | None = None,
        type_decoders: TypeDecodersSequence | None = None,
        type_encoders: TypeEncodersMap | None = None,
        websocket_class: type[WebSocket] | None = None,
        **kwargs: Any,
    ) -> None: ...

    def __init__(
        self,
        path: str | list[str] | None = None,
        *,
        connection_accept_handler: Callable[[WebSocket], Coroutine[Any, Any, None]] = WebSocket.accept,
        connection_lifespan: Callable[..., AbstractAsyncContextManager[Any]] | None = None,
        dependencies: Dependencies | None = None,
        dto: type[AbstractDTO] | None | EmptyType = Empty,
        exception_handlers: dict[int | type[Exception], ExceptionHandler] | None = None,
        guards: list[Guard] | None = None,
        middleware: list[Middleware] | None = None,
        receive_mode: WebSocketMode = "text",
        send_mode: WebSocketMode = "text",
        name: str | None = None,
        on_accept: AnyCallable | None = None,
        on_disconnect: AnyCallable | None = None,
        opt: dict[str, Any] | None = None,
        return_dto: type[AbstractDTO] | None | EmptyType = Empty,
        signature_namespace: Mapping[str, Any] | None = None,
        type_decoders: TypeDecodersSequence | None = None,
        type_encoders: TypeEncodersMap | None = None,
        websocket_class: type[WebSocket] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize ``WebsocketRouteHandler``

        Args:
            path: A path fragment for the route handler function or a sequence of path fragments. If not given defaults
                to ``/``
            connection_accept_handler: A callable that accepts a :class:`WebSocket <.connection.WebSocket>` instance
                and returns a coroutine that when awaited, will accept the connection. Defaults to ``WebSocket.accept``.
            connection_lifespan: An asynchronous context manager, handling the lifespan of the connection. By default,
                it calls the ``connection_accept_handler``, ``on_connect`` and ``on_disconnect``. Can request any
                dependencies, for example the :class:`WebSocket <.connection.WebSocket>` connection
            dependencies: A string keyed mapping of dependency :class:`Provider <.di.Provide>` instances.
            dto: :class:`AbstractDTO <.dto.base_dto.AbstractDTO>` to use for (de)serializing and
                validation of request data.
            exception_handlers: A mapping of status codes and/or exception types to handler functions.
            guards: A sequence of :class:`Guard <.types.Guard>` callables.
            middleware: A sequence of :class:`Middleware <.types.Middleware>`.
            receive_mode: Websocket mode to receive data in, either `text` or `binary`.
            send_mode: Websocket mode to receive data in, either `text` or `binary`.
            name: A string identifying the route handler.
            on_accept: Callback invoked after a connection has been accepted. Can request any dependencies, for example
                the :class:`WebSocket <.connection.WebSocket>` connection
            on_disconnect: Callback invoked after a connection has been closed. Can request any dependencies, for
                example the :class:`WebSocket <.connection.WebSocket>` connection
            opt: A string keyed mapping of arbitrary values that can be accessed in :class:`Guards <.types.Guard>` or
                wherever you have access to :class:`Request <.connection.Request>` or
                :class:`ASGI Scope <.types.Scope>`.
            return_dto: :class:`AbstractDTO <.dto.base_dto.AbstractDTO>` to use for serializing
                outbound response data.
            signature_namespace: A mapping of names to types for use in forward reference resolution during signature
                modelling.
            type_decoders: A sequence of tuples, each composed of a predicate testing for type identity and a msgspec
                hook for deserialization.
            type_encoders: A mapping of types to callables that transform them into types supported for serialization.
            **kwargs: Any additional kwarg - will be set in the opt dictionary.
            websocket_class: A custom subclass of :class:`WebSocket <.connection.WebSocket>` to be used as route handler's
                default websocket class.
        """
        if connection_lifespan and any([on_accept, on_disconnect, connection_accept_handler is not WebSocket.accept]):
            raise ImproperlyConfiguredException(
                "connection_lifespan can not be used with connection hooks "
                "(on_accept, on_disconnect, connection_accept_handler)",
            )

        self._receive_mode: WebSocketMode = receive_mode
        self._send_mode: WebSocketMode = send_mode
        self._connection_lifespan = connection_lifespan
        self._send_handler: Callable[[WebSocket, Any], Coroutine[None, None, None]] | EmptyType = Empty
        self._receive_handler: Callable[[WebSocket], Any] | EmptyType = Empty

        self.connection_accept_handler = connection_accept_handler
        self.on_accept = ensure_async_callable(on_accept) if on_accept else None
        self.on_disconnect = ensure_async_callable(on_disconnect) if on_disconnect else None
        self.type_decoders = type_decoders
        self.type_encoders = type_encoders
        self.websocket_class = websocket_class

        listener_dependencies = dict(dependencies or {})

        listener_dependencies["connection_lifespan_dependencies"] = create_stub_dependency(
            connection_lifespan or self.default_connection_lifespan
        )

        if self.on_accept:
            listener_dependencies["on_accept_dependencies"] = create_stub_dependency(self.on_accept)

        if self.on_disconnect:
            listener_dependencies["on_disconnect_dependencies"] = create_stub_dependency(self.on_disconnect)

        super().__init__(
            path=path,
            dependencies=listener_dependencies,
            exception_handlers=exception_handlers,
            guards=guards,
            middleware=middleware,
            name=name,
            opt=opt,
            signature_namespace=signature_namespace,
            dto=dto,
            return_dto=return_dto,
            type_decoders=type_decoders,
            type_encoders=type_encoders,
            websocket_class=websocket_class,
            **kwargs,
        )

    def __call__(self, fn: AnyCallable) -> Self:
        parsed_signature = ParsedSignature.from_fn(fn, self.resolve_signature_namespace())

        if "data" not in parsed_signature.parameters:
            raise ImproperlyConfiguredException("Websocket listeners must accept a 'data' parameter")

        for param in ("request", "body"):
            if param in parsed_signature.parameters:
                raise ImproperlyConfiguredException(f"The {param} kwarg is not supported with websocket listeners")

        # we are manipulating the signature of the decorated function below, so we must store the original values for
        # use elsewhere.
        self._parsed_return_field = parsed_signature.return_type
        self._parsed_data_field = parsed_signature.parameters.get("data")
        self._parsed_fn_signature = ParsedSignature.from_signature(
            create_handler_signature(parsed_signature.original_signature),
            fn_type_hints={
                **get_fn_type_hints(fn, namespace=self.resolve_signature_namespace()),
                **get_fn_type_hints(ListenerHandler.__call__, namespace=self.resolve_signature_namespace()),
            },
        )

        return super().__call__(
            ListenerHandler(
                listener=self, fn=fn, parsed_signature=parsed_signature, namespace=self.resolve_signature_namespace()
            )
        )

    def _validate_handler_function(self) -> None:
        """Validate the route handler function once it's set by inspecting its return annotations."""
        # validation occurs in the call method

    @property
    def signature_model(self) -> type[SignatureModel]:
        """Get the signature model for the route handler.

        Returns:
            A signature model for the route handler.

        """
        if self._signature_model is Empty:
            self._signature_model = SignatureModel.create(
                dependency_name_set=self.dependency_name_set,
                fn=cast("AnyCallable", self.fn),
                parsed_signature=self.parsed_fn_signature,
                type_decoders=self.resolve_type_decoders(),
            )
        return self._signature_model

    @asynccontextmanager
    async def default_connection_lifespan(
        self,
        socket: WebSocket,
        on_accept_dependencies: Optional[Dict[str, Any]] = None,  # noqa: UP006, UP007
        on_disconnect_dependencies: Optional[Dict[str, Any]] = None,  # noqa: UP006, UP007
    ) -> AsyncGenerator[None, None]:
        """Handle the connection lifespan of a :class:`WebSocket <.connection.WebSocket>`.

        Args:
            socket: The :class:`WebSocket <.connection.WebSocket>` connection
            on_accept_dependencies: Dependencies requested by the :attr:`on_accept` hook
            on_disconnect_dependencies: Dependencies requested by the :attr:`on_disconnect` hook

        By, default this will

            - Call :attr:`connection_accept_handler` to accept a connection
            - Call :attr:`on_accept` if defined after a connection has been accepted
            - Call :attr:`on_disconnect` upon leaving the context
        """
        await self.connection_accept_handler(socket)

        if self.on_accept:
            await self.on_accept(**(on_accept_dependencies or {}))

        try:
            yield
        except WebSocketDisconnect:
            pass
        finally:
            if self.on_disconnect:
                await self.on_disconnect(**(on_disconnect_dependencies or {}))

    def resolve_receive_handler(self) -> Callable[[WebSocket], Any]:
        if self._receive_handler is Empty:
            self._receive_handler = create_handle_receive(self)
        return self._receive_handler

    def resolve_send_handler(self) -> Callable[[WebSocket, Any], Coroutine[None, None, None]]:
        if self._send_handler is Empty:
            self._send_handler = create_handle_send(self)
        return self._send_handler


websocket_listener = WebsocketListenerRouteHandler


class WebsocketListener(ABC):
    path: str | list[str] | None = None
    """A path fragment for the route handler function or a sequence of path fragments. If not given defaults to ``/``"""
    dependencies: Dependencies | None = None
    """A string keyed mapping of dependency :class:`Provider <.di.Provide>` instances."""
    dto: type[AbstractDTO] | None | EmptyType = Empty
    """:class:`AbstractDTO <.dto.base_dto.AbstractDTO>` to use for (de)serializing and validation of request data"""
    exception_handlers: dict[int | type[Exception], ExceptionHandler] | None = None
    """A mapping of status codes and/or exception types to handler functions."""
    guards: list[Guard] | None = None
    """A sequence of :class:`Guard <.types.Guard>` callables."""
    middleware: list[Middleware] | None = None
    """A sequence of :class:`Middleware <.types.Middleware>`."""
    on_accept: AnyCallable | None = None
    """Called after a :class:`WebSocket <.connection.WebSocket>` connection has been accepted. Can receive any dependencies"""
    on_disconnect: AnyCallable | None = None
    """Called after a :class:`WebSocket <.connection.WebSocket>` connection has been disconnected. Can receive any dependencies"""
    receive_mode: WebSocketMode = "text"
    """:class:`WebSocket <.connection.WebSocket>` mode to receive data in, either ``text`` or ``binary``."""
    send_mode: WebSocketMode = "text"
    """Websocket mode to send data in, either `text` or `binary`."""
    name: str | None = None
    """A string identifying the route handler."""
    opt: dict[str, Any] | None = None
    """
    A string keyed mapping of arbitrary values that can be accessed in :class:`Guards <.types.Guard>` or wherever you
    have access to :class:`Request <.connection.Request>` or :class:`ASGI Scope <.types.Scope>`.
    """
    return_dto: type[AbstractDTO] | None | EmptyType = Empty
    """:class:`AbstractDTO <.dto.base_dto.AbstractDTO>` to use for serializing outbound response data."""
    signature_namespace: Mapping[str, Any] | None = None
    """
    A mapping of names to types for use in forward reference resolution during signature modelling.
    """
    type_decoders: TypeDecodersSequence | None = None
    """
    type_decoders: A sequence of tuples, each composed of a predicate testing for type identity and a msgspec
        hook for deserialization.
    """
    type_encoders: TypeEncodersMap | None = None
    """
    type_encoders: A mapping of types to callables that transform them into types supported for serialization.
    """
    websocket_class: type[WebSocket] | None = None
    """
    websocket_class: A custom subclass of :class:`WebSocket <.connection.WebSocket>` to be used as route handler's
    default websocket class.
    """

    def __init__(self, owner: Router) -> None:
        """Initialize a WebsocketListener instance.

        Args:
            owner: The :class:`Router <.router.Router>` instance that owns this listener.
        """
        self._owner = owner

    def to_handler(self) -> WebsocketListenerRouteHandler:
        handler = WebsocketListenerRouteHandler(
            dependencies=self.dependencies,
            dto=self.dto,
            exception_handlers=self.exception_handlers,
            guards=self.guards,
            middleware=self.middleware,
            send_mode=self.send_mode,
            receive_mode=self.receive_mode,
            name=self.name,
            on_accept=self.on_accept,
            on_disconnect=self.on_disconnect,
            opt=self.opt,
            path=self.path,
            return_dto=self.return_dto,
            signature_namespace=self.signature_namespace,
            type_decoders=self.type_decoders,
            type_encoders=self.type_encoders,
            websocket_class=self.websocket_class,
        )(self.on_receive)
        handler.owner = self._owner
        return handler

    @abstractmethod
    def on_receive(self, *args: Any, **kwargs: Any) -> Any:
        """Called after data has been received from the WebSocket.

        This should take a ``data`` argument, receiving the processed WebSocket data,
        and can additionally include handler dependencies such as ``state``, or other
        regular dependencies.

        Data returned from this function will be serialized and sent via the socket
        according to handler configuration.
        """
        raise NotImplementedError
