from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Iterable


class ChannelsBackend(ABC):
    @abstractmethod
    async def on_startup(self) -> None:
        """Called by the plugin on application startup"""
        ...

    @abstractmethod
    async def on_shutdown(self) -> None:
        """Called by the plugin on application shutdown"""
        ...

    @abstractmethod
    async def publish(self, data: bytes, channels: Iterable[str]) -> None:
        """Publish the message ``data`` to all ``channels``"""
        ...

    @abstractmethod
    async def subscribe(self, channels: Iterable[str]) -> None:
        """Start listening for events on ``channels``"""
        ...

    @abstractmethod
    async def unsubscribe(self, channels: Iterable[str]) -> None:
        """Stop listening for events on ``channels``"""
        ...

    @abstractmethod
    def stream_events(self) -> AsyncGenerator[tuple[str, bytes], None]:
        """Return a generator, iterating over events of subscribed channels as they become available"""
        ...

    @abstractmethod
    async def get_history(self, channel: str, limit: int | None = None) -> list[bytes]:
        """Return the event history of ``channel``, at most ``limit`` entries"""
        ...
