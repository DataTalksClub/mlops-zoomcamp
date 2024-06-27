from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pandas as pd

from evidently.base_metric import ColumnName
from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.calculations.data_quality import calculate_category_correlation
from evidently.calculations.data_quality import calculate_numerical_correlation
from evidently.core import ColumnType
from evidently.core import IncludeTags
from evidently.metric_results import ColumnCorrelations
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import TabData
from evidently.renderers.html_widgets import get_histogram_for_distribution
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import widget_tabs
from evidently.utils.data_preprocessing import DataDefinition


class ColumnCorrelationsMetricResult(MetricResult):
    class Config:
        field_tags = {
            "current": {IncludeTags.Current},
            "reference": {IncludeTags.Reference},
            "column_name": {IncludeTags.Parameter},
        }

    column_name: str
    current: Dict[str, ColumnCorrelations]
    reference: Optional[Dict[str, ColumnCorrelations]] = None

    def get_pandas(self) -> pd.DataFrame:
        dfs = []
        for field in ["current", "reference"]:
            value = getattr(self, field)
            if value is None:
                continue
            for corr in value.values():
                df = corr.get_pandas()
                df.columns = [f"{field}_{col}" for col in df.columns]
                df["column_name"] = self.column_name
                dfs.append(df)
        if len(dfs) == 0:
            return pd.DataFrame()
        return pd.concat(dfs)


class ColumnCorrelationsMetric(Metric[ColumnCorrelationsMetricResult]):
    """Calculates correlations between the selected column and all the other columns.
    In the current and reference (if presented) datasets"""

    column_name: ColumnName

    def __init__(self, column_name: Union[str, ColumnName], options: AnyOptions = None) -> None:
        self.column_name = ColumnName.from_any(column_name)
        super().__init__(options=options)

    @staticmethod
    def _calculate_correlation(
        column_name: ColumnName,
        column_data: pd.Series,
        dataset: pd.DataFrame,
        data_definition: DataDefinition,
        column_type: ColumnType,
    ) -> Dict[str, ColumnCorrelations]:
        if column_type == ColumnType.Categorical:
            cat_features = data_definition.get_columns(ColumnType.Categorical, features_only=True)

            correlations = calculate_category_correlation(
                column_name.display_name,
                column_data,
                dataset[[feature.column_name for feature in cat_features if feature.column_name != column_name.name]],
            )
        elif column_type == ColumnType.Numerical:
            num_features = data_definition.get_columns(ColumnType.Numerical, features_only=True)
            correlations = calculate_numerical_correlation(
                column_name.display_name,
                column_data,
                dataset[[feature.column_name for feature in num_features if feature.column_name != column_name.name]],
            )
        else:
            raise ValueError(f"Cannot calculate correlations for '{column_type}' column type.")
        return {corr.kind: corr for corr in correlations}

    def calculate(self, data: InputData) -> ColumnCorrelationsMetricResult:
        if not data.has_column(self.column_name):
            raise ValueError(f"Column '{self.column_name.name}' was not found in data.")

        column_type, current_data, reference_data = data.get_data(self.column_name)

        current_correlations = self._calculate_correlation(
            self.column_name,
            current_data,
            data.current_data,
            data.data_definition,
            column_type,
        )

        reference_correlations = None
        if reference_data is not None:
            reference_correlations = self._calculate_correlation(
                self.column_name,
                reference_data,
                data.reference_data,
                data.data_definition,
                column_type,
            )

        return ColumnCorrelationsMetricResult(
            column_name=self.column_name.display_name,
            current=current_correlations,
            reference=reference_correlations if reference_correlations is not None else None,
        )


@default_renderer(wrap_type=ColumnCorrelationsMetric)
class ColumnCorrelationsMetricRenderer(MetricRenderer):
    def _get_plots_correlations(self, metric_result: ColumnCorrelationsMetricResult) -> Optional[BaseWidgetInfo]:
        tabs = []

        for correlation_name, current_correlation in metric_result.current.items():
            reference_correlation_values = None

            if metric_result.reference and correlation_name in metric_result.reference:
                reference_correlation_values = metric_result.reference[correlation_name].values

            if current_correlation.values or reference_correlation_values:
                tabs.append(
                    TabData(
                        title=correlation_name,
                        widget=get_histogram_for_distribution(
                            title="",
                            current_distribution=current_correlation.values,
                            reference_distribution=reference_correlation_values,
                            xaxis_title="Columns",
                            yaxis_title="Correlation",
                            color_options=self.color_options,
                        ),
                    )
                )

        if tabs:
            return widget_tabs(tabs=tabs)

        else:
            return None

    def render_html(self, obj: ColumnCorrelationsMetric) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        correlation_plots = self._get_plots_correlations(metric_result)

        if correlation_plots:
            return [
                header_text(label=f"Correlations for column '{metric_result.column_name}'."),
                correlation_plots,
            ]

        else:
            # no correlations, draw nothing
            return []
