from __future__ import annotations

from typing import (
    AsyncGenerator,
    Awaitable,
    Callable,
    Generic,
    Iterable,
    Iterator,
    TypeVar,
)

from typing_extensions import ParamSpec

from litestar.concurrency import sync_to_thread
from litestar.utils.predicates import is_async_callable

__all__ = ("ensure_async_callable", "AsyncIteratorWrapper", "AsyncCallable", "is_async_callable")


P = ParamSpec("P")
T = TypeVar("T")


def ensure_async_callable(fn: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    """Ensure that ``fn`` is an asynchronous callable.
    If it is an asynchronous, return the original object, else wrap it in an
    ``AsyncCallable``
    """
    if is_async_callable(fn):
        return fn
    return AsyncCallable(fn)  # pyright: ignore


class AsyncCallable:
    """Wrap a given callable to be called in a thread pool using
    ``anyio.to_thread.run_sync``, keeping a reference to the original callable as
    :attr:`func`
    """

    def __init__(self, fn: Callable[P, T]) -> None:  # pyright: ignore
        self.func = fn

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Awaitable[T]:  # pyright: ignore
        return sync_to_thread(self.func, *args, **kwargs)  # pyright: ignore


class AsyncIteratorWrapper(Generic[T]):
    """Asynchronous generator, wrapping an iterable or iterator."""

    __slots__ = ("iterator", "generator")

    def __init__(self, iterator: Iterator[T] | Iterable[T]) -> None:
        """Take a sync iterator or iterable and yields values from it asynchronously.

        Args:
            iterator: A sync iterator or iterable.
        """
        self.iterator = iterator if isinstance(iterator, Iterator) else iter(iterator)
        self.generator = self._async_generator()

    def _call_next(self) -> T:
        try:
            return next(self.iterator)
        except StopIteration as e:
            raise ValueError from e

    async def _async_generator(self) -> AsyncGenerator[T, None]:
        while True:
            try:
                yield await sync_to_thread(self._call_next)
            except ValueError:
                return

    def __aiter__(self) -> AsyncIteratorWrapper[T]:
        return self

    async def __anext__(self) -> T:
        return await self.generator.__anext__()
