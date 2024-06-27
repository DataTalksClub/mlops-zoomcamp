from __future__ import annotations

from dataclasses import MISSING, fields, replace
from typing import TYPE_CHECKING, Generic, TypeVar

from litestar.dto.base_dto import AbstractDTO
from litestar.dto.data_structures import DTOFieldDefinition
from litestar.dto.field import extract_dto_field
from litestar.params import DependencyKwarg, KwargDefinition
from litestar.types.empty import Empty

if TYPE_CHECKING:
    from typing import Collection, Generator

    from litestar.types.protocols import DataclassProtocol
    from litestar.typing import FieldDefinition


__all__ = ("DataclassDTO", "T")

T = TypeVar("T", bound="DataclassProtocol | Collection[DataclassProtocol]")
AnyDataclass = TypeVar("AnyDataclass", bound="DataclassProtocol")


class DataclassDTO(AbstractDTO[T], Generic[T]):
    """Support for domain modelling with dataclasses."""

    @classmethod
    def generate_field_definitions(
        cls, model_type: type[DataclassProtocol]
    ) -> Generator[DTOFieldDefinition, None, None]:
        dc_fields = {f.name: f for f in fields(model_type)}
        for key, field_definition in cls.get_model_type_hints(model_type).items():
            if not (dc_field := dc_fields.get(key)):
                continue

            default = dc_field.default if dc_field.default is not MISSING else Empty
            default_factory = dc_field.default_factory if dc_field.default_factory is not MISSING else None
            field_defintion = replace(
                DTOFieldDefinition.from_field_definition(
                    field_definition=field_definition,
                    default_factory=default_factory,
                    dto_field=extract_dto_field(field_definition, dc_field.metadata),
                    model_name=model_type.__name__,
                ),
                name=key,
                default=default,
            )

            yield (
                replace(field_defintion, default=Empty, kwarg_definition=default)
                if isinstance(default, (KwargDefinition, DependencyKwarg))
                else field_defintion
            )

    @classmethod
    def detect_nested_field(cls, field_definition: FieldDefinition) -> bool:
        return hasattr(field_definition.annotation, "__dataclass_fields__")
