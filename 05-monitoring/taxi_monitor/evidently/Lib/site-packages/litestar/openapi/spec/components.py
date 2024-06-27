from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from litestar.openapi.spec.base import BaseSchemaObject

__all__ = ("Components",)


if TYPE_CHECKING:
    from litestar.openapi.spec.callback import Callback
    from litestar.openapi.spec.example import Example
    from litestar.openapi.spec.header import OpenAPIHeader
    from litestar.openapi.spec.link import Link
    from litestar.openapi.spec.parameter import Parameter
    from litestar.openapi.spec.path_item import PathItem
    from litestar.openapi.spec.reference import Reference
    from litestar.openapi.spec.request_body import RequestBody
    from litestar.openapi.spec.response import OpenAPIResponse
    from litestar.openapi.spec.schema import Schema
    from litestar.openapi.spec.security_scheme import SecurityScheme


@dataclass
class Components(BaseSchemaObject):
    """Holds a set of reusable objects for different aspects of the OAS.

    All objects defined within the components object will have no effect
    on the API unless they are explicitly referenced from properties
    outside the components object.
    """

    schemas: dict[str, Schema] = field(default_factory=dict)
    """An object to hold reusable
    `Schema Objects <https://spec.openapis.org/oas/v3.1.0#schemaObject>`_"""

    responses: dict[str, OpenAPIResponse | Reference] | None = None
    """An object to hold reusable
    `Response Objects <https://spec.openapis.org/oas/v3.1.0#responseObject>`_"""

    parameters: dict[str, Parameter | Reference] | None = None
    """An object to hold reusable
    `Parameter Objects <https://spec.openapis.org/oas/v3.1.0#parameterObject>`_"""

    examples: dict[str, Example | Reference] | None = None
    """An object to hold reusable
    `Example Objects <https://spec.openapis.org/oas/v3.1.0#exampleObject>`_"""

    request_bodies: dict[str, RequestBody | Reference] | None = None
    """An object to hold reusable
    `Request Body Objects <https://spec.openapis.org/oas/v3.1.0#requestBodyObject>`_"""

    headers: dict[str, OpenAPIHeader | Reference] | None = None
    """An object to hold reusable
    `Header  Objects <https://spec.openapis.org/oas/v3.1.0#headerObject>`_"""

    security_schemes: dict[str, SecurityScheme | Reference] | None = None
    """An object to hold reusable
    `Security Scheme  Objects <https://spec.openapis.org/oas/v3.1.0#securitySchemeObject>`_"""

    links: dict[str, Link | Reference] | None = None
    """An object to hold reusable
    `Link Objects <https://spec.openapis.org/oas/v3.1.0#linkObject>`_"""

    callbacks: dict[str, Callback | Reference] | None = None
    """An object to hold reusable
    `Callback Objects <https://spec.openapis.org/oas/v3.1.0#callbackObject>`_"""

    path_items: dict[str, PathItem | Reference] | None = None
    """An object to hold reusable
    `Path Item Object <https://spec.openapis.org/oas/v3.1.0#pathItemObject>`_"""
