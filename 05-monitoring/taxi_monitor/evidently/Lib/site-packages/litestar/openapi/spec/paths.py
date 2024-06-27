from __future__ import annotations

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from litestar.openapi.spec import PathItem

Paths = Dict[str, "PathItem"]
"""Holds the relative paths to the individual endpoints and their operations. The path is appended to the URL from the.

`Server Object <https://spec.openapis.org/oas/v3.1.0#serverObject>`_ in order to construct the full URL.

The Paths MAY be empty, due to
`Access Control List (ACL) constraints <https://spec.openapis.org/oas/v3.1.0#securityFiltering>`_.

Patterned Fields

/{path}: PathItem

A relative path to an individual endpoint. The field name MUST begin with a forward slash (``/``). The path is
**appended** (no relative URL resolution) to the expanded URL from the
`Server Object <https://spec.openapis.org/oas/v3.1.0#serverObject>`_ 's ``url`` field in order to construct the full
URL. `Path templating <https://spec.openapis.org/oas/v3.1.0#pathTemplating>`_ is allowed. When matching URLs, concrete
(non-templated) paths would be matched before their templated counterparts. Templated paths with the same hierarchy but
different templated names MUST NOT exist as they are identical. In case of ambiguous matching, it's up to the tooling to
decide which one to use.
"""
