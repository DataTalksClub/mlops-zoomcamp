from __future__ import annotations

from typing import TYPE_CHECKING

import msgspec
from msgspec import Struct
from msgspec.structs import fields

from litestar.plugins import OpenAPISchemaPlugin
from litestar.types.empty import Empty
from litestar.typing import FieldDefinition
from litestar.utils.predicates import is_optional_union

if TYPE_CHECKING:
    from msgspec.structs import FieldInfo

    from litestar._openapi.schema_generation import SchemaCreator
    from litestar.openapi.spec import Schema


class StructSchemaPlugin(OpenAPISchemaPlugin):
    def is_plugin_supported_field(self, field_definition: FieldDefinition) -> bool:
        return not field_definition.is_union and field_definition.is_subclass_of(Struct)

    def to_openapi_schema(self, field_definition: FieldDefinition, schema_creator: SchemaCreator) -> Schema:
        def is_field_required(field: FieldInfo) -> bool:
            return field.required or field.default_factory is Empty

        type_hints = field_definition.get_type_hints(include_extras=True, resolve_generics=True)
        struct_fields = fields(field_definition.type_)

        return schema_creator.create_component_schema(
            field_definition,
            required=sorted(
                [
                    field.encode_name
                    for field in struct_fields
                    if is_field_required(field=field) and not is_optional_union(type_hints[field.name])
                ]
            ),
            property_fields={
                field.encode_name: FieldDefinition.from_kwarg(
                    type_hints[field.name],
                    field.encode_name,
                    default=field.default if field.default not in {msgspec.NODEFAULT, msgspec.UNSET} else Empty,
                )
                for field in struct_fields
            },
        )
