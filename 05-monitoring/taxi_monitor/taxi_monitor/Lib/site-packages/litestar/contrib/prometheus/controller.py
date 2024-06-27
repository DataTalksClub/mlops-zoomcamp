from __future__ import annotations

import os

from litestar import Controller, get
from litestar.exceptions import MissingDependencyException
from litestar.response import Response

try:
    import prometheus_client  # noqa: F401
except ImportError as e:
    raise MissingDependencyException("prometheus_client", "prometheus-client", "prometheus") from e

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    CollectorRegistry,
    generate_latest,
    multiprocess,
)
from prometheus_client.openmetrics.exposition import (
    CONTENT_TYPE_LATEST as OPENMETRICS_CONTENT_TYPE_LATEST,
)
from prometheus_client.openmetrics.exposition import (
    generate_latest as openmetrics_generate_latest,
)

__all__ = [
    "PrometheusController",
]


class PrometheusController(Controller):
    """Controller for Prometheus endpoints."""

    path: str = "/metrics"
    """The path to expose the metrics on."""
    openmetrics_format: bool = False
    """Whether to expose the metrics in OpenMetrics format."""

    @get()
    async def get(self) -> Response:
        registry = REGISTRY
        if "prometheus_multiproc_dir" in os.environ or "PROMETHEUS_MULTIPROC_DIR" in os.environ:
            registry = CollectorRegistry()
            multiprocess.MultiProcessCollector(registry)  # type: ignore[no-untyped-call]

        if self.openmetrics_format:
            headers = {"Content-Type": OPENMETRICS_CONTENT_TYPE_LATEST}
            return Response(openmetrics_generate_latest(registry), status_code=200, headers=headers)  # type: ignore[no-untyped-call]

        headers = {"Content-Type": CONTENT_TYPE_LATEST}
        return Response(generate_latest(registry), status_code=200, headers=headers)
