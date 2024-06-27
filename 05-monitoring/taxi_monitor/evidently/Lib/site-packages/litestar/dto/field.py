"""DTO domain types."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from litestar.exceptions import ImproperlyConfiguredException

if TYPE_CHECKING:
    from typing import Any, Literal, Mapping

    from litestar.typing import FieldDefinition

__all__ = (
    "DTO_FIELD_META_KEY",
    "DTOField",
    "Mark",
    "dto_field",
    "extract_dto_field",
)

DTO_FIELD_META_KEY = "__dto__"


class Mark(str, Enum):
    """For marking field definitions on domain models."""

    READ_ONLY = "read-only"
    """To mark a field that can be read, but not updated by clients."""
    WRITE_ONLY = "write-only"
    """To mark a field that can be written to, but not read by clients."""
    PRIVATE = "private"
    """To mark a field that can neither be read or updated by clients."""


@dataclass
class DTOField:
    """For configuring DTO behavior on model fields."""

    mark: Mark | Literal["read-only", "write-only", "private"] | None = None
    """Mark the field as read-only, or private."""


def dto_field(mark: Literal["read-only", "write-only", "private"] | Mark) -> dict[str, DTOField]:
    """Create a field metadata mapping.

    Args:
        mark: A DTO mark for the field, e.g., "read-only".

    Returns:
        A dict for setting as field metadata, such as the dataclass "metadata" field key, or the SQLAlchemy "info"
        field.

        Marking a field automates its inclusion/exclusion from DTO field definitions, depending on the DTO's purpose.
    """
    return {DTO_FIELD_META_KEY: DTOField(mark=Mark(mark))}


def extract_dto_field(field_definition: FieldDefinition, field_info_mapping: Mapping[str, Any]) -> DTOField:
    """Extract ``DTOField`` instance for a model field.

    Supports ``DTOField`` to bet set via ``Annotated`` or via a field info/metadata mapping.

    E.g., ``Annotated[str, DTOField(mark="read-only")]`` or ``info=dto_field(mark="read-only")``.

    If a value is found in ``field_info_mapping``, it is prioritized over the field definition's metadata.

    Args:
        field_definition: A field definition.
        field_info_mapping: A field metadata/info attribute mapping, e.g., SQLAlchemy's ``info`` attribute,
          or dataclasses ``metadata`` attribute.

    Returns:
        DTO field info, if any.
    """
    if inst := field_info_mapping.get(DTO_FIELD_META_KEY):
        if not isinstance(inst, DTOField):
            raise ImproperlyConfiguredException(f"DTO field info must be an instance of DTOField, got '{inst}'")
        return inst

    return next((f for f in field_definition.metadata if isinstance(f, DTOField)), DTOField())
