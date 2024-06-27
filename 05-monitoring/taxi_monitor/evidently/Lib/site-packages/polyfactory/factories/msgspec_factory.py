from __future__ import annotations

from inspect import isclass
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

from typing_extensions import get_type_hints

from polyfactory.exceptions import MissingDependencyException
from polyfactory.factories.base import BaseFactory
from polyfactory.field_meta import FieldMeta, Null
from polyfactory.value_generators.constrained_numbers import handle_constrained_int
from polyfactory.value_generators.primitives import create_random_bytes

if TYPE_CHECKING:
    from typing_extensions import TypeGuard

try:
    import msgspec
    from msgspec.structs import fields
except ImportError as e:
    msg = "msgspec is not installed"
    raise MissingDependencyException(msg) from e

T = TypeVar("T", bound=msgspec.Struct)


class MsgspecFactory(Generic[T], BaseFactory[T]):
    """Base factory for msgspec Structs."""

    __is_base_factory__ = True

    @classmethod
    def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
        def get_msgpack_ext() -> msgspec.msgpack.Ext:
            code = handle_constrained_int(cls.__random__, ge=-128, le=127)
            data = create_random_bytes(cls.__random__)
            return msgspec.msgpack.Ext(code, data)

        msgspec_provider_map = {msgspec.UnsetType: lambda: msgspec.UNSET, msgspec.msgpack.Ext: get_msgpack_ext}

        provider_map = super().get_provider_map()
        provider_map.update(msgspec_provider_map)

        return provider_map

    @classmethod
    def is_supported_type(cls, value: Any) -> TypeGuard[type[T]]:
        return isclass(value) and hasattr(value, "__struct_fields__")

    @classmethod
    def get_model_fields(cls) -> list[FieldMeta]:
        fields_meta: list[FieldMeta] = []

        type_hints = get_type_hints(cls.__model__, include_extras=True)
        for field in fields(cls.__model__):
            annotation = type_hints[field.name]
            if field.default is not msgspec.NODEFAULT:
                default_value = field.default
            elif field.default_factory is not msgspec.NODEFAULT:
                default_value = field.default_factory()
            else:
                default_value = Null

            fields_meta.append(
                FieldMeta.from_type(
                    annotation=annotation,
                    name=field.name,
                    default=default_value,
                    random=cls.__random__,
                ),
            )
        return fields_meta
