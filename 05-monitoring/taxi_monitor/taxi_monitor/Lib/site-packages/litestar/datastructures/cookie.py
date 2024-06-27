from __future__ import annotations

from dataclasses import asdict, dataclass, field
from http.cookies import SimpleCookie
from typing import Any, Literal

__all__ = ("Cookie",)


@dataclass
class Cookie:
    """Container class for defining a cookie using the ``Set-Cookie`` header.

    See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie for more details regarding this header.
    """

    key: str
    """Key for the cookie."""
    path: str = "/"
    """Path fragment that must exist in the request url for the cookie to be valid.

    Defaults to ``/``.
    """
    value: str | None = field(default=None)
    """Value for the cookie, if none given defaults to empty string."""
    max_age: int | None = field(default=None)
    """Maximal age of the cookie before its invalidated."""
    expires: int | None = field(default=None)
    """Seconds from now until the cookie expires."""
    domain: str | None = field(default=None)
    """Domain for which the cookie is valid."""
    secure: bool | None = field(default=None)
    """Https is required for the cookie."""
    httponly: bool | None = field(default=None)
    """Forbids javascript to access the cookie via ``document.cookie``."""
    samesite: Literal["lax", "strict", "none"] = field(default="lax")
    """Controls whether or not a cookie is sent with cross-site requests.

    Defaults to 'lax'.
    """
    description: str | None = field(default=None)
    """Description of the response cookie header for OpenAPI documentation."""
    documentation_only: bool = field(default=False)
    """Defines the Cookie instance as for OpenAPI documentation purpose only."""

    @property
    def simple_cookie(self) -> SimpleCookie:
        """Get a simple cookie object from the values.

        Returns:
            A :class:`SimpleCookie <http.cookies.SimpleCookie>`
        """
        simple_cookie: SimpleCookie = SimpleCookie()
        simple_cookie[self.key] = self.value or ""

        namespace = simple_cookie[self.key]
        for key, value in self.dict.items():
            if key in {"key", "value"}:
                continue
            if value is not None:
                updated_key = key
                if updated_key == "max_age":
                    updated_key = "max-age"
                namespace[updated_key] = value

        return simple_cookie

    def to_header(self, **kwargs: Any) -> str:
        """Return a string representation suitable to be sent as HTTP headers.

        Args:
            **kwargs: Any kwargs to pass to the simple cookie output method.
        """
        return self.simple_cookie.output(**kwargs).strip()

    def to_encoded_header(self) -> tuple[bytes, bytes]:
        """Create encoded header for ASGI ``send``.

        Returns:
            A two tuple of bytes.
        """
        return b"set-cookie", self.to_header(header="").strip().encode("latin-1")

    @property
    def dict(self) -> dict[str, Any]:
        """Get the cookie as a dict.

        Returns:
            A dict of values
        """
        return {
            k: v
            for k, v in asdict(self).items()
            if k not in {"documentation_only", "description", "__pydantic_initialised__"}
        }

    def __hash__(self) -> int:
        return hash((self.key, self.path, self.domain))

    def __eq__(self, other: Any) -> bool:
        """Determine whether two cookie instances are equal according to the cookie spec, i.e. hey have a similar path,
        domain and key.

        Args:
            other: An arbitrary value

        Returns:
            A boolean
        """
        if isinstance(other, Cookie):
            return other.key == self.key and other.path == self.path and other.domain == self.domain
        return False
