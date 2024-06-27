from __future__ import annotations

import io
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, AsyncGenerator, AsyncIterable, AsyncIterator, Iterable, Iterator

from litestar.concurrency import sync_to_thread
from litestar.exceptions import ImproperlyConfiguredException
from litestar.response.streaming import Stream
from litestar.utils import AsyncIteratorWrapper

if TYPE_CHECKING:
    from litestar.background_tasks import BackgroundTask, BackgroundTasks
    from litestar.types import ResponseCookies, ResponseHeaders, SSEData, StreamType

_LINE_BREAK_RE = re.compile(r"\r\n|\r|\n")
DEFAULT_SEPARATOR = "\r\n"


class _ServerSentEventIterator(AsyncIteratorWrapper[bytes]):
    __slots__ = ("content_async_iterator", "event_id", "event_type", "retry_duration", "comment_message")

    content_async_iterator: AsyncIterable[SSEData]

    def __init__(
        self,
        content: str | bytes | StreamType[SSEData],
        event_type: str | None = None,
        event_id: int | str | None = None,
        retry_duration: int | None = None,
        comment_message: str | None = None,
    ) -> None:
        self.comment_message = comment_message
        self.event_id = event_id
        self.event_type = event_type
        self.retry_duration = retry_duration
        chunks: list[bytes] = []
        if comment_message is not None:
            chunks.extend([f": {chunk}\r\n".encode() for chunk in _LINE_BREAK_RE.split(comment_message)])

        if event_id is not None:
            chunks.append(f"id: {event_id}\r\n".encode())

        if event_type is not None:
            chunks.append(f"event: {event_type}\r\n".encode())

        if retry_duration is not None:
            chunks.append(f"retry: {retry_duration}\r\n".encode())

        super().__init__(iterator=chunks)

        if not isinstance(content, (Iterator, AsyncIterator, AsyncIteratorWrapper)) and callable(content):
            content = content()  # type: ignore[unreachable]

        if isinstance(content, (str, bytes)):
            self.content_async_iterator = AsyncIteratorWrapper([content])
        elif isinstance(content, (Iterable, Iterator)):
            self.content_async_iterator = AsyncIteratorWrapper(content)
        elif isinstance(content, (AsyncIterable, AsyncIterator, AsyncIteratorWrapper)):
            self.content_async_iterator = content
        else:
            raise ImproperlyConfiguredException(f"Invalid type {type(content)} for ServerSentEvent")

    def ensure_bytes(self, data: str | int | bytes | dict | ServerSentEventMessage | Any, sep: str) -> bytes:
        if isinstance(data, ServerSentEventMessage):
            return data.encode()
        if isinstance(data, dict):
            data["sep"] = sep
            return ServerSentEventMessage(**data).encode()

        return ServerSentEventMessage(
            data=data, id=self.event_id, event=self.event_type, retry=self.retry_duration, sep=sep
        ).encode()

    def _call_next(self) -> bytes:
        try:
            return next(self.iterator)
        except StopIteration as e:
            raise ValueError from e

    async def _async_generator(self) -> AsyncGenerator[bytes, None]:
        while True:
            try:
                yield await sync_to_thread(self._call_next)
            except ValueError:
                async for value in self.content_async_iterator:
                    yield self.ensure_bytes(value, DEFAULT_SEPARATOR)
                break


@dataclass
class ServerSentEventMessage:
    data: str | int | bytes | None = ""
    event: str | None = None
    id: int | str | None = None
    retry: int | None = None
    comment: str | None = None
    sep: str = DEFAULT_SEPARATOR

    def encode(self) -> bytes:
        buffer = io.StringIO()
        if self.comment is not None:
            for chunk in _LINE_BREAK_RE.split(str(self.comment)):
                buffer.write(f": {chunk}")
                buffer.write(self.sep)

        if self.id is not None:
            buffer.write(_LINE_BREAK_RE.sub("", f"id: {self.id}"))
            buffer.write(self.sep)

        if self.event is not None:
            buffer.write(_LINE_BREAK_RE.sub("", f"event: {self.event}"))
            buffer.write(self.sep)

        if self.data is not None:
            data = self.data
            for chunk in _LINE_BREAK_RE.split(data.decode() if isinstance(data, bytes) else str(data)):
                buffer.write(f"data: {chunk}")
                buffer.write(self.sep)

        if self.retry is not None:
            buffer.write(f"retry: {self.retry}")
            buffer.write(self.sep)

        buffer.write(self.sep)
        return buffer.getvalue().encode("utf-8")


class ServerSentEvent(Stream):
    def __init__(
        self,
        content: str | bytes | StreamType[SSEData],
        *,
        background: BackgroundTask | BackgroundTasks | None = None,
        cookies: ResponseCookies | None = None,
        encoding: str = "utf-8",
        headers: ResponseHeaders | None = None,
        event_type: str | None = None,
        event_id: int | str | None = None,
        retry_duration: int | None = None,
        comment_message: str | None = None,
        status_code: int | None = None,
    ) -> None:
        """Initialize the response.

        Args:
            content: Bytes, string or a sync or async iterator or iterable.
            background: A :class:`BackgroundTask <.background_tasks.BackgroundTask>` instance or
                :class:`BackgroundTasks <.background_tasks.BackgroundTasks>` to execute after the response is finished.
                Defaults to None.
            cookies: A list of :class:`Cookie <.datastructures.Cookie>` instances to be set under the response
                ``Set-Cookie`` header.
            encoding: The encoding to be used for the response headers.
            headers: A string keyed dictionary of response headers. Header keys are insensitive.
            status_code: The response status code. Defaults to 200.
            event_type: The type of the SSE event. If given, the browser will sent the event to any 'event-listener'
                declared for it (e.g. via 'addEventListener' in JS).
            event_id: The event ID. This sets the event source's 'last event id'.
            retry_duration: Retry duration in milliseconds.
            comment_message: A comment message. This value is ignored by clients and is used mostly for pinging.
        """
        super().__init__(
            content=_ServerSentEventIterator(
                content=content,
                event_type=event_type,
                event_id=event_id,
                retry_duration=retry_duration,
                comment_message=comment_message,
            ),
            media_type="text/event-stream",
            background=background,
            cookies=cookies,
            encoding=encoding,
            headers=headers,
            status_code=status_code,
        )
        self.headers.setdefault("Cache-Control", "no-cache")
        self.headers["Connection"] = "keep-alive"
        self.headers["X-Accel-Buffering"] = "no"
