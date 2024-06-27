"""Compute method resolution order. Implements `Class.mro` attribute."""

# Copyright (c) 2019 Vitaly R. Samigullin
# Adapted from https://github.com/pilosus/c3linear
# Adapted from https://github.com/tristanlatr/pydocspec

from __future__ import annotations

from itertools import islice
from typing import Deque, TypeVar

T = TypeVar("T")


class _Dependency(Deque[T]):
    """A class representing a (doubly-ended) queue of items."""

    @property
    def head(self) -> T | None:
        """Head of the dependency."""
        try:
            return self[0]
        except IndexError:
            return None

    @property
    def tail(self) -> islice:
        """Tail of the dependency.

        The `islice` object is sufficient for iteration or testing membership (`in`).
        """
        try:
            return islice(self, 1, self.__len__())
        except (ValueError, IndexError):
            return islice([], 0, 0)


class _DependencyList:
    """A class representing a list of linearizations (dependencies).

    The last element of DependencyList is a list of parents.
    It's needed  to the merge process preserves the local
    precedence order of direct parent classes.
    """

    def __init__(self, *lists: list[T | None]) -> None:
        """Initialize the list.

        Parameters:
            *lists: Lists of items.
        """
        self._lists = [_Dependency(lst) for lst in lists]

    def __contains__(self, item: T) -> bool:
        """Return True if any linearization's tail contains an item."""
        return any(item in lst.tail for lst in self._lists)

    def __len__(self) -> int:
        size = len(self._lists)
        return (size - 1) if size else 0

    def __repr__(self) -> str:
        return self._lists.__repr__()

    @property
    def heads(self) -> list[T | None]:
        """Return the heads."""
        return [lst.head for lst in self._lists]

    @property
    def tails(self) -> _DependencyList:
        """Return self so that `__contains__` could be called."""
        return self

    @property
    def exhausted(self) -> bool:
        """True if all elements of the lists are exhausted."""
        return all(len(x) == 0 for x in self._lists)

    def remove(self, item: T | None) -> None:
        """Remove an item from the lists.

        Once an item removed from heads, the leftmost elements of the tails
        get promoted to become the new heads.
        """
        for i in self._lists:
            if i and i.head == item:
                i.popleft()


def c3linear_merge(*lists: list[T]) -> list[T]:
    """Merge lists of lists in the order defined by the C3Linear algorithm.

    Parameters:
        *lists: Lists of items.

    Returns:
        The merged list of items.
    """
    result: list[T] = []
    linearizations = _DependencyList(*lists)  # type: ignore[arg-type]

    while True:
        if linearizations.exhausted:
            return result

        for head in linearizations.heads:
            if head and (head not in linearizations.tails):
                result.append(head)  # type: ignore[arg-type]
                linearizations.remove(head)

                # Once candidate is found, continue iteration
                # from the first element of the list.
                break
        else:
            # Loop never broke, no linearization could possibly be found.
            raise ValueError("Cannot compute C3 linearization")


__all__ = ["c3linear_merge"]
