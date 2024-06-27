import datetime
import traceback
import uuid
import warnings
from functools import wraps
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from evidently._pydantic_compat import BaseModel
from evidently._pydantic_compat import Field
from evidently._pydantic_compat import validator
from evidently.base_metric import Metric
from evidently.model.dashboard import DashboardInfo
from evidently.model.widget import BaseWidgetInfo
from evidently.pydantic_utils import EnumValueMixin
from evidently.pydantic_utils import EvidentlyBaseModel
from evidently.pydantic_utils import FieldPath
from evidently.pydantic_utils import PolymorphicModel
from evidently.renderers.html_widgets import CounterData
from evidently.renderers.html_widgets import WidgetSize
from evidently.renderers.html_widgets import counter
from evidently.report import Report
from evidently.suite.base_suite import ReportBase
from evidently.test_suite import TestSuite
from evidently.ui.type_aliases import PanelID
from evidently.ui.type_aliases import ProjectID
from evidently.ui.type_aliases import TabID

from .utils import getattr_nested

if TYPE_CHECKING:
    from evidently.ui.base import DataStorage


class ReportFilter(BaseModel):
    metadata_values: Dict[str, str]
    tag_values: List[str]
    include_test_suites: bool = False

    def filter(self, report: ReportBase):
        if not self.include_test_suites and isinstance(report, TestSuite):
            return False
        return all(report.metadata.get(key) == value for key, value in self.metadata_values.items()) and all(
            tag in report.tags for tag in self.tag_values
        )


class PanelValue(BaseModel):
    field_path: Union[str, FieldPath]
    metric_id: Optional[str] = None
    metric_fingerprint: Optional[str] = None
    metric_args: Dict[str, Union[EvidentlyBaseModel, Any]] = {}
    legend: Optional[str] = None

    def __init__(
        self,
        *,
        field_path: Union[str, FieldPath],
        metric_id: Optional[str] = None,
        metric_fingerprint: Optional[str] = None,
        metric_args: Dict[str, Union[EvidentlyBaseModel, Any]] = None,
        legend: Optional[str] = None,
        metric_hash: Optional[str] = None,
    ):
        # this __init__ is needed to support old-style metric_hash arg
        if metric_hash is not None:
            warnings.warn("metric_hash arg is deperecated, please use metric_fingerprint")
            metric_fingerprint = metric_hash
        super().__init__(
            field_path=field_path,
            metric_id=metric_id,
            metric_fingerprint=metric_fingerprint,
            metric_args=metric_args or {},
            legend=legend,
        )

    @property
    def field_path_str(self):
        if isinstance(self.field_path, FieldPath):
            return self.field_path.get_path()
        return self.field_path

    @validator("field_path")
    def validate_field_path(cls, value):
        if isinstance(value, FieldPath):
            value = value.get_path()
        return value

    def metric_matched(self, metric: Metric) -> bool:
        if self.metric_fingerprint is not None:
            return metric.get_fingerprint() == self.metric_fingerprint
        if self.metric_id is not None and self.metric_id != metric.get_id():
            return False
        for field, value in self.metric_args.items():
            try:
                if getattr_nested(metric, field.split(".")) != value:
                    return False
            except AttributeError:
                return False
        return True

    def get(self, report: ReportBase) -> Dict[Metric, Any]:
        results = {}
        metrics = []
        if isinstance(report, Report):
            metrics = report._first_level_metrics
        elif isinstance(report, TestSuite):
            metrics = report._inner_suite.context.metrics
        for metric in metrics:
            if self.metric_matched(metric):
                try:
                    results[metric] = getattr_nested(metric.get_result(), self.field_path_str.split("."))
                except AttributeError:
                    pass
        return results


def assign_panel_id(f):
    @wraps(f)
    def inner(self: "DashboardPanel", *args, **kwargs) -> BaseWidgetInfo:
        r = f(self, *args, **kwargs)
        r.id = str(self.id)
        return r

    return inner


class DashboardPanel(EnumValueMixin, PolymorphicModel):
    id: PanelID = Field(default_factory=uuid.uuid4)
    title: str
    filter: ReportFilter
    size: WidgetSize = WidgetSize.FULL

    def build(
        self,
        data_storage: "DataStorage",
        project_id: ProjectID,
        timestamp_start: Optional[datetime.datetime],
        timestamp_end: Optional[datetime.datetime],
    ) -> BaseWidgetInfo:
        raise NotImplementedError

    def safe_build(
        self,
        data_storage: "DataStorage",
        project_id: ProjectID,
        timestamp_start: Optional[datetime.datetime],
        timestamp_end: Optional[datetime.datetime],
    ) -> BaseWidgetInfo:
        try:
            return self.build(data_storage, project_id, timestamp_start, timestamp_end)
        except Exception as e:
            traceback.print_exc()
            c = counter(counters=[CounterData(f"{e.__class__.__name__}: {e.args[0]}", "Error")])
            c.id = str(self.id)
            return c


class DashboardTab(BaseModel):
    id: TabID = Field(default_factory=uuid.uuid4)
    title: Optional[str] = "Untitled"


class DashboardConfig(BaseModel):
    name: str
    panels: List[DashboardPanel]
    tabs: List[DashboardTab] = []
    tab_id_to_panel_ids: Dict[str, List[str]] = {}

    def add_panel(
        self,
        panel: DashboardPanel,
        *,
        tab: Optional[Union[str, TabID, DashboardTab]] = None,
        create_if_not_exists=True,
    ):
        self.panels.append(panel)

        if tab is None:
            return

        result_tab = self._get_or_create_tab(tab, create_if_not_exists)

        tab_id_str = str(result_tab.id)
        panel_id_str = str(panel.id)

        tab_panel_ids = self.tab_id_to_panel_ids.get(tab_id_str, [])

        if panel_id_str not in tab_panel_ids:
            tab_panel_ids.append(panel_id_str)
        self.tab_id_to_panel_ids[tab_id_str] = tab_panel_ids

    def create_tab(self, title) -> DashboardTab:
        return self._get_or_create_tab(title)

    def _raise_if_tab_title_exists(self, tab_title: Optional[str]):
        if any(tab.title == tab_title for tab in self.tabs):
            raise ValueError(f"""tab with title "{tab_title}" already exists""")

    def _find_tab_by_id(self, tab_id: TabID) -> Optional[DashboardTab]:
        tabs = [t for t in self.tabs if t.id == tab_id]
        if len(tabs) == 0:
            return None
        return tabs[0]

    def _find_tab_by_title(self, title: str) -> Optional[DashboardTab]:
        tabs = [t for t in self.tabs if t.title == title]
        if len(tabs) == 0:
            return None
        return tabs[0]

    def _get_or_create_tab(
        self,
        tab_descriptor: Union[DashboardTab, TabID, str],
        create_if_not_exists=True,
    ) -> DashboardTab:
        tab: Optional[DashboardTab] = None
        to_create: Optional[DashboardTab] = None
        if isinstance(tab_descriptor, DashboardTab):
            tab = self._find_tab_by_id(tab_descriptor.id)
            to_create = tab_descriptor
        if isinstance(tab_descriptor, str):
            try:
                tab = self._find_tab_by_id(uuid.UUID(tab_descriptor))
            except ValueError:
                tab = self._find_tab_by_title(tab_descriptor)
                to_create = DashboardTab(title=tab_descriptor)
        if isinstance(tab_descriptor, TabID):
            tab = self._find_tab_by_id(tab_descriptor)

        if tab is not None:
            return tab

        if not create_if_not_exists or to_create is None:
            raise ValueError(f"""tab "{tab_descriptor}" not found""")

        self.tabs.append(to_create)
        return to_create

    def build(
        self,
        data_storage: "DataStorage",
        project_id: ProjectID,
        timestamp_start: Optional[datetime.datetime],
        timestamp_end: Optional[datetime.datetime],
    ):
        widgets = [p.safe_build(data_storage, project_id, timestamp_start, timestamp_end) for p in self.panels]

        return DashboardInfo(name=self.name, widgets=widgets)
