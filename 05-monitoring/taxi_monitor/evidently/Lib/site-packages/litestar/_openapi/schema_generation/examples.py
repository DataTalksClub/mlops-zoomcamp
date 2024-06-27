from __future__ import annotations

import typing
from dataclasses import replace
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Any

import msgspec
from polyfactory.exceptions import ParameterException
from polyfactory.factories import DataclassFactory
from polyfactory.field_meta import FieldMeta, Null
from polyfactory.utils.helpers import unwrap_annotation
from polyfactory.utils.predicates import is_union
from typing_extensions import get_args

from litestar.contrib.pydantic.utils import is_pydantic_model_instance
from litestar.openapi.spec import Example
from litestar.types import Empty

if TYPE_CHECKING:
    from litestar.typing import FieldDefinition


class ExampleFactory(DataclassFactory[Example]):
    __model__ = Example
    __random_seed__ = 10


def _normalize_example_value(value: Any) -> Any:
    """Normalize the example value to make it look a bit prettier."""
    # if UnsetType is part of the union, then it might get chosen as the value
    # but that will not be properly serialized by msgspec unless it is for a field
    # in a msgspec Struct
    if is_union(value):
        args = list(get_args(value))
        try:
            args.remove(msgspec.UnsetType)
            value = typing.Union[tuple(args)]  # pyright: ignore
        except ValueError:
            # UnsetType not part of the Union
            pass

    value = unwrap_annotation(annotation=value, random=ExampleFactory.__random__)
    if isinstance(value, (Decimal, float)):
        value = round(float(value), 2)
    if isinstance(value, Enum):
        value = value.value
    if is_pydantic_model_instance(value):
        from litestar.contrib.pydantic import _model_dump

        value = _model_dump(value)
    if isinstance(value, (list, set)):
        value = [_normalize_example_value(v) for v in value]
    if isinstance(value, dict):
        for k, v in value.items():
            value[k] = _normalize_example_value(v)
    return value


def _create_field_meta(field: FieldDefinition) -> FieldMeta:
    return FieldMeta.from_type(
        annotation=field.annotation,
        default=field.default if field.default is not Empty else Null,
        name=field.name,
        random=ExampleFactory.__random__,
    )


def create_examples_for_field(field: FieldDefinition) -> list[Example]:
    """Create an OpenAPI Example instance.

    Args:
        field: A signature field.

    Returns:
        A list including a single example.
    """
    try:
        field_meta = _create_field_meta(replace(field, annotation=_normalize_example_value(field.annotation)))
        value = ExampleFactory.get_field_value(field_meta)
        return [Example(description=f"Example {field.name} value", value=value)]
    except ParameterException:
        return []
