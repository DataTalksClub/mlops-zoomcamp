from __future__ import annotations

from dataclasses import dataclass

from litestar.openapi.spec.base import BaseSchemaObject

__all__ = ("ServerVariable",)


@dataclass
class ServerVariable(BaseSchemaObject):
    """An object representing a Server Variable for server URL template substitution."""

    default: str
    """**REQUIRED**. The default value to use for substitution, which SHALL be sent if an alternate value is _not_
    supplied. Note this behavior is different than the
    `Schema Object's <https://spec.openapis.org/oas/v3.1.0#schemaObject>`_ treatment of default values, because in those
    cases parameter values are optional.  If the `enum <https://spec.openapis.org/oas/v3.1.0#serverVariableEnum>`_ is
    defined, the value MUST exist in the enum's values.
    """

    enum: list[str] | None = None
    """An enumeration of string values to be used if the substitution options are from a limited set.

    The array SHOULD NOT be empty.
    """

    description: str | None = None
    """An optional description for the server variable.

    `CommonMark syntax <https://spec.commonmark.org/>`_ MAY be used for rich text representation.
    """
