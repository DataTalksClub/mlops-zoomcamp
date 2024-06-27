from typing import List
from typing import Optional
from typing import Union

import numpy as np

from evidently.base_metric import ColumnName
from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.core import ColumnType
from evidently.core import IncludeTags
from evidently.metric_results import Distribution
from evidently.metric_results import HistogramData
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import WidgetSize
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import plotly_figure
from evidently.utils.visualizations import get_distribution_for_column
from evidently.utils.visualizations import plot_distr_with_perc_button


class ColumnDistributionMetricResult(MetricResult):
    class Config:
        field_tags = {
            "current": {IncludeTags.Current},
            "reference": {IncludeTags.Reference},
            "column_name": {IncludeTags.Parameter},
        }

    column_name: str
    current: Distribution
    reference: Optional[Distribution] = None


class ColumnDistributionMetric(Metric[ColumnDistributionMetricResult]):
    """Calculates distribution for the column"""

    column_name: ColumnName

    def __init__(self, column_name: Union[str, ColumnName], options: AnyOptions = None) -> None:
        self.column_name = ColumnName.from_any(column_name)
        super().__init__(options=options)

    def calculate(self, data: InputData) -> ColumnDistributionMetricResult:
        if not data.has_column(self.column_name):
            raise ValueError(f"Column '{self.column_name.display_name}' was not found in data.")

        if not self.column_name.is_main_dataset():
            column_type = ColumnType.Numerical
        else:
            column_type = data.data_definition.get_column(self.column_name.name).column_type
        current_column = data.get_current_column(self.column_name).replace([np.inf, -np.inf], np.nan)
        reference_column = data.get_reference_column(self.column_name)
        if reference_column is not None:
            reference_column = reference_column.replace([np.inf, -np.inf], np.nan)
        current, reference = get_distribution_for_column(
            column_type=column_type.value,
            current=current_column,
            reference=reference_column,
        )

        return ColumnDistributionMetricResult(
            column_name=self.column_name.display_name,
            current=current,
            reference=reference,
        )


@default_renderer(wrap_type=ColumnDistributionMetric)
class ColumnDistributionMetricRenderer(MetricRenderer):
    def render_html(self, obj: ColumnDistributionMetric) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        distr_fig = plot_distr_with_perc_button(
            hist_curr=HistogramData.from_distribution(metric_result.current),
            hist_ref=HistogramData.from_distribution(metric_result.reference),
            xaxis_name="",
            yaxis_name="Count",
            yaxis_name_perc="Percent",
            same_color=False,
            color_options=self.color_options,
            subplots=False,
            to_json=False,
        )

        result = [
            header_text(label=f"Distribution for column '{metric_result.column_name}'."),
            plotly_figure(title="", figure=distr_fig, size=WidgetSize.FULL),
        ]
        return result
