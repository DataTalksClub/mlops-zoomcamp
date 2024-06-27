from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator, Mapping, MutableSequence
from typing import AbstractSet, Any, Generic, Set, TypeVar, cast

from typing_extensions import ParamSpec

from polyfactory.exceptions import ParameterException


class CoverageContainerBase(ABC):
    """Base class for coverage container implementations.

    A coverage container is a wrapper providing values for a particular field. Coverage containers return field values and
    track a "done" state to indicate that all coverage examples have been generated.
    """

    @abstractmethod
    def next_value(self) -> Any:
        """Provide the next value"""
        ...

    @abstractmethod
    def is_done(self) -> bool:
        """Indicate if this container has provided every coverage example it has"""
        ...


T = TypeVar("T")


class CoverageContainer(CoverageContainerBase, Generic[T]):
    """A coverage container that wraps a collection of values.

    When calling ``next_value()`` a greater number of times than the length of the given collection will cause duplicate
    examples to be returned (wraps around).

    If there are any coverage containers within the given collection, the values from those containers are essentially merged
    into the parent container.
    """

    def __init__(self, instances: Iterable[T]) -> None:
        self._pos = 0
        self._instances = list(instances)
        if not self._instances:
            msg = "CoverageContainer must have at least one instance"
            raise ValueError(msg)

    def next_value(self) -> T:
        value = self._instances[self._pos % len(self._instances)]
        if isinstance(value, CoverageContainerBase):
            result = value.next_value()
            if value.is_done():
                # Only move onto the next instance if the sub-container is done
                self._pos += 1
            return cast(T, result)

        self._pos += 1
        return value

    def is_done(self) -> bool:
        return self._pos >= len(self._instances)

    def __repr__(self) -> str:
        return f"CoverageContainer(instances={self._instances}, is_done={self.is_done()})"


P = ParamSpec("P")


class CoverageContainerCallable(CoverageContainerBase, Generic[T]):
    """A coverage container that wraps a callable.

    When calling ``next_value()`` the wrapped callable is called to provide a value.
    """

    def __init__(self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> None:
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def next_value(self) -> T:
        try:
            return self._func(*self._args, **self._kwargs)
        except Exception as e:  # noqa: BLE001
            msg = f"Unsupported type: {self._func!r}\n\nEither extend the providers map or add a factory function for this type."
            raise ParameterException(msg) from e

    def is_done(self) -> bool:
        return True


def _resolve_next(unresolved: Any) -> tuple[Any, bool]:  # noqa: C901
    if isinstance(unresolved, CoverageContainerBase):
        result, done = _resolve_next(unresolved.next_value())
        return result, unresolved.is_done() and done

    if isinstance(unresolved, Mapping):
        result = {}
        done_status = True
        for key, value in unresolved.items():
            val_resolved, val_done = _resolve_next(value)
            key_resolved, key_done = _resolve_next(key)
            result[key_resolved] = val_resolved
            done_status = done_status and val_done and key_done
        return result, done_status

    if isinstance(unresolved, (tuple, MutableSequence)):
        result = []
        done_status = True
        for value in unresolved:
            resolved, done = _resolve_next(value)
            result.append(resolved)
            done_status = done_status and done
        if isinstance(unresolved, tuple):
            result = tuple(result)
        return result, done_status

    if isinstance(unresolved, Set):
        result = type(unresolved)()
        done_status = True
        for value in unresolved:
            resolved, done = _resolve_next(value)
            result.add(resolved)
            done_status = done_status and done
        return result, done_status

    if issubclass(type(unresolved), AbstractSet):
        result = type(unresolved)()
        done_status = True
        resolved_values = []
        for value in unresolved:
            resolved, done = _resolve_next(value)
            resolved_values.append(resolved)
            done_status = done_status and done
        return result.union(resolved_values), done_status

    return unresolved, True


def resolve_kwargs_coverage(kwargs: dict[str, Any]) -> Iterator[dict[str, Any]]:
    done = False
    while not done:
        resolved, done = _resolve_next(kwargs)
        yield resolved
