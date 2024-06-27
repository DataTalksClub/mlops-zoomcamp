from __future__ import annotations

from typing import TYPE_CHECKING

from litestar.plugins import OpenAPISchemaPlugin
from litestar.typing import FieldDefinition

if TYPE_CHECKING:
    from litestar._openapi.schema_generation import SchemaCreator
    from litestar.openapi.spec import Schema


class TypedDictSchemaPlugin(OpenAPISchemaPlugin):
    def is_plugin_supported_field(self, field_definition: FieldDefinition) -> bool:
        return field_definition.is_typeddict_type

    def to_openapi_schema(self, field_definition: FieldDefinition, schema_creator: SchemaCreator) -> Schema:
        type_hints = field_definition.get_type_hints(include_extras=True, resolve_generics=True)

        return schema_creator.create_component_schema(
            field_definition,
            required=sorted(getattr(field_definition.type_, "__required_keys__", [])),
            property_fields={k: FieldDefinition.from_kwarg(v, k) for k, v in type_hints.items()},
        )
