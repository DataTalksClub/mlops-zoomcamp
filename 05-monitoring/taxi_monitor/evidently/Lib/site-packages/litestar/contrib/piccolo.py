from __future__ import annotations

import warnings
from dataclasses import replace
from decimal import Decimal
from typing import Any, Generator, Generic, List, Optional, TypeVar

from msgspec import Meta
from typing_extensions import Annotated

from litestar.dto import AbstractDTO, DTOField, Mark
from litestar.dto.data_structures import DTOFieldDefinition
from litestar.exceptions import LitestarWarning, MissingDependencyException
from litestar.types import Empty
from litestar.typing import FieldDefinition
from litestar.utils import warn_deprecation

try:
    from piccolo.columns import Column, column_types
    from piccolo.table import Table
except ImportError as e:
    raise MissingDependencyException("piccolo") from e


T = TypeVar("T", bound=Table)

__all__ = ("PiccoloDTO",)


def __getattr__(name: str) -> Any:
    warn_deprecation(
        deprecated_name=f"litestar.contrib.piccolo.{name}",
        version="2.3.2",
        kind="import",
        removal_in="3.0.0",
        info="importing from 'litestar.contrib.piccolo' is deprecated and will be removed in 3.0, please import from 'litestar_piccolo' package directly instead",
    )
    return getattr(name, name)


def _parse_piccolo_type(column: Column, extra: dict[str, Any]) -> FieldDefinition:
    is_optional = not column._meta.required

    if isinstance(column, (column_types.Decimal, column_types.Numeric)):
        column_type: Any = Decimal
        meta = Meta(extra=extra)
    elif isinstance(column, (column_types.Email, column_types.Varchar)):
        column_type = str
        if is_optional:
            meta = Meta(extra=extra)
            warnings.warn(
                f"Dropping max_length constraint for column {column!r} because the " "column is optional",
                category=LitestarWarning,
                stacklevel=2,
            )
        else:
            meta = Meta(max_length=column.length, extra=extra)
    elif isinstance(column, column_types.Array):
        column_type = List[column.base_column.value_type]  # type: ignore[name-defined]
        meta = Meta(extra=extra)
    elif isinstance(column, (column_types.JSON, column_types.JSONB)):
        column_type = str
        meta = Meta(extra={**extra, "format": "json"})
    elif isinstance(column, column_types.Text):
        column_type = str
        meta = Meta(extra={**extra, "format": "text-area"})
    else:
        column_type = column.value_type
        meta = Meta(extra=extra)

    if is_optional:
        column_type = Optional[column_type]

    return FieldDefinition.from_annotation(Annotated[column_type, meta])


def _create_column_extra(column: Column) -> dict[str, Any]:
    extra: dict[str, Any] = {}

    if column._meta.help_text:
        extra["description"] = column._meta.help_text

    if column._meta.get_choices_dict():
        extra["enum"] = column._meta.get_choices_dict()

    return extra


class PiccoloDTO(AbstractDTO[T], Generic[T]):
    @classmethod
    def generate_field_definitions(cls, model_type: type[Table]) -> Generator[DTOFieldDefinition, None, None]:
        for column in model_type._meta.columns:
            mark = Mark.WRITE_ONLY if column._meta.secret else Mark.READ_ONLY if column._meta.primary_key else None
            yield replace(
                DTOFieldDefinition.from_field_definition(
                    field_definition=_parse_piccolo_type(column, _create_column_extra(column)),
                    dto_field=DTOField(mark=mark),
                    model_name=model_type.__name__,
                    default_factory=None,
                ),
                default=Empty if column._meta.required else None,
                name=column._meta.name,
            )

    @classmethod
    def detect_nested_field(cls, field_definition: FieldDefinition) -> bool:
        return field_definition.is_subclass_of(Table)
