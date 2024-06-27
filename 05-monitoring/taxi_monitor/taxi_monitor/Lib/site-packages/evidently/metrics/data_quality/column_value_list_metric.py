from typing import Any
from typing import List
from typing import Optional
from typing import Tuple

import pandas as pd

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.calculations.data_quality import get_rows_count
from evidently.core import IncludeTags
from evidently.metric_results import DistributionIncluded
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import CounterData
from evidently.renderers.html_widgets import TabData
from evidently.renderers.html_widgets import counter
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import table_data
from evidently.renderers.html_widgets import widget_tabs


class ValueListStat(MetricResult):
    class Config:
        field_tags = {
            "values_in_list_dist": {IncludeTags.Extra},
            "values_not_in_list_dist": {IncludeTags.Extra},
            "rows_count": {IncludeTags.Extra},
        }

    def __init__(self, **data: Any):
        if "values_in_list" in data:
            values_in_list: List[Tuple[Any, int]] = data.pop("values_in_list")
            data["values_in_list_dist"] = DistributionIncluded(
                x=[v[0] for v in values_in_list], y=[v[1] for v in values_in_list]
            )
        if "values_not_in_list" in data:
            values_not_in_list: List[Tuple[Any, int]] = data.pop("values_not_in_list")
            data["values_not_in_list_dist"] = DistributionIncluded(
                x=[v[0] for v in values_not_in_list], y=[v[1] for v in values_not_in_list]
            )

        super().__init__(**data)

    number_in_list: int
    number_not_in_list: int
    share_in_list: float
    share_not_in_list: float
    rows_count: int
    values_in_list_dist: DistributionIncluded
    values_not_in_list_dist: DistributionIncluded

    @property
    def values_in_list(self) -> List[Tuple[Any, int]]:
        return [(x, y) for x, y in zip(self.values_in_list_dist.x, self.values_in_list_dist.y)]

    @property
    def values_not_in_list(self) -> List[Tuple[Any, int]]:
        return [(x, y) for x, y in zip(self.values_not_in_list_dist.x, self.values_not_in_list_dist.y)]


class ColumnValueListMetricResult(MetricResult):
    class Config:
        field_tags = {
            "current": {IncludeTags.Current},
            "reference": {IncludeTags.Reference},
            "column_name": {IncludeTags.Parameter},
            "values": {IncludeTags.Parameter},
        }

    column_name: str
    values: List[Any]
    current: ValueListStat
    reference: Optional[ValueListStat] = None


class ColumnValueListMetric(Metric[ColumnValueListMetricResult]):
    """Calculates count and shares of values in the predefined values list"""

    column_name: str
    values: Optional[list]

    def __init__(self, column_name: str, values: Optional[list] = None, options: AnyOptions = None) -> None:
        self.values = values
        self.column_name = column_name
        super().__init__(options=options)

    @staticmethod
    def _calculate_stats(values: list, column: pd.Series) -> ValueListStat:
        rows_count = get_rows_count(column)
        values_in_list = {}
        values_not_in_list = {}

        if rows_count == 0:
            number_in_list = 0
            number_not_in_list = 0
            share_in_list = 0.0
            share_not_in_list = 0.0

        else:
            value_counts = dict(column.value_counts(dropna=True))

            for value in value_counts:
                if value in values:
                    values_in_list[value] = value_counts[value]

                else:
                    values_not_in_list[value] = value_counts[value]

            number_in_list = sum(values_in_list.values())
            share_in_list = number_in_list / rows_count
            number_not_in_list = rows_count - number_in_list
            share_not_in_list = number_not_in_list / rows_count
            # fill other values from list with zeroes
            for value in values:
                if value not in values_in_list:
                    values_in_list[value] = 0

        return ValueListStat(
            number_in_list=number_in_list,
            number_not_in_list=number_not_in_list,
            share_in_list=share_in_list,
            share_not_in_list=share_not_in_list,
            values_in_list=[(k, v) for k, v in values_in_list.items()],
            values_not_in_list=[(k, v) for k, v in values_not_in_list.items()],
            rows_count=rows_count,
        )

    def calculate(self, data: InputData) -> ColumnValueListMetricResult:
        if data.reference_data is not None and self.column_name not in data.reference_data:
            raise ValueError(f"Column '{self.column_name}' is not in reference data.")

        if self.values is None:
            if data.reference_data is None:
                raise ValueError("Reference or values list should be present.")
            values = list(data.reference_data[self.column_name].unique())

        else:
            values = self.values

        if not values:
            raise ValueError("Values list should not be empty.")

        if self.column_name not in data.current_data:
            raise ValueError(f"Column '{self.column_name}' is not in current data.")

        current_stats = self._calculate_stats(values, data.current_data[self.column_name])

        if data.reference_data is not None:
            reference_stats: Optional[ValueListStat] = self._calculate_stats(
                values, data.reference_data[self.column_name]
            )

        else:
            reference_stats = None

        return ColumnValueListMetricResult(
            column_name=self.column_name,
            values=list(values),
            current=current_stats,
            reference=reference_stats,
        )


@default_renderer(wrap_type=ColumnValueListMetric)
class ColumnValueListMetricRenderer(MetricRenderer):
    @staticmethod
    def _get_table_stat(dataset_name: str, stats: ValueListStat) -> BaseWidgetInfo:
        matched_stat_headers = ["Value", "Count"]
        tabs = [
            TabData(
                title="In list (top-10)",
                widget=table_data(
                    title="",
                    column_names=matched_stat_headers,
                    data=[(k, v) for k, v in stats.values_in_list if v > 0][:10],
                ),
            ),
            TabData(
                title="Not found (top-10)",
                widget=table_data(
                    title="",
                    column_names=matched_stat_headers,
                    data=[(k, v) for k, v in stats.values_in_list if v <= 0][:10],
                ),
            ),
            TabData(
                title="Out of list (top-10)",
                widget=table_data(
                    title="",
                    column_names=matched_stat_headers,
                    data=list(stats.values_not_in_list)[:10],
                ),
            ),
        ]
        return widget_tabs(title=f"{dataset_name.capitalize()} dataset", tabs=tabs)

    @staticmethod
    def _get_count_info(stat: ValueListStat) -> str:
        percents = round(stat.share_in_list * 100, 3)
        return f"{stat.number_in_list} ({percents}%)"

    def _get_counters(self, metric_result: ColumnValueListMetricResult) -> BaseWidgetInfo:
        counters = [
            CounterData.string(
                label="In list (current)",
                value=self._get_count_info(metric_result.current),
            ),
        ]

        if metric_result.reference is not None:
            counters.append(
                CounterData.string(
                    label="In list (reference)",
                    value=self._get_count_info(metric_result.reference),
                ),
            )

        return counter(counters=counters)

    def render_html(self, obj: ColumnValueListMetric) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        result = [
            header_text(label=f"Column '{metric_result.column_name}'. Value list."),
            self._get_counters(metric_result),
            self._get_table_stat("current", metric_result.current),
        ]

        if metric_result.reference:
            result.append(self._get_table_stat("reference", metric_result.reference))

        return result
