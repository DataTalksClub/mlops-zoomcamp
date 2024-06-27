from enum import Enum
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import plotly.io as pio

from evidently._pydantic_compat import BaseModel
from evidently.base_metric import ColumnName
from evidently.base_metric import Metric
from evidently.pydantic_utils import EvidentlyBaseModel
from evidently.tests.base_test import Test
from evidently.tests.base_test import TestStatus

if TYPE_CHECKING:
    from .base import PanelValue

COLOR_DISCRETE_SEQUENCE = (
    "#ed0400",
    "#0a5f38",
    "#6c3461",
    "#71aa34",
    "#6b8ba4",
    "#60460f",
    "#a00498",
    "#017b92",
    "#ffad01",
    "#464196",
)

pio.templates[pio.templates.default].layout.colorway = COLOR_DISCRETE_SEQUENCE


class PlotType(Enum):
    # todo: move it to core lib?
    SCATTER = "scatter"
    BAR = "bar"
    LINE = "line"
    HISTOGRAM = "histogram"


class HistBarMode(Enum):
    STACK = "stack"
    GROUP = "group"
    OVERLAY = "overlay"
    RELATIVE = "relative"


class CounterAgg(Enum):
    SUM = "sum"
    LAST = "last"
    NONE = "none"


class TestSuitePanelType(Enum):
    AGGREGATE = "aggregate"
    DETAILED = "detailed"


def get_nested(d: dict, path: List[str]):
    if len(path) == 1:
        return d[path[0]]
    return get_nested(d[path[0]], path[1:])


_not_set = object()


def _getattr_or_getitem(obj: Any, item: str, default=_not_set):
    if isinstance(obj, dict):
        if default is _not_set:
            return obj[item]
        return obj.get(item, default)
    if default is _not_set:
        return getattr(obj, item)
    return getattr(obj, item, default)


def getattr_nested(obj: Any, path: List[str], default=_not_set):
    item = path[0]
    if len(path) == 1:
        return _getattr_or_getitem(obj, item, default)
    return getattr_nested(_getattr_or_getitem(obj, item, default), path[1:], default)


def _flatten_params_rec(obj: Any, paths: List[str]) -> List[Tuple[List[str], str]]:
    res = []
    if isinstance(obj, ColumnName) and obj == ColumnName.from_any(obj.name):
        return [(paths, obj.name)]
    if isinstance(obj, BaseModel):
        for field_name, field in obj.__fields__.items():
            if isinstance(obj, EvidentlyBaseModel) and field_name == "type":
                continue
            field_value = getattr(obj, field_name)
            if field_value == field.default:
                continue
            if isinstance(field.type_, type) and issubclass(field.type_, BaseModel):
                res.extend(_flatten_params_rec(field_value, paths + [field_name]))
            else:
                res.append((paths + [field_name], str(field_value)))
    return res


def _flatten_params(obj: EvidentlyBaseModel) -> Dict[str, str]:
    return {".".join(path): val for path, val in _flatten_params_rec(obj, [])}


def _get_metric_hover(metric: Metric, value: "PanelValue"):
    params = []
    for name, v in metric.dict().items():
        if name in ["type"]:
            continue
        if v is None:
            continue
        params.append(f"{name}: {v}")
    params_join = "<br>".join(params)
    hover = f"<b>Timestamp: %{{x}}</b><br><b>Value: %{{y}}</b><br>{params_join}<br>.{value.field_path}"
    return hover


TEST_COLORS = {
    TestStatus.ERROR: "#6B8BA4",
    TestStatus.FAIL: "#ed0400",
    TestStatus.WARNING: "#ffad01",
    TestStatus.SUCCESS: "#0a5f38",
    TestStatus.SKIPPED: "#a00498",
}

tests_colors_order = {ts: i for i, ts in enumerate(TEST_COLORS)}


def _get_test_hover(test: Test):
    params = [f"{k}: {v}" for k, v in _flatten_params(test).items()]
    params_join = "<br>".join(params)
    hover = f"<b>Timestamp: %{{x}}</b><br><b>{test.name}</b><br>{params_join}<br>%{{customdata}}<br>"
    return hover
