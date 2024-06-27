from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from litestar.dto.data_structures import DTOFieldDefinition

if TYPE_CHECKING:
    from typing import Any

    from typing_extensions import Self

    from litestar.typing import FieldDefinition


@dataclass(frozen=True)
class NestedFieldInfo:
    """Type for representing fields and model type of nested model type."""

    __slots__ = ("model", "field_definitions")

    model: type[Any]
    field_definitions: tuple[TransferDTOFieldDefinition, ...]


@dataclass(frozen=True)
class TransferType:
    """Type for representing model types for data transfer."""

    __slots__ = ("field_definition",)

    field_definition: FieldDefinition


@dataclass(frozen=True)
class SimpleType(TransferType):
    """Represents indivisible, non-composite types."""

    __slots__ = ("nested_field_info",)

    nested_field_info: NestedFieldInfo | None
    """If the type is a 'nested' type, this is the model generated for transfer to/from it."""

    @property
    def has_nested(self) -> bool:
        return self.nested_field_info is not None


@dataclass(frozen=True)
class CompositeType(TransferType):
    """A type that is made up of other types."""

    __slots__ = ("has_nested",)

    has_nested: bool
    """Whether the type represents nested model types within itself."""


@dataclass(frozen=True)
class UnionType(CompositeType):
    """Type for representing union types for data transfer."""

    __slots__ = ("inner_types",)

    inner_types: tuple[CompositeType | SimpleType, ...]


@dataclass(frozen=True)
class CollectionType(CompositeType):
    """Type for representing collection types for data transfer."""

    __slots__ = ("inner_type",)

    inner_type: CompositeType | SimpleType


@dataclass(frozen=True)
class TupleType(CompositeType):
    """Type for representing tuples for data transfer."""

    __slots__ = ("inner_types",)

    inner_types: tuple[CompositeType | SimpleType, ...]


@dataclass(frozen=True)
class MappingType(CompositeType):
    """Type for representing mappings for data transfer."""

    __slots__ = ("key_type", "value_type")

    key_type: CompositeType | SimpleType
    value_type: CompositeType | SimpleType


@dataclass(frozen=True)
class TransferDTOFieldDefinition(DTOFieldDefinition):
    __slots__ = (
        "is_excluded",
        "is_partial",
        "serialization_name",
        "transfer_type",
        "unique_name",
    )

    transfer_type: TransferType
    """Type of the field for transfer."""
    serialization_name: str | None
    """Name of the field as it should appear in serialized form."""
    is_partial: bool
    """Whether the field is optional for transfer."""
    is_excluded: bool
    """Whether the field should be excluded from transfer."""

    @classmethod
    def from_dto_field_definition(
        cls,
        field_definition: DTOFieldDefinition,
        transfer_type: TransferType,
        serialization_name: str | None,
        is_partial: bool,
        is_excluded: bool,
    ) -> Self:
        return cls(
            annotation=field_definition.annotation,
            args=field_definition.args,
            default=field_definition.default,
            default_factory=field_definition.default_factory,
            dto_field=field_definition.dto_field,
            extra=field_definition.extra,
            inner_types=field_definition.inner_types,
            instantiable_origin=field_definition.instantiable_origin,
            is_excluded=is_excluded,
            is_partial=is_partial,
            kwarg_definition=field_definition.kwarg_definition,
            metadata=field_definition.metadata,
            name=field_definition.name,
            origin=field_definition.origin,
            raw=field_definition.raw,
            safe_generic_origin=field_definition.safe_generic_origin,
            serialization_name=serialization_name,
            transfer_type=transfer_type,
            type_wrappers=field_definition.type_wrappers,
            model_name=field_definition.model_name,
        )
