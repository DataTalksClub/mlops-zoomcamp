from typing import List
from typing import Optional
from typing import Union

import numpy as np
import pandas as pd

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import UsesRawDataMixin
from evidently.metric_results import ColumnAggScatterResult
from evidently.metric_results import ColumnScatter
from evidently.metric_results import ColumnScatterResult
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import header_text
from evidently.utils.data_operations import process_columns
from evidently.utils.visualizations import plot_agg_line_data
from evidently.utils.visualizations import plot_line_in_time
from evidently.utils.visualizations import prepare_df_for_time_index_plot


class RegressionErrorPlot(UsesRawDataMixin, Metric[ColumnScatterResult]):
    def __init__(self, options: AnyOptions = None):
        super().__init__(options=options)

    def calculate(self, data: InputData) -> ColumnScatterResult:
        dataset_columns = process_columns(data.current_data, data.column_mapping)
        target_name = dataset_columns.utility_columns.target
        prediction_name = dataset_columns.utility_columns.prediction
        datetime_column_name = dataset_columns.utility_columns.date
        curr_df = data.current_data.copy()
        ref_df = data.reference_data
        if target_name is None or prediction_name is None:
            raise ValueError("The columns 'target' and 'prediction' columns should be present")
        if not isinstance(prediction_name, str):
            raise ValueError("Expect one column for prediction. List of columns was provided.")
        curr_df = self._make_df_for_plot(curr_df, target_name, prediction_name, datetime_column_name)
        curr_error = curr_df[prediction_name] - curr_df[target_name]
        ref_error: Optional[pd.Series] = None
        if ref_df is not None:
            ref_df = self._make_df_for_plot(ref_df.copy(), target_name, prediction_name, datetime_column_name)
            ref_error = ref_df[prediction_name] - ref_df[target_name]
        current_scatter = {}
        reference_scatter: Optional[Union[dict, ColumnScatter]] = None
        raw_data = self.get_options().render_options.raw_data
        if raw_data:
            current_scatter["Predicted - Actual"] = curr_error
            if datetime_column_name is not None:
                current_scatter["x"] = curr_df[datetime_column_name]
                x_name = "Timestamp"
            else:
                current_scatter["x"] = curr_df.index
                x_name = "Index"

            if ref_df is not None:
                reference_scatter = {}
                reference_scatter["Predicted - Actual"] = ref_error
                reference_scatter["x"] = ref_df[datetime_column_name] if datetime_column_name else ref_df.index

            return ColumnScatterResult(
                current=current_scatter,
                reference=reference_scatter,
                x_name=x_name,
            )
        curr_df["Predicted - Actual"] = curr_error
        plot_df, prefix = prepare_df_for_time_index_plot(curr_df, "Predicted - Actual", datetime_column_name)
        current_scatter["Predicted - Actual"] = plot_df
        x_name_ref: Optional[str] = None
        if ref_df is not None:
            reference_scatter = {}
            ref_df["Predicted - Actual"] = ref_error
            plot_df, prefix_ref = prepare_df_for_time_index_plot(ref_df, "Predicted - Actual", datetime_column_name)
            reference_scatter["Predicted - Actual"] = plot_df
            if datetime_column_name is None:
                x_name_ref = "Index binned"
            else:
                x_name_ref = datetime_column_name + f" ({prefix_ref})"
        if datetime_column_name is None:
            x_name = "Index binned"
        else:
            x_name = datetime_column_name + f" ({prefix})"
        cls = ColumnScatterResult
        if not raw_data:
            cls = ColumnAggScatterResult

        return cls(
            current=current_scatter,
            reference=reference_scatter,
            x_name=x_name,
            x_name_ref=x_name_ref,
        )

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


@default_renderer(wrap_type=RegressionErrorPlot)
class RegressionErrorPlotRenderer(MetricRenderer):
    def render_html(self, obj: RegressionErrorPlot) -> List[BaseWidgetInfo]:
        result = obj.get_result()
        current = result.current
        reference = None
        if result.reference is not None:
            reference = result.reference
        if obj.get_options().render_options.raw_data:
            fig = plot_line_in_time(
                curr=current,
                ref=reference,
                x_name="x",
                y_name="Predicted - Actual",
                xaxis_name=result.x_name,
                yaxis_name="Error",
                color_options=self.color_options,
            )
        else:
            fig = plot_agg_line_data(
                curr_data=current,
                ref_data=reference,
                line=0,
                std=None,
                xaxis_name=result.x_name,
                xaxis_name_ref=result.x_name_ref,
                yaxis_name="Error",
                color_options=self.color_options,
            )
        return [
            header_text(label="Error (Predicted - Actual)"),
            BaseWidgetInfo(
                title="",
                size=2,
                type="big_graph",
                params={"data": fig["data"], "layout": fig["layout"]},
            ),
        ]
