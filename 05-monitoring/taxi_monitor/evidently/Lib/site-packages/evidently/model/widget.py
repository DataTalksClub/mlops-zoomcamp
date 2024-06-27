#!/usr/bin/env python
# coding: utf-8
# pylint: disable=invalid-name
import dataclasses
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import Iterable
from typing import List
from typing import Optional
from typing import Union


@dataclass()
class TriggeredAlertStats:
    period: int
    last_24h: int


@dataclass
class AlertStats:
    """
    Attributes:
        active: Number of active alerts.
        eggs: An integer count of the eggs we have laid.
    """

    active: int
    triggered: TriggeredAlertStats


@dataclass
class Insight:
    """
    Attributes:
        title: Insight title
        severity: Severity level for insight information (one of 'info', 'warning', 'error', 'success')
        text: Insidght information
    """

    title: str
    severity: str
    text: str


@dataclass
class Alert:
    value: Union[str, int, float]
    state: str
    text: str
    longText: str


@dataclass
class AdditionalGraphInfo:
    id: str
    params: Any


@dataclass
class PlotlyGraphInfo:
    data: Any
    layout: Any
    id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))


class WidgetType(Enum):
    COUNTER = "counter"
    TABLE = "table"
    BIG_TABLE = "big_table"
    BIG_GRAPH = "big_graph"
    RICH_DATA = "rich_data"
    TABBED_GRAPH = "tabbed_graph"
    TABS = "tabs"


@dataclass
class BaseWidgetInfo:
    type: str
    title: str
    size: int
    id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))
    details: str = ""
    alertsPosition: Optional[str] = None
    alertStats: Optional[AlertStats] = None
    params: Any = None
    insights: Iterable[Insight] = ()
    additionalGraphs: Iterable[Union[AdditionalGraphInfo, "BaseWidgetInfo", PlotlyGraphInfo]] = ()
    alerts: Iterable[Alert] = ()
    tabs: Iterable["TabInfo"] = ()
    widgets: Iterable["BaseWidgetInfo"] = ()
    pageSize: int = 5

    def get_additional_graphs(self) -> List[Union[AdditionalGraphInfo, PlotlyGraphInfo, "BaseWidgetInfo"]]:
        return list(self.additionalGraphs) + [
            graph for widget in self.widgets for graph in widget.get_additional_graphs()
        ]


@dataclass
class TabInfo:
    id: str
    title: str
    widget: BaseWidgetInfo
