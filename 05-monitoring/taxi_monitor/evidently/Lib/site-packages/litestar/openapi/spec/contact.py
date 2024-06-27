from __future__ import annotations

from dataclasses import dataclass

from litestar.openapi.spec.base import BaseSchemaObject

__all__ = ("Contact",)


@dataclass
class Contact(BaseSchemaObject):
    """Contact information for the exposed API."""

    name: str | None = None
    """The identifying name of the contact person/organization."""

    url: str | None = None
    """The URL pointing to the contact information. MUST be in the form of a URL."""

    email: str | None = None
    """The email address of the contact person/organization. MUST be in the form of an email address."""
