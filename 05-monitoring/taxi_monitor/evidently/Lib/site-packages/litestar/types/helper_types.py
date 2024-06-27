from __future__ import annotations

from functools import partial
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Dict,
    Iterable,
    Iterator,
    Literal,
    Optional,
    Sequence,
    TypeVar,
    Union,
)

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    from litestar.response.sse import ServerSentEventMessage


T = TypeVar("T")

__all__ = ("OptionalSequence", "SyncOrAsyncUnion", "AnyIOBackend", "StreamType", "MaybePartial", "SSEData")

OptionalSequence: TypeAlias = Optional[Sequence[T]]
"""Types 'T' as union of Sequence[T] and None."""

SyncOrAsyncUnion: TypeAlias = Union[T, Awaitable[T]]
"""Types 'T' as a union of T and awaitable T."""


AnyIOBackend: TypeAlias = Literal["asyncio", "trio"]
"""Anyio backend names."""

StreamType: TypeAlias = Union[Iterable[T], Iterator[T], AsyncIterable[T], AsyncIterator[T]]
"""A stream type."""

MaybePartial: TypeAlias = Union[T, partial]
"""A potentially partial callable."""

SSEData: TypeAlias = Union[int, str, bytes, Dict[str, Any], "ServerSentEventMessage"]
"""A type alias for SSE data."""
