from __future__ import annotations

from dataclasses import dataclass

from litestar.openapi.spec.base import BaseSchemaObject

__all__ = ("OAuthFlow",)


@dataclass
class OAuthFlow(BaseSchemaObject):
    """Configuration details for a supported OAuth Flow."""

    authorization_url: str | None = None
    """
    **REQUIRED** for ``oauth2`` ("implicit", "authorizationCode"). The authorization URL to be used for this flow. This
    MUST be in the form of a URL. The OAuth2 standard requires the use of TLS.
    """

    token_url: str | None = None
    """
    **REQUIRED** for ``oauth2`` ("password", "clientCredentials", "authorizationCode"). The token URL to be used for
    this flow. This MUST be in the form of a URL. The OAuth2 standard requires the use of TLS.
    """

    refresh_url: str | None = None
    """The URL to be used for obtaining refresh tokens.

    This MUST be in the form of a URL. The OAuth2 standard requires the use of TLS.
    """

    scopes: dict[str, str] | None = None
    """
    **REQUIRED** for ``oauth2``. The available scopes for the OAuth2 security scheme. A map between the scope name and a
    short description for it the map MAY be empty.
    """
