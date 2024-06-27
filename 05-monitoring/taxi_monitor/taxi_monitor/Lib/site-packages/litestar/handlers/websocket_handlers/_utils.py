from __future__ import annotations

from functools import wraps
from inspect import Parameter, Signature
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict

from msgspec.json import Encoder as JsonEncoder

from litestar.di import Provide
from litestar.serialization import decode_json
from litestar.types.builtin_types import NoneType
from litestar.utils import ensure_async_callable
from litestar.utils.helpers import unwrap_partial

if TYPE_CHECKING:
    from litestar import WebSocket
    from litestar.handlers.websocket_handlers.listener import WebsocketListenerRouteHandler
    from litestar.types import AnyCallable
    from litestar.utils.signature import ParsedSignature


def create_handle_receive(listener: WebsocketListenerRouteHandler) -> Callable[[WebSocket], Coroutine[Any, None, None]]:
    if data_dto := listener.resolve_data_dto():

        async def handle_receive(socket: WebSocket) -> Any:
            received_data = await socket.receive_data(mode=listener._receive_mode)
            return data_dto(socket).decode_bytes(
                received_data.encode("utf-8") if isinstance(received_data, str) else received_data
            )

    elif listener.parsed_data_field and listener.parsed_data_field.annotation is str:

        async def handle_receive(socket: WebSocket) -> Any:
            received_data = await socket.receive_data(mode=listener._receive_mode)
            return received_data.decode("utf-8") if isinstance(received_data, bytes) else received_data

    elif listener.parsed_data_field and listener.parsed_data_field.annotation is bytes:

        async def handle_receive(socket: WebSocket) -> Any:
            received_data = await socket.receive_data(mode=listener._receive_mode)
            return received_data.encode("utf-8") if isinstance(received_data, str) else received_data

    else:

        async def handle_receive(socket: WebSocket) -> Any:
            received_data = await socket.receive_data(mode=listener._receive_mode)
            return decode_json(value=received_data, type_decoders=socket.route_handler.resolve_type_decoders())

    return handle_receive


def create_handle_send(
    listener: WebsocketListenerRouteHandler,
) -> Callable[[WebSocket, Any], Coroutine[None, None, None]]:
    json_encoder = JsonEncoder(enc_hook=listener.default_serializer)

    if return_dto := listener.resolve_return_dto():

        async def handle_send(socket: WebSocket, data: Any) -> None:
            encoded_data = return_dto(socket).data_to_encodable_type(data)
            data = json_encoder.encode(encoded_data)
            await socket.send_data(data=data, mode=listener._send_mode)

    elif listener.parsed_return_field.is_subclass_of((str, bytes)) or (
        listener.parsed_return_field.is_optional and listener.parsed_return_field.has_inner_subclass_of((str, bytes))
    ):

        async def handle_send(socket: WebSocket, data: Any) -> None:
            await socket.send_data(data=data, mode=listener._send_mode)

    else:

        async def handle_send(socket: WebSocket, data: Any) -> None:
            data = json_encoder.encode(data)
            await socket.send_data(data=data, mode=listener._send_mode)

    return handle_send


class ListenerHandler:
    __slots__ = ("_can_send_data", "_fn", "_listener", "_pass_socket")

    def __init__(
        self,
        listener: WebsocketListenerRouteHandler,
        fn: AnyCallable,
        parsed_signature: ParsedSignature,
        namespace: dict[str, Any],
    ) -> None:
        self._can_send_data = not parsed_signature.return_type.is_subclass_of(NoneType)
        self._fn = ensure_async_callable(fn)
        self._listener = listener
        self._pass_socket = "socket" in parsed_signature.parameters

    async def __call__(
        self,
        *args: Any,
        socket: WebSocket,
        connection_lifespan_dependencies: Dict[str, Any],  # noqa: UP006
        **kwargs: Any,
    ) -> None:
        lifespan_mananger = self._listener._connection_lifespan or self._listener.default_connection_lifespan
        handle_send = self._listener.resolve_send_handler() if self._can_send_data else None
        handle_receive = self._listener.resolve_receive_handler()

        if self._pass_socket:
            kwargs["socket"] = socket

        async with lifespan_mananger(**connection_lifespan_dependencies):
            while True:
                received_data = await handle_receive(socket)
                data = await self._fn(*args, data=received_data, **kwargs)
                if handle_send:
                    await handle_send(socket, data)


def create_handler_signature(callback_signature: Signature) -> Signature:
    """Creates a :class:`Signature` for the handler function for signature modelling.

    This is required for two reasons:

        1. the :class:`.handlers.WebsocketHandler` signature model cannot contain the ``data`` parameter, which is
            required for :class:`.handlers.websocket_listener` handlers.
        2. the :class;`.handlers.WebsocketHandler` signature model must include the ``socket`` parameter, which is
            optional for :class:`.handlers.websocket_listener` handlers.

    Args:
        callback_signature: The :class:`Signature` of the listener callback.

    Returns:
        The :class:`Signature` for the listener callback as required for signature modelling.
    """
    new_params = [p for p in callback_signature.parameters.values() if p.name != "data"]
    if "socket" not in callback_signature.parameters:
        new_params.append(Parameter(name="socket", kind=Parameter.KEYWORD_ONLY, annotation="WebSocket"))

    new_params.append(
        Parameter(name="connection_lifespan_dependencies", kind=Parameter.KEYWORD_ONLY, annotation="Dict[str, Any]")
    )

    return callback_signature.replace(parameters=new_params)


def create_stub_dependency(src: AnyCallable) -> Provide:
    """Create a stub dependency, accepting any kwargs defined in ``src``, and
    wrap it in ``Provide``
    """
    src = unwrap_partial(src)

    @wraps(src)
    async def stub(**kwargs: Any) -> Dict[str, Any]:  # noqa: UP006
        return kwargs

    return Provide(stub)
