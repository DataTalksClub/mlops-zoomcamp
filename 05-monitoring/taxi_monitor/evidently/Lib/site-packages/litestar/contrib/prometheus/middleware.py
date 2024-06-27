from __future__ import annotations

import time
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, ClassVar, cast

from litestar.connection.request import Request
from litestar.enums import ScopeType
from litestar.exceptions import MissingDependencyException
from litestar.middleware.base import AbstractMiddleware

__all__ = ("PrometheusMiddleware",)

from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR

try:
    import prometheus_client  # noqa: F401
except ImportError as e:
    raise MissingDependencyException("prometheus_client", "prometheus-client", "prometheus") from e

from prometheus_client import Counter, Gauge, Histogram

if TYPE_CHECKING:
    from prometheus_client.metrics import MetricWrapperBase

    from litestar.contrib.prometheus import PrometheusConfig
    from litestar.types import ASGIApp, Message, Receive, Scope, Send


class PrometheusMiddleware(AbstractMiddleware):
    """Prometheus Middleware."""

    _metrics: ClassVar[dict[str, MetricWrapperBase]] = {}

    def __init__(self, app: ASGIApp, config: PrometheusConfig) -> None:
        """Middleware that adds Prometheus instrumentation to the application.

        Args:
            app: The ``next`` ASGI app to call.
            config: An instance of :class:`PrometheusConfig <.contrib.prometheus.PrometheusConfig>`
        """
        super().__init__(app=app, scopes=config.scopes, exclude=config.exclude, exclude_opt_key=config.exclude_opt_key)
        self._config = config
        self._kwargs: dict[str, Any] = {}

        if self._config.buckets is not None:
            self._kwargs["buckets"] = self._config.buckets

    def request_count(self, labels: dict[str, str | int | float]) -> Counter:
        metric_name = f"{self._config.prefix}_requests_total"

        if metric_name not in PrometheusMiddleware._metrics:
            PrometheusMiddleware._metrics[metric_name] = Counter(
                name=metric_name,
                documentation="Total requests",
                labelnames=[*labels.keys()],
            )

        return cast("Counter", PrometheusMiddleware._metrics[metric_name])

    def request_time(self, labels: dict[str, str | int | float]) -> Histogram:
        metric_name = f"{self._config.prefix}_request_duration_seconds"

        if metric_name not in PrometheusMiddleware._metrics:
            PrometheusMiddleware._metrics[metric_name] = Histogram(
                name=metric_name,
                documentation="Request duration, in seconds",
                labelnames=[*labels.keys()],
                **self._kwargs,
            )
        return cast("Histogram", PrometheusMiddleware._metrics[metric_name])

    def requests_in_progress(self, labels: dict[str, str | int | float]) -> Gauge:
        metric_name = f"{self._config.prefix}_requests_in_progress"

        if metric_name not in PrometheusMiddleware._metrics:
            PrometheusMiddleware._metrics[metric_name] = Gauge(
                name=metric_name,
                documentation="Total requests currently in progress",
                labelnames=[*labels.keys()],
                multiprocess_mode="livesum",
            )
        return cast("Gauge", PrometheusMiddleware._metrics[metric_name])

    def requests_error_count(self, labels: dict[str, str | int | float]) -> Counter:
        metric_name = f"{self._config.prefix}_requests_error_total"

        if metric_name not in PrometheusMiddleware._metrics:
            PrometheusMiddleware._metrics[metric_name] = Counter(
                name=metric_name,
                documentation="Total errors in requests",
                labelnames=[*labels.keys()],
            )
        return cast("Counter", PrometheusMiddleware._metrics[metric_name])

    def _get_extra_labels(self, request: Request[Any, Any, Any]) -> dict[str, str]:
        """Get extra labels provided by the config and if they are callable, parse them.

        Args:
        request: The request object.

        Returns:
        A dictionary of extra labels.
        """

        return {k: str(v(request) if callable(v) else v) for k, v in (self._config.labels or {}).items()}

    def _get_default_labels(self, request: Request[Any, Any, Any]) -> dict[str, str | int | float]:
        """Get default label values from the request.

        Args:
            request: The request object.

        Returns:
            A dictionary of default labels.
        """

        path = request.url.path
        if self._config.group_path:
            path_parts = path.split("/")[1:]
            path = ""
            for path_parameter, path_parameter_value in request.scope.get("path_params", {}).items():
                for path_part in path_parts:
                    path_parameter_value = str(path_parameter_value)
                    if path_part == path_parameter_value:
                        path += f"/{{{path_parameter}}}"
                    else:
                        path += f"/{path_part}"
        return {
            "method": request.method if request.scope["type"] == ScopeType.HTTP else request.scope["type"],
            "path": path,
            "status_code": 200,
            "app_name": self._config.app_name,
        }

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI callable.

        Args:
            scope: The ASGI connection scope.
            receive: The ASGI receive function.
            send: The ASGI send function.

        Returns:
            None
        """

        request = Request[Any, Any, Any](scope, receive)

        if self._config.excluded_http_methods and request.method in self._config.excluded_http_methods:
            await self.app(scope, receive, send)
            return

        labels = {**self._get_default_labels(request), **self._get_extra_labels(request)}

        request_span = {"start_time": time.perf_counter(), "end_time": 0, "duration": 0, "status_code": 200}

        wrapped_send = self._get_wrapped_send(send, request_span)

        self.requests_in_progress(labels).labels(*labels.values()).inc()

        try:
            await self.app(scope, receive, wrapped_send)
        finally:
            extra: dict[str, Any] = {}
            if self._config.exemplars:
                extra["exemplar"] = self._config.exemplars(request)

            self.requests_in_progress(labels).labels(*labels.values()).dec()

            labels["status_code"] = request_span["status_code"]
            label_values = [*labels.values()]

            if request_span["status_code"] >= HTTP_500_INTERNAL_SERVER_ERROR:
                self.requests_error_count(labels).labels(*label_values).inc(**extra)

            self.request_count(labels).labels(*label_values).inc(**extra)
            self.request_time(labels).labels(*label_values).observe(request_span["duration"], **extra)

    def _get_wrapped_send(self, send: Send, request_span: dict[str, float]) -> Callable:
        @wraps(send)
        async def wrapped_send(message: Message) -> None:
            if message["type"] == "http.response.start":
                request_span["status_code"] = message["status"]

            if message["type"] == "http.response.body":
                end = time.perf_counter()
                request_span["duration"] = end - request_span["start_time"]
                request_span["end_time"] = end
            await send(message)

        return wrapped_send
