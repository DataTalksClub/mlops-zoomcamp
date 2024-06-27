from __future__ import annotations

from dataclasses import dataclass

from litestar.openapi.spec.base import BaseSchemaObject

__all__ = ("License",)


@dataclass
class License(BaseSchemaObject):
    """License information for the exposed API."""

    name: str
    """**REQUIRED**. The license name used for the API."""

    identifier: str | None = None
    """An
    `SPDX <https://spdx.github.io/spdx-spec/v2.3/SPDX-license-list/#a1-licenses-with-short-identifiers>`_ license expression for the API.

    The ``identifier`` field is mutually exclusive of the ``url`` field.
    """

    url: str | None = None
    """A URL to the license used for the API.

    This MUST be in the form of a URL. The ``url`` field is mutually exclusive of the ``identifier`` field.
    """
