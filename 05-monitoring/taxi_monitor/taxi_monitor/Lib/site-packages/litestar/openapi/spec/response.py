from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from litestar.openapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar.openapi.spec.header import OpenAPIHeader
    from litestar.openapi.spec.link import Link
    from litestar.openapi.spec.media_type import OpenAPIMediaType
    from litestar.openapi.spec.reference import Reference


__all__ = ("OpenAPIResponse",)


@dataclass
class OpenAPIResponse(BaseSchemaObject):
    """Describes a single response from an API Operation, including design-time, static ``links`` to operations based on
    the response.
    """

    description: str
    """**REQUIRED**. A short description of the response.
    `CommonMark syntax <https://spec.commonmark.org/>`_ MAY be used for rich text representation.
    """

    headers: dict[str, OpenAPIHeader | Reference] | None = None
    """Maps a header name to its definition.
    `RFC7230 <https://tools.ietf.org/html/rfc7230#page-22>`_ states header names are case insensitive.
    If a response header is defined with the name ``Content-Type``, it SHALL be ignored.
    """

    content: dict[str, OpenAPIMediaType] | None = None
    """A map containing descriptions of potential response payloads. The key is a media type or
    `media type range <https://tools.ietf.org/html/rfc7231#appendix-D>`_ and the value describes it.

    For responses that match multiple keys, only the most specific key is applicable. e.g. ``text/plain`` overrides
    ``text/*``
    """

    links: dict[str, Link | Reference] | None = None
    """A map of operations links that can be followed from the response.

    The key of the map is a short name for the link, following the naming constraints of the names for
    `Component Objects <https://spec.openapis.org/oas/v3.1.0#componentsObject>`_.
    """
