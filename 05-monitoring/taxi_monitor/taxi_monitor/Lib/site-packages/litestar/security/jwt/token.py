from __future__ import annotations

import dataclasses
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from jose import JWSError, JWTError, jwt

from litestar.exceptions import ImproperlyConfiguredException, NotAuthorizedException

if TYPE_CHECKING:
    from typing_extensions import Self


__all__ = ("Token",)


def _normalize_datetime(value: datetime) -> datetime:
    """Convert the given value into UTC and strip microseconds.

    Args:
        value: A datetime instance

    Returns:
        A datetime instance
    """
    if value.tzinfo is not None:
        value.astimezone(timezone.utc)

    return value.replace(microsecond=0)


@dataclass
class Token:
    """JWT Token DTO."""

    exp: datetime
    """Expiration - datetime for token expiration."""
    sub: str
    """Subject - usually a unique identifier of the user or equivalent entity."""
    iat: datetime = field(default_factory=lambda: _normalize_datetime(datetime.now(timezone.utc)))
    """Issued at - should always be current now."""
    iss: str | None = field(default=None)
    """Issuer - optional unique identifier for the issuer."""
    aud: str | None = field(default=None)
    """Audience - intended audience."""
    jti: str | None = field(default=None)
    """JWT ID - a unique identifier of the JWT between different issuers."""
    extras: dict[str, Any] = field(default_factory=dict)
    """Extra fields that were found on the JWT token."""

    def __post_init__(self) -> None:
        if len(self.sub) < 1:
            raise ImproperlyConfiguredException("sub must be a string with a length greater than 0")

        if isinstance(self.exp, datetime) and (
            (exp := _normalize_datetime(self.exp)).timestamp()
            >= _normalize_datetime(datetime.now(timezone.utc)).timestamp()
        ):
            self.exp = exp
        else:
            raise ImproperlyConfiguredException("exp value must be a datetime in the future")

        if isinstance(self.iat, datetime) and (
            (iat := _normalize_datetime(self.iat)).timestamp()
            <= _normalize_datetime(datetime.now(timezone.utc)).timestamp()
        ):
            self.iat = iat
        else:
            raise ImproperlyConfiguredException("iat must be a current or past time")

    @classmethod
    def decode(cls, encoded_token: str, secret: str | dict[str, str], algorithm: str) -> Self:
        """Decode a passed in token string and returns a Token instance.

        Args:
            encoded_token: A base64 string containing an encoded JWT.
            secret: The secret with which the JWT is encoded. It may optionally be an individual JWK or JWS set dict
            algorithm: The algorithm used to encode the JWT.

        Returns:
            A decoded Token instance.

        Raises:
            NotAuthorizedException: If the token is invalid.
        """
        try:
            payload = jwt.decode(token=encoded_token, key=secret, algorithms=[algorithm], options={"verify_aud": False})
            exp = datetime.fromtimestamp(payload.pop("exp"), tz=timezone.utc)
            iat = datetime.fromtimestamp(payload.pop("iat"), tz=timezone.utc)
            field_names = {f.name for f in dataclasses.fields(Token)}
            extra_fields = payload.keys() - field_names
            extras = payload.pop("extras", {})
            for key in extra_fields:
                extras[key] = payload.pop(key)
            return cls(exp=exp, iat=iat, **payload, extras=extras)
        except (KeyError, JWTError, ImproperlyConfiguredException) as e:
            raise NotAuthorizedException("Invalid token") from e

    def encode(self, secret: str, algorithm: str) -> str:
        """Encode the token instance into a string.

        Args:
            secret: The secret with which the JWT is encoded.
            algorithm: The algorithm used to encode the JWT.

        Returns:
            An encoded token string.

        Raises:
            ImproperlyConfiguredException: If encoding fails.
        """
        try:
            return jwt.encode(
                claims={k: v for k, v in asdict(self).items() if v is not None}, key=secret, algorithm=algorithm
            )
        except (JWTError, JWSError) as e:
            raise ImproperlyConfiguredException("Failed to encode token") from e
