from __future__ import annotations

import asyncio
from asyncio import CancelledError, Queue, QueueFull
from collections import deque
from contextlib import AsyncExitStack, asynccontextmanager, suppress
from typing import TYPE_CHECKING, Any, AsyncGenerator, Awaitable, Callable, Generic, Literal, TypeVar

if TYPE_CHECKING:
    from litestar.channels import ChannelsPlugin


T = TypeVar("T")

BacklogStrategy = Literal["backoff", "dropleft"]

EventCallback = Callable[[bytes], Awaitable[Any]]


class AsyncDeque(Queue, Generic[T]):
    def __init__(self, maxsize: int | None) -> None:
        self._deque_maxlen = maxsize
        super().__init__()

    def _init(self, maxsize: int) -> None:
        self._queue: deque[T] = deque(maxlen=self._deque_maxlen)


class Subscriber:
    """A wrapper around a stream of events published to subscribed channels"""

    def __init__(
        self,
        plugin: ChannelsPlugin,
        max_backlog: int | None = None,
        backlog_strategy: BacklogStrategy = "backoff",
    ) -> None:
        self._task: asyncio.Task | None = None
        self._plugin = plugin
        self._backend = plugin._backend
        self._queue: Queue[bytes | None] | AsyncDeque[bytes | None]

        if max_backlog and backlog_strategy == "dropleft":
            self._queue = AsyncDeque(maxsize=max_backlog or 0)
        else:
            self._queue = Queue(maxsize=max_backlog or 0)

    async def put(self, item: bytes | None) -> None:
        await self._queue.put(item)

    def put_nowait(self, item: bytes | None) -> bool:
        """Put an item in the subscriber's stream without waiting"""
        try:
            self._queue.put_nowait(item)
            return True
        except QueueFull:
            return False

    @property
    def qsize(self) -> int:
        return self._queue.qsize()

    async def iter_events(self) -> AsyncGenerator[bytes, None]:
        """Iterate over the stream of events. If no items are available, block until
        one becomes available
        """
        while True:
            item = await self._queue.get()
            if item is None:
                self._queue.task_done()
                break
            yield item
            self._queue.task_done()

    @asynccontextmanager
    async def run_in_background(self, on_event: EventCallback, join: bool = True) -> AsyncGenerator[None, None]:
        """Start a task in the background that sends events from the subscriber's stream
        to ``socket`` as they become available. On exit, it will prevent the stream from
        accepting new events and wait until the currently enqueued ones are processed.
        Should the context be left with an exception, the task will be cancelled
        immediately.

        Args:
            on_event: Callback to invoke with the event data for every event
            join: If ``True``, wait for all items in the stream to be processed before
                stopping the worker. Note that an error occurring within the context
                will always lead to the immediate cancellation of the worker
        """
        self._start_in_background(on_event=on_event)
        async with AsyncExitStack() as exit_stack:
            exit_stack.push_async_callback(self.stop, join=False)
            yield
            exit_stack.pop_all()
            await self.stop(join=join)

    async def _worker(self, on_event: EventCallback) -> None:
        async for event in self.iter_events():
            await on_event(event)

    def _start_in_background(self, on_event: EventCallback) -> None:
        """Start a task in the background that sends events from the subscriber's stream
        to ``socket`` as they become available.

        Args:
            on_event: Callback to invoke with the event data for every event
        """
        if self._task is not None:
            raise RuntimeError("Subscriber is already running")
        self._task = asyncio.create_task(self._worker(on_event))

    @property
    def is_running(self) -> bool:
        """Return whether a sending task is currently running"""
        return self._task is not None

    async def stop(self, join: bool = False) -> None:
        """Stop a task was previously started with :meth:`run_in_background`. If the
        task is not yet done it will be cancelled and awaited

        Args:
            join: If ``True`` wait for all items to be processed before stopping the task
        """
        if not self._task:
            return

        if join:
            await self._queue.join()

        if not self._task.done():
            self._task.cancel()

        with suppress(CancelledError):
            await self._task

        self._task = None
