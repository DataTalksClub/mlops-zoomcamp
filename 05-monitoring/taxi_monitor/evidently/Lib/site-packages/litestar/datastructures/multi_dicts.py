from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any, Generator, Generic, Iterable, Mapping, TypeVar

from multidict import MultiDict as BaseMultiDict
from multidict import MultiDictProxy, MultiMapping

from litestar.datastructures.upload_file import UploadFile

if TYPE_CHECKING:
    from typing_extensions import Self


__all__ = ("FormMultiDict", "ImmutableMultiDict", "MultiDict", "MultiMixin")


T = TypeVar("T")


class MultiMixin(Generic[T], MultiMapping[T], ABC):
    """Mixin providing common methods for multi dicts, used by :class:`ImmutableMultiDict` and :class:`MultiDict`"""

    def dict(self) -> dict[str, list[Any]]:
        """Return the multi-dict as a dict of lists.

        Returns:
            A dict of lists
        """
        return {k: self.getall(k) for k in set(self.keys())}

    def multi_items(self) -> Generator[tuple[str, T], None, None]:
        """Get all keys and values, including duplicates.

        Returns:
            A list of tuples containing key-value pairs
        """
        for key in set(self):
            for value in self.getall(key):
                yield key, value


class MultiDict(BaseMultiDict[T], MultiMixin[T], Generic[T]):
    """MultiDict, using :class:`MultiDict <multidict.MultiDictProxy>`."""

    def __init__(self, args: MultiMapping | Mapping[str, T] | Iterable[tuple[str, T]] | None = None) -> None:
        """Initialize ``MultiDict`` from a`MultiMapping``,
        :class:`Mapping <typing.Mapping>` or an iterable of tuples.

        Args:
            args: Mapping-like structure to create the ``MultiDict`` from
        """
        super().__init__(args or {})

    def immutable(self) -> ImmutableMultiDict[T]:
        """Create an.

        :class:`ImmutableMultiDict` view.

        Returns:
            An immutable multi dict
        """
        return ImmutableMultiDict[T](self)  # pyright: ignore

    def copy(self) -> Self:
        """Return a shallow copy"""
        return type(self)(list(self.multi_items()))


class ImmutableMultiDict(MultiDictProxy[T], MultiMixin[T], Generic[T]):
    """Immutable MultiDict, using class:`MultiDictProxy <multidict.MultiDictProxy>`."""

    def __init__(self, args: MultiMapping | Mapping[str, Any] | Iterable[tuple[str, Any]] | None = None) -> None:
        """Initialize ``ImmutableMultiDict`` from a `MultiMapping``,
        :class:`Mapping <typing.Mapping>` or an iterable of tuples.

        Args:
            args: Mapping-like structure to create the ``ImmutableMultiDict`` from
        """
        super().__init__(BaseMultiDict(args or {}))

    def mutable_copy(self) -> MultiDict[T]:
        """Create a mutable copy as a :class:`MultiDict`

        Returns:
            A mutable multi dict
        """
        return MultiDict(list(self.multi_items()))

    def copy(self) -> Self:  # type: ignore[override]
        """Return a shallow copy"""
        return type(self)(self.items())


class FormMultiDict(ImmutableMultiDict[Any]):
    """MultiDict for form data."""

    async def close(self) -> None:
        """Close all files in the multi-dict.

        Returns:
            None
        """
        for _, value in self.multi_items():
            if isinstance(value, UploadFile):
                await value.close()
