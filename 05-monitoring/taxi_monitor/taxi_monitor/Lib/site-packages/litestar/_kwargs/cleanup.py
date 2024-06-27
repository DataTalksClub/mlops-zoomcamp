from __future__ import annotations

from inspect import Traceback, isasyncgen
from typing import TYPE_CHECKING, Any, AsyncGenerator, Awaitable, Callable, Generator

from anyio import create_task_group

from litestar.utils import ensure_async_callable
from litestar.utils.compat import async_next

__all__ = ("DependencyCleanupGroup",)


if TYPE_CHECKING:
    from litestar.types import AnyGenerator


class DependencyCleanupGroup:
    """Wrapper for generator based dependencies.

    Simplify cleanup by wrapping :func:`next` / :func:`anext` calls and providing facilities to
    :meth:`throw <generator.throw>` / :meth:`athrow <agen.athrow>` into all generators consecutively. An instance of
    this class can be used as a contextmanager, which will automatically throw any exceptions into its generators. All
    exceptions caught in this manner will be re-raised after they have been thrown in the generators.
    """

    __slots__ = ("_generators", "_closed")

    def __init__(self, generators: list[AnyGenerator] | None = None) -> None:
        """Initialize ``DependencyCleanupGroup``.

        Args:
            generators: An optional list of generators to be called at cleanup
        """
        self._generators = generators or []
        self._closed = False

    def add(self, generator: Generator[Any, None, None] | AsyncGenerator[Any, None]) -> None:
        """Add a new generator to the group.

        Args:
            generator: The generator to add

        Returns:
            None
        """
        if self._closed:
            raise RuntimeError("Cannot call cleanup on a closed DependencyCleanupGroup")
        self._generators.append(generator)

    @staticmethod
    def _wrap_next(generator: AnyGenerator) -> Callable[[], Awaitable[None]]:
        if isasyncgen(generator):

            async def wrapped_async() -> None:
                await async_next(generator, None)

            return wrapped_async

        def wrapped() -> None:
            next(generator, None)  # type: ignore[arg-type]

        return ensure_async_callable(wrapped)

    async def cleanup(self) -> None:
        """Execute cleanup by calling :func:`next` / :func:`anext` on all generators.

        If there are multiple generators to be called, they will be executed in a :class:`anyio.TaskGroup`.

        Returns:
            None
        """
        if self._closed:
            raise RuntimeError("Cannot call cleanup on a closed DependencyCleanupGroup")

        self._closed = True

        if not self._generators:
            return

        if len(self._generators) == 1:
            await self._wrap_next(self._generators[0])()
            return

        async with create_task_group() as task_group:
            for generator in self._generators:
                task_group.start_soon(self._wrap_next(generator))

    async def __aenter__(self) -> None:
        """Support the async contextmanager protocol to allow for easier catching and throwing of exceptions into the
        generators.
        """

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Traceback | None,
    ) -> None:
        """If an exception was raised within the contextmanager block, throw it into all generators."""
        if exc_val:
            await self.throw(exc_val)

    async def throw(self, exc: BaseException) -> None:
        """Throw an exception in all generators sequentially.

        Args:
            exc: Exception to throw
        """
        for gen in self._generators:
            try:
                if isasyncgen(gen):
                    await gen.athrow(exc)
                else:
                    gen.throw(exc)  # type: ignore[union-attr]
            except (StopIteration, StopAsyncIteration):
                continue
