from __future__ import annotations

from inspect import isclass
from typing import TYPE_CHECKING, Generic, TypeVar

from polyfactory.exceptions import MissingDependencyException
from polyfactory.factories.base import BaseFactory
from polyfactory.field_meta import FieldMeta, Null

if TYPE_CHECKING:
    from typing import Any, TypeGuard


try:
    import attrs
    from attr._make import Factory
    from attrs import AttrsInstance
except ImportError as ex:
    msg = "attrs is not installed"
    raise MissingDependencyException(msg) from ex


T = TypeVar("T", bound=AttrsInstance)


class AttrsFactory(Generic[T], BaseFactory[T]):
    """Base factory for attrs classes."""

    __model__: type[T]

    __is_base_factory__ = True

    @classmethod
    def is_supported_type(cls, value: Any) -> TypeGuard[type[T]]:
        return isclass(value) and hasattr(value, "__attrs_attrs__")

    @classmethod
    def get_model_fields(cls) -> list[FieldMeta]:
        field_metas: list[FieldMeta] = []
        none_type = type(None)

        cls.resolve_types(cls.__model__)
        fields = attrs.fields(cls.__model__)

        for field in fields:
            if not field.init:
                continue

            annotation = none_type if field.type is None else field.type

            default = field.default
            if isinstance(default, Factory):
                # The default value is not currently being used when generating
                # the field values. When that is implemented, this would need
                # to be handled differently since the `default.factory` could
                # take a `self` argument.
                default_value = default.factory
            elif default is None:
                default_value = Null
            else:
                default_value = default

            field_metas.append(
                FieldMeta.from_type(
                    annotation=annotation,
                    name=field.alias,
                    default=default_value,
                    random=cls.__random__,
                ),
            )

        return field_metas

    @classmethod
    def resolve_types(cls, model: type[T], **kwargs: Any) -> None:
        """Resolve any strings and forward annotations in type annotations.

        :param model: The model to resolve the type annotations for.
        :param kwargs: Any parameters that need to be passed to `attrs.resolve_types`.
        """

        attrs.resolve_types(model, **kwargs)
