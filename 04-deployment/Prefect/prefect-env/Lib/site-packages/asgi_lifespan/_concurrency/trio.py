import types
import typing

import trio

from .._compat import AsyncExitStack
from .base import BaseEvent, BaseQueue, ConcurrencyBackend


class TrioEvent(BaseEvent):
    def __init__(self) -> None:
        self._event = trio.Event()

    def set(self) -> None:
        self._event.set()

    async def wait(self) -> None:
        await self._event.wait()


class TrioQueue(BaseQueue):
    def __init__(self, capacity: int) -> None:
        self._send_channel, self._receive_channel = trio.open_memory_channel(
            max_buffer_size=capacity
        )

    async def get(self) -> typing.Any:
        return await self._receive_channel.receive()

    async def put(self, value: typing.Any) -> None:
        await self._send_channel.send(value)


class TrioBackend(ConcurrencyBackend):
    def create_event(self) -> BaseEvent:
        return TrioEvent()

    def create_queue(self, capacity: int) -> BaseQueue:
        return TrioQueue(capacity=capacity)

    async def run_and_fail_after(
        self,
        seconds: typing.Optional[float],
        coroutine: typing.Callable[[], typing.Awaitable[None]],
    ) -> None:
        with trio.move_on_after(seconds if seconds is not None else float("inf")):
            await coroutine()
            return
        raise TimeoutError

    def run_in_background(
        self, coroutine: typing.Callable[[], typing.Awaitable[None]]
    ) -> typing.AsyncContextManager:
        return Background(coroutine)


class Background:
    def __init__(self, coroutine: typing.Callable[[], typing.Awaitable[None]]) -> None:
        self.coroutine = coroutine
        self._exit_stack = AsyncExitStack()

    async def __aenter__(self) -> None:
        nursery = await self._exit_stack.enter_async_context(trio.open_nursery())
        nursery.start_soon(self.coroutine)

    async def __aexit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]] = None,
        exc_value: typing.Optional[BaseException] = None,
        traceback: typing.Optional[types.TracebackType] = None,
    ) -> None:
        await self._exit_stack.__aexit__(exc_type, exc_value, traceback)
