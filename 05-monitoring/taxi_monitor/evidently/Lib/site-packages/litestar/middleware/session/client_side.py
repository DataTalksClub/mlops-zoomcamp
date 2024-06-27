from __future__ import annotations

import binascii
import contextlib
import re
import time
from base64 import b64decode, b64encode
from dataclasses import dataclass, field, fields
from os import urandom
from typing import TYPE_CHECKING, Any, Final, Literal, Mapping

from litestar.datastructures import MutableScopeHeaders
from litestar.datastructures.cookie import Cookie
from litestar.enums import ScopeType
from litestar.exceptions import (
    ImproperlyConfiguredException,
    MissingDependencyException,
)
from litestar.serialization import decode_json, encode_json
from litestar.types import Empty, Scopes
from litestar.utils.dataclass import extract_dataclass_items

from .base import ONE_DAY_IN_SECONDS, BaseBackendConfig, BaseSessionBackend

__all__ = ("ClientSideSessionBackend", "CookieBackendConfig")


try:
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError as e:
    raise MissingDependencyException("cryptography") from e

if TYPE_CHECKING:
    from litestar.connection import ASGIConnection
    from litestar.types import Message, Scope, ScopeSession

NONCE_SIZE = 12
CHUNK_SIZE = 4096 - 64
AAD = b"additional_authenticated_data="
SET_COOKIE_INCLUDE = {f.name for f in fields(Cookie) if f.name not in {"key", "secret"}}
CLEAR_COOKIE_INCLUDE = {f.name for f in fields(Cookie) if f.name not in {"key", "secret", "max_age"}}


class ClientSideSessionBackend(BaseSessionBackend["CookieBackendConfig"]):
    """Cookie backend for SessionMiddleware."""

    __slots__ = (
        "_clear_cookie_params",
        "_set_cookie_params",
        "aesgcm",
        "cookie_re",
    )

    def __init__(self, config: CookieBackendConfig) -> None:
        """Initialize ``ClientSideSessionBackend``.

        Args:
            config: SessionCookieConfig instance.
        """
        super().__init__(config)
        self.aesgcm = AESGCM(config.secret)
        self.cookie_re = re.compile(rf"{self.config.key}(?:-\d+)?")
        self._set_cookie_params: Final[Mapping[str, Any]] = dict(
            extract_dataclass_items(config, exclude_none=True, include=SET_COOKIE_INCLUDE)
        )
        self._clear_cookie_params: Final[Mapping[str, Any]] = dict(
            extract_dataclass_items(config, exclude_none=True, include=CLEAR_COOKIE_INCLUDE)
        )

    def dump_data(self, data: Any, scope: Scope | None = None) -> list[bytes]:
        """Given serializable data, including pydantic models and numpy types, dump it into a bytes string, encrypt,
        encode and split it into chunks of the desirable size.

        Args:
            data: Data to serialize, encrypt, encode and chunk.
            scope: The ASGI connection scope.

        Notes:
            - The returned list is composed of a chunks of a single base64 encoded
              string that is encrypted using AES-CGM.

        Returns:
            List of encoded bytes string of a maximum length equal to the ``CHUNK_SIZE`` constant.
        """
        serialized = self.serialize_data(data, scope)
        associated_data = encode_json({"expires_at": round(time.time()) + self.config.max_age})
        nonce = urandom(NONCE_SIZE)
        encrypted = self.aesgcm.encrypt(nonce, serialized, associated_data=associated_data)
        encoded = b64encode(nonce + encrypted + AAD + associated_data)
        return [encoded[i : i + CHUNK_SIZE] for i in range(0, len(encoded), CHUNK_SIZE)]

    def load_data(self, data: list[bytes]) -> dict[str, Any]:
        """Given a list of strings, decodes them into the session object.

        Args:
            data: A list of strings derived from the request's session cookie(s).

        Returns:
            A deserialized session value.
        """
        decoded = b64decode(b"".join(data))
        nonce = decoded[:NONCE_SIZE]
        aad_starts_from = decoded.find(AAD)
        associated_data = decoded[aad_starts_from:].replace(AAD, b"") if aad_starts_from != -1 else None
        if associated_data and decode_json(value=associated_data)["expires_at"] > round(time.time()):
            encrypted_session = decoded[NONCE_SIZE:aad_starts_from]
            decrypted = self.aesgcm.decrypt(nonce, encrypted_session, associated_data=associated_data)
            return self.deserialize_data(decrypted)
        return {}

    def get_cookie_keys(self, connection: ASGIConnection) -> list[str]:
        """Return a list of cookie-keys from the connection if they match the session-cookie pattern.

        Args:
            connection: An ASGIConnection instance

        Returns:
            A list of session-cookie keys
        """
        return sorted(key for key in connection.cookies if self.cookie_re.fullmatch(key))

    def get_cookie_key_set(self, connection: ASGIConnection) -> set[str]:
        """Return a set of cookie-keys from the connection if they match the session-cookie pattern.

        .. versionadded:: 2.8.3

        Args:
            connection: An ASGIConnection instance

        Returns:
            A set of session-cookie keys
        """
        return {key for key in connection.cookies if self.cookie_re.fullmatch(key)}

    def _create_session_cookies(self, data: list[bytes]) -> list[Cookie]:
        """Create a list of cookies containing the session data.
        If the data is split into multiple cookies, the key will be of the format ``session-{segment number}``,
        however if only one cookie is needed, the key will be ``session``.
        """
        cookie_params = self._set_cookie_params

        if len(data) == 1:
            return [
                Cookie(
                    value=data[0].decode("utf-8"),
                    key=self.config.key,
                    **cookie_params,
                )
            ]

        return [
            Cookie(
                value=datum.decode("utf-8"),
                key=f"{self.config.key}-{i}",
                **cookie_params,
            )
            for i, datum in enumerate(data)
        ]

    async def store_in_message(self, scope_session: ScopeSession, message: Message, connection: ASGIConnection) -> None:
        """Store data from ``scope_session`` in ``Message`` in the form of cookies. If the contents of ``scope_session``
        are too large to fit a single cookie, it will be split across several cookies, following the naming scheme of
        ``<cookie key>-<n>``. If the session is empty or shrinks, cookies will be cleared by setting their value to
        ``"null"``

        Args:
            scope_session: Current session to store
            message: Outgoing send-message
            connection: Originating ASGIConnection containing the scope

        Returns:
            None
        """

        scope = connection.scope
        headers = MutableScopeHeaders.from_message(message)
        connection_cookies = self.get_cookie_key_set(connection)
        response_cookies: set[str] = set()

        if scope_session and scope_session is not Empty:
            data = self.dump_data(scope_session, scope=scope)
            for cookie in self._create_session_cookies(data):
                headers.add("Set-Cookie", cookie.to_header(header=""))
                response_cookies.add(cookie.key)

            cookies_to_clear = connection_cookies - response_cookies
        else:
            cookies_to_clear = connection_cookies

        for cookie_key in cookies_to_clear:
            headers.add(
                "Set-Cookie",
                Cookie(value="null", key=cookie_key, expires=0, **self._clear_cookie_params).to_header(header=""),
            )

    async def load_from_connection(self, connection: ASGIConnection) -> dict[str, Any]:
        """Load session data from a connection's session-cookies and return it as a dictionary.

        Args:
            connection: Originating ASGIConnection

        Returns:
            The session data
        """
        if cookie_keys := self.get_cookie_keys(connection):
            data = [connection.cookies[key].encode("utf-8") for key in cookie_keys]
            # If these exceptions occur, the session must remain empty so do nothing.
            with contextlib.suppress(InvalidTag, binascii.Error):
                return self.load_data(data)
        return {}

    def get_session_id(self, connection: ASGIConnection) -> str | None:
        return None


@dataclass
class CookieBackendConfig(BaseBackendConfig[ClientSideSessionBackend]):  # pyright: ignore
    """Configuration for [SessionMiddleware] middleware."""

    _backend_class = ClientSideSessionBackend

    secret: bytes
    """A secret key to use for generating an encryption key.

    Must have a length of 16 (128 bits), 24 (192 bits) or 32 (256 bits) characters.
    """
    key: str = field(default="session")
    """Key to use for the cookie inside the header, e.g. ``session=<data>`` where ``session`` is the cookie key and
    ``<data>`` is the session data.

    Notes:
        - If a session cookie exceeds 4KB in size it is split. In this case the key will be of the format
          ``session-{segment number}``.

    """
    max_age: int = field(default=ONE_DAY_IN_SECONDS * 14)
    """Maximal age of the cookie before its invalidated."""
    scopes: Scopes = field(default_factory=lambda: {ScopeType.HTTP, ScopeType.WEBSOCKET})
    """Scopes for the middleware - options are ``http`` and ``websocket`` with the default being both"""
    path: str = field(default="/")
    """Path fragment that must exist in the request url for the cookie to be valid.

    Defaults to ``'/'``.
    """
    domain: str | None = field(default=None)
    """Domain for which the cookie is valid."""
    secure: bool = field(default=False)
    """Https is required for the cookie."""
    httponly: bool = field(default=True)
    """Forbids javascript to access the cookie via 'Document.cookie'."""
    samesite: Literal["lax", "strict", "none"] = field(default="lax")
    """Controls whether or not a cookie is sent with cross-site requests.

    Defaults to ``lax``.
    """
    exclude: str | list[str] | None = field(default=None)
    """A pattern or list of patterns to skip in the session middleware."""
    exclude_opt_key: str = field(default="skip_session")
    """An identifier to use on routes to disable the session middleware for a particular route."""

    def __post_init__(self) -> None:
        if len(self.key) < 1 or len(self.key) > 256:
            raise ImproperlyConfiguredException("key must be a string with a length between 1-256")
        if self.max_age < 1:
            raise ImproperlyConfiguredException("max_age must be greater than 0")
        if len(self.secret) not in {16, 24, 32}:
            raise ImproperlyConfiguredException("secret length must be 16 (128 bit), 24 (192 bit) or 32 (256 bit)")
