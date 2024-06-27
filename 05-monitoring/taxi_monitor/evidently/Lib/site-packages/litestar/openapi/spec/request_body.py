from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from litestar.openapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar.openapi.spec.media_type import OpenAPIMediaType

__all__ = ("RequestBody",)


@dataclass
class RequestBody(BaseSchemaObject):
    """Describes a single request body."""

    content: dict[str, OpenAPIMediaType]
    """
    **REQUIRED**. The content of the request body.
    The key is a media type or `media type range <https://tools.ietf.org/html/rfc7231#appendix-D>`_ and the value
    describes it.

    For requests that match multiple keys, only the most specific key is applicable. e.g. ``text/plain`` overrides
    ``text/*``
    """

    description: str | None = None
    """A brief description of the request body. This could contain examples of use.

    `CommonMark syntax <https://spec.commonmark.org/>`_ MAY be used for rich text representation.
    """

    required: bool = False
    """Determines if the request body is required in the request.

    Defaults to ``False``.
    """
