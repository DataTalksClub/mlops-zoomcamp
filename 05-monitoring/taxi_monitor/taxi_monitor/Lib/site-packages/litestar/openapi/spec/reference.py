from __future__ import annotations

from dataclasses import dataclass

from litestar.openapi.spec.base import BaseSchemaObject

__all__ = ("Reference",)


@dataclass
class Reference(BaseSchemaObject):
    """A simple object to allow referencing other components in the OpenAPI document, internally and externally.

    The ``$ref`` string value contains a URI `RFC3986 <https://tools.ietf.org/html/rfc3986>`_ , which identifies the
    location of the value being referenced.

    See the rules for resolving `Relative References <https://spec.openapis.org/oas/v3.1.0#relativeReferencesURI>`_.
    """

    ref: str
    """**REQUIRED**. The reference identifier. This MUST be in the form of a URI."""

    summary: str | None = None
    """A short summary which by default SHOULD override that of the referenced component.

    If the referenced object-type does not allow a ``summary`` field, then this field has no effect.
    """

    description: str | None = None
    """A description which by default SHOULD override that of the referenced component.

    `CommonMark syntax <https://spec.commonmark.org/>`_ MAY be used for rich text representation. If the referenced
    object-type does not allow a ``description`` field, then this field has no effect.
    """

    @property
    def value(self) -> str:
        return self.ref.split("/")[-1]
