from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

__all__ = ("CSRFConfig",)


if TYPE_CHECKING:
    from litestar.types import Method


@dataclass
class CSRFConfig:
    """Configuration for CSRF (Cross Site Request Forgery) protection.

    To enable CSRF protection, pass an instance of this class to the :class:`Litestar <litestar.app.Litestar>` constructor using
    the 'csrf_config' key.
    """

    secret: str
    """A string that is used to create an HMAC to sign the CSRF token."""
    cookie_name: str = field(default="csrftoken")
    """The CSRF cookie name."""
    cookie_path: str = field(default="/")
    """The CSRF cookie path."""
    header_name: str = field(default="x-csrftoken")
    """The header that will be expected in each request."""
    cookie_secure: bool = field(default=False)
    """A boolean value indicating whether to set the ``Secure`` attribute on the cookie."""
    cookie_httponly: bool = field(default=False)
    """A boolean value indicating whether to set the ``HttpOnly`` attribute on the cookie."""
    cookie_samesite: Literal["lax", "strict", "none"] = field(default="lax")
    """The value to set in the ``SameSite`` attribute of the cookie."""
    cookie_domain: str | None = field(default=None)
    """Specifies which hosts can receive the cookie."""
    safe_methods: set[Method] = field(default_factory=lambda: {"GET", "HEAD", "OPTIONS"})
    """A set of "safe methods" that can set the cookie."""
    exclude: str | list[str] | None = field(default=None)
    """A pattern or list of patterns to skip in the CSRF middleware."""
    exclude_from_csrf_key: str = "exclude_from_csrf"
    """An identifier to use on routes to disable CSRF for a particular route."""
