from __future__ import annotations

import asyncio
import contextvars
from functools import partial
from typing import TYPE_CHECKING, Callable, TypeVar

import sniffio
from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from concurrent.futures import ThreadPoolExecutor

    import trio


T = TypeVar("T")
P = ParamSpec("P")


__all__ = (
    "sync_to_thread",
    "set_asyncio_executor",
    "get_asyncio_executor",
    "set_trio_capacity_limiter",
    "get_trio_capacity_limiter",
)


class _State:
    EXECUTOR: ThreadPoolExecutor | None = None
    LIMITER: trio.CapacityLimiter | None = None


async def _run_sync_asyncio(fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    ctx = contextvars.copy_context()
    bound_fn = partial(ctx.run, fn, *args, **kwargs)
    return await asyncio.get_running_loop().run_in_executor(get_asyncio_executor(), bound_fn)  # pyright: ignore


async def _run_sync_trio(fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    import trio

    return await trio.to_thread.run_sync(partial(fn, *args, **kwargs), limiter=get_trio_capacity_limiter())


async def sync_to_thread(fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    """Run the synchronous callable ``fn`` asynchronously in a worker thread.

    When called from asyncio, uses :meth:`asyncio.loop.run_in_executor` to
    run the callable. No executor is specified by default so the current loop's executor
    is used. A specific executor can be set using
    :func:`~litestar.concurrency.set_asyncio_executor`. This does not affect the loop's
    default executor.

    When called from trio, uses :func:`trio.to_thread.run_sync` to run the callable. No
    capacity limiter is specified by default, but one can be set using
    :func:`~litestar.concurrency.set_trio_capacity_limiter`. This does not affect trio's
    default capacity limiter.
    """
    if (library := sniffio.current_async_library()) == "asyncio":
        return await _run_sync_asyncio(fn, *args, **kwargs)

    if library == "trio":
        return await _run_sync_trio(fn, *args, **kwargs)

    raise RuntimeError("Unsupported async library or not in async context")


def set_asyncio_executor(executor: ThreadPoolExecutor | None) -> None:
    """Set the executor in which synchronous callables will be run within an asyncio
    context
    """
    try:
        sniffio.current_async_library()
    except sniffio.AsyncLibraryNotFoundError:
        pass
    else:
        raise RuntimeError("Cannot set executor from running loop")

    _State.EXECUTOR = executor


def get_asyncio_executor() -> ThreadPoolExecutor | None:
    """Get the executor in which synchronous callables will be run within an asyncio
    context
    """
    return _State.EXECUTOR


def set_trio_capacity_limiter(limiter: trio.CapacityLimiter | None) -> None:
    """Set the capacity limiter used when running synchronous callable within a trio
    context
    """
    try:
        sniffio.current_async_library()
    except sniffio.AsyncLibraryNotFoundError:
        pass
    else:
        raise RuntimeError("Cannot set limiter while in async context")

    _State.LIMITER = limiter


def get_trio_capacity_limiter() -> trio.CapacityLimiter | None:
    """Get the capacity limiter used when running synchronous callable within a trio
    context
    """
    return _State.LIMITER
