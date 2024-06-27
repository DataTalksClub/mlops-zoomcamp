from __future__ import annotations

from typing import TYPE_CHECKING

from litestar.openapi.spec import OpenAPIType, Schema
from litestar.pagination import ClassicPagination, CursorPagination, OffsetPagination
from litestar.plugins import OpenAPISchemaPlugin

if TYPE_CHECKING:
    from litestar._openapi.schema_generation import SchemaCreator
    from litestar.typing import FieldDefinition


class PaginationSchemaPlugin(OpenAPISchemaPlugin):
    def is_plugin_supported_field(self, field_definition: FieldDefinition) -> bool:
        return field_definition.origin in (ClassicPagination, CursorPagination, OffsetPagination)

    def to_openapi_schema(self, field_definition: FieldDefinition, schema_creator: SchemaCreator) -> Schema:
        if field_definition.origin is ClassicPagination:
            return Schema(
                type=OpenAPIType.OBJECT,
                properties={
                    "items": Schema(
                        type=OpenAPIType.ARRAY,
                        items=schema_creator.for_field_definition(field_definition.inner_types[0]),
                    ),
                    "page_size": Schema(type=OpenAPIType.INTEGER, description="Number of items per page."),
                    "current_page": Schema(type=OpenAPIType.INTEGER, description="Current page number."),
                    "total_pages": Schema(type=OpenAPIType.INTEGER, description="Total number of pages."),
                },
            )

        if field_definition.origin is OffsetPagination:
            return Schema(
                type=OpenAPIType.OBJECT,
                properties={
                    "items": Schema(
                        type=OpenAPIType.ARRAY,
                        items=schema_creator.for_field_definition(field_definition.inner_types[0]),
                    ),
                    "limit": Schema(type=OpenAPIType.INTEGER, description="Maximal number of items to send."),
                    "offset": Schema(type=OpenAPIType.INTEGER, description="Offset from the beginning of the query."),
                    "total": Schema(type=OpenAPIType.INTEGER, description="Total number of items."),
                },
            )

        cursor_schema = schema_creator.not_generating_examples.for_field_definition(field_definition.inner_types[0])
        cursor_schema.description = "Unique ID, designating the last identifier in the given data set. This value can be used to request the 'next' batch of records."

        return Schema(
            type=OpenAPIType.OBJECT,
            properties={
                "items": Schema(
                    type=OpenAPIType.ARRAY,
                    items=schema_creator.for_field_definition(field_definition=field_definition.inner_types[1]),
                ),
                "cursor": cursor_schema,
                "results_per_page": Schema(type=OpenAPIType.INTEGER, description="Maximal number of items to send."),
            },
        )
