from __future__ import annotations

from asyncio import Queue
from collections import defaultdict, deque
from typing import Any, AsyncGenerator, Iterable

from litestar.channels.backends.base import ChannelsBackend


class MemoryChannelsBackend(ChannelsBackend):
    """An in-memory channels backend"""

    def __init__(self, history: int = 0) -> None:
        self._max_history_length = history
        self._channels: set[str] = set()
        self._queue: Queue[tuple[str, bytes]] | None = None
        self._history: defaultdict[str, deque[bytes]] = defaultdict(lambda: deque(maxlen=self._max_history_length))

    async def on_startup(self) -> None:
        self._queue = Queue()

    async def on_shutdown(self) -> None:
        self._queue = None

    async def publish(self, data: bytes, channels: Iterable[str]) -> None:
        """Publish ``data`` to ``channels``. If a channel has not yet been subscribed to,
        this will be a no-op.

        Args:
            data: Data to publish
            channels: Channels to publish to

        Returns:
            None

        Raises:
            RuntimeError: If ``on_startup`` has not been called yet
        """
        if not self._queue:
            raise RuntimeError("Backend not yet initialized. Did you forget to call on_startup?")

        for channel in channels:
            if channel not in self._channels:
                continue

            self._queue.put_nowait((channel, data))
        if self._max_history_length:
            for channel in channels:
                self._history[channel].append(data)

    async def subscribe(self, channels: Iterable[str]) -> None:
        """Subscribe to ``channels``, and enable publishing to them"""
        self._channels.update(channels)

    async def unsubscribe(self, channels: Iterable[str]) -> None:
        """Unsubscribe from ``channels``"""
        self._channels -= set(channels)
        try:
            for channel in channels:
                del self._history[channel]
        except KeyError:
            pass

    async def stream_events(self) -> AsyncGenerator[tuple[str, Any], None]:
        """Return a generator, iterating over events of subscribed channels as they become available"""
        if self._queue is None:
            raise RuntimeError("Backend not yet initialized. Did you forget to call on_startup?")

        while True:
            channel, message = await self._queue.get()
            self._queue.task_done()

            # if a message is published to a channel and the channel is then
            # unsubscribed before retrieving that message from the stream, it can still
            # end up here, so we double-check if we still are interested in this message
            if channel in self._channels:
                yield channel, message

    async def get_history(self, channel: str, limit: int | None = None) -> list[bytes]:
        """Return the event history of ``channel``, at most ``limit`` entries"""
        history = list(self._history[channel])
        if limit:
            history = history[-limit:]
        return history
