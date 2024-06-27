from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any, AsyncGenerator, Generic

from litestar._multipart import parse_content_header, parse_multipart_form
from litestar._parsers import parse_url_encoded_form_data
from litestar.connection.base import (
    ASGIConnection,
    AuthT,
    StateT,
    UserT,
    empty_receive,
    empty_send,
)
from litestar.datastructures.headers import Accept
from litestar.datastructures.multi_dicts import FormMultiDict
from litestar.enums import ASGIExtension, RequestEncodingType
from litestar.exceptions import (
    InternalServerException,
    LitestarException,
    LitestarWarning,
)
from litestar.serialization import decode_json, decode_msgpack
from litestar.types import Empty

__all__ = ("Request",)


if TYPE_CHECKING:
    from litestar.handlers.http_handlers import HTTPRouteHandler  # noqa: F401
    from litestar.types.asgi_types import HTTPScope, Method, Receive, Scope, Send
    from litestar.types.empty import EmptyType


SERVER_PUSH_HEADERS = {
    "accept",
    "accept-encoding",
    "accept-language",
    "cache-control",
    "user-agent",
}


class Request(Generic[UserT, AuthT, StateT], ASGIConnection["HTTPRouteHandler", UserT, AuthT, StateT]):
    """The Litestar Request class."""

    __slots__ = (
        "_json",
        "_form",
        "_body",
        "_msgpack",
        "_content_type",
        "_accept",
        "is_connected",
        "supports_push_promise",
    )

    scope: HTTPScope  # pyright: ignore
    """The ASGI scope attached to the connection."""
    receive: Receive
    """The ASGI receive function."""
    send: Send
    """The ASGI send function."""

    def __init__(self, scope: Scope, receive: Receive = empty_receive, send: Send = empty_send) -> None:
        """Initialize ``Request``.

        Args:
            scope: The ASGI connection scope.
            receive: The ASGI receive function.
            send: The ASGI send function.
        """
        super().__init__(scope, receive, send)
        self.is_connected: bool = True
        self._body: bytes | EmptyType = Empty
        self._form: dict[str, str | list[str]] | EmptyType = Empty
        self._json: Any = Empty
        self._msgpack: Any = Empty
        self._content_type: tuple[str, dict[str, str]] | EmptyType = Empty
        self._accept: Accept | EmptyType = Empty
        self.supports_push_promise = ASGIExtension.SERVER_PUSH in self._server_extensions

    @property
    def method(self) -> Method:
        """Return the request method.

        Returns:
            The request :class:`Method <litestar.types.Method>`
        """
        return self.scope["method"]

    @property
    def content_type(self) -> tuple[str, dict[str, str]]:
        """Parse the request's 'Content-Type' header, returning the header value and any options as a dictionary.

        Returns:
            A tuple with the parsed value and a dictionary containing any options send in it.
        """
        if self._content_type is Empty:
            if (content_type := self._connection_state.content_type) is not Empty:
                self._content_type = content_type
            else:
                self._content_type = self._connection_state.content_type = parse_content_header(
                    self.headers.get("Content-Type", "")
                )
        return self._content_type

    @property
    def accept(self) -> Accept:
        """Parse the request's 'Accept' header, returning an :class:`Accept <litestar.datastructures.headers.Accept>` instance.

        Returns:
            An :class:`Accept <litestar.datastructures.headers.Accept>` instance, representing the list of acceptable media types.
        """
        if self._accept is Empty:
            if (accept := self._connection_state.accept) is not Empty:
                self._accept = accept
            else:
                self._accept = self._connection_state.accept = Accept(self.headers.get("Accept", "*/*"))
        return self._accept

    async def json(self) -> Any:
        """Retrieve the json request body from the request.

        Returns:
            An arbitrary value
        """
        if self._json is Empty:
            if (json_ := self._connection_state.json) is not Empty:
                self._json = json_
            else:
                body = await self.body()
                self._json = self._connection_state.json = decode_json(
                    body or b"null", type_decoders=self.route_handler.resolve_type_decoders()
                )
        return self._json

    async def msgpack(self) -> Any:
        """Retrieve the MessagePack request body from the request.

        Returns:
            An arbitrary value
        """
        if self._msgpack is Empty:
            if (msgpack := self._connection_state.msgpack) is not Empty:
                self._msgpack = msgpack
            else:
                body = await self.body()
                self._msgpack = self._connection_state.msgpack = decode_msgpack(
                    body or b"\xc0", type_decoders=self.route_handler.resolve_type_decoders()
                )
        return self._msgpack

    async def stream(self) -> AsyncGenerator[bytes, None]:
        """Return an async generator that streams chunks of bytes.

        Returns:
            An async generator.

        Raises:
            RuntimeError: if the stream is already consumed
        """
        if self._body is Empty:
            if not self.is_connected:
                raise InternalServerException("stream consumed")
            while event := await self.receive():
                if event["type"] == "http.request":
                    if event["body"]:
                        yield event["body"]

                    if not event.get("more_body", False):
                        break

                if event["type"] == "http.disconnect":
                    raise InternalServerException("client disconnected prematurely")

            self.is_connected = False
            yield b""

        else:
            yield self._body
            yield b""
            return

    async def body(self) -> bytes:
        """Return the body of the request.

        Returns:
            A byte-string representing the body of the request.
        """
        if self._body is Empty:
            if (body := self._connection_state.body) is not Empty:
                self._body = body
            else:
                self._body = self._connection_state.body = b"".join([c async for c in self.stream()])
        return self._body

    async def form(self) -> FormMultiDict:
        """Retrieve form data from the request. If the request is either a 'multipart/form-data' or an
        'application/x-www-form- urlencoded', return a FormMultiDict instance populated with the values sent in the
        request, otherwise, an empty instance.

        Returns:
            A FormMultiDict instance
        """
        if self._form is Empty:
            if (form := self._connection_state.form) is not Empty:
                self._form = form
            else:
                content_type, options = self.content_type
                if content_type == RequestEncodingType.MULTI_PART:
                    self._form = parse_multipart_form(
                        body=await self.body(),
                        boundary=options.get("boundary", "").encode(),
                        multipart_form_part_limit=self.app.multipart_form_part_limit,
                    )
                elif content_type == RequestEncodingType.URL_ENCODED:
                    self._form = parse_url_encoded_form_data(
                        await self.body(),
                    )
                else:
                    self._form = {}

                self._connection_state.form = self._form

        return FormMultiDict(self._form)

    async def send_push_promise(self, path: str, raise_if_unavailable: bool = False) -> None:
        """Send a push promise.

        This method requires the `http.response.push` extension to be sent from the ASGI server.

        Args:
            path: Path to send the promise to.
            raise_if_unavailable: Raise an exception if server push is not supported by
                the server

        Returns:
            None
        """
        if not self.supports_push_promise:
            if raise_if_unavailable:
                raise LitestarException("Attempted to send a push promise but the server does not support it")

            warnings.warn(
                "Attempted to send a push promise but the server does not support it. In a future version, this will "
                "raise an exception. To enable this behaviour in the current version, set raise_if_unavailable=True. "
                "To prevent this behaviour, make sure that the server you are using supports the 'http.response.push' "
                "ASGI extension, or check this dynamically via "
                ":attr:`~litestar.connection.Request.supports_push_promise`",
                stacklevel=2,
                category=LitestarWarning,
            )

            return

        raw_headers = [
            (header_name.encode("latin-1"), value.encode("latin-1"))
            for header_name in (self.headers.keys() & SERVER_PUSH_HEADERS)
            for value in self.headers.getall(header_name, [])
        ]
        await self.send({"type": "http.response.push", "path": path, "headers": raw_headers})
