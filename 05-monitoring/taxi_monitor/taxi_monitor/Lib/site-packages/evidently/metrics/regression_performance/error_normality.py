import json
from typing import Any
from typing import List
from typing import Optional
from typing import Union

import numpy as np
import pandas as pd
from plotly import graph_objs as go
from plotly.subplots import make_subplots
from scipy.stats import probplot

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.base_metric import UsesRawDataMixin
from evidently.core import IncludeTags
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import header_text
from evidently.utils.data_operations import process_columns


class RegressionErrorNormalityResults(MetricResult):
    class Config:
        dict_exclude_fields = {"current_plot", "current_theoretical", "reference_plot", "reference_theoretical"}
        pd_exclude_fields = {"current_plot", "current_theoretical", "reference_plot", "reference_theoretical"}

        field_tags = {
            "current_plot": {IncludeTags.Render, IncludeTags.Current},
            "current_theoretical": {IncludeTags.Extra, IncludeTags.Current},
            "reference_plot": {IncludeTags.Render, IncludeTags.Reference},
            "reference_theoretical": {IncludeTags.Extra, IncludeTags.Reference},
        }

    current_plot: pd.DataFrame
    current_theoretical: pd.DataFrame
    reference_plot: Optional[pd.DataFrame]
    reference_theoretical: Optional[pd.DataFrame]


class RegressionErrorNormality(UsesRawDataMixin, Metric[RegressionErrorNormalityResults]):
    def __init__(self, options: AnyOptions = None):
        super().__init__(options=options)

    def calculate(self, data: InputData) -> RegressionErrorNormalityResults:
        dataset_columns = process_columns(data.current_data, data.column_mapping)
        target_name = dataset_columns.utility_columns.target
        prediction_name = dataset_columns.utility_columns.prediction
        curr_df = data.current_data
        ref_df = data.reference_data
        if target_name is None or prediction_name is None:
            raise ValueError("The columns 'target' and 'prediction' columns should be present")
        if not isinstance(prediction_name, str):
            raise ValueError("Expect one column for prediction. List of columns was provided.")
        agg_data = True
        if self.get_options().render_options.raw_data:
            agg_data = False
        curr_df = self._make_df_for_plot(curr_df, target_name, prediction_name, None)
        current_error = curr_df[prediction_name] - curr_df[target_name]
        curr_qq_lines = probplot(current_error, dist="norm", plot=None)
        current_theoretical = self._get_theoretical_line(curr_qq_lines)
        current_plot_data = self._get_plot_data(curr_qq_lines, current_error, agg_data)
        reference_theoretical = None
        reference_plot_data = None
        if ref_df is not None:
            ref_df = self._make_df_for_plot(ref_df, target_name, prediction_name, None)
            reference_error = ref_df[prediction_name] - ref_df[target_name]
            ref_qq_lines = probplot(reference_error, dist="norm", plot=None)
            reference_theoretical = self._get_theoretical_line(ref_qq_lines)
            reference_plot_data = self._get_plot_data(ref_qq_lines, reference_error, agg_data)
        return RegressionErrorNormalityResults(
            current_plot=current_plot_data,
            current_theoretical=current_theoretical,
            reference_plot=reference_plot_data,
            reference_theoretical=reference_theoretical,
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

    def _get_theoretical_line(self, res: Any):
        x = [res[0][0][0], res[0][0][-1]]
        y = [res[1][0] * res[0][0][0] + res[1][1], res[1][0] * res[0][0][-1] + res[1][1]]
        return pd.DataFrame({"x": x, "y": y})

    def _get_plot_data(self, res: Any, err_data: pd.Series, agg_data: bool):
        df = pd.DataFrame({"x": res[0][0], "y": res[0][1]})
        if not agg_data:
            return df
        df["bin"] = pd.cut(err_data.sort_values().values, bins=10, labels=False, retbins=False)
        return (
            df.groupby("bin", group_keys=False)
            .apply(lambda x: x.sample(n=min(100, x.shape[0]), random_state=0))
            .drop("bin", axis=1)
        )


@default_renderer(wrap_type=RegressionErrorNormality)
class RegressionErrorNormalityRenderer(MetricRenderer):
    def render_html(self, obj: RegressionErrorNormality) -> List[BaseWidgetInfo]:
        result = obj.get_result()
        current_plot = result.current_plot
        current_theoretical = result.current_theoretical
        reference_plot = result.reference_plot
        reference_theoretical = result.reference_theoretical
        color_options = self.color_options
        cols = 1
        subplot_titles: Union[list, str] = ""

        if reference_plot is not None:
            cols = 2
            subplot_titles = ["current", "reference"]

        fig = make_subplots(rows=1, cols=cols, shared_yaxes=False, subplot_titles=subplot_titles)

        sample_quantile_trace = go.Scatter(
            x=current_plot["x"],
            y=current_plot["y"],
            mode="markers",
            name="Dataset Quantiles",
            legendgroup="Dataset Quantiles",
            marker=dict(size=6, color=color_options.primary_color),
        )

        theoretical_quantile_trace = go.Scatter(
            x=current_theoretical["x"],
            y=current_theoretical["y"],
            mode="lines",
            name="Theoretical Quantiles",
            legendgroup="Theoretical Quantiles",
            marker=dict(size=6, color=color_options.secondary_color),
        )
        fig.add_trace(sample_quantile_trace, 1, 1)
        fig.add_trace(theoretical_quantile_trace, 1, 1)
        fig.update_xaxes(title_text="Theoretical Quantiles", row=1, col=1)
        if reference_plot is not None and reference_theoretical is not None:
            sample_quantile_trace = go.Scatter(
                x=reference_plot["x"],
                y=reference_plot["y"],
                mode="markers",
                name="Dataset Quantiles",
                legendgroup="Dataset Quantiles",
                showlegend=False,
                marker=dict(size=6, color=color_options.primary_color),
            )

            theoretical_quantile_trace = go.Scatter(
                x=reference_theoretical["x"],
                y=reference_theoretical["y"],
                mode="lines",
                name="Theoretical Quantiles",
                legendgroup="Theoretical Quantiles",
                showlegend=False,
                marker=dict(size=6, color=color_options.secondary_color),
            )
            fig.add_trace(sample_quantile_trace, 1, 2)
            fig.add_trace(theoretical_quantile_trace, 1, 2)
            fig.update_xaxes(title_text="Theoretical Quantiles", row=1, col=2)
        fig.update_layout(yaxis_title="Dataset Quantiles")
        fig = json.loads(fig.to_json())

        return [
            header_text(label="Error Normality"),
            BaseWidgetInfo(
                title="",
                size=2,
                type="big_graph",
                params={"data": fig["data"], "layout": fig["layout"]},
            ),
        ]
