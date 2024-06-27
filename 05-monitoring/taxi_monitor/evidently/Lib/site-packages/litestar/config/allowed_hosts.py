from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from litestar.exceptions import ImproperlyConfiguredException

__all__ = ("AllowedHostsConfig",)


if TYPE_CHECKING:
    from litestar.types import Scopes


@dataclass
class AllowedHostsConfig:
    """Configuration for allowed hosts protection.

    To enable allowed hosts protection, pass an instance of this class to the :class:`Litestar <litestar.app.Litestar>`
    constructor using the ``allowed_hosts`` key.
    """

    allowed_hosts: list[str] = field(default_factory=lambda: ["*"])
    """A list of trusted hosts.

    Use ``*.`` to allow all hosts, or prefix domains with ``*.`` to allow all sub domains.
    """
    exclude: str | list[str] | None = field(default=None)
    """A pattern or list of patterns to skip in the Allowed Hosts middleware."""
    exclude_opt_key: str | None = field(default=None)
    """An identifier to use on routes to disable hosts check for a particular route."""
    scopes: Scopes | None = field(default=None)
    """ASGI scopes processed by the middleware, if None both ``http`` and ``websocket`` will be processed."""
    www_redirect: bool = field(default=True)
    """A boolean dictating whether to redirect requests that start with ``www.`` and otherwise match a trusted host."""

    def __post_init__(self) -> None:
        """Ensure that the trusted hosts have correct domain wildcards."""
        for host in self.allowed_hosts:
            if host != "*" and "*" in host and not host.startswith("*."):
                raise ImproperlyConfiguredException(
                    "domain wildcards can only appear in the beginning of the domain, e.g. ``*.example.com``"
                )
