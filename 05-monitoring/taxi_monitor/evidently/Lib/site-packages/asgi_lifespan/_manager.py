import typing
from contextlib import AsyncExitStack
from types import TracebackType

from ._concurrency import detect_concurrency_backend
from ._exceptions import LifespanNotSupported
from ._types import ASGIApp, Message, Receive, Scope, Send


def state_middleware(app: ASGIApp, state: typing.Dict[str, typing.Any]) -> ASGIApp:
    async def app_with_state(scope: Scope, receive: Receive, send: Send) -> None:
        scope["state"] = state
        await app(scope, receive, send)

    return app_with_state


class LifespanManager:
    def __init__(
        self,
        app: ASGIApp,
        startup_timeout: typing.Optional[float] = 5,
        shutdown_timeout: typing.Optional[float] = 5,
    ) -> None:
        self._state: typing.Dict[str, typing.Any] = {}
        self.app = state_middleware(app, self._state)
        self.startup_timeout = startup_timeout
        self.shutdown_timeout = shutdown_timeout

        self._concurrency_backend = detect_concurrency_backend()
        self._startup_complete = self._concurrency_backend.create_event()
        self._shutdown_complete = self._concurrency_backend.create_event()
        self._receive_queue = self._concurrency_backend.create_queue(capacity=2)
        self._receive_called = False
        self._app_exception: typing.Optional[BaseException] = None
        self._exit_stack = AsyncExitStack()

    async def startup(self) -> None:
        await self._receive_queue.put({"type": "lifespan.startup"})
        await self._concurrency_backend.run_and_fail_after(
            self.startup_timeout, self._startup_complete.wait
        )
        if self._app_exception:
            # Let the caller deal with the exception.
            raise self._app_exception

    async def shutdown(self) -> None:
        await self._receive_queue.put({"type": "lifespan.shutdown"})
        await self._concurrency_backend.run_and_fail_after(
            self.shutdown_timeout, self._shutdown_complete.wait
        )

    async def receive(self) -> Message:
        self._receive_called = True
        return await self._receive_queue.get()

    async def send(self, message: Message) -> None:
        if not self._receive_called:
            raise LifespanNotSupported(
                "Application called send() before receive(). "
                "Is it missing `assert scope['type'] == 'http'` or similar?"
            )

        if message["type"] == "lifespan.startup.complete":
            self._startup_complete.set()
        elif message["type"] == "lifespan.shutdown.complete":
            self._shutdown_complete.set()

    async def run_app(self) -> None:
        scope: Scope = {"type": "lifespan"}

        try:
            await self.app(scope, self.receive, self.send)
        except BaseException as exc:
            self._app_exception = exc

            # We crashed, so don't make '.startup()' and '.shutdown()'
            # wait unnecessarily (or they'll timeout).
            self._startup_complete.set()
            self._shutdown_complete.set()

            if not self._receive_called:
                raise LifespanNotSupported(
                    "Application failed before making its first call to 'receive()'. "
                    "We expect this to originate from a statement similar to "
                    "`assert scope['type'] == 'type'`. "
                    "If that is not the case, then this crash is unexpected and "
                    "there is probably more debug output in the cause traceback."
                ) from exc

            raise

    async def __aenter__(self) -> "LifespanManager":
        await self._exit_stack.__aenter__()
        await self._exit_stack.enter_async_context(
            self._concurrency_backend.run_in_background(self.run_app)
        )
        try:
            await self.startup()
            return self
        except BaseException:
            await self._exit_stack.aclose()
            raise

    async def __aexit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]] = None,
        exc_value: typing.Optional[BaseException] = None,
        traceback: typing.Optional[TracebackType] = None,
    ) -> typing.Optional[bool]:
        if exc_type is None:
            self._exit_stack.push_async_callback(self.shutdown)
        return await self._exit_stack.__aexit__(exc_type, exc_value, traceback)
