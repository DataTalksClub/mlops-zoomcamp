from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from litestar.datastructures import Cookie, MutableScopeHeaders
from litestar.enums import ScopeType
from litestar.exceptions import ImproperlyConfiguredException
from litestar.middleware.session.base import ONE_DAY_IN_SECONDS, BaseBackendConfig, BaseSessionBackend
from litestar.types import Empty, Message, Scopes, ScopeSession
from litestar.utils.dataclass import extract_dataclass_items

__all__ = ("ServerSideSessionBackend", "ServerSideSessionConfig")


if TYPE_CHECKING:
    from litestar import Litestar
    from litestar.connection import ASGIConnection
    from litestar.stores.base import Store


class ServerSideSessionBackend(BaseSessionBackend["ServerSideSessionConfig"]):
    """Base class for server-side backends.

    Implements :class:`BaseSessionBackend` and defines and interface which subclasses can
    implement to facilitate the storage of session data.
    """

    def __init__(self, config: ServerSideSessionConfig) -> None:
        """Initialize ``ServerSideSessionBackend``

        Args:
            config: A subclass of ``ServerSideSessionConfig``
        """
        super().__init__(config=config)

    async def get(self, session_id: str, store: Store) -> bytes | None:
        """Retrieve data associated with ``session_id``.

        Args:
            session_id: The session-ID
            store: Store to retrieve the session data from

        Returns:
            The session data, if existing, otherwise ``None``.
        """
        max_age = int(self.config.max_age) if self.config.max_age is not None else None
        return await store.get(session_id, renew_for=max_age if self.config.renew_on_access else None)

    async def set(self, session_id: str, data: bytes, store: Store) -> None:
        """Store ``data`` under the ``session_id`` for later retrieval.

        If there is already data associated with ``session_id``, replace
        it with ``data`` and reset its expiry time

        Args:
            session_id: The session-ID
            data: Serialized session data
            store: Store to save the session data in

        Returns:
            None
        """
        expires_in = int(self.config.max_age) if self.config.max_age is not None else None
        await store.set(session_id, data, expires_in=expires_in)

    async def delete(self, session_id: str, store: Store) -> None:
        """Delete the data associated with ``session_id``. Fails silently if no such session-ID exists.

        Args:
            session_id: The session-ID
            store: Store to delete the session data from

        Returns:
            None
        """
        await store.delete(session_id)

    def get_session_id(self, connection: ASGIConnection) -> str:
        """Try to fetch session id from the connection. If one does not exist, generate one.

        If a session ID already exists in the cookies, it is returned.
        If there is no ID in the cookies but one in the connection state, then the session exists but has not yet
        been returned to the user.
        Otherwise, a new session must be created.

        Args:
            connection: Originating ASGIConnection containing the scope
        Returns:
            Session id str or None if the concept of a session id does not apply.
        """
        session_id = connection.cookies.get(self.config.key)
        if not session_id or session_id == "null":
            session_id = connection.get_session_id()
            if not session_id:
                session_id = self.generate_session_id()
        return session_id

    def generate_session_id(self) -> str:
        """Generate a new session-ID, with
        n=:attr:`session_id_bytes <ServerSideSessionConfig.session_id_bytes>` random bytes.

        Returns:
            A session-ID
        """
        return secrets.token_hex(self.config.session_id_bytes)

    async def store_in_message(self, scope_session: ScopeSession, message: Message, connection: ASGIConnection) -> None:
        """Store the necessary information in the outgoing ``Message`` by setting a cookie containing the session-ID.

        If the session is empty, a null-cookie will be set. Otherwise, the serialised
        data will be stored using :meth:`set <ServerSideSessionBackend.set>`, under the current session-id. If no session-ID
        exists, a new ID will be generated using :meth:`generate_session_id <ServerSideSessionBackend.generate_session_id>`.

        Args:
            scope_session: Current session to store
            message: Outgoing send-message
            connection: Originating ASGIConnection containing the scope

        Returns:
            None
        """
        scope = connection.scope
        store = self.config.get_store_from_app(scope["app"])
        headers = MutableScopeHeaders.from_message(message)
        session_id = self.get_session_id(connection)

        cookie_params = dict(extract_dataclass_items(self.config, exclude_none=True, include=Cookie.__dict__.keys()))

        if scope_session is Empty:
            await self.delete(session_id, store=store)
            headers.add(
                "Set-Cookie",
                Cookie(value="null", key=self.config.key, expires=0, **cookie_params).to_header(header=""),
            )
        else:
            serialised_data = self.serialize_data(scope_session, scope)
            await self.set(session_id=session_id, data=serialised_data, store=store)
            headers.add(
                "Set-Cookie", Cookie(value=session_id, key=self.config.key, **cookie_params).to_header(header="")
            )

    async def load_from_connection(self, connection: ASGIConnection) -> dict[str, Any]:
        """Load session data from a connection and return it as a dictionary to be used in the current application
        scope.

        The session-ID will be gathered from a cookie with the key set in
        :attr:`BaseBackendConfig.key`. If a cookie is found, its value will be used as the session-ID and data associated
        with this ID will be loaded using :meth:`get <ServerSideSessionBackend.get>`.
        If no cookie was found or no data was loaded from the store, this will return an
        empty dictionary.

        Args:
            connection: An ASGIConnection instance

        Returns:
            The current session data
        """
        if session_id := connection.cookies.get(self.config.key):
            store = self.config.get_store_from_app(connection.scope["app"])
            data = await self.get(session_id, store=store)
            if data is not None:
                return self.deserialize_data(data)
        return {}


@dataclass
class ServerSideSessionConfig(BaseBackendConfig[ServerSideSessionBackend]):  # pyright: ignore
    """Base configuration for server side backends."""

    _backend_class = ServerSideSessionBackend

    session_id_bytes: int = field(default=32)
    """Number of bytes used to generate a random session-ID."""
    renew_on_access: bool = field(default=False)
    """Renew expiry times of sessions when they're being accessed"""
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
    """Controls whether or not a cookie is sent with cross-site requests. Defaults to ``lax``."""
    exclude: str | list[str] | None = field(default=None)
    """A pattern or list of patterns to skip in the session middleware."""
    exclude_opt_key: str = field(default="skip_session")
    """An identifier to use on routes to disable the session middleware for a particular route."""
    store: str = "sessions"
    """Name of the :class:`Store <.stores.base.Store>` to use"""

    def __post_init__(self) -> None:
        if len(self.key) < 1 or len(self.key) > 256:
            raise ImproperlyConfiguredException("key must be a string with a length between 1-256")
        if self.max_age < 1:
            raise ImproperlyConfiguredException("max_age must be greater than 0")

    def get_store_from_app(self, app: Litestar) -> Store:
        """Get the store defined in :attr:`store` from an :class:`Litestar <.app.Litestar>` instance"""
        return app.stores.get(self.store)
