from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from litestar.openapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar.openapi.spec.callback import Callback
    from litestar.openapi.spec.external_documentation import ExternalDocumentation
    from litestar.openapi.spec.parameter import Parameter
    from litestar.openapi.spec.reference import Reference
    from litestar.openapi.spec.request_body import RequestBody
    from litestar.openapi.spec.responses import Responses
    from litestar.openapi.spec.security_requirement import SecurityRequirement
    from litestar.openapi.spec.server import Server

__all__ = ("Operation",)


@dataclass
class Operation(BaseSchemaObject):
    """Describes a single API operation on a path."""

    tags: list[str] | None = None
    """A list of tags for API documentation control.

    Tags can be used for logical grouping of operations by resources or any other qualifier.
    """

    summary: str | None = None
    """A short summary of what the operation does."""

    description: str | None = None
    """A verbose explanation of the operation behavior.

    `CommonMark syntax <https://spec.commonmark.org/>`_ MAY be used for rich text representation.
    """

    external_docs: ExternalDocumentation | None = None
    """Additional external documentation for this operation."""

    operation_id: str | None = None
    """Unique string used to identify the operation.

    The id MUST be unique among all operations described in the API. The operationId value is **case-sensitive**. Tools
    and libraries MAY use the operationId to uniquely identify an operation, therefore, it is RECOMMENDED to follow
    common programming naming conventions.
    """

    parameters: list[Parameter | Reference] | None = None
    """A list of parameters that are applicable for this operation.

    If a parameter is already defined at the `Path Item <https://spec.openapis.org/oas/v3.1.0#pathItemParameters>`_,
    the new definition will override it but can never remove it. The list MUST NOT include duplicated parameters. A
    unique parameter is defined by a combination of a `name <https://spec.openapis.org/oas/v3.1.0#parameterName>`_ and
    `location <https://spec.openapis.org/oas/v3.1.0#parameterIn>`_. The list can use the
    `Reference Object <https://spec.openapis.org/oas/v3.1.0#referenceObject>`_ to link to parameters that are defined at
    the `OpenAPI Object's components/parameters <https://spec.openapis.org/oas/v3.1.0#componentsParameters>`_.
    """

    request_body: RequestBody | Reference | None = None
    """The request body applicable for this operation.

    The ``requestBody`` is fully supported in HTTP methods where the HTTP 1.1 specification
    :rfc:`7231` has explicitly defined semantics for request bodies. In other cases where the HTTP spec is vague (such
    as `GET <https://tools.ietf.org/html/rfc7231#section-4.3.1>`_,
    `HEAD <https://tools.ietf.org/html/rfc7231#section-4.3.2>`_ and
    `DELETE <https://tools.ietf.org/html/rfc7231#section-4.3.5>`_, ``requestBody`` is permitted but does not have
    well-defined semantics and SHOULD be avoided if possible.
    """

    responses: Responses | None = None
    """The list of possible responses as they are returned from executing this operation."""

    callbacks: dict[str, Callback | Reference] | None = None
    """A map of possible out-of band callbacks related to the parent operation.

    The key is a unique identifier for the Callback Object. Each value in the map is a
    `Callback Object <https://spec.openapis.org/oas/v3.1.0#callbackObject>`_ that describes a request that may be
    initiated by the API provider and the expected responses.
    """

    deprecated: bool = False
    """Declares this operation to be deprecated.

    Consumers SHOULD refrain from usage of the declared operation. Default value is ``False``.
    """

    security: list[SecurityRequirement] | None = None
    """A declaration of which security mechanisms can be used for this operation.

    The list of values includes alternative security requirement objects that can be used. Only one of the security
    requirement objects need to be satisfied to authorize a request. To make security optional, an empty security
    requirement (``{}``) can be included in the array. This definition overrides any declared top-level
    `security <https://spec.openapis.org/oas/v3.1.0#oasSecurity>`_. To remove a top-level security declaration, an empty
    array can be used.
    """

    servers: list[Server] | None = None
    """An alternative ``server`` array to service this operation.

    If an alternative ``server`` object is specified at the Path Item Object or Root level, it will be overridden by
    this value.
    """
