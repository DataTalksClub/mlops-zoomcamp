from __future__ import annotations

from dataclasses import MISSING, fields, is_dataclass
from typing import Any, Generic

from typing_extensions import TypeGuard, get_type_hints

from polyfactory.factories.base import BaseFactory, T
from polyfactory.field_meta import FieldMeta, Null


class DataclassFactory(Generic[T], BaseFactory[T]):
    """Dataclass base factory"""

    __is_base_factory__ = True

    @classmethod
    def is_supported_type(cls, value: Any) -> TypeGuard[type[T]]:
        """Determine whether the given value is supported by the factory.

        :param value: An arbitrary value.
        :returns: A typeguard
        """
        return bool(is_dataclass(value))

    @classmethod
    def get_model_fields(cls) -> list["FieldMeta"]:
        """Retrieve a list of fields from the factory's model.


        :returns: A list of field MetaData instances.

        """
        fields_meta: list["FieldMeta"] = []

        model_type_hints = get_type_hints(cls.__model__, include_extras=True)

        for field in fields(cls.__model__):  # type: ignore[arg-type]
            if not field.init:
                continue

            if field.default_factory and field.default_factory is not MISSING:
                default_value = field.default_factory()
            elif field.default is not MISSING:
                default_value = field.default
            else:
                default_value = Null

            fields_meta.append(
                FieldMeta.from_type(
                    annotation=model_type_hints[field.name],
                    name=field.name,
                    default=default_value,
                    random=cls.__random__,
                ),
            )

        return fields_meta
