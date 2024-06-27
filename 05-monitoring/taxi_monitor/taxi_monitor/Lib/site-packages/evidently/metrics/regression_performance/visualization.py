import json
from typing import Optional
from typing import Union

import numpy as np
from plotly import graph_objs as go
from plotly.subplots import make_subplots

from evidently.metric_results import Histogram
from evidently.metrics.regression_performance.objects import RegressionMetricScatter
from evidently.metrics.regression_performance.objects import RegressionScatter
from evidently.options.color_scheme import ColorOptions


def plot_error_bias_colored_scatter(
    curr_scatter_data: RegressionScatter,
    ref_scatter_data: Optional[RegressionScatter],
    color_options: ColorOptions,
):
    cols = 1
    subplot_titles: Union[list, str] = ""

    if ref_scatter_data is not None:
        cols = 2
        subplot_titles = ["current", "reference"]

    fig = make_subplots(rows=1, cols=cols, shared_yaxes=True, subplot_titles=subplot_titles)

    for name, value, color in zip(
        ["Underestimation", "Overestimation", "Majority"],
        [curr_scatter_data.underestimation, curr_scatter_data.overestimation, curr_scatter_data.majority],
        [color_options.underestimation_color, color_options.overestimation_color, color_options.majority_color],
    ):
        trace = go.Scatter(
            x=value.actual,
            y=value.predicted,
            mode="markers",
            name=name,
            legendgroup=name,
            marker_color=color,
            # marker=dict(color=color_options.underestimation_color, showscale=False),
        )
        fig.add_trace(trace, 1, 1)
    fig.update_xaxes(title_text="Actual value", row=1, col=1)

    if ref_scatter_data is not None:
        for name, value, color in zip(
            ["Underestimation", "Overestimation", "Majority"],
            [ref_scatter_data.underestimation, ref_scatter_data.overestimation, ref_scatter_data.majority],
            [color_options.underestimation_color, color_options.overestimation_color, color_options.majority_color],
        ):
            trace = go.Scatter(
                x=value.actual,
                y=value.predicted,
                mode="markers",
                name=name,
                legendgroup=name,
                showlegend=False,
                marker_color=color,
                # marker=dict(color=color_options.underestimation_color, showscale=False),
            )
            fig.add_trace(trace, 1, 2)
        fig.update_xaxes(title_text="Actual value", row=1, col=2)

    fig.update_layout(
        yaxis_title="Predicted value",
        xaxis=dict(showticklabels=True),
        yaxis=dict(showticklabels=True),
    )
    fig = json.loads(fig.to_json())
    return fig


def regression_perf_plot(
    *,
    val_for_plot: RegressionMetricScatter,
    hist_for_plot: Histogram,
    name: str,
    curr_metric: float,
    ref_metric: float = None,
    color_options: ColorOptions,
):
    current_color = color_options.get_current_data_color()
    reference_color = color_options.get_reference_data_color()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    sorted_index = val_for_plot.current.data.sort_index()
    x = [str(idx) for idx in sorted_index.index]
    y = list(sorted_index)
    trace = go.Scatter(x=x, y=y, mode="lines+markers", name=name, marker_color=current_color)
    fig.add_trace(trace, 1, 1)

    df = hist_for_plot.current.to_df().sort_values("x")
    x = [str(x) for x in df.x]
    y = list(df["count"])
    trace = go.Bar(name="current", x=x, y=y, marker_color=current_color)
    fig.add_trace(trace, 2, 1)

    if hist_for_plot.reference is not None:
        assert val_for_plot.reference is not None
        sorted_index = val_for_plot.reference.data.sort_index()
        x = [str(idx) for idx in sorted_index.index]
        y = list(sorted_index)
        trace = go.Scatter(x=x, y=y, mode="lines+markers", name=name, marker_color=reference_color)
        fig.add_trace(trace, 1, 1)

        df = hist_for_plot.reference.to_df().sort_values("x")
        x = [str(x) for x in df.x]
        y = list(df["count"])
        trace = go.Bar(name="reference", x=x, y=y, marker_color=reference_color)
        fig.add_trace(trace, 2, 1)

    fig.update_yaxes(title_text=name, row=1, col=1)
    fig.update_yaxes(title_text="count", row=2, col=1)
    title = f"current {name}: {np.round(curr_metric, 3)}"

    if hist_for_plot.reference is not None:
        title += f", reference {name}: {np.round(ref_metric, 3) if ref_metric is not None else '--'}"

    fig.update_layout(title=title)
    return fig
