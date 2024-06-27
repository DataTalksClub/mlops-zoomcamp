from __future__ import annotations

from enum import Enum
from functools import partial
from typing import TYPE_CHECKING, TypeVar, cast
from urllib.parse import quote

from litestar.utils.typing import get_origin_or_inner_type

if TYPE_CHECKING:
    from collections.abc import Container

    from litestar.types import MaybePartial

__all__ = (
    "get_enum_string_value",
    "get_name",
    "unwrap_partial",
    "url_quote",
    "unique_name_for_scope",
)

T = TypeVar("T")


def get_name(value: object) -> str:
    """Get the ``__name__`` of an object.

    Args:
        value: An arbitrary object.

    Returns:
        A name string.
    """

    name = getattr(value, "__name__", None)
    if name is not None:
        return cast("str", name)

    # On Python 3.8 and 3.9, Foo[int] does not have the __name__ attribute.
    if origin := get_origin_or_inner_type(value):
        return cast("str", origin.__name__)

    return type(value).__name__


def get_enum_string_value(value: Enum | str) -> str:
    """Return the string value of a string enum.

    See: https://github.com/litestar-org/litestar/pull/633#issuecomment-1286519267

    Args:
        value: An enum or string.

    Returns:
        A string.
    """
    return value.value if isinstance(value, Enum) else value  # type: ignore[no-any-return]


def unwrap_partial(value: MaybePartial[T]) -> T:
    """Unwraps a partial, returning the underlying callable.

    Args:
        value: A partial function.

    Returns:
        Callable
    """
    from litestar.utils.sync import AsyncCallable

    return cast("T", value.func if isinstance(value, (partial, AsyncCallable)) else value)


def url_quote(value: str | bytes) -> str:
    """Quote a URL.

    Args:
        value: A URL.

    Returns:
        A quoted URL.
    """
    return quote(value, safe="/#%[]=:;$&()+,!?*@'~")


def unique_name_for_scope(base_name: str, scope: Container[str]) -> str:
    """Create a name derived from ``base_name`` that's unique within ``scope``"""
    i = 0
    while True:
        if (unique_name := f"{base_name}_{i}") not in scope:
            return unique_name
        i += 1


def get_exception_group() -> type[BaseException]:
    """Get the exception group class with version compatibility."""
    try:
        return cast("type[BaseException]", ExceptionGroup)  # type:ignore[name-defined]
    except NameError:
        from exceptiongroup import ExceptionGroup as _ExceptionGroup  # pyright: ignore

        return cast("type[BaseException]", _ExceptionGroup)
