from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from litestar.openapi.spec.base import BaseSchemaObject


@dataclass
class Example(BaseSchemaObject):
    summary: str | None = None
    """Short description for the example."""

    description: str | None = None
    """Long description for the example.

    `CommonMark syntax <https://spec.commonmark.org/>`_ MAY be used for rich text representation.
    """

    value: Any | None = None
    """Embedded literal example.

    The ``value`` field and ``externalValue`` field are mutually exclusive. To represent examples of media types that
    cannot naturally represented in JSON or YAML, use a string value to contain the example, escaping where necessary.
    """

    external_value: str | None = None
    """A URL that points to the literal example. This provides the capability to reference examples that cannot easily
    be included in JSON or YAML documents.

    The ``value`` field and ``externalValue`` field are mutually exclusive. See the rules for resolving
    `Relative References <https://spec.openapis.org/oas/v3.1.0#relativeReferencesURI>`_.
    """
