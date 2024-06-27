from __future__ import annotations

from datetime import date, datetime, timezone
from re import Pattern
from typing import TYPE_CHECKING

from litestar.openapi.spec.enums import OpenAPIFormat, OpenAPIType
from litestar.openapi.spec.schema import Schema

if TYPE_CHECKING:
    from decimal import Decimal

    from litestar.params import KwargDefinition

__all__ = (
    "create_date_constrained_field_schema",
    "create_numerical_constrained_field_schema",
    "create_string_constrained_field_schema",
)


def create_numerical_constrained_field_schema(
    field_type: type[int] | type[float] | type[Decimal],
    kwarg_definition: KwargDefinition,
) -> Schema:
    """Create Schema from Constrained Int/Float/Decimal field."""
    schema = Schema(type=OpenAPIType.INTEGER if issubclass(field_type, int) else OpenAPIType.NUMBER)
    if kwarg_definition.le is not None:
        schema.maximum = float(kwarg_definition.le)
    if kwarg_definition.lt is not None:
        schema.exclusive_maximum = float(kwarg_definition.lt)
    if kwarg_definition.ge is not None:
        schema.minimum = float(kwarg_definition.ge)
    if kwarg_definition.gt is not None:
        schema.exclusive_minimum = float(kwarg_definition.gt)
    if kwarg_definition.multiple_of is not None:
        schema.multiple_of = float(kwarg_definition.multiple_of)
    return schema


def create_date_constrained_field_schema(
    field_type: type[date] | type[datetime],
    kwarg_definition: KwargDefinition,
) -> Schema:
    """Create Schema from Constrained Date Field."""
    schema = Schema(
        type=OpenAPIType.STRING, format=OpenAPIFormat.DATE if issubclass(field_type, date) else OpenAPIFormat.DATE_TIME
    )
    for kwarg_definition_attr, schema_attr in [
        ("le", "maximum"),
        ("lt", "exclusive_maximum"),
        ("ge", "minimum"),
        ("gt", "exclusive_minimum"),
    ]:
        if attr := getattr(kwarg_definition, kwarg_definition_attr):
            setattr(
                schema,
                schema_attr,
                datetime.combine(
                    datetime.fromtimestamp(attr, tz=timezone.utc) if isinstance(attr, (float, int)) else attr,
                    datetime.min.time(),
                    tzinfo=timezone.utc,
                ).timestamp(),
            )

    return schema


def create_string_constrained_field_schema(
    field_type: type[str] | type[bytes],
    kwarg_definition: KwargDefinition,
) -> Schema:
    """Create Schema from Constrained Str/Bytes field."""
    schema = Schema(type=OpenAPIType.STRING)
    if issubclass(field_type, bytes):
        schema.content_encoding = "utf-8"
    if kwarg_definition.min_length:
        schema.min_length = kwarg_definition.min_length
    if kwarg_definition.max_length:
        schema.max_length = kwarg_definition.max_length
    if kwarg_definition.pattern:
        schema.pattern = (
            kwarg_definition.pattern.pattern  # type: ignore[attr-defined]
            if isinstance(kwarg_definition.pattern, Pattern)  # type: ignore[unreachable]
            else kwarg_definition.pattern
        )
    if kwarg_definition.lower_case:
        schema.description = "must be in lower case"
    if kwarg_definition.upper_case:
        schema.description = "must be in upper case"
    return schema
