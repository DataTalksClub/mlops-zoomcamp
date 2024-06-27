from __future__ import annotations

from inspect import isclass
from typing import Any, Literal, NewType, Optional, TypeVar, get_args

from typing_extensions import Annotated, NotRequired, ParamSpec, Required, TypeGuard, _AnnotatedAlias, get_origin

from polyfactory.constants import TYPE_MAPPING
from polyfactory.utils.types import UNION_TYPES, NoneType

P = ParamSpec("P")
T = TypeVar("T")


def is_safe_subclass(annotation: Any, class_or_tuple: type[T] | tuple[type[T], ...]) -> "TypeGuard[type[T]]":
    """Determine whether a given annotation is a subclass of a give type

    :param annotation: A type annotation.
    :param class_or_tuple: A potential super class or classes.

    :returns: A typeguard
    """
    origin = get_type_origin(annotation)
    if not origin and not isclass(annotation):
        return False
    try:
        return issubclass(origin or annotation, class_or_tuple)
    except TypeError:  # pragma: no cover
        return False


def is_any(annotation: Any) -> "TypeGuard[Any]":
    """Determine whether a given annotation is 'typing.Any'.

    :param annotation: A type annotation.

    :returns: A typeguard.
    """
    return (
        annotation is Any
        or getattr(annotation, "_name", "") == "typing.Any"
        or (get_origin(annotation) in UNION_TYPES and Any in get_args(annotation))
    )


def is_dict_key_or_value_type(annotation: Any) -> "TypeGuard[Any]":
    """Determine whether a given annotation is a valid dict key or value type:
    ``typing.KT`` or ``typing.VT``.

    :returns: A typeguard.
    """
    return str(annotation) in {"~KT", "~VT"}


def is_union(annotation: Any) -> "TypeGuard[Any]":
    """Determine whether a given annotation is 'typing.Union'.

    :param annotation: A type annotation.

    :returns: A typeguard.
    """
    return get_type_origin(annotation) in UNION_TYPES


def is_optional(annotation: Any) -> "TypeGuard[Any | None]":
    """Determine whether a given annotation is 'typing.Optional'.

    :param annotation: A type annotation.

    :returns: A typeguard.
    """
    origin = get_type_origin(annotation)
    return origin is Optional or (get_origin(annotation) in UNION_TYPES and NoneType in get_args(annotation))


def is_literal(annotation: Any) -> bool:
    """Determine whether a given annotation is 'typing.Literal'.

    :param annotation: A type annotation.

    :returns: A boolean.
    """
    return (
        get_type_origin(annotation) is Literal
        or repr(annotation).startswith("typing.Literal")
        or repr(annotation).startswith("typing_extensions.Literal")
    )


def is_new_type(annotation: Any) -> "TypeGuard[type[NewType]]":
    """Determine whether a given annotation is 'typing.NewType'.

    :param annotation: A type annotation.

    :returns: A typeguard.
    """
    return hasattr(annotation, "__supertype__")


def is_annotated(annotation: Any) -> bool:
    """Determine whether a given annotation is 'typing.Annotated'.

    :param annotation: A type annotation.

    :returns: A boolean.
    """
    return get_origin(annotation) is Annotated or (
        isinstance(annotation, _AnnotatedAlias) and getattr(annotation, "__args__", None) is not None
    )


def is_any_annotated(annotation: Any) -> bool:
    """Determine whether any of the types in the given annotation is
    `typing.Annotated`.

    :param annotation: A type annotation.

    :returns: A boolean
    """

    return any(is_annotated(arg) or hasattr(arg, "__args__") and is_any_annotated(arg) for arg in get_args(annotation))


def get_type_origin(annotation: Any) -> Any:
    """Get the type origin of an annotation - safely.

    :param annotation: A type annotation.

    :returns: A type annotation.
    """
    origin = get_origin(annotation)
    if origin in (Annotated, Required, NotRequired):
        origin = get_args(annotation)[0]
    return mapped_type if (mapped_type := TYPE_MAPPING.get(origin)) else origin
