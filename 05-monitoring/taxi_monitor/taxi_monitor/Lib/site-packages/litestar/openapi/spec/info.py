from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from litestar.openapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar.openapi.spec.contact import Contact
    from litestar.openapi.spec.license import License

__all__ = ("Info",)


@dataclass
class Info(BaseSchemaObject):
    """The object provides metadata about the API.

    The metadata MAY be used by the clients if needed, and MAY be presented in editing or documentation generation tools
    for convenience.
    """

    title: str
    """
    **REQUIRED**. The title of the API.
    """

    version: str
    """
    **REQUIRED**. The version of the OpenAPI document which is distinct from the
    `OpenAPI Specification version <https://spec.openapis.org/oas/v3.1.0#oasVersion>`_ or the API implementation version
    """

    summary: str | None = None
    """A short summary of the API."""

    description: str | None = None
    """A description of the API.

    `CommonMark syntax <https://spec.commonmark.org/>`_ MAY be used for rich text representation.
    """

    terms_of_service: str | None = None
    """A URL to the Terms of Service for the API. MUST be in the form of a URL."""

    contact: Contact | None = None
    """The contact information for the exposed API."""

    license: License | None = None
    """The license information for the exposed API."""
