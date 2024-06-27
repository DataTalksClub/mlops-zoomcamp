from __future__ import annotations

import re
from collections import abc, defaultdict, deque
from typing import (
    AbstractSet,
    Any,
    AsyncGenerator,
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Collection,
    Container,
    Coroutine,
    DefaultDict,
    Deque,
    Dict,
    FrozenSet,
    Generator,
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    List,
    Mapping,
    MappingView,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Reversible,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
    ValuesView,
    cast,
)

from typing_extensions import Annotated, NewType, NotRequired, Required, get_args, get_origin, get_type_hints

from litestar.types.builtin_types import NoneType, UnionTypes

__all__ = (
    "get_instantiable_origin",
    "get_origin_or_inner_type",
    "get_safe_generic_origin",
    "instantiable_type_mapping",
    "make_non_optional_union",
    "safe_generic_origin_map",
    "unwrap_annotation",
)


T = TypeVar("T")
UnionT = TypeVar("UnionT", bound="Union")

tuple_types_regex = re.compile(
    "^"
    + "|".join(
        [*[repr(x) for x in (List, Sequence, Iterable, Iterator, Tuple, Deque)], "tuple", "list", "collections.deque"]
    )
)

instantiable_type_mapping = {
    AbstractSet: set,
    DefaultDict: defaultdict,
    Deque: deque,
    Dict: dict,
    FrozenSet: frozenset,
    List: list,
    Mapping: dict,
    MutableMapping: dict,
    MutableSequence: list,
    MutableSet: set,
    Sequence: list,
    Set: set,
    Tuple: tuple,
    abc.Mapping: dict,
    abc.MutableMapping: dict,
    abc.MutableSequence: list,
    abc.MutableSet: set,
    abc.Sequence: list,
    abc.Set: set,
    defaultdict: defaultdict,
    deque: deque,
    dict: dict,
    frozenset: frozenset,
    list: list,
    set: set,
    tuple: tuple,
}

safe_generic_origin_map = {
    set: AbstractSet,
    defaultdict: DefaultDict,
    deque: Deque,
    dict: Dict,
    frozenset: FrozenSet,
    list: List,
    tuple: Tuple,
    abc.Mapping: Mapping,
    abc.MutableMapping: MutableMapping,
    abc.MutableSequence: MutableSequence,
    abc.MutableSet: MutableSet,
    abc.Sequence: Sequence,
    abc.Set: AbstractSet,
    abc.Collection: Collection,
    abc.Container: Container,
    abc.ItemsView: ItemsView,
    abc.KeysView: KeysView,
    abc.MappingView: MappingView,
    abc.ValuesView: ValuesView,
    abc.Iterable: Iterable,
    abc.Iterator: Iterator,
    abc.Generator: Generator,
    abc.Reversible: Reversible,
    abc.Coroutine: Coroutine,
    abc.AsyncGenerator: AsyncGenerator,
    abc.AsyncIterable: AsyncIterable,
    abc.AsyncIterator: AsyncIterator,
    abc.Awaitable: Awaitable,
    **{union_t: Union for union_t in UnionTypes},
}
"""A mapping of types to equivalent types that are safe to be used as generics across all Python versions.

This is necessary because occasionally we want to rebuild a generic outer type with different args, and types such as
``collections.abc.Mapping``, are not valid generic types in Python 3.8.
"""

wrapper_type_set = {Annotated, Required, NotRequired}
"""Types that always contain a wrapped type annotation as their first arg."""


def normalize_type_annotation(annotation: Any) -> Any:
    """Normalize a type annotation to a standard form."""
    return instantiable_type_mapping.get(annotation, annotation)


def make_non_optional_union(annotation: UnionT | None) -> UnionT:
    """Make a :data:`Union <typing.Union>` type that excludes ``NoneType``.

    Args:
        annotation: A type annotation.

    Returns:
        The union with all original members, except ``NoneType``.
    """
    args = tuple(tp for tp in get_args(annotation) if tp is not NoneType)
    return cast("UnionT", Union[args])  # pyright: ignore


def unwrap_annotation(annotation: Any) -> tuple[Any, tuple[Any, ...], set[Any]]:
    """Remove "wrapper" annotation types, such as ``Annotated``, ``Required``, and ``NotRequired``.

    Note:
        ``annotation`` should have been retrieved from :func:`get_type_hints()` with ``include_extras=True``. This
        ensures that any nested ``Annotated`` types are flattened according to the PEP 593 specification.

    Args:
        annotation: A type annotation.

    Returns:
        A tuple of the unwrapped annotation and any ``Annotated`` metadata, and a set of any wrapper types encountered.
    """
    origin = get_origin(annotation)
    wrappers = set()
    metadata = []
    while origin in wrapper_type_set:
        wrappers.add(origin)
        annotation, *meta = get_args(annotation)
        metadata.extend(meta)
        origin = get_origin(annotation)
    return annotation, tuple(metadata), wrappers


def unwrap_new_type(new_type: Any) -> Any:
    """Unwrap a (nested) ``typing.NewType``"""
    inner = new_type
    while isinstance(inner, NewType):
        inner = inner.__supertype__
    return inner


def get_origin_or_inner_type(annotation: Any) -> Any:
    """Get origin or unwrap it. Returns None for non-generic types.

    Args:
        annotation: A type annotation.

    Returns:
        Any type.
    """
    origin = get_origin(annotation)
    if origin in wrapper_type_set:
        inner, _, _ = unwrap_annotation(annotation)
        # we need to recursively call here 'get_origin_or_inner_type' because we might be dealing
        # with a generic type alias e.g. Annotated[dict[str, list[int]]
        origin = get_origin_or_inner_type(inner)
    return instantiable_type_mapping.get(origin, origin)


def get_safe_generic_origin(origin_type: Any, annotation: Any) -> Any:
    """Get a type that is safe to use as a generic type across all supported Python versions.

    If a builtin collection type is annotated without generic args, e.g, ``a: dict``, then the origin type will be
    ``None``. In this case, we can use the annotation to determine the correct generic type, if one exists.

    Args:
        origin_type: A type - would be the return value of :func:`get_origin()`.
        annotation: Type annotation associated with the origin type. Should be unwrapped from any wrapper types, such
            as ``Annotated``.

    Returns:
        The ``typing`` module equivalent of the given type, if it exists. Otherwise, the original type is returned.
    """
    if origin_type is None:
        return safe_generic_origin_map.get(annotation)
    return safe_generic_origin_map.get(origin_type, origin_type)


def get_instantiable_origin(origin_type: Any, annotation: Any) -> Any:
    """Get a type that is safe to instantiate for the given origin type.

    If a builtin collection type is annotated without generic args, e.g, ``a: dict``, then the origin type will be
    ``None``. In this case, we can use the annotation to determine the correct instantiable type, if one exists.

    Args:
        origin_type: A type - would be the return value of :func:`get_origin()`.
        annotation: Type annotation associated with the origin type. Should be unwrapped from any wrapper types, such
            as ``Annotated``.

    Returns:
        A builtin type that is safe to instantiate for the given origin type.
    """
    if origin_type is None:
        return instantiable_type_mapping.get(annotation)
    return instantiable_type_mapping.get(origin_type, origin_type)


def get_type_hints_with_generics_resolved(
    annotation: Any,
    globalns: dict[str, Any] | None = None,
    localns: dict[str, Any] | None = None,
    include_extras: bool = False,
    type_hints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Get the type hints for the given object after resolving the generic types as much as possible.

    Args:
        annotation: A type annotation.
        globalns: The global namespace.
        localns: The local namespace.
        include_extras: A flag indicating whether to include the ``Annotated[T, ...]`` or not.
        type_hints: Already resolved type hints
    """
    origin = get_origin(annotation)

    if origin is None:
        # Implies the generic types have not been specified in the annotation
        if type_hints is None:  # pragma: no cover
            type_hints = get_type_hints(annotation, globalns=globalns, localns=localns, include_extras=include_extras)
        typevar_map = {p: p for p in annotation.__parameters__}
    else:
        if type_hints is None:  # pragma: no cover
            type_hints = get_type_hints(origin, globalns=globalns, localns=localns, include_extras=include_extras)
        # the __parameters__ is only available on the origin itself and not the annotation
        typevar_map = dict(zip(origin.__parameters__, get_args(annotation)))

    return {n: _substitute_typevars(type_, typevar_map) for n, type_ in type_hints.items()}


def expand_type_var_in_type_hint(type_hint: dict[str, Any], namespace: dict[str, Any] | None) -> dict[str, Any]:
    """Expand TypeVar for any parameters in type_hint

    Args:
        type_hint: mapping of parameter to type obtained from calling `get_type_hints` or `get_fn_type_hints`
        namespace: mapping of TypeVar to concrete type

    Returns:
        type_hint with any TypeVar parameter expanded
    """
    if namespace:
        return {name: _substitute_typevars(hint, namespace) for name, hint in type_hint.items()}
    return type_hint


def _substitute_typevars(obj: Any, typevar_map: Mapping[Any, Any]) -> Any:
    if params := getattr(obj, "__parameters__", None):
        args = tuple(_substitute_typevars(typevar_map.get(p, p), typevar_map) for p in params)
        return obj[args]

    if isinstance(obj, TypeVar):
        # If there's a mapped type for the TypeVar already, then it should be returned instead
        # of considering __constraints__ or __bound__. For a generic `Foo[T]`, if Foo[int] is given
        # then int should be returned and if `Foo` is given then the __bounds__ and __constraints__
        # should be considered.
        if (type_ := typevar_map.get(obj, None)) is not None and not isinstance(type_, TypeVar):
            return type_

        if obj.__bound__ is not None:
            return obj.__bound__

        if obj.__constraints__:
            return Union[obj.__constraints__]  # pyright: ignore

    return obj
