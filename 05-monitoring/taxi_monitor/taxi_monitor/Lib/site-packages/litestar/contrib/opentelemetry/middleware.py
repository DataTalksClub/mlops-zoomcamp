from __future__ import annotations

from typing import TYPE_CHECKING

from litestar.exceptions import MissingDependencyException
from litestar.middleware.base import AbstractMiddleware

__all__ = ("OpenTelemetryInstrumentationMiddleware",)


try:
    import opentelemetry  # noqa: F401
except ImportError as e:
    raise MissingDependencyException("opentelemetry") from e

from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from opentelemetry.util.http import get_excluded_urls

if TYPE_CHECKING:
    from litestar.contrib.opentelemetry import OpenTelemetryConfig
    from litestar.types import ASGIApp, Receive, Scope, Send


class OpenTelemetryInstrumentationMiddleware(AbstractMiddleware):
    """OpenTelemetry Middleware."""

    def __init__(self, app: ASGIApp, config: OpenTelemetryConfig) -> None:
        """Middleware that adds OpenTelemetry instrumentation to the application.

        Args:
            app: The ``next`` ASGI app to call.
            config: An instance of :class:`OpenTelemetryConfig <.contrib.opentelemetry.OpenTelemetryConfig>`
        """
        super().__init__(app=app, scopes=config.scopes, exclude=config.exclude, exclude_opt_key=config.exclude_opt_key)
        self.open_telemetry_middleware = OpenTelemetryMiddleware(
            app=app,
            client_request_hook=config.client_request_hook_handler,
            client_response_hook=config.client_response_hook_handler,
            default_span_details=config.scope_span_details_extractor,
            excluded_urls=get_excluded_urls(config.exclude_urls_env_key),
            meter=config.meter,
            meter_provider=config.meter_provider,
            server_request_hook=config.server_request_hook_handler,
            tracer_provider=config.tracer_provider,
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI callable.

        Args:
            scope: The ASGI connection scope.
            receive: The ASGI receive function.
            send: The ASGI send function.

        Returns:
            None
        """
        await self.open_telemetry_middleware(scope, receive, send)  # type: ignore[arg-type] # pyright: ignore[reportGeneralTypeIssues]
