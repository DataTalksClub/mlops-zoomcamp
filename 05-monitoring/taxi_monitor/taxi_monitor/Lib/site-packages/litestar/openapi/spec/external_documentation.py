from __future__ import annotations

from dataclasses import dataclass

from litestar.openapi.spec.base import BaseSchemaObject

__all__ = ("ExternalDocumentation",)


@dataclass
class ExternalDocumentation(BaseSchemaObject):
    """Allows referencing an external resource for extended documentation."""

    url: str
    """**REQUIRED**. The URL for the target documentation. Value MUST be in the form of a URL."""

    description: str | None = None
    """A short description of the target documentation.

    `CommonMark syntax <https://spec.commonmark.org/>`_ MAY be used for rich text representation.
    """
