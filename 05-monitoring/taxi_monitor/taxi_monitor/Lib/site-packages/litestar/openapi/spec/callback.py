from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Union

if TYPE_CHECKING:
    from litestar.openapi.spec.path_item import PathItem
    from litestar.openapi.spec.reference import Reference


Callback = Dict[str, Union["PathItem", "Reference"]]
"""A map of possible out-of band callbacks related to the parent operation. Each value in the map is a
`Path Item Object <https://spec.openapis.org/oas/v3.1.0#pathItemObject>`_ that describes a set of requests that may be
initiated by the API provider and the expected responses. The key value used to identify the path item object is an
expression, evaluated at runtime, that identifies a URL to use for the callback operation.

Patterned Fields

{expression}: 'PathItem' = ...

A Path Item Object used to define a callback request and expected responses.

A `complete example <https://github.com/OAI/OpenAPI-Specification/blob/main/examples/v3.1/webhook-example.yaml>`_ is
available.
"""
