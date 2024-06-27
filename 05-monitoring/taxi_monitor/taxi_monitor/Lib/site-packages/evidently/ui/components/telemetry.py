import os
from functools import partial
from typing import ClassVar
from typing import Dict

from iterative_telemetry import IterativeTelemetryLogger
from litestar.di import Provide

import evidently
from evidently.telemetry import DO_NOT_TRACK_ENV
from evidently.ui.components.base import Component
from evidently.ui.components.base import ComponentContext


class TelemetryComponent(Component):
    __section__: ClassVar = "telemetry"

    url: str = "http://35.232.253.5:8000/api/v1/s2s/event?ip_policy=strict"
    tool_name: str = "evidently"
    service_name: str = "service"
    token: str = "s2s.5xmxpip2ax4ut5rrihfjhb.uqcoh71nviknmzp77ev6rd"
    enabled: bool = True

    def get_dependencies(self, ctx: ComponentContext) -> Dict[str, Provide]:
        return {
            "log_event": Provide(self.get_event_logger, use_cache=True, sync_to_thread=False),
        }

    def get_event_logger(self):
        _event_logger = IterativeTelemetryLogger(
            self.tool_name,
            evidently.__version__,
            url=self.url,
            token=self.token,
            enabled=self.enabled and os.environ.get(DO_NOT_TRACK_ENV, None) is None,
        )
        return partial(_event_logger.send_event, self.service_name)
