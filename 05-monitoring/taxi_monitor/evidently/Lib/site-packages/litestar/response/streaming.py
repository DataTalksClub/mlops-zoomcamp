from __future__ import annotations

import itertools
from functools import partial
from typing import TYPE_CHECKING, Any, AsyncGenerator, AsyncIterable, AsyncIterator, Callable, Iterable, Iterator, Union

from anyio import CancelScope, create_task_group

from litestar.enums import MediaType
from litestar.response.base import ASGIResponse, Response
from litestar.types.helper_types import StreamType
from litestar.utils.deprecation import warn_deprecation
from litestar.utils.helpers import get_enum_string_value
from litestar.utils.sync import AsyncIteratorWrapper

if TYPE_CHECKING:
    from litestar.app import Litestar
    from litestar.background_tasks import BackgroundTask, BackgroundTasks
    from litestar.connection import Request
    from litestar.datastructures.cookie import Cookie
    from litestar.enums import OpenAPIMediaType
    from litestar.types import HTTPResponseBodyEvent, Receive, ResponseCookies, ResponseHeaders, Send, TypeEncodersMap

__all__ = (
    "ASGIStreamingResponse",
    "Stream",
)


class ASGIStreamingResponse(ASGIResponse):
    """A streaming response."""

    __slots__ = ("iterator",)

    _should_set_content_length = False

    def __init__(
        self,
        *,
        iterator: StreamType,
        background: BackgroundTask | BackgroundTasks | None = None,
        body: bytes | str = b"",
        content_length: int | None = None,
        cookies: Iterable[Cookie] | None = None,
        encoded_headers: Iterable[tuple[bytes, bytes]] | None = None,
        encoding: str = "utf-8",
        headers: dict[str, Any] | None = None,
        is_head_response: bool = False,
        media_type: MediaType | str | None = None,
        status_code: int | None = None,
    ) -> None:
        """A low-level ASGI streaming response.

        Args:
            background: A background task or a list of background tasks to be executed after the response is sent.
            body: encoded content to send in the response body.
            content_length: The response content length.
            cookies: The response cookies.
            encoded_headers: The response headers.
            encoding: The response encoding.
            headers: The response headers.
            is_head_response: A boolean indicating if the response is a HEAD response.
            iterator: An async iterator or iterable.
            media_type: The response media type.
            status_code: The response status code.
        """
        super().__init__(
            background=background,
            body=body,
            content_length=content_length,
            cookies=cookies,
            encoding=encoding,
            headers=headers,
            is_head_response=is_head_response,
            media_type=media_type,
            status_code=status_code,
            encoded_headers=encoded_headers,
        )
        self.iterator: AsyncIterable[str | bytes] | AsyncGenerator[str | bytes, None] = (
            iterator if isinstance(iterator, (AsyncIterable, AsyncIterator)) else AsyncIteratorWrapper(iterator)
        )

    async def _listen_for_disconnect(self, cancel_scope: CancelScope, receive: Receive) -> None:
        """Listen for a cancellation message, and if received - call cancel on the cancel scope.

        Args:
            cancel_scope: A task group cancel scope instance.
            receive: The ASGI receive function.

        Returns:
            None
        """
        if not cancel_scope.cancel_called:
            message = await receive()
            if message["type"] == "http.disconnect":
                # despite the IDE warning, this is not a coroutine because anyio 3+ changed this.
                # therefore make sure not to await this.
                cancel_scope.cancel()
            else:
                await self._listen_for_disconnect(cancel_scope=cancel_scope, receive=receive)

    async def _stream(self, send: Send) -> None:
        """Send the chunks from the iterator as a stream of ASGI 'http.response.body' events.

        Args:
            send: The ASGI Send function.

        Returns:
            None
        """
        async for chunk in self.iterator:
            stream_event: HTTPResponseBodyEvent = {
                "type": "http.response.body",
                "body": chunk if isinstance(chunk, bytes) else chunk.encode(self.encoding),
                "more_body": True,
            }
            await send(stream_event)
        terminus_event: HTTPResponseBodyEvent = {"type": "http.response.body", "body": b"", "more_body": False}
        await send(terminus_event)

    async def send_body(self, send: Send, receive: Receive) -> None:
        """Emit a stream of events correlating with the response body.

        Args:
            send: The ASGI send function.
            receive: The ASGI receive function.

        Returns:
            None
        """

        async with create_task_group() as task_group:
            task_group.start_soon(partial(self._stream, send))
            await self._listen_for_disconnect(cancel_scope=task_group.cancel_scope, receive=receive)


class Stream(Response[StreamType[Union[str, bytes]]]):
    """An HTTP response that streams the response data as a series of ASGI ``http.response.body`` events."""

    __slots__ = ("iterator",)

    def __init__(
        self,
        content: StreamType[str | bytes] | Callable[[], StreamType[str | bytes]],
        *,
        background: BackgroundTask | BackgroundTasks | None = None,
        cookies: ResponseCookies | None = None,
        encoding: str = "utf-8",
        headers: ResponseHeaders | None = None,
        media_type: MediaType | OpenAPIMediaType | str | None = None,
        status_code: int | None = None,
    ) -> None:
        """Initialize the response.

        Args:
            content: A sync or async iterator or iterable.
            background: A :class:`BackgroundTask <.background_tasks.BackgroundTask>` instance or
                :class:`BackgroundTasks <.background_tasks.BackgroundTasks>` to execute after the response is finished.
                Defaults to None.
            cookies: A list of :class:`Cookie <.datastructures.Cookie>` instances to be set under the response
                ``Set-Cookie`` header.
            encoding: The encoding to be used for the response headers.
            headers: A string keyed dictionary of response headers. Header keys are insensitive.
            media_type: A value for the response ``Content-Type`` header.
            status_code: An HTTP status code.
        """
        super().__init__(
            background=background,
            content=b"",  # type: ignore[arg-type]
            cookies=cookies,
            encoding=encoding,
            headers=headers,
            media_type=media_type,
            status_code=status_code,
        )
        self.iterator = content

    def to_asgi_response(
        self,
        app: Litestar | None,
        request: Request,
        *,
        background: BackgroundTask | BackgroundTasks | None = None,
        cookies: Iterable[Cookie] | None = None,
        encoded_headers: Iterable[tuple[bytes, bytes]] | None = None,
        headers: dict[str, str] | None = None,
        is_head_response: bool = False,
        media_type: MediaType | str | None = None,
        status_code: int | None = None,
        type_encoders: TypeEncodersMap | None = None,
    ) -> ASGIResponse:
        """Create an ASGIStreamingResponse from a StremaingResponse instance.

        Args:
            app: The :class:`Litestar <.app.Litestar>` application instance.
            background: Background task(s) to be executed after the response is sent.
            cookies: A list of cookies to be set on the response.
            encoded_headers: A list of already encoded headers.
            headers: Additional headers to be merged with the response headers. Response headers take precedence.
            is_head_response: Whether the response is a HEAD response.
            media_type: Media type for the response. If ``media_type`` is already set on the response, this is ignored.
            request: The :class:`Request <.connection.Request>` instance.
            status_code: Status code for the response. If ``status_code`` is already set on the response, this is
            type_encoders: A dictionary of type encoders to use for encoding the response content.

        Returns:
            An ASGIStreamingResponse instance.
        """
        if app is not None:
            warn_deprecation(
                version="2.1",
                deprecated_name="app",
                kind="parameter",
                removal_in="3.0.0",
                alternative="request.app",
            )

        headers = {**headers, **self.headers} if headers is not None else self.headers
        cookies = self.cookies if cookies is None else itertools.chain(self.cookies, cookies)

        media_type = get_enum_string_value(media_type or self.media_type or MediaType.JSON)

        iterator = self.iterator
        if not isinstance(iterator, (Iterable, Iterator, AsyncIterable, AsyncIterator)) and callable(iterator):
            iterator = iterator()

        return ASGIStreamingResponse(
            background=self.background or background,
            body=b"",
            content_length=0,
            cookies=cookies,
            encoded_headers=encoded_headers,
            encoding=self.encoding,
            headers=headers,
            is_head_response=is_head_response,
            iterator=iterator,
            media_type=media_type,
            status_code=self.status_code or status_code,
        )
