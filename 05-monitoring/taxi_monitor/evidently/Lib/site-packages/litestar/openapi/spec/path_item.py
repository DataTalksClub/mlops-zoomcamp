from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from litestar.openapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar.openapi.spec.operation import Operation
    from litestar.openapi.spec.parameter import Parameter
    from litestar.openapi.spec.reference import Reference
    from litestar.openapi.spec.server import Server

__all__ = ("PathItem",)


@dataclass
class PathItem(BaseSchemaObject):
    """Describes the operations available on a single path.

    A Path Item MAY be empty, due to `ACL constraints <https://spec.openapis.org/oas/v3.1.0#securityFiltering>`_. The
    path itself is still exposed to the documentation viewer, but they will not know which operations and parameters are
    available.
    """

    ref: str | None = None
    """Allows for an external definition of this path item. The referenced structure MUST be in the format of a
    `Path Item Object <https://spec.openapis.org/oas/v3.1.0#pathItemObject>`.

    In case a Path Item Object field appears both in the defined object and the referenced object, the behavior is
    undefined. See the rules for resolving
    `Relative References <https://spec.openapis.org/oas/v3.1.0#relativeReferencesURI>`_.
    """

    summary: str | None = None
    """An optional, string summary, intended to apply to all operations in this path."""

    description: str | None = None
    """An optional, string description, intended to apply to all operations in this path.

    `CommonMark syntax <https://spec.commonmark.org/>`_ MAY be used for rich text representation.
    """

    get: Operation | None = None
    """A definition of a GET operation on this path."""

    put: Operation | None = None
    """A definition of a PUT operation on this path."""

    post: Operation | None = None
    """A definition of a POST operation on this path."""

    delete: Operation | None = None
    """A definition of a DELETE operation on this path."""

    options: Operation | None = None
    """A definition of a OPTIONS operation on this path."""

    head: Operation | None = None
    """A definition of a HEAD operation on this path."""

    patch: Operation | None = None
    """A definition of a PATCH operation on this path."""

    trace: Operation | None = None
    """A definition of a TRACE operation on this path."""

    servers: list[Server] | None = None
    """An alternative ``server`` array to service all operations in this path."""

    parameters: list[Parameter | Reference] | None = None
    """A list of parameters that are applicable for all the operations described under this path. These parameters can
    be overridden at the operation level, but cannot be removed there. The list MUST NOT include duplicated parameters.
    A unique parameter is defined by a combination of a `name <https://spec.openapis.org/oas/v3.1.0#parameterName>`_ and
    `location <https://spec.openapis.org/oas/v3.1.0#parameterIn>`_. The list can use the
    `Reference Object <https://spec.openapis.org/oas/v3.1.0#referenceObject>`_ to link to parameters that are defined at
    the `OpenAPI Object's components/parameters <https://spec.openapis.org/oas/v3.1.0#componentsParameters>`_.
    """
