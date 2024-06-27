from typing import List
from typing import Optional
from typing import Union

import numpy as np
import pandas as pd

from evidently.base_metric import ColumnName
from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.calculations.data_quality import get_rows_count
from evidently.core import ColumnType
from evidently.core import IncludeTags
from evidently.metric_results import Distribution
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import CounterData
from evidently.renderers.html_widgets import HistogramData
from evidently.renderers.html_widgets import TabData
from evidently.renderers.html_widgets import counter
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import plotly_figure
from evidently.renderers.html_widgets import table_data
from evidently.renderers.html_widgets import widget_tabs
from evidently.utils.types import Numeric
from evidently.utils.visualizations import get_distribution_for_column
from evidently.utils.visualizations import plot_distr_with_cond_perc_button


class ValuesInRangeStat(MetricResult):
    class Config:
        field_tags = {"number_of_values": {IncludeTags.Extra}}

    number_in_range: int
    number_not_in_range: int
    share_in_range: float
    share_not_in_range: float
    # number of rows without null-like values
    number_of_values: int
    distribution: Distribution


class ColumnValueRangeMetricResult(MetricResult):
    class Config:
        field_tags = {
            "current": {IncludeTags.Current},
            "reference": {IncludeTags.Reference},
            "column_name": {IncludeTags.Parameter},
            "left": {IncludeTags.Parameter},
            "right": {IncludeTags.Parameter},
        }

    column_name: str
    left: Numeric
    right: Numeric
    current: ValuesInRangeStat
    reference: Optional[ValuesInRangeStat] = None


class ColumnValueRangeMetric(Metric[ColumnValueRangeMetricResult]):
    """Calculates count and shares of values in the predefined values range"""

    column_name: ColumnName
    left: Optional[Numeric]
    right: Optional[Numeric]

    def __init__(
        self,
        column_name: Union[str, ColumnName],
        left: Optional[Numeric] = None,
        right: Optional[Numeric] = None,
        options: AnyOptions = None,
    ) -> None:
        self.left = left
        self.right = right
        self.column_name = ColumnName.from_any(column_name)
        super().__init__(options=options)

    @staticmethod
    def _calculate_in_range_stats(
        column: pd.Series, left: Numeric, right: Numeric, distribution: Distribution
    ) -> ValuesInRangeStat:
        column = column.dropna()
        rows_count = get_rows_count(column)

        if rows_count == 0:
            number_in_range = 0
            number_not_in_range = 0
            share_in_range = 0.0
            share_not_in_range = 0.0

        else:
            number_in_range = column.between(left=float(left), right=float(right), inclusive="both").sum()
            number_not_in_range = rows_count - number_in_range
            share_in_range = number_in_range / rows_count
            share_not_in_range = number_not_in_range / rows_count

        return ValuesInRangeStat(
            number_in_range=number_in_range,
            number_not_in_range=number_not_in_range,
            share_in_range=share_in_range,
            share_not_in_range=share_not_in_range,
            number_of_values=rows_count,
            distribution=distribution,
        )

    def calculate(self, data: InputData) -> ColumnValueRangeMetricResult:
        if not data.has_column(self.column_name):
            raise ValueError(f"Column {self.column_name} isn't present in data")
        column_type, current_data, reference_data = data.get_data(self.column_name)
        if column_type != ColumnType.Numerical:
            raise ValueError(f"Column {self.column_name} in reference data should be numeric.")

        if self.left is None:
            if reference_data is None:
                raise ValueError("Reference should be present")
            else:
                left: Numeric = float(reference_data.min())

        else:
            left = self.left

        if self.right is None:
            if reference_data is None:
                raise ValueError("Reference should be present")
            else:
                right: Numeric = float(reference_data.max())

        else:
            right = self.right

        # calculate distribution for visualisation
        cur_distribution, ref_distribution = get_distribution_for_column(
            column_type="num",
            current=current_data.replace([np.inf, -np.inf], np.nan),
            reference=reference_data.replace([np.inf, -np.inf], np.nan) if reference_data is not None else None,
        )

        current = self._calculate_in_range_stats(current_data, left, right, cur_distribution)
        reference = None
        if reference_data is not None:
            # always should be present
            assert ref_distribution is not None
            reference = self._calculate_in_range_stats(reference_data, left, right, ref_distribution)

        return ColumnValueRangeMetricResult(
            column_name=self.column_name if isinstance(self.column_name, str) else self.column_name.display_name,
            left=left,
            right=right,
            current=current,
            reference=reference,
        )


@default_renderer(wrap_type=ColumnValueRangeMetric)
class ColumnValueRangeMetricRenderer(MetricRenderer):
    @staticmethod
    def _get_table_stat(metric_result: ColumnValueRangeMetricResult) -> BaseWidgetInfo:
        matched_stat_headers = ["Metric", "Current"]
        matched_stat = [
            ["Values in range", metric_result.current.number_in_range],
            ["%", np.round(metric_result.current.share_in_range * 100, 3)],
            ["Values out of range", metric_result.current.number_not_in_range],
            ["%", np.round(metric_result.current.share_not_in_range * 100, 3)],
            ["Values count", metric_result.current.number_of_values],
        ]

        if metric_result.reference is not None:
            matched_stat_headers.append("Reference")

            matched_stat[0].append(metric_result.reference.number_in_range)
            matched_stat[1].append(np.round(metric_result.reference.share_in_range * 100, 3))
            matched_stat[2].append(metric_result.reference.number_not_in_range)
            matched_stat[3].append(np.round(metric_result.reference.share_not_in_range * 100, 3))
            matched_stat[4].append(metric_result.reference.number_of_values)

        return table_data(
            title="",
            column_names=matched_stat_headers,
            data=matched_stat,
        )

    def _get_tabs(self, metric_result: ColumnValueRangeMetricResult) -> BaseWidgetInfo:
        if metric_result.reference is not None:
            reference_histogram: Optional[HistogramData] = HistogramData.from_distribution(
                metric_result.reference.distribution,
                name="reference",
            )

        else:
            reference_histogram = None

        figure = plot_distr_with_cond_perc_button(
            hist_curr=HistogramData.from_distribution(metric_result.current.distribution),
            hist_ref=reference_histogram,
            xaxis_name="",
            yaxis_name="Count",
            yaxis_name_perc="Percent",
            color_options=self.color_options,
            to_json=False,
            condition=None,
            lt=metric_result.left,
            gt=metric_result.right,
            dict_rename={"lt": "left", "gt": "right"},
        )

        tabs: List[TabData] = [
            TabData(
                title="Distribution",
                widget=plotly_figure(title="", figure=figure),
            ),
            TabData(
                title="Statistics",
                widget=self._get_table_stat(metric_result),
            ),
        ]
        return widget_tabs(
            title="",
            tabs=tabs,
        )

    @staticmethod
    def _get_in_range_info(stat: ValuesInRangeStat) -> str:
        percents = round(stat.share_in_range * 100, 3)
        return f"{stat.number_in_range} ({percents}%)"

    def render_html(self, obj: ColumnValueRangeMetric) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        column_name = metric_result.column_name

        counters = [
            CounterData.string(
                label="Value range",
                value=f"[{metric_result.left}, {metric_result.right}]",
            ),
            CounterData.string(
                label="In range (current)",
                value=self._get_in_range_info(metric_result.current),
            ),
        ]

        if metric_result.reference is not None:
            counters.append(
                CounterData.string(
                    label="In range (reference)",
                    value=self._get_in_range_info(metric_result.reference),
                ),
            )

        result: List[BaseWidgetInfo] = [
            header_text(
                label=f"Column '{column_name}'. Value range.",
            ),
            counter(counters=counters),
            self._get_tabs(metric_result),
        ]
        return result
