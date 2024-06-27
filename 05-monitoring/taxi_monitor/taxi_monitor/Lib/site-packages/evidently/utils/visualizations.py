import json
from typing import TYPE_CHECKING
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import numpy as np
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype
from plotly import graph_objs as go
from plotly.subplots import make_subplots
from scipy import stats
from scipy.linalg.basic import LinAlgError

from evidently.metric_results import ContourData
from evidently.metric_results import Distribution
from evidently.metric_results import Histogram
from evidently.metric_results import HistogramData
from evidently.metric_results import Label
from evidently.metric_results import ScatterData
from evidently.options.color_scheme import ColorOptions
from evidently.utils.types import ApproxValue

if TYPE_CHECKING:
    from evidently.tests.base_test import TestValueCondition

OPTIMAL_POINTS = 150


def plot_distr(
    *, hist_curr: HistogramData, hist_ref: Optional[HistogramData] = None, orientation="v", color_options: ColorOptions
) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="current",
            x=hist_curr.x,
            y=hist_curr.count,
            marker_color=color_options.get_current_data_color(),
            orientation=orientation,
        )
    )
    cats = list(hist_curr.x)
    if hist_ref is not None:
        fig.add_trace(
            go.Bar(
                name="reference",
                x=hist_ref.x,
                y=hist_ref.count,
                marker_color=color_options.get_reference_data_color(),
                orientation=orientation,
            )
        )
        cats = cats + list(np.setdiff1d(hist_ref.x, cats))

    if "other" in cats:
        cats.remove("other")
        cats = cats + ["other"]
        fig.update_xaxes(categoryorder="array", categoryarray=cats)

    return fig


def collect_updatemenus(name1: str, name2: str, y_name_1: str, y_name_2: str, visible: List[bool]):
    button1 = dict(method="update", args=[{"visible": visible}, {"yaxis": {"title": y_name_1}}], label=name1)
    button2 = dict(
        method="update", args=[{"visible": [not x for x in visible]}, {"yaxis": {"title": y_name_2}}], label=name2
    )
    updatemenus = [dict(type="buttons", direction="right", buttons=[button1, button2], x=1.05, y=1.2, yanchor="top")]
    return updatemenus


def add_traces_with_perc(fig, hist_data, x, y, marker_color, name):
    trace_1 = go.Bar(
        x=hist_data.x,
        y=hist_data.count,
        visible=True,
        marker_color=marker_color,
        name=name,
    )

    trace_2 = go.Bar(
        x=hist_data.x,
        y=(hist_data.count / hist_data.count.sum()) * 100,
        visible=False,
        marker_color=marker_color,
        name=name,
    )

    fig.add_trace(trace_1, x, y)
    fig.add_trace(trace_2, x, y)
    return fig


def plot_distr_with_perc_button(
    *,
    hist_curr: HistogramData,
    hist_ref: Optional[HistogramData] = None,
    xaxis_name: str = "",
    yaxis_name: str = "",
    yaxis_name_perc: str = "",
    same_color: bool = False,
    color_options: ColorOptions,
    subplots: bool = True,
    to_json: bool = True,
):
    if not same_color:
        curr_color = color_options.get_current_data_color()
        ref_color = color_options.get_reference_data_color()

    else:
        curr_color = color_options.get_current_data_color()
        ref_color = curr_color
    cols = 1
    subplot_titles: Union[list, str] = ""
    visible = [True, False]
    is_subplots = hist_ref is not None and subplots

    if is_subplots:
        cols = 2
        subplot_titles = ["current", "reference"]
    fig = make_subplots(rows=1, cols=cols, shared_yaxes=True, subplot_titles=subplot_titles)

    fig = add_traces_with_perc(fig, hist_curr, 1, 1, curr_color, "current")
    fig.update_xaxes(title_text=xaxis_name, row=1, col=1)
    if hist_ref is not None:
        fig = add_traces_with_perc(fig, hist_ref, 1, int(is_subplots) + 1, ref_color, "reference")
        fig.update_xaxes(title_text=xaxis_name, row=1, col=2)
        visible += [True, False]

    fig.update_layout(yaxis_title=yaxis_name)

    updatemenus = collect_updatemenus("abs", "perc", yaxis_name, yaxis_name_perc, visible)
    fig.update_layout(updatemenus=updatemenus)
    if is_subplots:
        fig.update_layout(showlegend=False)
    if to_json:
        fig = json.loads(fig.to_json())
    return fig


def plot_distr_with_cond_perc_button(
    *,
    hist_curr: HistogramData,
    hist_ref: Optional[HistogramData] = None,
    xaxis_name: str = "",
    yaxis_name: str = "",
    yaxis_name_perc: str = "",
    color_options: ColorOptions,
    to_json: bool = True,
    condition: Optional["TestValueCondition"],
    value: Optional[float] = None,
    value_name: Optional[str] = None,
    lt: Optional[float] = None,
    gt: Optional[float] = None,
    fill: Optional[bool] = True,
    dict_rename: Dict[str, str] = {},
    dict_style: Dict[str, str] = {},
):
    fig = make_subplots(rows=1, cols=1)
    visible = [True, False]
    fig = add_traces_with_perc(fig, hist_curr, 1, 1, color_options.get_current_data_color(), "current")
    if hist_ref is not None:
        fig = add_traces_with_perc(fig, hist_ref, 1, 1, color_options.get_reference_data_color(), "reference")
        visible += [True, False]
    lines = []
    left_line: Optional[float] = None
    right_line: Optional[float] = None
    if condition is not None:
        left_line = pd.Series([condition.gt, condition.gte]).max()
        if not pd.isnull(left_line):
            left_line_name = ["gt", "gte"][pd.Series([condition.gt, condition.gte]).argmax()]
            lines.append((left_line, left_line_name))

        right_line = pd.Series([condition.lt, condition.lte]).min()
        if not pd.isnull(right_line):
            right_line_name = ["lt", "lte"][pd.Series([condition.lt, condition.lte]).argmin()]
            lines.append((right_line, right_line_name))
        if condition.eq is not None and not isinstance(condition.eq, ApproxValue):
            lines.append((condition.eq, "eq"))

        if condition.eq is not None and isinstance(condition.eq, ApproxValue):
            lines.append((condition.eq.value, "approx"))

        if condition.not_eq is not None:
            lines.append((condition.not_eq, "not_eq"))

        if condition.eq is not None and isinstance(condition.eq, ApproxValue):
            left_border = 0.0
            right_border = 0.0

            if condition.eq.relative > 1e-6:
                left_border = condition.eq.value - condition.eq.value * condition.eq.relative
                right_border = condition.eq.value + condition.eq.value * condition.eq.relative
                fig.add_vrect(
                    x0=left_border,
                    x1=right_border,
                    fillcolor="green",
                    opacity=0.25,
                    line_width=0,
                )

            elif condition.eq.absolute > 1e-12:
                left_border = condition.eq.value - condition.eq.absolute
                right_border = condition.eq.value + condition.eq.absolute
                fig.add_vrect(
                    x0=left_border,
                    x1=right_border,
                    fillcolor="green",
                    opacity=0.25,
                    line_width=0,
                )

            fig.add_vrect(
                x0=left_border,
                x1=right_border,
                fillcolor="green",
                opacity=0.25,
                line_width=0,
            )

    if gt is not None:
        left_line = gt
        left_line_name = dict_rename.get("gt", "gt")
        lines.append((left_line, left_line_name))
    if lt is not None:
        right_line = lt
        right_line_name = dict_rename.get("lt", "lt")
        lines.append((right_line, right_line_name))
    if value is not None and value_name is not None:
        lines.append((value, value_name))
        dict_style[value_name] = "solid"

    max_y = np.max([np.max(x["y"]) for x in pd.Series(fig.data)[visible]])
    not_visible = [not x for x in visible]
    max_y_perc = np.max([np.max(x["y"]) for x in pd.Series(fig.data)[not_visible]])

    if len(lines) > 0:
        for line, name in lines:
            fig.add_trace(
                go.Scatter(
                    x=(line, line),
                    y=(0, max_y),
                    visible=True,
                    mode="lines",
                    line=dict(color="green", width=3, dash=dict_style.get(name, "dash")),
                    name=name,
                ),
                1,
                1,
            )
            fig.add_trace(
                go.Scatter(
                    x=(line, line),
                    y=(0, max_y_perc),
                    visible=False,
                    mode="lines",
                    line=dict(color="green", width=3, dash=dict_style.get(name, "dash")),
                    name=name,
                ),
                1,
                1,
            )
            visible += [True, False]

    if fill and left_line and right_line:
        fig.add_vrect(x0=left_line, x1=right_line, fillcolor="green", opacity=0.25, line_width=0)

    fig.update_xaxes(title_text=xaxis_name)
    fig.update_layout(yaxis_title=yaxis_name)

    updatemenus = collect_updatemenus("abs", "perc", yaxis_name, yaxis_name_perc, visible)
    fig.update_layout(updatemenus=updatemenus)
    if to_json:
        fig = json.loads(fig.to_json())
    return fig


def plot_distr_with_log_button(
    curr_data: HistogramData,
    curr_data_log: HistogramData,
    ref_data: Optional[HistogramData],
    ref_data_log: Optional[HistogramData],
    color_options: ColorOptions,
):
    traces = []
    visible = [True, False]
    traces.append(
        go.Bar(
            x=curr_data.x,
            y=curr_data.count,
            marker_color=color_options.get_current_data_color(),
            name="current",
        )
    )
    traces.append(
        go.Bar(
            x=curr_data_log.x,
            y=curr_data_log.count,
            visible=False,
            marker_color=color_options.get_current_data_color(),
            name="current",
        )
    )
    if ref_data is not None:
        traces.append(
            go.Bar(
                x=ref_data.x,
                y=ref_data.count,
                marker_color=color_options.get_reference_data_color(),
                name="reference",
            )
        )
        visible.append(True)
        if ref_data_log is not None:
            traces.append(
                go.Bar(
                    x=ref_data_log.x,
                    y=ref_data_log.count,
                    visible=False,
                    marker_color=color_options.get_reference_data_color(),
                    name="reference",
                )
            )
            visible.append(False)

    updatemenus = [
        dict(
            type="buttons",
            direction="right",
            x=1.0,
            yanchor="top",
            buttons=list(
                [
                    dict(
                        label="Linear Scale",
                        method="update",
                        args=[{"visible": visible}],
                    ),
                    dict(
                        label="Log Scale",
                        method="update",
                        args=[{"visible": [not x for x in visible]}],
                    ),
                ]
            ),
        )
    ]
    layout = dict(updatemenus=updatemenus)

    fig = go.Figure(data=traces, layout=layout)
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig = json.loads(fig.to_json())
    return fig


def plot_num_feature_in_time(
    curr_data: pd.DataFrame,
    ref_data: Optional[pd.DataFrame],
    feature_name: str,
    datetime_name: str,
    freq: str,
    color_options: ColorOptions,
    transpose: bool = False,
):
    """
    Accepts current and reference data as pandas dataframes with two columns: datetime_name and feature_name.
    """
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=curr_data.sort_values(datetime_name)[datetime_name]
            if not transpose
            else curr_data.sort_values(datetime_name)[feature_name],
            y=curr_data.sort_values(datetime_name)[feature_name]
            if not transpose
            else curr_data.sort_values(datetime_name)[datetime_name],
            line=dict(color=color_options.get_current_data_color(), shape="spline"),
            name="current",
        )
    )
    if ref_data is not None:
        fig.add_trace(
            go.Scatter(
                x=ref_data.sort_values(datetime_name)[datetime_name]
                if not transpose
                else ref_data.sort_values(datetime_name)[feature_name],
                y=ref_data.sort_values(datetime_name)[feature_name]
                if not transpose
                else ref_data.sort_values(datetime_name)[datetime_name],
                line=dict(color=color_options.get_reference_data_color(), shape="spline"),
                name="reference",
            )
        )
    if not transpose:
        fig.update_layout(yaxis_title="Mean " + feature_name + " per " + freq)
    else:
        fig.update_layout(xaxis_title="Mean " + feature_name + " per " + freq)
    feature_in_time_figure = json.loads(fig.to_json())
    return feature_in_time_figure


def plot_time_feature_distr(current: HistogramData, reference: Optional[HistogramData], color_options: ColorOptions):
    """
    Accepts current and reference data as pandas dataframes with two columns: feature_name, "number_of_items"
    """
    curr_data = current.to_df().sort_values("x")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=curr_data["x"],
            y=curr_data["count"],
            line=dict(color=color_options.get_current_data_color(), shape="spline"),
            name="current",
        )
    )
    if reference is not None:
        ref_data = reference.to_df().sort_values("x")

        fig.add_trace(
            go.Scatter(
                x=ref_data["x"],
                y=ref_data["count"],
                line=dict(color=color_options.get_reference_data_color(), shape="spline"),
                name="reference",
            )
        )
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig = json.loads(fig.to_json())
    return fig


def plot_cat_feature_in_time(
    curr_data: pd.DataFrame,
    ref_data: Optional[pd.DataFrame],
    feature_name: str,
    datetime_name: str,
    freq: str,
    color_options: ColorOptions,
    transpose: bool = False,
):
    """
    Accepts current and reference data as pandas dataframes with two columns: datetime_name and feature_name.
    """
    title = "current"
    fig = go.Figure()
    orientation = "v" if not transpose else "h"
    values = curr_data[feature_name].astype(str).unique()
    if ref_data is not None:
        values = np.union1d(curr_data[feature_name].astype(str).unique(), ref_data[feature_name].astype(str).unique())
    for i, val in enumerate(values):
        x = curr_data.loc[curr_data[feature_name].astype(str) == val, datetime_name]
        y = curr_data.loc[curr_data[feature_name].astype(str) == val, "num"]
        fig.add_trace(
            go.Bar(
                x=x if not transpose else y,
                y=y if not transpose else x,
                name=str(val),
                marker_color=color_options.color_sequence[i],
                legendgroup=str(val),
                orientation=orientation,
            )
        )
        if ref_data is not None:
            title = "reference/current"
            x = ref_data.loc[ref_data[feature_name].astype(str) == val, datetime_name]
            y = ref_data.loc[ref_data[feature_name].astype(str) == val, "num"]
            fig.add_trace(
                go.Bar(
                    x=x if not transpose else y,
                    y=y if not transpose else x,
                    name=str(val),
                    marker_color=color_options.color_sequence[i],
                    # showlegend=False,
                    legendgroup=str(val),
                    opacity=0.6,
                    orientation=orientation,
                )
            )
    fig.update_traces(marker_line_width=0.01)
    fig.update_layout(
        barmode="stack",
        bargap=0,
        title=title,
    )
    if not transpose:
        fig.update_layout(yaxis_title="count category values per " + freq)
    else:
        fig.update_layout(xaxis_title="count category values per " + freq)
    feature_in_time_figure = json.loads(fig.to_json())
    return feature_in_time_figure


def plot_boxes(
    curr_for_plots: dict,
    ref_for_plots: Optional[dict],
    yaxis_title: str,
    xaxis_title: str,
    color_options: ColorOptions,
    transpose: bool = False,
):
    """
    Accepts current and reference data as dicts with box parameters ("mins", "lowers", "uppers", "means", "maxs")
    and name of boxes parameter - "values"
    """
    fig = go.Figure()
    trace = go.Box(
        lowerfence=curr_for_plots["mins"],
        q1=curr_for_plots["lowers"],
        q3=curr_for_plots["uppers"],
        median=curr_for_plots["means"],
        upperfence=curr_for_plots["maxs"],
        x=curr_for_plots["values"] if not transpose else None,
        y=curr_for_plots["values"] if transpose else None,
        name="current",
        marker_color=color_options.get_current_data_color(),
        orientation="v" if not transpose else "h",
    )
    fig.add_trace(trace)
    if ref_for_plots is not None:
        trace = go.Box(
            lowerfence=curr_for_plots["mins"],
            q1=ref_for_plots["lowers"],
            q3=ref_for_plots["uppers"],
            median=ref_for_plots["means"],
            upperfence=ref_for_plots["maxs"],
            x=ref_for_plots["values"] if not transpose else None,
            y=ref_for_plots["values"] if transpose else None,
            name="reference",
            marker_color=color_options.get_reference_data_color(),
            orientation="v" if not transpose else "h",
        )
        fig.add_trace(trace)
        fig.update_layout(boxmode="group")
    fig.update_layout(
        yaxis_title=yaxis_title if not transpose else xaxis_title,
        xaxis_title=xaxis_title if not transpose else yaxis_title,
        boxmode="group",
    )
    fig = json.loads(fig.to_json())
    return fig


def histogram_for_data(
    curr: pd.Series,
    ref: Optional[pd.Series] = None,
) -> Tuple[HistogramData, Optional[HistogramData]]:
    if ref is not None:
        ref = ref.dropna()
    bins = np.histogram_bin_edges(pd.concat([curr.dropna(), ref]), bins="doane")
    curr_hist = np.histogram(curr, bins=bins)
    current = make_hist_df(curr_hist)
    reference = None
    if ref is not None:
        ref_hist = np.histogram(ref, bins=bins)
        reference = make_hist_df(ref_hist)

    return HistogramData.from_df(current), HistogramData.from_df(reference) if reference is not None else None


def make_hist_for_num_plot(curr: pd.Series, ref: Optional[pd.Series] = None, calculate_log: bool = False) -> Histogram:
    current, reference = histogram_for_data(curr, ref)
    current_log = None
    reference_log = None
    if calculate_log:
        current_log, reference_log = histogram_for_data(
            np.log10(curr[curr > 0]),
            np.log10(ref[ref > 0]) if ref is not None else None,
        )
    return Histogram(
        current=current,
        reference=reference,
        current_log=current_log,
        reference_log=reference_log,
    )


def plot_cat_cat_rel(
    curr: pd.DataFrame, ref: pd.DataFrame, target_name: str, feature_name: str, color_options: ColorOptions
):
    """
    Accepts current and reference data as pandas dataframes with two columns: feature_name and "count_objects".
    """
    cols = 1
    subplot_titles: Union[list, str] = ""
    if ref is not None:
        cols = 2
        subplot_titles = ["current", "reference"]
    fig = make_subplots(rows=1, cols=cols, shared_yaxes=True, subplot_titles=subplot_titles)
    visible = []
    for i, val in enumerate(curr[target_name].astype(str).unique()):
        trace = go.Bar(
            x=curr.loc[curr[target_name].astype(str) == val, feature_name],
            y=curr.loc[curr[target_name].astype(str) == val, "count_objects"],
            marker_color=color_options.color_sequence[i],
            name=str(val),
            legendgroup=str(val),
            visible=True,
        )
        fig.add_trace(trace, 1, 1)

        trace = go.Bar(
            x=curr.loc[curr[target_name].astype(str) == val, feature_name],
            y=curr.loc[curr[target_name].astype(str) == val, "count_objects"] * 100 / curr["count_objects"].sum(),
            marker_color=color_options.color_sequence[i],
            name=str(val),
            legendgroup=str(val),
            visible=False,
        )
        fig.add_trace(trace, 1, 1)

        visible += [True, False]

    if ref is not None:
        for i, val in enumerate(ref[target_name].astype(str).unique()):
            trace = go.Bar(
                x=ref.loc[ref[target_name].astype(str) == val, feature_name],
                y=ref.loc[ref[target_name].astype(str) == val, "count_objects"],
                marker_color=color_options.color_sequence[i],
                opacity=0.6,
                name=str(val),
                legendgroup=str(val),
            )
            fig.add_trace(trace, 1, 2)

            trace = go.Bar(
                x=ref.loc[ref[target_name].astype(str) == val, feature_name],
                y=ref.loc[ref[target_name].astype(str) == val, "count_objects"] * 100 / ref["count_objects"].sum(),
                marker_color=color_options.color_sequence[i],
                opacity=0.6,
                name=str(val),
                legendgroup=str(val),
                visible=False,
            )
            fig.add_trace(trace, 1, 2)

            visible += [True, False]
    fig.update_layout(yaxis_title="count")
    updatemenus = collect_updatemenus("abs", "perc", "count", "percent", visible)
    fig.update_layout(updatemenus=updatemenus)
    # if is_subplots:
    #     fig.update_layout(showlegend=False)
    fig = json.loads(fig.to_json())
    return fig


def plot_num_num_rel(
    curr: Dict[str, list],
    ref: Optional[Dict[str, list]],
    target_name: str,
    column_name: str,
    color_options: ColorOptions,
):
    cols = 1
    if ref is not None:
        cols = 2
    fig = make_subplots(rows=1, cols=cols, shared_yaxes=True)
    trace = go.Scatter(
        x=curr[column_name],
        y=curr[target_name],
        mode="markers",
        marker_color=color_options.get_current_data_color(),
        name="current",
    )
    fig.add_trace(trace, 1, 1)
    fig.update_xaxes(title_text=column_name, row=1, col=1)
    if ref is not None:
        trace = go.Scatter(
            x=ref[column_name],
            y=ref[target_name],
            mode="markers",
            marker_color=color_options.get_reference_data_color(),
            name="reference",
        )
        fig.add_trace(trace, 1, 2)
        fig.update_xaxes(title_text=column_name, row=1, col=2)
    fig.update_layout(yaxis_title=target_name, legend={"itemsizing": "constant"})
    fig.update_traces(marker_size=4)
    fig = json.loads(fig.to_json())
    return fig


def make_hist_for_cat_plot(curr: pd.Series, ref: pd.Series = None, normalize: bool = False, dropna=False) -> Histogram:
    hist_df = curr.astype(str).value_counts(normalize=normalize, dropna=dropna).reset_index()
    hist_df.columns = ["x", "count"]
    current = HistogramData.from_df(hist_df)

    reference = None
    if ref is not None:
        hist_df = ref.astype(str).value_counts(normalize=normalize, dropna=dropna).reset_index()
        hist_df.columns = ["x", "count"]
        reference = HistogramData.from_df(hist_df)
    return Histogram(current=current, reference=reference)


def get_distribution_for_category_column(column: pd.Series, normalize: bool = False) -> Distribution:
    value_counts = column.value_counts(normalize=normalize, dropna=False)

    # filter out na values if it amount == 0
    new_values = [(k, v) for k, v in value_counts.items() if (not pd.isna(k) or v > 0)]

    return Distribution(
        x=[x[0] for x in new_values],
        y=[x[1] for x in new_values],
    )


def get_distribution_for_numerical_column(
    column: pd.Series,
    bins: Optional[Union[list, np.ndarray]] = None,
) -> Distribution:
    if bins is None:
        bins = np.histogram_bin_edges(column, bins="doane")

    histogram = np.histogram(column, bins=bins)
    return Distribution(
        x=histogram[1],
        y=histogram[0],
    )


def get_distribution_for_column(
    *, column_type: str, current: pd.Series, reference: Optional[pd.Series] = None
) -> Tuple[Distribution, Optional[Distribution]]:
    reference_distribution: Optional[Distribution] = None

    if column_type == "cat":
        current_distribution = get_distribution_for_category_column(current)

        if reference is not None:
            reference_distribution = get_distribution_for_category_column(reference)

    elif column_type == "num":
        if reference is not None:
            bins = np.histogram_bin_edges(pd.concat([current.dropna(), reference.dropna()]), bins="doane")
            reference_distribution = get_distribution_for_numerical_column(reference, bins)

        else:
            bins = np.histogram_bin_edges(current.dropna(), bins="doane")

        current_distribution = get_distribution_for_numerical_column(current, bins)

    else:
        raise ValueError(f"Cannot get distribution for a column with type {column_type}")

    return current_distribution, reference_distribution


def make_hist_df(hist: Tuple[np.ndarray, np.ndarray]) -> pd.DataFrame:
    hist_df = pd.DataFrame(
        np.array([hist[1][:-1], hist[0], [f"{x[0]}-{x[1]}" for x in zip(hist[1][:-1], hist[1][1:])]]).T,
        columns=["x", "count", "range"],
    )

    hist_df["x"] = hist_df["x"].astype(float)
    hist_df["count"] = hist_df["count"].astype(int)
    return hist_df


def plot_scatter(
    *,
    curr: Dict[str, ScatterData],
    ref: Optional[Dict[str, ScatterData]],
    x: str,
    y: str,
    xaxis_name: str = None,
    yaxis_name: str = None,
    color_options: ColorOptions,
):
    cols = 1
    if xaxis_name is None:
        xaxis_name = x
    if yaxis_name is None:
        yaxis_name = y
    if ref is not None:
        cols = 2
    fig = make_subplots(rows=1, cols=cols, shared_yaxes=True)
    trace = go.Scatter(
        x=curr[x],
        y=curr[y],
        mode="markers",
        marker_color=color_options.get_current_data_color(),
        name="current",
    )
    fig.add_trace(trace, 1, 1)
    fig.update_xaxes(title_text=xaxis_name, row=1, col=1)
    if ref is not None:
        trace = go.Scatter(
            x=ref[x],
            y=ref[y],
            mode="markers",
            marker_color=color_options.get_reference_data_color(),
            name="reference",
        )
        fig.add_trace(trace, 1, 2)
        fig.update_xaxes(title_text=xaxis_name, row=1, col=2)
    fig.update_layout(yaxis_title=yaxis_name, legend={"itemsizing": "constant"})
    fig.update_traces(marker_size=4)
    fig = json.loads(fig.to_json())
    return fig


def plot_pred_actual_time(
    *,
    curr: Dict[Label, pd.Series],
    ref: Optional[Dict[Label, pd.Series]],
    x_name: str = "x",
    xaxis_name: str = "",
    yaxis_name: str = "",
    color_options: ColorOptions,
):
    cols = 1
    subplot_titles: Union[list, str] = ""

    if ref is not None:
        cols = 2
        subplot_titles = ["current", "reference"]

    fig = make_subplots(rows=1, cols=cols, shared_yaxes=True, subplot_titles=subplot_titles)
    for name, color in zip(
        ["Predicted", "Actual"], [color_options.get_current_data_color(), color_options.get_reference_data_color()]
    ):
        trace = go.Scatter(x=curr[x_name], y=curr[name], mode="lines", marker_color=color, name=name, legendgroup=name)
        fig.add_trace(trace, 1, 1)

        if ref is not None:
            trace = go.Scatter(
                x=ref[x_name],
                y=ref[name],
                mode="lines",
                marker_color=color,
                name=name,
                legendgroup=name,
                showlegend=False,
            )
            fig.add_trace(trace, 1, 2)

    # Add zero trace
    trace = go.Scatter(
        x=curr[x_name],
        y=[0] * len(curr[x_name]),
        mode="lines",
        marker_color=color_options.zero_line_color,
        showlegend=False,
    )
    fig.add_trace(trace, 1, 1)
    if ref is not None:
        trace = go.Scatter(
            x=ref[x_name],
            y=[0] * len(ref[x_name]),
            mode="lines",
            marker_color=color_options.zero_line_color,
            showlegend=False,
        )
        fig.add_trace(trace, 1, 2)
        fig.update_xaxes(title_text=xaxis_name, row=1, col=2)

    fig.update_xaxes(title_text=xaxis_name, row=1, col=1)
    fig.update_layout(yaxis_title=yaxis_name)
    fig.update_traces(marker_size=6)
    fig = json.loads(fig.to_json())
    return fig


def plot_line_in_time(
    *,
    curr: Dict[Label, pd.Series],
    ref: Optional[Dict[Label, pd.Series]],
    x_name: str,
    y_name: str,
    xaxis_name: str = "",
    yaxis_name: str = "",
    color_options: ColorOptions,
):
    cols = 1
    subplot_titles: Union[list, str] = ""

    if ref is not None:
        cols = 2
        subplot_titles = ["current", "reference"]

    fig = make_subplots(rows=1, cols=cols, shared_yaxes=True, subplot_titles=subplot_titles)
    trace = go.Scatter(
        x=curr[x_name],
        y=curr[y_name],
        mode="lines",
        marker_color=color_options.get_current_data_color(),
        name=y_name,
        legendgroup=y_name,
    )
    fig.add_trace(trace, 1, 1)
    # Add zero trace
    trace = go.Scatter(
        x=curr[x_name],
        y=[0] * len(curr[x_name]),
        mode="lines",
        marker_color=color_options.zero_line_color,
        showlegend=False,
    )
    fig.add_trace(trace, 1, 1)

    if ref is not None:
        trace = go.Scatter(
            x=ref[x_name],
            y=ref[y_name],
            mode="lines",
            marker_color=color_options.get_current_data_color(),
            name=y_name,
            legendgroup=y_name,
            showlegend=False,
        )
        fig.add_trace(trace, 1, 2)
        # Add zero trace
        trace = go.Scatter(
            x=ref[x_name],
            y=[0] * len(ref[x_name]),
            mode="lines",
            marker_color=color_options.zero_line_color,
            showlegend=False,
        )
        fig.add_trace(trace, 1, 2)
        fig.update_xaxes(title_text=xaxis_name, row=1, col=2)
    fig.update_xaxes(title_text=xaxis_name, row=1, col=1)
    fig.update_layout(yaxis_title=yaxis_name)
    fig.update_traces(marker_size=6)
    fig = json.loads(fig.to_json())
    return fig


def plot_scatter_for_data_drift(
    curr_y: list, curr_x: list, y0: float, y1: float, y_name: str, x_name: str, color_options: ColorOptions
):
    fig = go.Figure()

    x0 = np.max(curr_x)
    x1 = np.min(curr_x)

    fig.add_trace(
        go.Scatter(
            x=[x1, x0, x0, x1],
            y=[y0, y0, y1, y1],
            fill="toself",
            fillcolor=color_options.fill_color,
            opacity=0.5,
            name="reference (+/- 1std)",
            line=dict(color=color_options.fill_color, width=0, dash="solid"),
            marker=dict(size=0),
        )
    )
    fig.add_trace(
        go.Scattergl(
            x=curr_x,
            y=curr_y,
            mode="markers",
            name="Current",
            marker=dict(size=6, color=color_options.get_current_data_color()),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=curr_x,
            y=[(y0 + y1) / 2] * len(curr_x),
            mode="lines",
            marker_color=color_options.zero_line_color,
            name="reference (mean)",
        )
    )

    fig.update_layout(
        xaxis_title=x_name,
        yaxis_title=y_name,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def plot_conf_mtrx(curr_mtrx, ref_mtrx):
    if ref_mtrx is not None:
        cols = 2
        subplot_titles = ["current", "reference"]
    else:
        cols = 1
        subplot_titles = [""]
    fig = make_subplots(rows=1, cols=cols, subplot_titles=subplot_titles, shared_yaxes=True)
    trace = go.Heatmap(
        z=curr_mtrx.values,
        x=[str(item) for item in curr_mtrx.labels],
        y=[str(item) for item in curr_mtrx.labels],
        text=np.array(curr_mtrx.values).astype(str),
        texttemplate="%{text}",
        coloraxis="coloraxis",
    )
    fig.add_trace(trace, 1, 1)

    if ref_mtrx is not None:
        trace = go.Heatmap(
            z=ref_mtrx.values,
            x=[str(item) for item in ref_mtrx.labels],
            y=[str(item) for item in ref_mtrx.labels],
            text=np.array(ref_mtrx.values).astype(str),
            texttemplate="%{text}",
            coloraxis="coloraxis",
        )
        fig.add_trace(trace, 1, 2)
    fig.update_layout(coloraxis={"colorscale": "RdBu_r"})
    return fig


def is_possible_contour(m1, m2) -> bool:
    try:
        values = np.vstack([m1, m2])
        stats.gaussian_kde(values)
        return True
    except (LinAlgError, ValueError):
        return False


def get_gaussian_kde(m1, m2):
    xmin = m1.min()
    xmax = m1.max()
    ymin = m2.min()
    ymax = m2.max()
    xdelta = 2 * (xmax - xmin) / 10
    ydelta = 2 * (ymax - ymin) / 10
    # X, Y = np.mgrid[xmin - border(xmin) : xmax + border(xmax) : 30j, ymin - border(ymin) : ymax + border(ymax) : 30j]
    X, Y = np.mgrid[xmin - xdelta : xmax + xdelta : 30j, ymin - ydelta : ymax + ydelta : 30j]
    x = np.linspace(xmin - xdelta, xmax + xdelta, num=30)
    y = np.linspace(ymin - ydelta, ymax + ydelta, num=30)
    positions = np.vstack([X.ravel(), Y.ravel()])
    values = np.vstack([m1, m2])
    kernel = stats.gaussian_kde(values)
    Z = np.reshape(kernel(positions).T, X.shape)
    return Z, list(x), list(y)


def plot_contour_single(z1: np.ndarray, z2: Optional[np.ndarray], xtitle: str = "", ytitle: str = ""):
    color_options = ColorOptions()
    if z2 is not None:
        cols = 2
        subplot_titles = ["current", "reference"]
    else:
        cols = 1
        subplot_titles = [""]
    fig = make_subplots(rows=1, cols=cols, shared_yaxes=True, subplot_titles=subplot_titles)
    trace = go.Contour(
        z=z1,
        line_width=1,
        name="current",
        showscale=False,
        showlegend=True,
        colorscale=[[0, "white"], [1, color_options.get_current_data_color()]],
    )
    fig.add_trace(trace, 1, 1)
    fig.update_xaxes(title_text=xtitle, row=1, col=1)

    if z2 is not None:
        trace = go.Contour(
            z=z2,
            line_width=1,
            name="reference",
            showscale=False,
            showlegend=True,
            colorscale=[[0, "white"], [1, color_options.get_reference_data_color()]],
        )
        fig.add_trace(trace, 1, 2)
        fig.update_xaxes(title_text=xtitle, row=1, col=2)
    fig.update_layout(yaxis_title=ytitle)
    return fig


def plot_contour(curr_contour: ContourData, ref_contour: Optional[ContourData], xtitle: str = "", ytitle: str = ""):
    color_options = ColorOptions()
    if ref_contour is not None:
        cols = 2
        subplot_titles = ["current", "reference"]
    else:
        cols = 1
        subplot_titles = [""]
    fig = make_subplots(rows=1, cols=cols, shared_yaxes=True, subplot_titles=subplot_titles)
    z1, y1, x1 = curr_contour[0], curr_contour[1], curr_contour[2]
    trace = go.Contour(
        z=z1,
        x=x1,
        y=y1,
        line_width=1,
        name="current",
        showscale=False,
        showlegend=True,
        colorscale=[[0, "white"], [1, color_options.get_current_data_color()]],
    )
    fig.add_trace(trace, 1, 1)
    fig.update_xaxes(title_text=xtitle, row=1, col=1)

    if ref_contour is not None:
        z2, y2, x2 = ref_contour[0], ref_contour[1], ref_contour[2]
        trace = go.Contour(
            z=z2,
            x=x2,
            y=y2,
            line_width=1,
            name="reference",
            showscale=False,
            showlegend=True,
            colorscale=[[0, "white"], [1, color_options.get_reference_data_color()]],
        )
        fig.add_trace(trace, 1, 2)
        fig.update_xaxes(title_text=xtitle, row=1, col=2)
    fig.update_layout(yaxis_title=ytitle)
    return fig


def plot_top_error_contours(
    curr_contour: Dict[str, ContourData],
    ref_contour: Optional[Dict[str, ContourData]],
    xtitle: str = "",
    ytitle: str = "",
):
    color_options = ColorOptions()
    if ref_contour is not None:
        cols = 2
        subplot_titles = ["current", "reference"]
    else:
        cols = 1
        subplot_titles = [""]
    fig = make_subplots(rows=1, cols=cols, shared_yaxes=True, subplot_titles=subplot_titles)
    for label, color in zip(
        ["underestimation", "majority", "overestimation"],
        [color_options.underestimation_color, color_options.majority_color, color_options.overestimation_color],
    ):
        z, y, x = curr_contour[label]
        trace = go.Contour(
            z=z,
            x=x,
            y=y,
            line_width=1,
            name=label,
            showscale=False,
            legendgroup=label,
            showlegend=True,
            contours_coloring="lines",
            colorscale=[[0, color], [1, color]],
        )
        fig.add_trace(trace, 1, 1)
        fig.update_xaxes(title_text=xtitle, row=1, col=1)

        if ref_contour is not None:
            z, y, x = ref_contour[label]
            trace = go.Contour(
                z=z,
                x=x,
                y=y,
                line_width=1,
                name=label,
                showscale=False,
                legendgroup=label,
                showlegend=False,
                contours_coloring="lines",
                colorscale=[[0, color], [1, color]],
            )
            fig.add_trace(trace, 1, 2)
            fig.update_xaxes(title_text=xtitle, row=1, col=2)
    fig.update_layout(yaxis_title=ytitle)
    return fig


def choose_agg_period(current_date_column: pd.Series, reference_date_column: Optional[pd.Series]) -> Tuple[str, str]:
    prefix_dict = {"A": "year", "Q": "quarter", "M": "month", "W": "week", "D": "day", "H": "hour", "min": "minute"}
    datetime_feature = current_date_column
    if reference_date_column is not None:
        datetime_feature = pd.concat([datetime_feature, reference_date_column])
    days = (datetime_feature.max() - datetime_feature.min()).days
    if days == 0:
        days = (datetime_feature.max() - datetime_feature.min()).seconds / (3600 * 24)
    time_points = pd.Series(
        index=["A", "Q", "M", "W", "D", "H", "min"],
        data=[
            abs(OPTIMAL_POINTS - days / 365),
            abs(OPTIMAL_POINTS - days / 90),
            abs(OPTIMAL_POINTS - days / 30),
            abs(OPTIMAL_POINTS - days / 7),
            abs(OPTIMAL_POINTS - days),
            abs(OPTIMAL_POINTS - days * 24),
            abs(OPTIMAL_POINTS - days * 24 * 60),
        ],
    )
    period_prefix = prefix_dict[time_points.idxmin()]
    return period_prefix, str(time_points.idxmin())


def get_plot_df(df, datetime_name, column_name, freq):
    plot_df = df.copy()
    plot_df["per"] = plot_df[datetime_name].dt.to_period(freq=freq)
    plot_df = plot_df.groupby("per")[column_name].agg(["mean", "std"]).reset_index()
    plot_df["per"] = plot_df["per"].dt.to_timestamp()
    return plot_df


def prepare_df_for_time_index_plot(
    df: pd.DataFrame,
    column_name: str,
    datetime_name: Optional[str],
    prefix: Optional[str] = None,
    freq: Optional[str] = None,
    bins: Optional[np.ndarray] = None,
) -> Tuple[pd.DataFrame, Optional[str]]:
    index_name = df.index.name
    if index_name is None:
        index_name = "index"
    if datetime_name is None and is_datetime64_any_dtype(df.index):
        df = df.copy().reset_index()
        datetime_name = index_name
    if datetime_name is not None:
        if prefix is None and freq is None:
            prefix, freq = choose_agg_period(df[datetime_name], None)
        plot_df = df.copy()
        plot_df["per"] = plot_df[datetime_name].dt.to_period(freq=freq)
        plot_df = plot_df.groupby("per")[column_name].agg(["mean", "std"]).reset_index()
        plot_df["per"] = plot_df["per"].dt.to_timestamp()
        return plot_df, prefix
    plot_df = df[column_name].reset_index().sort_values(index_name)
    plot_df["per"] = pd.cut(plot_df[index_name], OPTIMAL_POINTS if bins is None else bins, labels=False)
    plot_df = plot_df.groupby("per")[column_name].agg(["mean", "std"]).reset_index()
    return plot_df, None


def get_traces(df, color, error_band_opacity, name, showlegend):
    error_band_trace = go.Scatter(
        x=list(df["per"]) + list(df["per"][::-1]),  # x, then x reversed
        y=list(df["mean"] + df["std"].fillna(0))
        + list(df["mean"] - df["std"].fillna(0))[::-1],  # upper, then lower reversed
        fill="toself",
        fillcolor=color,
        opacity=error_band_opacity,
        line=dict(color=color),
        hoverinfo="skip",
        showlegend=False,
    )
    line_trace = go.Scatter(
        x=df["per"],
        y=df["mean"],
        line=dict(color=color),
        mode="lines",
        name=name,
        legendgroup=name,
        showlegend=showlegend,
    )
    return error_band_trace, line_trace


def rect_trace(line, std, min_value, max_value, color):
    return go.Scatter(
        x=[min_value, max_value, max_value, min_value],
        y=[line + std, line + std, line - std, line - std],
        fill="toself",
        fillcolor=color,
        opacity=0.5,
        name="reference (+/- 1std)",
        line=dict(color=color, width=0, dash="solid"),
        marker=dict(size=0),
    )


def collect_traces(
    data: Dict,
    line: Optional[float],
    std: Optional[float],
    color_options: ColorOptions,
    showlegend: bool,
    line_name: Optional[str] = None,
):
    name = list(data.keys())[0]
    traces = []
    if line is not None:
        green_line_trace = go.Scatter(
            x=data[name]["per"],
            y=[line] * len(data[name]["per"]),
            mode="lines",
            marker_color=color_options.zero_line_color,
            name=line_name,
            showlegend=True if line_name is not None else False,
        )
        traces.append(green_line_trace)
    if std is not None and line is not None:
        trace_rect = rect_trace(line, std, data[name]["per"].min(), data[name]["per"].max(), color_options.fill_color)
        traces.append(trace_rect)
    if len(data.keys()) == 1:
        error_band_trace, line_trace = get_traces(
            data[name], color_options.get_current_data_color(), 0.2, name, showlegend
        )
        traces += [error_band_trace, line_trace]
        return traces

    if {"Predicted", "Actual"} == set(data.keys()):
        error_band_trace_pred, line_trace_pred = get_traces(
            data["Predicted"],
            color_options.get_current_data_color(),
            0.2,
            "Predicted",
            showlegend,
        )
        error_band_trace_act, line_trace_act = get_traces(
            data["Actual"],
            color_options.get_reference_data_color(),
            0.3,
            "Actual",
            showlegend,
        )
        traces += [error_band_trace_act, error_band_trace_pred, line_trace_act, line_trace_pred]
        return traces
    assert {"reference", "current"} == set(data.keys())
    error_band_trace_pred, line_trace_pred = get_traces(
        data["current"],
        color_options.get_current_data_color(),
        0.2,
        "current",
        showlegend,
    )
    error_band_trace_act, line_trace_act = get_traces(
        data["reference"],
        color_options.get_reference_data_color(),
        0.2,
        "reference",
        showlegend,
    )
    traces += [error_band_trace_act, error_band_trace_pred, line_trace_act, line_trace_pred]

    return traces


def plot_agg_line_data(
    curr_data: Dict,
    ref_data: Optional[Dict],
    line: Optional[float],
    std: Optional[float],
    xaxis_name: str,
    xaxis_name_ref: Optional[str],
    yaxis_name: str,
    color_options: ColorOptions,
    return_json: bool = True,
    line_name: Optional[str] = None,
):
    cols = 1
    subplot_titles: Union[list, str] = ""

    if ref_data is not None:
        cols = 2
        subplot_titles = ["current", "reference"]

    fig = make_subplots(rows=1, cols=cols, shared_yaxes=True, subplot_titles=subplot_titles)
    curr_traces = collect_traces(curr_data, line, std, color_options, True, line_name)
    for trace in curr_traces:
        fig.add_trace(trace, 1, 1)
    if ref_data is not None:
        ref_traces = collect_traces(ref_data, line, std, color_options, False)
        for trace in ref_traces:
            fig.add_trace(trace, 1, 2)
        fig.update_xaxes(title_text=xaxis_name_ref, row=1, col=2)
    fig.update_xaxes(title_text=xaxis_name, row=1, col=1)
    fig.update_layout(yaxis_title=yaxis_name)

    if return_json:
        return json.loads(fig.to_json())
    return fig


def plot_metric_k(curr_data: pd.Series, ref_data: Optional[pd.Series], yaxis_name: str):
    color_options = ColorOptions()
    cols = 1
    subplot_titles: Union[list, str] = ""

    if ref_data is not None:
        cols = 2
        subplot_titles = ["current", "reference"]

    fig = make_subplots(rows=1, cols=cols, shared_yaxes=True, subplot_titles=subplot_titles)
    fig.add_trace(go.Scatter(x=curr_data.index, y=curr_data, marker_color=color_options.get_current_data_color()), 1, 1)
    if ref_data is not None:
        fig.add_trace(
            go.Scatter(x=ref_data.index, y=ref_data, marker_color=color_options.get_reference_data_color()), 1, 2
        )
    fig.update_xaxes(title_text="k", tickformat=",d")
    fig.update_layout(yaxis_title=yaxis_name, showlegend=False)
    return fig


def plot_bias(
    curr: Distribution,
    curr_train: Distribution,
    ref: Optional[Distribution],
    ref_train: Optional[Distribution],
    xaxis_name: str,
):
    color_options = ColorOptions()

    cols = 1
    subplot_titles: Union[list, str] = ""
    if ref is not None:
        cols = 2
        subplot_titles = ["current", "reference"]
    fig = make_subplots(rows=1, cols=cols, shared_yaxes=True, subplot_titles=subplot_titles)
    trace = go.Bar(
        x=curr.x,
        y=(curr.count / curr.count.sum()) * 100,
        marker_color=color_options.get_current_data_color(),
        name="recommendation",
        legendgroup="recommendation",
    )
    fig.add_trace(trace, 1, 1)
    trace = go.Bar(
        x=curr_train.x,
        y=(curr_train.count / curr_train.count.sum()) * 100,
        marker_color=color_options.additional_data_color,
        name="train",
        legendgroup="train",
    )
    fig.add_trace(trace, 1, 1)
    if ref is not None and ref_train is not None:
        trace = go.Bar(
            x=ref.x,
            y=(ref.count / ref.count.sum()) * 100,
            marker_color=color_options.get_current_data_color(),
            name="recommendation",
            legendgroup="recommendation",
            showlegend=False,
        )
        fig.add_trace(trace, 1, 2)
        trace = go.Bar(
            x=ref_train.x,
            y=(ref_train.count / ref_train.count.sum()) * 100,
            marker_color=color_options.additional_data_color,
            name="train",
            legendgroup="train",
            showlegend=False,
        )
        fig.add_trace(trace, 1, 2)
    fig.update_layout(yaxis_title="percent")
    fig.update_xaxes(title_text=xaxis_name)
    return fig


def plot_4_distr(
    curr_1: Distribution,
    curr_2: Optional[Distribution],
    ref_1: Optional[Distribution],
    ref_2: Optional[Distribution],
    name_1: str,
    name_2: str,
    xaxis_name: str,
    color_2: str = "additional",
):
    color_options = ColorOptions()
    if color_2 == "additional":
        color_2 = color_options.additional_data_color
    else:
        color_2 = color_options.secondary_color

    cols = 1
    subplot_titles: Union[list, str] = ""
    if ref_1 is not None:
        cols = 2
        subplot_titles = ["current", "reference"]
    fig = make_subplots(rows=1, cols=cols, shared_yaxes=True, subplot_titles=subplot_titles)
    trace = go.Bar(
        x=curr_1.x,
        y=(curr_1.count / curr_1.count.sum()) * 100,
        marker_color=color_options.get_current_data_color(),
        name=name_1,
        legendgroup=name_1,
    )
    fig.add_trace(trace, 1, 1)
    if curr_2 is not None:
        trace = go.Bar(
            x=curr_2.x,
            y=(curr_2.count / curr_2.count.sum()) * 100,
            marker_color=color_2,
            name=name_2,
            legendgroup=name_2,
        )
        fig.add_trace(trace, 1, 1)
    if ref_1 is not None:
        trace = go.Bar(
            x=ref_1.x,
            y=(ref_1.count / ref_1.count.sum()) * 100,
            marker_color=color_options.get_current_data_color(),
            name=name_1,
            legendgroup=name_1,
            showlegend=False,
        )
        fig.add_trace(trace, 1, 2)
    if ref_2 is not None:
        trace = go.Bar(
            x=ref_2.x,
            y=(ref_2.count / ref_2.count.sum()) * 100,
            marker_color=color_2,
            name=name_2,
            legendgroup=name_2,
            showlegend=False,
        )
        fig.add_trace(trace, 1, 2)
    fig.update_layout(yaxis_title="percent")
    fig.update_xaxes(title_text=xaxis_name)
    return fig
