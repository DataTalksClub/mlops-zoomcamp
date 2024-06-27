from __future__ import annotations

from contextlib import AsyncExitStack
from typing import AsyncGenerator, Iterable

import psycopg

from .base import ChannelsBackend


def _safe_quote(ident: str) -> str:
    return '"{}"'.format(ident.replace('"', '""'))  # sourcery skip


class PsycoPgChannelsBackend(ChannelsBackend):
    _listener_conn: psycopg.AsyncConnection

    def __init__(self, pg_dsn: str) -> None:
        self._pg_dsn = pg_dsn
        self._subscribed_channels: set[str] = set()
        self._exit_stack = AsyncExitStack()

    async def on_startup(self) -> None:
        self._listener_conn = await psycopg.AsyncConnection.connect(self._pg_dsn, autocommit=True)
        await self._exit_stack.enter_async_context(self._listener_conn)

    async def on_shutdown(self) -> None:
        await self._exit_stack.aclose()

    async def publish(self, data: bytes, channels: Iterable[str]) -> None:
        dec_data = data.decode("utf-8")
        async with await psycopg.AsyncConnection.connect(self._pg_dsn) as conn:
            for channel in channels:
                await conn.execute("SELECT pg_notify(%s, %s);", (channel, dec_data))

    async def subscribe(self, channels: Iterable[str]) -> None:
        for channel in set(channels) - self._subscribed_channels:
            # can't use placeholders in LISTEN
            await self._listener_conn.execute(f"LISTEN {_safe_quote(channel)};")  # pyright: ignore

            self._subscribed_channels.add(channel)

    async def unsubscribe(self, channels: Iterable[str]) -> None:
        for channel in channels:
            # can't use placeholders in UNLISTEN
            await self._listener_conn.execute(f"UNLISTEN {_safe_quote(channel)};")  # pyright: ignore
        self._subscribed_channels = self._subscribed_channels - set(channels)

    async def stream_events(self) -> AsyncGenerator[tuple[str, bytes], None]:
        async for notify in self._listener_conn.notifies():
            yield notify.channel, notify.payload.encode("utf-8")

    async def get_history(self, channel: str, limit: int | None = None) -> list[bytes]:
        raise NotImplementedError()
