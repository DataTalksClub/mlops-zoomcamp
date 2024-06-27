from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from litestar.openapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar.openapi.spec.oauth_flow import OAuthFlow

__all__ = ("OAuthFlows",)


@dataclass
class OAuthFlows(BaseSchemaObject):
    """Allows configuration of the supported OAuth Flows."""

    implicit: OAuthFlow | None = None
    """Configuration for the OAuth Implicit flow."""

    password: OAuthFlow | None = None
    """Configuration for the OAuth Resource Owner Password flow."""

    client_credentials: OAuthFlow | None = None
    """Configuration for the OAuth Client Credentials flow. Previously called ``application`` in OpenAPI 2.0."""

    authorization_code: OAuthFlow | None = None
    """Configuration for the OAuth Authorization Code flow. Previously called ``accessCode`` in OpenAPI 2.0."""
