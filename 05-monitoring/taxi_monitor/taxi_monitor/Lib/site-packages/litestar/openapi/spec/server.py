from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from litestar.openapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar.openapi.spec.server_variable import ServerVariable

__all__ = ("Server",)


@dataclass
class Server(BaseSchemaObject):
    """An object representing a Server."""

    url: str
    """
    **REQUIRED**. A URL to the target host.

    This URL supports Server Variables and MAY be relative, to indicate that the host location is relative to the
    location where the OpenAPI document is being served. Variable substitutions will be made when a variable is named in
    ``{brackets}``.
    """

    description: str | None = None
    """An optional string describing the host designated by the URL.

    `CommonMark syntax <https://spec.commonmark.org/>`_ MAY be used for rich text representation.
    """

    variables: dict[str, ServerVariable] | None = None
    """A map between a variable name and its value. The value is used for substitution in the server's URL template."""
