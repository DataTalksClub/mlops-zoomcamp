from typing import List
from typing import Optional

import numpy as np

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.core import IncludeTags
from evidently.metric_results import HistogramData
from evidently.model.widget import BaseWidgetInfo
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import header_text
from evidently.utils.data_operations import process_columns
from evidently.utils.visualizations import make_hist_for_num_plot
from evidently.utils.visualizations import plot_distr_with_perc_button


class RegressionErrorDistributionResults(MetricResult):
    class Config:
        dict_exclude_fields = {"current_bins", "reference_bins"}
        pd_exclude_fields = {"current_bins", "reference_bins"}

        field_tags = {"current_bins": {IncludeTags.Current}, "reference_bins": {IncludeTags.Reference}}

    current_bins: HistogramData
    reference_bins: Optional[HistogramData]


class RegressionErrorDistribution(Metric[RegressionErrorDistributionResults]):
    def calculate(self, data: InputData) -> RegressionErrorDistributionResults:
        dataset_columns = process_columns(data.current_data, data.column_mapping)
        target_name = dataset_columns.utility_columns.target
        prediction_name = dataset_columns.utility_columns.prediction
        curr_df = data.current_data
        ref_df = data.reference_data
        if target_name is None or prediction_name is None:
            raise ValueError("The columns 'target' and 'prediction' columns should be present")
        if not isinstance(prediction_name, str):
            raise ValueError("Expect one column for prediction. List of columns was provided.")
        curr_df = self._make_df_for_plot(curr_df, target_name, prediction_name, None)
        curr_error = curr_df[prediction_name] - curr_df[target_name]
        ref_error = None
        if ref_df is not None:
            ref_df = self._make_df_for_plot(ref_df, target_name, prediction_name, None)
            ref_error = ref_df[prediction_name] - ref_df[target_name]

        result = make_hist_for_num_plot(curr_error, ref_error)
        current_bins = result.current
        reference_bins = result.reference

        return RegressionErrorDistributionResults(current_bins=current_bins, reference_bins=reference_bins)

    def _make_df_for_plot(self, df, target_name: str, prediction_name: str, datetime_column_name: Optional[str]):
        result = df.replace([np.inf, -np.inf], np.nan)
        if datetime_column_name is not None:
            result.dropna(
                axis=0,
                how="any",
                inplace=True,
                subset=[target_name, prediction_name, datetime_column_name],
            )
            return result.sort_values(datetime_column_name)
        result.dropna(axis=0, how="any", inplace=True, subset=[target_name, prediction_name])
        return result.sort_index()


@default_renderer(wrap_type=RegressionErrorDistribution)
class RegressionErrorDistributionRenderer(MetricRenderer):
    def render_html(self, obj: RegressionErrorDistribution) -> List[BaseWidgetInfo]:
        result = obj.get_result()
        current_bins = result.current_bins
        reference_bins = None
        if result.reference_bins is not None:
            reference_bins = result.reference_bins

        fig = plot_distr_with_perc_button(
            hist_curr=current_bins,
            hist_ref=reference_bins,
            xaxis_name="Error (Predicted - Actual)",
            yaxis_name="Number Of Objects",
            yaxis_name_perc="Percent",
            same_color=True,
            color_options=self.color_options,
        )

        return [
            header_text(label="Error Distribution"),
            BaseWidgetInfo(
                title="",
                size=2,
                type="big_graph",
                params={"data": fig["data"], "layout": fig["layout"]},
            ),
        ]
