from __future__ import annotations

import contextlib
import re
from copy import copy
from dataclasses import asdict
from http import HTTPStatus
from operator import attrgetter
from typing import TYPE_CHECKING, Any, Iterator

from litestar._openapi.schema_generation import SchemaCreator
from litestar._openapi.schema_generation.utils import get_formatted_examples
from litestar.enums import MediaType
from litestar.exceptions import HTTPException, ValidationException
from litestar.openapi.spec import Example, OpenAPIResponse, Reference
from litestar.openapi.spec.enums import OpenAPIFormat, OpenAPIType
from litestar.openapi.spec.header import OpenAPIHeader
from litestar.openapi.spec.media_type import OpenAPIMediaType
from litestar.openapi.spec.schema import Schema
from litestar.response import (
    File,
    Redirect,
    Stream,
    Template,
)
from litestar.response import (
    Response as LitestarResponse,
)
from litestar.response.base import ASGIResponse
from litestar.types.builtin_types import NoneType
from litestar.typing import FieldDefinition
from litestar.utils import get_enum_string_value, get_name

if TYPE_CHECKING:
    from litestar._openapi.datastructures import OpenAPIContext
    from litestar.datastructures.cookie import Cookie
    from litestar.handlers.http_handlers import HTTPRouteHandler
    from litestar.openapi.spec.responses import Responses


__all__ = ("create_responses_for_handler",)

CAPITAL_LETTERS_PATTERN = re.compile(r"(?=[A-Z])")


def pascal_case_to_text(string: str) -> str:
    """Given a 'PascalCased' string, return its split form- 'Pascal Cased'."""
    return " ".join(re.split(CAPITAL_LETTERS_PATTERN, string)).strip()


def create_cookie_schema(cookie: Cookie) -> Schema:
    """Given a Cookie instance, return its corresponding OpenAPI schema.

    Args:
        cookie: Cookie

    Returns:
        Schema
    """
    cookie_copy = copy(cookie)
    cookie_copy.value = "<string>"
    value = cookie_copy.to_header(header="")
    return Schema(description=cookie.description or "", example=value)


class ResponseFactory:
    """Factory for creating a Response instance for a given route handler."""

    def __init__(self, context: OpenAPIContext, route_handler: HTTPRouteHandler) -> None:
        """Initialize the factory.

        Args:
            context: An OpenAPIContext instance.
            route_handler: An HTTPRouteHandler instance.
        """
        self.context = context
        self.route_handler = route_handler
        self.field_definition = route_handler.parsed_fn_signature.return_type
        self.schema_creator = SchemaCreator.from_openapi_context(context, prefer_alias=False)

    def create_responses(self, raises_validation_error: bool) -> Responses | None:
        """Create the schema for responses, if any.

        Args:
            raises_validation_error: Boolean flag indicating whether the handler raises a ValidationException.

        Returns:
            Responses
        """
        responses: Responses = {
            str(self.route_handler.status_code): self.create_success_response(),
        }

        exceptions = list(self.route_handler.raises or [])
        if raises_validation_error and ValidationException not in exceptions:
            exceptions.append(ValidationException)

        for status_code, response in create_error_responses(exceptions=exceptions):
            responses[status_code] = response

        for status_code, response in self.create_additional_responses():
            responses[status_code] = response

        return responses or None

    def create_description(self) -> str:
        """Create the description for a success response."""
        default_descriptions: dict[Any, str] = {
            Stream: "Stream Response",
            Redirect: "Redirect Response",
            File: "File Download",
        }
        return (
            self.route_handler.response_description
            or default_descriptions.get(self.field_definition.annotation)
            or HTTPStatus(self.route_handler.status_code).description
        )

    def create_success_response(self) -> OpenAPIResponse:
        """Create the schema for a success response."""
        if self.field_definition.is_subclass_of((NoneType, ASGIResponse)):
            response = OpenAPIResponse(content=None, description=self.create_description())
        elif self.field_definition.is_subclass_of(Redirect):
            response = self.create_redirect_response()
        elif self.field_definition.is_subclass_of((File, Stream)):
            response = self.create_file_response()
        else:
            media_type = self.route_handler.media_type

            if dto := self.route_handler.resolve_return_dto():
                result = dto.create_openapi_schema(
                    field_definition=self.field_definition,
                    handler_id=self.route_handler.handler_id,
                    schema_creator=self.schema_creator,
                )
            else:
                if self.field_definition.is_subclass_of(Template):
                    field_def = FieldDefinition.from_annotation(str)
                    media_type = media_type or MediaType.HTML
                elif self.field_definition.is_subclass_of(LitestarResponse):
                    field_def = (
                        self.field_definition.inner_types[0]
                        if self.field_definition.inner_types
                        else FieldDefinition.from_annotation(Any)
                    )
                    media_type = media_type or MediaType.JSON
                else:
                    field_def = self.field_definition

                result = self.schema_creator.for_field_definition(field_def)

            schema = (
                result if isinstance(result, Schema) else self.context.schema_registry.from_reference(result).schema
            )
            schema.content_encoding = self.route_handler.content_encoding
            schema.content_media_type = self.route_handler.content_media_type
            response = OpenAPIResponse(
                content={get_enum_string_value(media_type): OpenAPIMediaType(schema=result)},
                description=self.create_description(),
            )
        self.set_success_response_headers(response)
        return response

    def create_redirect_response(self) -> OpenAPIResponse:
        """Create the schema for a redirect response."""
        return OpenAPIResponse(
            content=None,
            description=self.create_description(),
            headers={
                "location": OpenAPIHeader(
                    schema=Schema(type=OpenAPIType.STRING), description="target path for the redirect"
                )
            },
        )

    def create_file_response(self) -> OpenAPIResponse:
        """Create the schema for a file/stream response."""
        return OpenAPIResponse(
            content={
                self.route_handler.media_type: OpenAPIMediaType(
                    schema=Schema(
                        type=OpenAPIType.STRING,
                        content_encoding=self.route_handler.content_encoding,
                        content_media_type=self.route_handler.content_media_type or "application/octet-stream",
                    ),
                )
            },
            description=self.create_description(),
            headers={
                "content-length": OpenAPIHeader(
                    schema=Schema(type=OpenAPIType.STRING), description="File size in bytes"
                ),
                "last-modified": OpenAPIHeader(
                    schema=Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.DATE_TIME),
                    description="Last modified data-time in RFC 2822 format",
                ),
                "etag": OpenAPIHeader(schema=Schema(type=OpenAPIType.STRING), description="Entity tag"),
            },
        )

    def set_success_response_headers(self, response: OpenAPIResponse) -> None:
        """Set the schema for success response headers, if any."""

        if response.headers is None:
            response.headers = {}

        if not self.schema_creator.generate_examples:
            schema_creator = self.schema_creator
        else:
            schema_creator = SchemaCreator.from_openapi_context(self.context, generate_examples=False)

        for response_header in self.route_handler.resolve_response_headers():
            header = OpenAPIHeader()
            for attribute_name, attribute_value in (
                (k, v) for k, v in asdict(response_header).items() if v is not None
            ):
                if attribute_name == "value":
                    header.schema = schema_creator.for_field_definition(
                        FieldDefinition.from_annotation(type(attribute_value))
                    )
                elif attribute_name != "documentation_only":
                    setattr(header, attribute_name, attribute_value)

            response.headers[response_header.name] = header

        if cookies := self.route_handler.resolve_response_cookies():
            response.headers["Set-Cookie"] = OpenAPIHeader(
                schema=Schema(
                    all_of=[create_cookie_schema(cookie=cookie) for cookie in sorted(cookies, key=attrgetter("key"))]
                )
            )

    def create_additional_responses(self) -> Iterator[tuple[str, OpenAPIResponse]]:
        """Create the schema for additional responses, if any."""
        if not self.route_handler.responses:
            return

        for status_code, additional_response in self.route_handler.responses.items():
            schema_creator = SchemaCreator.from_openapi_context(
                self.context,
                prefer_alias=False,
                generate_examples=additional_response.generate_examples,
            )
            field_def = FieldDefinition.from_annotation(additional_response.data_container)

            examples: dict[str, Example | Reference] | None = (
                dict(get_formatted_examples(field_def, additional_response.examples))
                if additional_response.examples
                else None
            )

            content: dict[str, OpenAPIMediaType] | None
            if additional_response.data_container is not None:
                schema = schema_creator.for_field_definition(field_def)
                content = {additional_response.media_type: OpenAPIMediaType(schema=schema, examples=examples)}
            else:
                content = None

            yield (
                str(status_code),
                OpenAPIResponse(
                    description=additional_response.description,
                    content=content,
                ),
            )


def create_error_responses(exceptions: list[type[HTTPException]]) -> Iterator[tuple[str, OpenAPIResponse]]:
    """Create the schema for error responses, if any."""
    grouped_exceptions: dict[int, list[type[HTTPException]]] = {}
    for exc in exceptions:
        if not grouped_exceptions.get(exc.status_code):
            grouped_exceptions[exc.status_code] = []
        grouped_exceptions[exc.status_code].append(exc)
    for status_code, exception_group in grouped_exceptions.items():
        exceptions_schemas = []
        group_description: str = ""
        for exc in exception_group:
            example_detail = ""
            if hasattr(exc, "detail") and exc.detail:
                group_description = exc.detail
                example_detail = exc.detail

            if not example_detail:
                with contextlib.suppress(Exception):
                    example_detail = HTTPStatus(status_code).phrase

            exceptions_schemas.append(
                Schema(
                    type=OpenAPIType.OBJECT,
                    required=["detail", "status_code"],
                    properties={
                        "status_code": Schema(type=OpenAPIType.INTEGER),
                        "detail": Schema(type=OpenAPIType.STRING),
                        "extra": Schema(
                            type=[OpenAPIType.NULL, OpenAPIType.OBJECT, OpenAPIType.ARRAY],
                            additional_properties=Schema(),
                        ),
                    },
                    description=pascal_case_to_text(get_name(exc)),
                    examples=[{"status_code": status_code, "detail": example_detail, "extra": {}}],
                )
            )
        if len(exceptions_schemas) > 1:  # noqa: SIM108
            schema = Schema(one_of=exceptions_schemas)
        else:
            schema = exceptions_schemas[0]

        if not group_description:
            with contextlib.suppress(Exception):
                group_description = HTTPStatus(status_code).description

        yield (
            str(status_code),
            OpenAPIResponse(
                description=group_description,
                content={MediaType.JSON: OpenAPIMediaType(schema=schema)},
            ),
        )


def create_responses_for_handler(
    context: OpenAPIContext, route_handler: HTTPRouteHandler, raises_validation_error: bool
) -> Responses | None:
    """Create the schema for responses, if any.

    Args:
        context: An OpenAPIContext instance.
        route_handler: An HTTPRouteHandler instance.
        raises_validation_error: Boolean flag indicating whether the handler raises a ValidationException.

    Returns:
        Responses
    """
    return ResponseFactory(context, route_handler).create_responses(raises_validation_error=raises_validation_error)
