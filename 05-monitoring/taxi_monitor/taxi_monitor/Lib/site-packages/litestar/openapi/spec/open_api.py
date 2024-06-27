from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from litestar.openapi.spec.base import BaseSchemaObject
from litestar.openapi.spec.components import Components
from litestar.openapi.spec.server import Server

if TYPE_CHECKING:
    from litestar.openapi.spec.external_documentation import ExternalDocumentation
    from litestar.openapi.spec.info import Info
    from litestar.openapi.spec.path_item import PathItem
    from litestar.openapi.spec.paths import Paths
    from litestar.openapi.spec.reference import Reference
    from litestar.openapi.spec.security_requirement import SecurityRequirement
    from litestar.openapi.spec.tag import Tag

__all__ = ("OpenAPI",)


@dataclass
class OpenAPI(BaseSchemaObject):
    """Root OpenAPI document."""

    info: Info
    """
    **REQUIRED**. Provides metadata about the API. The metadata MAY be used by tooling as required.
    """

    openapi: str = "3.1.0"
    """
    **REQUIRED**. This string MUST be the
    `version number <https://spec.openapis.org/oas/v3.1.0#versions>`_ of the OpenAPI Specification that the OpenAPI
    document uses. The ``openapi`` field SHOULD be used by tooling to interpret the OpenAPI document. This is *not*
    related to the API `info.version <https://spec.openapis.org/oas/v3.1.0#infoVersion>`_ string.
    """

    json_schema_dialect: str | None = None
    """The default value for the ``$schema`` keyword within
    `Schema Objects <https://spec.openapis.org/oas/v3.1.0#schemaObject>`_ contained within this OAS document.

    This MUST be in the form of a URI.
    """

    servers: list[Server] = field(default_factory=lambda x: [Server(url="/")])  # type: ignore[misc, arg-type]
    """An array of Server Objects, which provide connectivity information to a target server.

    If the ``servers`` property is not provided, or is an empty array, the default value would be a
    `Server Object <https://spec.openapis.org/oas/v3.1.0#serverObject>`_ with a
    `url <https://spec.openapis.org/oas/v3.1.0#serverUrl>`_ value of ``/``.
    """

    paths: Paths | None = None
    """The available paths and operations for the API."""

    webhooks: dict[str, PathItem | Reference] | None = None
    """The incoming webhooks that MAY be received as part of this API and that the API consumer MAY choose to implement.

    Closely related to the ``callbacks`` feature, this section describes requests initiated other than by an API call,
    for example by an out of band registration. The key name is a unique string to refer to each webhook, while the
    (optionally referenced) Path Item Object describes a request that may be initiated by the API provider and the
    expected responses. An
    `example <https://github.com/OAI/OpenAPI-Specification/blob/main/examples/v3.1/webhook-example.yaml>`_ is available.
    """

    components: Components = field(default_factory=Components)
    """An element to hold various schemas for the document."""

    security: list[SecurityRequirement] | None = None
    """A declaration of which security mechanisms can be used across the API.

    The list of values includes alternative security requirement objects that can be used. Only one of the security
    requirement objects need to be satisfied to authorize a request. Individual operations can override this definition.
    To make security optional, an empty security requirement ( ``{}`` ) can be included in the array.
    """

    tags: list[Tag] | None = None
    """A list of tags used by the document with additional metadata.

    The order of the tags can be used to reflect on their order by the parsing tools. Not all tags that are used by the
    `Operation Object <https://spec.openapis.org/oas/v3.1.0#operationObject>`_ must be declared. The tags that are not
    declared MAY be organized randomly or based on the tools' logic. Each tag name in the list MUST be unique.
    """

    external_docs: ExternalDocumentation | None = None
    """Additional external documentation."""
