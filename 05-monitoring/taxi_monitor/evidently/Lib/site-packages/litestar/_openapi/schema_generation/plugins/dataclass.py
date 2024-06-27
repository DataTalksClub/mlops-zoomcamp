from __future__ import annotations

import dataclasses
from dataclasses import MISSING, fields
from typing import TYPE_CHECKING

from litestar.plugins import OpenAPISchemaPlugin
from litestar.types import Empty
from litestar.typing import FieldDefinition
from litestar.utils.predicates import is_optional_union

if TYPE_CHECKING:
    from litestar._openapi.schema_generation import SchemaCreator
    from litestar.openapi.spec import Schema


class DataclassSchemaPlugin(OpenAPISchemaPlugin):
    def is_plugin_supported_field(self, field_definition: FieldDefinition) -> bool:
        return field_definition.is_dataclass_type

    def to_openapi_schema(self, field_definition: FieldDefinition, schema_creator: SchemaCreator) -> Schema:
        type_hints = field_definition.get_type_hints(include_extras=True, resolve_generics=True)
        dataclass_fields = fields(field_definition.type_)
        return schema_creator.create_component_schema(
            field_definition,
            required=sorted(
                field.name
                for field in dataclass_fields
                if (
                    field.default is MISSING
                    and field.default_factory is MISSING
                    and not is_optional_union(type_hints[field.name])
                )
            ),
            property_fields={
                field.name: FieldDefinition.from_kwarg(
                    annotation=type_hints[field.name],
                    name=field.name,
                    default=field.default if field.default is not dataclasses.MISSING else Empty,
                )
                for field in dataclass_fields
            },
        )
