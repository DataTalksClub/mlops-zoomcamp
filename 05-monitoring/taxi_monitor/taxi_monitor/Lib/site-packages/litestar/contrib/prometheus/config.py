from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Mapping, Sequence

from litestar.contrib.prometheus.middleware import (
    PrometheusMiddleware,
)
from litestar.exceptions import MissingDependencyException
from litestar.middleware.base import DefineMiddleware

__all__ = ("PrometheusConfig",)


try:
    import prometheus_client  # noqa: F401
except ImportError as e:
    raise MissingDependencyException("prometheus_client", "prometheus-client", "prometheus") from e


if TYPE_CHECKING:
    from litestar.connection.request import Request
    from litestar.types import Method, Scopes


@dataclass
class PrometheusConfig:
    """Configuration class for the PrometheusConfig middleware."""

    app_name: str = field(default="litestar")
    """The name of the application to use in the metrics."""
    prefix: str = "litestar"
    """The prefix to use for the metrics."""
    labels: Mapping[str, str | Callable] | None = field(default=None)
    """A mapping of labels to add to the metrics. The values can be either a string or a callable that returns a string."""
    exemplars: Callable[[Request], dict] | None = field(default=None)
    """A callable that returns a list of exemplars to add to the metrics. Only supported in opementrics-text exposition format."""
    buckets: list[str | float] | None = field(default=None)
    """A list of buckets to use for the histogram."""
    excluded_http_methods: Method | Sequence[Method] | None = field(default=None)
    """A list of http methods to exclude from the metrics."""
    exclude_unhandled_paths: bool = field(default=False)
    """Whether to ignore requests for unhandled paths from the metrics."""
    exclude: str | list[str] | None = field(default=None)
    """A pattern or list of patterns for routes to exclude from the metrics."""
    exclude_opt_key: str | None = field(default=None)
    """A key or list of keys in ``opt`` with which a route handler can "opt-out" of the middleware."""
    scopes: Scopes | None = field(default=None)
    """ASGI scopes processed by the middleware, if None both ``http`` and ``websocket`` will be processed."""
    middleware_class: type[PrometheusMiddleware] = field(default=PrometheusMiddleware)
    """The middleware class to use.
    """
    group_path: bool = field(default=False)
    """Whether to group paths in the metrics to avoid cardinality explosion.
    """

    @property
    def middleware(self) -> DefineMiddleware:
        """Create an instance of :class:`DefineMiddleware <litestar.middleware.base.DefineMiddleware>` that wraps with.

        [PrometheusMiddleware][litestar.contrib.prometheus.PrometheusMiddleware]. or a subclass
        of this middleware.

        Returns:
            An instance of ``DefineMiddleware``.
        """
        return DefineMiddleware(self.middleware_class, config=self)
