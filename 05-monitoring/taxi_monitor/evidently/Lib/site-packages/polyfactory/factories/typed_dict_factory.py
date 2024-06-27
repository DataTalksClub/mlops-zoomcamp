from __future__ import annotations

from typing import Any, Generic, TypeVar, get_args

from typing_extensions import (  # type: ignore[attr-defined]
    NotRequired,
    Required,
    TypeGuard,
    _TypedDictMeta,  # pyright: ignore[reportGeneralTypeIssues]
    get_origin,
    get_type_hints,
    is_typeddict,
)

from polyfactory.constants import DEFAULT_RANDOM
from polyfactory.factories.base import BaseFactory
from polyfactory.field_meta import FieldMeta, Null

TypedDictT = TypeVar("TypedDictT", bound=_TypedDictMeta)


class TypedDictFactory(Generic[TypedDictT], BaseFactory[TypedDictT]):
    """TypedDict base factory"""

    __is_base_factory__ = True

    @classmethod
    def is_supported_type(cls, value: Any) -> TypeGuard[type[TypedDictT]]:
        """Determine whether the given value is supported by the factory.

        :param value: An arbitrary value.
        :returns: A typeguard
        """
        return is_typeddict(value)

    @classmethod
    def get_model_fields(cls) -> list["FieldMeta"]:
        """Retrieve a list of fields from the factory's model.


        :returns: A list of field MetaData instances.

        """
        model_type_hints = get_type_hints(cls.__model__, include_extras=True)

        field_metas: list[FieldMeta] = []
        for field_name, annotation in model_type_hints.items():
            origin = get_origin(annotation)
            if origin in (Required, NotRequired):
                annotation = get_args(annotation)[0]  # noqa: PLW2901

            field_metas.append(
                FieldMeta.from_type(
                    annotation=annotation,
                    random=DEFAULT_RANDOM,
                    name=field_name,
                    default=getattr(cls.__model__, field_name, Null),
                ),
            )

        return field_metas
