from __future__ import annotations

from asyncio import iscoroutinefunction
from collections import defaultdict, deque
from collections.abc import Iterable as CollectionsIterable
from dataclasses import is_dataclass
from inspect import isasyncgenfunction, isclass, isgeneratorfunction
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    ClassVar,
    DefaultDict,
    Deque,
    Dict,
    FrozenSet,
    Generic,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeVar,
)

from typing_extensions import (
    ParamSpec,
    TypeGuard,
    _AnnotatedAlias,
    get_args,
)

from litestar.constants import UNDEFINED_SENTINELS
from litestar.types.builtin_types import NoneType, UnionTypes
from litestar.utils.deprecation import warn_deprecation
from litestar.utils.helpers import unwrap_partial
from litestar.utils.typing import get_origin_or_inner_type

if TYPE_CHECKING:
    from litestar.types.callable_types import AnyGenerator
    from litestar.types.protocols import DataclassProtocol


__all__ = (
    "is_annotated_type",
    "is_any",
    "is_async_callable",
    "is_class_and_subclass",
    "is_class_var",
    "is_dataclass_class",
    "is_dataclass_instance",
    "is_generic",
    "is_mapping",
    "is_non_string_iterable",
    "is_non_string_sequence",
    "is_optional_union",
    "is_undefined_sentinel",
    "is_union",
)

P = ParamSpec("P")
T = TypeVar("T")


def is_async_callable(value: Callable[P, T]) -> TypeGuard[Callable[P, Awaitable[T]]]:
    """Extend :func:`asyncio.iscoroutinefunction` to additionally detect async :func:`functools.partial` objects and
    class instances with ``async def __call__()`` defined.

    Args:
        value: Any

    Returns:
        Bool determining if type of ``value`` is an awaitable.
    """
    value = unwrap_partial(value)

    return iscoroutinefunction(value) or (
        callable(value) and iscoroutinefunction(value.__call__)  # type: ignore[operator]
    )


def is_dataclass_instance(obj: Any) -> TypeGuard[DataclassProtocol]:
    """Check if an object is a dataclass instance.

    Args:
        obj: An object to check.

    Returns:
        True if the object is a dataclass instance.
    """
    return hasattr(type(obj), "__dataclass_fields__")


def is_dataclass_class(annotation: Any) -> TypeGuard[type[DataclassProtocol]]:
    """Wrap :func:`is_dataclass <dataclasses.is_dataclass>` in a :data:`typing.TypeGuard`.

    Args:
        annotation: tested to determine if instance or type of :class:`dataclasses.dataclass`.

    Returns:
        ``True`` if instance or type of ``dataclass``.
    """
    try:
        origin = get_origin_or_inner_type(annotation)
        annotation = origin or annotation

        return isclass(annotation) and is_dataclass(annotation)
    except TypeError:  # pragma: no cover
        return False


def is_class_and_subclass(annotation: Any, type_or_type_tuple: type[T] | tuple[type[T], ...]) -> TypeGuard[type[T]]:
    """Return ``True`` if ``value`` is a ``class`` and is a subtype of ``t_type``.

    See https://github.com/litestar-org/litestar/issues/367

    Args:
        annotation: The value to check if is class and subclass of ``t_type``.
        type_or_type_tuple: Type used for :func:`issubclass` check of ``value``

    Returns:
        bool
    """
    origin = get_origin_or_inner_type(annotation)
    if not origin and not isclass(annotation):
        return False
    try:
        return issubclass(origin or annotation, type_or_type_tuple)
    except TypeError:  # pragma: no cover
        return False


def is_generic(annotation: Any) -> bool:
    """Given a type annotation determine if the annotation is a generic class.

    Args:
    annotation: A type.

    Returns:
        True if the annotation is a subclass of :data:`Generic <typing.Generic>` otherwise ``False``.
    """
    return is_class_and_subclass(annotation, Generic)  # type: ignore[arg-type]


def is_mapping(annotation: Any) -> TypeGuard[Mapping[Any, Any]]:
    """Given a type annotation determine if the annotation is a mapping type.

    Args:
    annotation: A type.

    Returns:
        A typeguard determining whether the type can be cast as :class:`Mapping <typing.Mapping>`.
    """
    _type = get_origin_or_inner_type(annotation) or annotation
    return isclass(_type) and issubclass(_type, (dict, defaultdict, DefaultDict, Mapping))


def is_non_string_iterable(annotation: Any) -> TypeGuard[Iterable[Any]]:
    """Given a type annotation determine if the annotation is an iterable.

    Args:
    annotation: A type.

    Returns:
        A typeguard determining whether the type can be cast as :class:`Iterable <typing.Iterable>` that is not a string.
    """
    origin = get_origin_or_inner_type(annotation)
    if not origin and not isclass(annotation):
        return False
    try:
        return not issubclass(origin or annotation, (str, bytes)) and (
            issubclass(origin or annotation, (Iterable, CollectionsIterable, Dict, dict, Mapping))
            or is_non_string_sequence(annotation)
        )
    except TypeError:  # pragma: no cover
        return False


def is_non_string_sequence(annotation: Any) -> TypeGuard[Sequence[Any]]:
    """Given a type annotation determine if the annotation is a sequence.

    Args:
    annotation: A type.

    Returns:
        A typeguard determining whether the type can be cast as :class`Sequence <typing.Sequence>` that is not a string.
    """
    origin = get_origin_or_inner_type(annotation)
    if not origin and not isclass(annotation):
        return False
    try:
        return not issubclass(origin or annotation, (str, bytes)) and issubclass(
            origin or annotation,
            (  # type: ignore[arg-type]
                Tuple,
                List,
                Set,
                FrozenSet,
                Deque,
                Sequence,
                list,
                tuple,
                deque,
                set,
                frozenset,
            ),
        )
    except TypeError:  # pragma: no cover
        return False


def is_any(annotation: Any) -> TypeGuard[Any]:
    """Given a type annotation determine if the annotation is Any.

    Args:
        annotation: A type.

    Returns:
        A typeguard determining whether the type is :data:`Any <typing.Any>`.
    """
    return (
        annotation is Any
        or getattr(annotation, "_name", "") == "typing.Any"
        or (get_origin_or_inner_type(annotation) in UnionTypes and Any in get_args(annotation))
    )


def is_union(annotation: Any) -> bool:
    """Given a type annotation determine if the annotation infers an optional union.

    Args:
        annotation: A type.

    Returns:
        A boolean determining whether the type is :data:`Union typing.Union>`.
    """
    return get_origin_or_inner_type(annotation) in UnionTypes


def is_optional_union(annotation: Any) -> TypeGuard[Any | None]:
    """Given a type annotation determine if the annotation infers an optional union.

    Args:
        annotation: A type.

    Returns:
        A typeguard determining whether the type is :data:`Union typing.Union>` with a
            None value or :data:`Optional <typing.Optional>` which is equivalent.
    """
    origin = get_origin_or_inner_type(annotation)
    return origin is Optional or (
        get_origin_or_inner_type(annotation) in UnionTypes and NoneType in get_args(annotation)
    )


def is_class_var(annotation: Any) -> bool:
    """Check if the given annotation is a ClassVar.

    Args:
        annotation: A type annotation

    Returns:
        A boolean.
    """
    annotation = get_origin_or_inner_type(annotation) or annotation
    return annotation is ClassVar


def _is_sync_or_async_generator(obj: Any) -> TypeGuard[AnyGenerator]:
    """Check if the given annotation is a sync or async generator.

    Args:
        obj: type to be tested for sync or async generator.

    Returns:
        A boolean.
    """
    return isgeneratorfunction(obj) or isasyncgenfunction(obj)


def is_annotated_type(annotation: Any) -> bool:
    """Check if the given annotation is an Annotated.

    Args:
        annotation: A type annotation

    Returns:
        A boolean.
    """
    return isinstance(annotation, _AnnotatedAlias) and getattr(annotation, "__args__", None) is not None


def is_undefined_sentinel(value: Any) -> bool:
    """Check if the given value is the undefined sentinel.

    Args:
        value: A value to be tested for undefined sentinel.

    Returns:
        A boolean.
    """
    return any(v is value for v in UNDEFINED_SENTINELS)


_deprecated_names = {"is_sync_or_async_generator": _is_sync_or_async_generator}


def __getattr__(name: str) -> Any:
    if name in _deprecated_names:
        warn_deprecation(
            deprecated_name=f"litestar.utils.scope.{name}",
            version="2.4",
            kind="import",
            removal_in="3.0",
            info=f"'litestar.utils.predicates.{name}' is deprecated.",
        )
        return globals()["_deprecated_names"][name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")  # pragma: no cover
