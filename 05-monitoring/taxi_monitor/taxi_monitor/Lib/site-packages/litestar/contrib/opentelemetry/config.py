from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

from litestar.contrib.opentelemetry._utils import get_route_details_from_scope
from litestar.contrib.opentelemetry.middleware import (
    OpenTelemetryInstrumentationMiddleware,
)
from litestar.exceptions import MissingDependencyException
from litestar.middleware.base import DefineMiddleware

__all__ = ("OpenTelemetryConfig",)


try:
    import opentelemetry  # noqa: F401
except ImportError as e:
    raise MissingDependencyException("opentelemetry") from e


from opentelemetry.trace import Span, TracerProvider  # pyright: ignore

if TYPE_CHECKING:
    from opentelemetry.metrics import Meter, MeterProvider

    from litestar.types import Scope, Scopes

OpenTelemetryHookHandler = Callable[[Span, dict], None]


@dataclass
class OpenTelemetryConfig:
    """Configuration class for the OpenTelemetry middleware.

    Consult the [OpenTelemetry ASGI documentation](https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/asgi/asgi.html) for more info about the configuration options.
    """

    scope_span_details_extractor: Callable[[Scope], tuple[str, dict[str, Any]]] = field(
        default=get_route_details_from_scope
    )
    """Callback which should return a string and a tuple, representing the desired default span name and a dictionary
    with any additional span attributes to set.
    """
    server_request_hook_handler: OpenTelemetryHookHandler | None = field(default=None)
    """Optional callback which is called with the server span and ASGI scope object for every incoming request."""
    client_request_hook_handler: OpenTelemetryHookHandler | None = field(default=None)
    """Optional callback which is called with the internal span and an ASGI scope which is sent as a dictionary for when
    the method receive is called.
    """
    client_response_hook_handler: OpenTelemetryHookHandler | None = field(default=None)
    """Optional callback which is called with the internal span and an ASGI event which is sent as a dictionary for when
    the method send is called.
    """
    meter_provider: MeterProvider | None = field(default=None)
    """Optional meter provider to use.

    If omitted the current globally configured one is used.
    """
    tracer_provider: TracerProvider | None = field(default=None)
    """Optional tracer provider to use.

    If omitted the current globally configured one is used.
    """
    meter: Meter | None = field(default=None)
    """Optional meter to use.

    If omitted the provided meter provider or the global one will be used.
    """
    exclude: str | list[str] | None = field(default=None)
    """A pattern or list of patterns to skip in the Allowed Hosts middleware."""
    exclude_opt_key: str | None = field(default=None)
    """An identifier to use on routes to disable hosts check for a particular route."""
    exclude_urls_env_key: str = "LITESTAR"
    """Key to use when checking whether a list of excluded urls is passed via ENV.

    OpenTelemetry supports excluding urls by passing an env in the format '{exclude_urls_env_key}_EXCLUDED_URLS'. With
    the default being ``LITESTAR_EXCLUDED_URLS``.
    """
    scopes: Scopes | None = field(default=None)
    """ASGI scopes processed by the middleware, if None both ``http`` and ``websocket`` will be processed."""
    middleware_class: type[OpenTelemetryInstrumentationMiddleware] = field(
        default=OpenTelemetryInstrumentationMiddleware
    )
    """The middleware class to use.

    Should be a subclass of OpenTelemetry
    InstrumentationMiddleware][litestar.contrib.opentelemetry.OpenTelemetryInstrumentationMiddleware].
    """

    @property
    def middleware(self) -> DefineMiddleware:
        """Create an instance of :class:`DefineMiddleware <litestar.middleware.base.DefineMiddleware>` that wraps with.

        [OpenTelemetry
        InstrumentationMiddleware][litestar.contrib.opentelemetry.OpenTelemetryInstrumentationMiddleware] or a subclass
        of this middleware.

        Returns:
            An instance of ``DefineMiddleware``.
        """
        return DefineMiddleware(self.middleware_class, config=self)
