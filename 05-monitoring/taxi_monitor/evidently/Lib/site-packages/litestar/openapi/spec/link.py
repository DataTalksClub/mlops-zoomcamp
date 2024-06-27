from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from litestar.openapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar.openapi.spec.server import Server

__all__ = ("Link",)


@dataclass
class Link(BaseSchemaObject):
    """The ``Link object`` represents a possible design-time link for a response. The presence of a link does not
    guarantee the caller's ability to successfully invoke it, rather it provides a known relationship and traversal
    mechanism between responses and other operations.

    Unlike _dynamic_ links (i.e. links provided **in** the response payload), the OAS linking mechanism does not require
    link information in the runtime response.

    For computing links, and providing instructions to execute them, a
    `runtime expression <https://spec.openapis.org/oas/v3.1.0#runtimeExpression>`_ is used for accessing values in an
    operation and using them as parameters while invoking the linked operation.
    """

    operation_ref: str | None = None
    """A relative or absolute URI reference to an OAS operation.

    This field is mutually exclusive of the ``operationId`` field, and MUST point to an
    `Operation Object <https://spec.openapis.org/oas/v3.1.0#operationObject>`_. Relative ``operationRef`` values MAY be
    used to locate an existing `Operation Object <https://spec.openapis.org/oas/v3.1.0#operationObject>`_ in the OpenAPI
    definition. See the rules for resolving
    `Relative References <https://spec.openapis.org/oas/v3.1.0#relativeReferencesURI>`_
    """

    operation_id: str | None = None
    """The name of an _existing_, resolvable OAS operation, as defined with a unique ``operationId``.

    This field is mutually exclusive of the ``operationRef`` field.
    """

    parameters: dict[str, Any] | None = None
    """A map representing parameters to pass to an operation as specified with ``operationId`` or identified via
    ``operationRef``. The key is the parameter name to be used, whereas the value can be a constant or an expression to
    be evaluated and passed to the linked operation.

    The parameter name can be qualified using the
    `parameter location <https://spec.openapis.org/oas/v3.1.0#parameterIn>`_ ``[{in}.]{name}`` for operations that use
    the same parameter name in different locations (e.g. path.id).
    """

    request_body: Any | None = None
    """A literal value or
    `{expression} <https://spec.openapis.org/oas/v3.1.0#runtimeExpression>`_ to use as a request body when calling the
    target operation."""

    description: str | None = None
    """A description of the link.

    `CommonMark syntax <https://spec.commonmark.org/>`_ MAY be used for rich text representation.
    """

    server: Server | None = None
    """A server object to be used by the target operation."""
