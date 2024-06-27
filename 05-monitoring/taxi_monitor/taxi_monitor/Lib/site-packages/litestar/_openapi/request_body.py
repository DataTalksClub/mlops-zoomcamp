from __future__ import annotations

from typing import TYPE_CHECKING

from litestar._openapi.schema_generation import SchemaCreator
from litestar.enums import RequestEncodingType
from litestar.openapi.spec.media_type import OpenAPIMediaType
from litestar.openapi.spec.request_body import RequestBody
from litestar.params import BodyKwarg

__all__ = ("create_request_body",)


if TYPE_CHECKING:
    from litestar._openapi.datastructures import OpenAPIContext
    from litestar.dto import AbstractDTO
    from litestar.typing import FieldDefinition


def create_request_body(
    context: OpenAPIContext,
    handler_id: str,
    resolved_data_dto: type[AbstractDTO] | None,
    data_field: FieldDefinition,
) -> RequestBody:
    """Create a RequestBody instance for the given route handler's data field.

    Args:
        context: The OpenAPIContext instance.
        handler_id: The handler id.
        resolved_data_dto: The resolved data dto.
        data_field: The data field.

    Returns:
        A RequestBody instance.
    """
    media_type: RequestEncodingType | str = RequestEncodingType.JSON
    schema_creator = SchemaCreator.from_openapi_context(context, prefer_alias=True)
    if isinstance(data_field.kwarg_definition, BodyKwarg) and data_field.kwarg_definition.media_type:
        media_type = data_field.kwarg_definition.media_type

    if resolved_data_dto:
        schema = resolved_data_dto.create_openapi_schema(
            field_definition=data_field,
            handler_id=handler_id,
            schema_creator=schema_creator,
        )
    else:
        schema = schema_creator.for_field_definition(data_field)

    return RequestBody(required=True, content={media_type: OpenAPIMediaType(schema=schema)})
