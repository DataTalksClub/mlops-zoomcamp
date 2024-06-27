from __future__ import annotations

import asyncio
from contextlib import AsyncExitStack
from functools import partial
from typing import AsyncGenerator, Awaitable, Callable, Iterable, overload

import asyncpg

from litestar.channels import ChannelsBackend
from litestar.exceptions import ImproperlyConfiguredException


class AsyncPgChannelsBackend(ChannelsBackend):
    _listener_conn: asyncpg.Connection

    @overload
    def __init__(self, dsn: str) -> None: ...

    @overload
    def __init__(
        self,
        *,
        make_connection: Callable[[], Awaitable[asyncpg.Connection]],
    ) -> None: ...

    def __init__(
        self,
        dsn: str | None = None,
        *,
        make_connection: Callable[[], Awaitable[asyncpg.Connection]] | None = None,
    ) -> None:
        if not (dsn or make_connection):
            raise ImproperlyConfiguredException("Need to specify dsn or make_connection")

        self._subscribed_channels: set[str] = set()
        self._exit_stack = AsyncExitStack()
        self._connect = make_connection or partial(asyncpg.connect, dsn=dsn)
        self._queue: asyncio.Queue[tuple[str, bytes]] | None = None

    async def on_startup(self) -> None:
        self._queue = asyncio.Queue()
        self._listener_conn = await self._connect()

    async def on_shutdown(self) -> None:
        await self._listener_conn.close()
        self._queue = None

    async def publish(self, data: bytes, channels: Iterable[str]) -> None:
        if self._queue is None:
            raise RuntimeError("Backend not yet initialized. Did you forget to call on_startup?")

        dec_data = data.decode("utf-8")

        conn = await self._connect()
        try:
            for channel in channels:
                await conn.execute("SELECT pg_notify($1, $2);", channel, dec_data)
        finally:
            await conn.close()

    async def subscribe(self, channels: Iterable[str]) -> None:
        for channel in set(channels) - self._subscribed_channels:
            await self._listener_conn.add_listener(channel, self._listener)  # type: ignore[arg-type]
            self._subscribed_channels.add(channel)

    async def unsubscribe(self, channels: Iterable[str]) -> None:
        for channel in channels:
            await self._listener_conn.remove_listener(channel, self._listener)  # type: ignore[arg-type]
        self._subscribed_channels = self._subscribed_channels - set(channels)

    async def stream_events(self) -> AsyncGenerator[tuple[str, bytes], None]:
        if self._queue is None:
            raise RuntimeError("Backend not yet initialized. Did you forget to call on_startup?")

        while True:
            channel, message = await self._queue.get()
            self._queue.task_done()
            # an UNLISTEN may be in transit while we're getting here, so we double-check
            # that we are actually supposed to deliver this message
            if channel in self._subscribed_channels:
                yield channel, message

    async def get_history(self, channel: str, limit: int | None = None) -> list[bytes]:
        raise NotImplementedError()

    def _listener(self, /, connection: asyncpg.Connection, pid: int, channel: str, payload: object) -> None:
        if not isinstance(payload, str):
            raise RuntimeError("Invalid data received")
        self._queue.put_nowait((channel, payload.encode("utf-8")))  # type: ignore[union-attr]
