from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from litestar.types import Empty, EmptyType

__all__ = ("async_next",)


if TYPE_CHECKING:
    from typing import Any, AsyncGenerator

T = TypeVar("T")
D = TypeVar("D")

try:
    async_next = anext  # type: ignore[name-defined]
except NameError:

    async def async_next(gen: AsyncGenerator[T, Any], default: D | EmptyType = Empty) -> T | D:
        """Backwards compatibility shim for Python<3.10."""
        try:
            return await gen.__anext__()
        except StopAsyncIteration as exc:
            if default is not Empty:
                return default
            raise exc
