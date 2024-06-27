from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, Mapping

from typing_extensions import TypeAliasType, get_args, get_origin

from polyfactory.constants import TYPE_MAPPING
from polyfactory.utils.predicates import is_annotated, is_new_type, is_optional, is_safe_subclass, is_union
from polyfactory.utils.types import NoneType

if TYPE_CHECKING:
    from random import Random
    from typing import Sequence


def unwrap_new_type(annotation: Any) -> Any:
    """Return base type if given annotation is a type derived with NewType, otherwise annotation.

    :param annotation: A type annotation, possibly one created using 'types.NewType'

    :returns: The unwrapped annotation.
    """
    while is_new_type(annotation):
        annotation = annotation.__supertype__

    return annotation


def unwrap_union(annotation: Any, random: Random) -> Any:
    """Unwraps union types - recursively.

    :param annotation: A type annotation, possibly a type union.
    :param random: An instance of random.Random.
    :returns: A type annotation
    """
    while is_union(annotation):
        args = list(get_args(annotation))
        annotation = random.choice(args)
    return annotation


def unwrap_optional(annotation: Any) -> Any:
    """Unwraps optional union types - recursively.

    :param annotation: A type annotation, possibly an optional union.

    :returns: A type annotation
    """
    while is_optional(annotation):
        annotation = next(arg for arg in get_args(annotation) if arg not in (NoneType, None))
    return annotation


def unwrap_annotation(annotation: Any, random: Random) -> Any:
    """Unwraps an annotation.

    :param annotation: A type annotation.
    :param random: An instance of random.Random.

    :returns: The unwrapped annotation.

    """
    while (
        is_optional(annotation)
        or is_union(annotation)
        or is_new_type(annotation)
        or is_annotated(annotation)
        or isinstance(annotation, TypeAliasType)
    ):
        if is_new_type(annotation):
            annotation = unwrap_new_type(annotation)
        elif is_optional(annotation):
            annotation = unwrap_optional(annotation)
        elif is_annotated(annotation):
            annotation = unwrap_annotated(annotation, random=random)[0]
        elif isinstance(annotation, TypeAliasType):
            annotation = annotation.__value__
        else:
            annotation = unwrap_union(annotation, random=random)

    return annotation


def flatten_annotation(annotation: Any) -> list[Any]:
    """Flattens an annotation.

    :param annotation: A type annotation.

    :returns: The flattened annotations.
    """
    flat = []
    if is_new_type(annotation):
        flat.extend(flatten_annotation(unwrap_new_type(annotation)))
    elif is_optional(annotation):
        for a in get_args(annotation):
            flat.extend(flatten_annotation(a))
    elif is_annotated(annotation):
        flat.extend(flatten_annotation(get_args(annotation)[0]))
    elif is_union(annotation):
        for a in get_args(annotation):
            flat.extend(flatten_annotation(a))
    else:
        flat.append(annotation)

    return flat


def unwrap_args(annotation: Any, random: Random) -> tuple[Any, ...]:
    """Unwrap the annotation and return any type args.

    :param annotation: A type annotation
    :param random: An instance of random.Random.

    :returns: A tuple of type args.

    """

    return get_args(unwrap_annotation(annotation=annotation, random=random))


def unwrap_annotated(annotation: Any, random: Random) -> tuple[Any, list[Any]]:
    """Unwrap an annotated type and return a tuple of type args and optional metadata.

    :param annotation: An annotated type annotation
    :param random: An instance of random.Random.

    :returns: A tuple of type args.

    """
    args = [arg for arg in get_args(annotation) if arg is not None]
    return unwrap_annotation(args[0], random=random), args[1:]


def normalize_annotation(annotation: Any, random: Random) -> Any:
    """Normalize an annotation.

    :param annotation: A type annotation.

    :returns: A normalized type annotation.

    """
    if is_new_type(annotation):
        annotation = unwrap_new_type(annotation)

    if is_annotated(annotation):
        annotation = unwrap_annotated(annotation, random=random)[0]

    # we have to maintain compatibility with the older non-subscriptable typings.
    if sys.version_info <= (3, 9):  # pragma: no cover
        return annotation

    origin = get_origin(annotation) or annotation

    if origin in TYPE_MAPPING:
        origin = TYPE_MAPPING[origin]

    if args := get_args(annotation):
        args = tuple(normalize_annotation(arg, random=random) for arg in args)
        return origin[args] if origin is not type else annotation

    return origin


def get_annotation_metadata(annotation: Any) -> Sequence[Any]:
    """Get the metadata in the annotation.

    :param annotation: A type annotation.

    :returns: The metadata.
    """

    return get_args(annotation)[1:]


def get_collection_type(annotation: Any) -> type[list | tuple | set | frozenset | dict]:
    """Get the collection type from the annotation.

    :param annotation: A type annotation.

    :returns: The collection type.
    """

    if is_safe_subclass(annotation, list):
        return list
    if is_safe_subclass(annotation, Mapping):
        return dict
    if is_safe_subclass(annotation, tuple):
        return tuple
    if is_safe_subclass(annotation, set):
        return set
    if is_safe_subclass(annotation, frozenset):
        return frozenset

    msg = f"Unknown collection type - {annotation}"
    raise ValueError(msg)
