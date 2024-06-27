from typing import List
from typing import Optional
from typing import Union

import numpy as np

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.base_metric import UsesRawDataMixin
from evidently.core import IncludeTags
from evidently.metric_results import ContourData
from evidently.metric_results import raw_agg_properties
from evidently.metrics.regression_performance.objects import PredActualScatter
from evidently.metrics.regression_performance.objects import scatter_as_dict
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import WidgetSize
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import plotly_figure
from evidently.utils.data_operations import process_columns
from evidently.utils.visualizations import get_gaussian_kde
from evidently.utils.visualizations import is_possible_contour
from evidently.utils.visualizations import plot_contour
from evidently.utils.visualizations import plot_scatter


class AggPredActualScatter(MetricResult):
    class Config:
        dict_include = False
        tags = {IncludeTags.Render}

    data: Optional[ContourData]


class RegressionPredictedVsActualScatterResults(MetricResult):
    class Config:
        dict_include = False
        tags = {IncludeTags.Render}
        field_tags = {"current": {IncludeTags.Current}, "reference": {IncludeTags.Reference}}

    current: Union[PredActualScatter, AggPredActualScatter]
    reference: Optional[Union[PredActualScatter, AggPredActualScatter]]
    agg_data: bool

    current_raw, current_agg = raw_agg_properties("current", PredActualScatter, AggPredActualScatter, False)
    reference_raw, reference_agg = raw_agg_properties("reference", PredActualScatter, AggPredActualScatter, True)


class RegressionPredictedVsActualScatter(UsesRawDataMixin, Metric[RegressionPredictedVsActualScatterResults]):
    def __init__(self, options: AnyOptions = None):
        super().__init__(options=options)

    def calculate(self, data: InputData) -> RegressionPredictedVsActualScatterResults:
        dataset_columns = process_columns(data.current_data, data.column_mapping)
        target_name = dataset_columns.utility_columns.target
        prediction_name = dataset_columns.utility_columns.prediction
        curr_df = data.current_data
        ref_df = data.reference_data
        if target_name is None or prediction_name is None:
            raise ValueError("The columns 'target' and 'prediction' columns should be present")
        if not isinstance(prediction_name, str):
            raise ValueError("Expect one column for prediction. List of columns was provided.")
        curr_df = self._make_df_for_plot(curr_df.copy(), target_name, prediction_name, None)
        if ref_df is not None:
            ref_df = self._make_df_for_plot(ref_df.copy(), target_name, prediction_name, None)

        if (
            self.get_options().render_options.raw_data
            or not is_possible_contour(curr_df[prediction_name], curr_df[target_name])
            or (ref_df is not None and not is_possible_contour(ref_df[prediction_name], ref_df[target_name]))
        ):
            curr_df.drop_duplicates(subset=[prediction_name, target_name], inplace=True)
            current_scatter = PredActualScatter(predicted=curr_df[prediction_name], actual=curr_df[target_name])
            reference_scatter: Optional[PredActualScatter] = None
            if ref_df is not None:
                ref_df.drop_duplicates(subset=[prediction_name, target_name], inplace=True)
                reference_scatter = PredActualScatter(predicted=ref_df[prediction_name], actual=ref_df[target_name])
            return RegressionPredictedVsActualScatterResults(
                current=current_scatter, reference=reference_scatter, agg_data=False
            )

        current_agg = AggPredActualScatter(data=get_gaussian_kde(curr_df[prediction_name], curr_df[target_name]))
        reference_agg = AggPredActualScatter(data=None)
        if ref_df is not None:
            reference_agg = AggPredActualScatter(data=get_gaussian_kde(ref_df[prediction_name], ref_df[target_name]))
        return RegressionPredictedVsActualScatterResults(current=current_agg, reference=reference_agg, agg_data=True)

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


@default_renderer(wrap_type=RegressionPredictedVsActualScatter)
class RegressionPredictedVsActualScatterRenderer(MetricRenderer):
    def render_raw(self, current: PredActualScatter, reference: Optional[PredActualScatter]):
        fig = plot_scatter(
            curr=scatter_as_dict(current),
            ref=scatter_as_dict(reference),
            x="actual",
            y="predicted",
            xaxis_name="Actual value",
            yaxis_name="Predicted value",
            color_options=self.color_options,
        )
        return [
            header_text(label="Predicted vs Actual"),
            BaseWidgetInfo(
                title="",
                size=2,
                type="big_graph",
                params={"data": fig["data"], "layout": fig["layout"]},
            ),
        ]

    def render_agg(self, current: AggPredActualScatter, reference: Optional[AggPredActualScatter]):
        if current.data is None:
            raise ValueError("Current data should be present")
        ref_data: Optional[ContourData] = None
        if reference is not None:
            ref_data = reference.data
        fig = plot_contour(current.data, ref_data, "Actual value", "Predicted value")

        return [header_text(label="Predicted vs Actual"), plotly_figure(title="", figure=fig, size=WidgetSize.FULL)]

    def render_html(self, obj: RegressionPredictedVsActualScatter) -> List[BaseWidgetInfo]:
        result = obj.get_result()
        if not result.agg_data:
            return self.render_raw(result.current_raw, result.reference_raw)
        return self.render_agg(result.current_agg, result.reference_agg)
