from __future__ import annotations

import math
import sys
from abc import ABC, abstractmethod
from collections import defaultdict
from contextlib import AsyncExitStack
from functools import partial
from typing import TYPE_CHECKING, Any, Sequence

if sys.version_info < (3, 9):
    from typing import AsyncContextManager
else:
    from contextlib import AbstractAsyncContextManager as AsyncContextManager

import anyio

from litestar.exceptions import ImproperlyConfiguredException

if TYPE_CHECKING:
    from types import TracebackType

    from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream

    from litestar.events.listener import EventListener

__all__ = ("BaseEventEmitterBackend", "SimpleEventEmitter")


class BaseEventEmitterBackend(AsyncContextManager["BaseEventEmitterBackend"], ABC):
    """Abstract class used to define event emitter backends."""

    __slots__ = ("listeners",)

    listeners: defaultdict[str, set[EventListener]]

    def __init__(self, listeners: Sequence[EventListener]) -> None:
        """Create an event emitter instance.

        Args:
            listeners: A list of listeners.
        """
        self.listeners = defaultdict(set)
        for listener in listeners:
            for event_id in listener.event_ids:
                self.listeners[event_id].add(listener)

    @abstractmethod
    def emit(self, event_id: str, *args: Any, **kwargs: Any) -> None:
        """Emit an event to all attached listeners.

        Args:
            event_id: The ID of the event to emit, e.g 'my_event'.
            *args: args to pass to the listener(s).
            **kwargs: kwargs to pass to the listener(s)

        Returns:
            None
        """
        raise NotImplementedError("not implemented")


class SimpleEventEmitter(BaseEventEmitterBackend):
    """Event emitter the works only in the current process"""

    __slots__ = ("_queue", "_exit_stack", "_receive_stream", "_send_stream")

    def __init__(self, listeners: Sequence[EventListener]) -> None:
        """Create an event emitter instance.

        Args:
            listeners: A list of listeners.
        """
        super().__init__(listeners=listeners)
        self._receive_stream: MemoryObjectReceiveStream | None = None
        self._send_stream: MemoryObjectSendStream | None = None
        self._exit_stack: AsyncExitStack | None = None

    async def _worker(self, receive_stream: MemoryObjectReceiveStream) -> None:
        """Run items from ``receive_stream`` in a task group.

        Returns:
            None
        """
        async with receive_stream, anyio.create_task_group() as task_group:
            async for item in receive_stream:
                fn, args, kwargs = item
                if kwargs:
                    fn = partial(fn, **kwargs)
                task_group.start_soon(fn, *args)  # pyright: ignore[reportGeneralTypeIssues]

    async def __aenter__(self) -> SimpleEventEmitter:
        self._exit_stack = AsyncExitStack()
        send_stream, receive_stream = anyio.create_memory_object_stream(math.inf)  # type: ignore[var-annotated]
        self._send_stream = send_stream
        task_group = anyio.create_task_group()

        await self._exit_stack.enter_async_context(task_group)
        await self._exit_stack.enter_async_context(send_stream)
        task_group.start_soon(self._worker, receive_stream)

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._exit_stack:
            await self._exit_stack.__aexit__(exc_type, exc_val, exc_tb)

        self._exit_stack = None
        self._send_stream = None

    def emit(self, event_id: str, *args: Any, **kwargs: Any) -> None:
        """Emit an event to all attached listeners.

        Args:
            event_id: The ID of the event to emit, e.g 'my_event'.
            *args: args to pass to the listener(s).
            **kwargs: kwargs to pass to the listener(s)

        Returns:
            None
        """
        if not (self._send_stream and self._exit_stack):
            raise RuntimeError("Emitter not initialized")

        if listeners := self.listeners.get(event_id):
            for listener in listeners:
                self._send_stream.send_nowait((listener.fn, args, kwargs))
            return
        raise ImproperlyConfiguredException(f"no event listeners are registered for event ID: {event_id}")
