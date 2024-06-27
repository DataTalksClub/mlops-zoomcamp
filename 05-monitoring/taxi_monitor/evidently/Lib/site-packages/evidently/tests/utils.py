from typing import List
from typing import Optional
from typing import Tuple

import numpy as np
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from evidently.metric_results import Boxes
from evidently.metric_results import RatesPlotData
from evidently.model.widget import BaseWidgetInfo
from evidently.options import ColorOptions
from evidently.renderers.base_renderer import DetailsInfo
from evidently.renderers.html_widgets import plotly_figure
from evidently.renderers.html_widgets import table_data
from evidently.utils.types import ApproxValue


def plot_check(fig, condition, color_options: ColorOptions):
    lines = []
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

    fig = go.Figure(fig)
    max_y = np.max([np.max(x["y"]) for x in fig.data])

    if len(lines) > 0:
        for line, name in lines:
            fig.add_trace(
                go.Scatter(
                    x=(line, line),
                    y=(0, max_y),
                    mode="lines",
                    line=dict(color=color_options.secondary_color, width=3, dash="dash"),
                    name=name,
                )
            )

    if left_line and right_line:
        fig.add_vrect(x0=left_line, x1=right_line, fillcolor="green", opacity=0.25, line_width=0)

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

    fig.update_layout(showlegend=True)
    return fig


def plot_metric_value(fig, metric_val: float, metric_name: str):
    fig = go.Figure(fig)
    max_y = np.max([np.max(x["y"]) for x in fig.data])
    min_y = np.min([np.min(x["y"]) for x in fig.data])
    fig.add_trace(
        go.Scatter(
            x=(metric_val, metric_val),
            y=(min_y, max_y),
            mode="lines",
            line=dict(color="green", width=3),
            name=metric_name,
        )
    )
    fig.update_layout(showlegend=True)
    return fig


def plot_value_counts_tables(feature_name, values, curr_df, ref_df, id_prfx):
    additional_plots = []
    if values is not None:
        curr_df = curr_df[curr_df["count"] != 0]
        curr_vals_inside_lst = curr_df[curr_df.x.isin(values)].sort_values("count", ascending=False)
        data = np.array(["", ""])
        if curr_vals_inside_lst.shape[0] > 0:
            data = curr_vals_inside_lst[:10].values
        additional_plots.append(
            DetailsInfo(
                title="Values inside the list (top 10)",
                info=table_data(
                    column_names=["value", "count"],
                    data=data,
                ),
            )
        )
        curr_vals_outside_lst = curr_df[~curr_df.x.isin(values)].sort_values("count", ascending=False)
        data = np.array(["", ""])
        if curr_vals_outside_lst.shape[0] > 0:
            data = curr_vals_outside_lst[:10].values
        additional_plots.append(
            DetailsInfo(
                title="Values outside the list (top 10)",
                info=table_data(
                    column_names=["value", "count"],
                    data=curr_vals_outside_lst[:10].values,
                ),
            )
        )

    return additional_plots


def plot_value_counts_tables_ref_curr(feature_name, curr_df, ref_df, id_prfx):
    additional_plots = []
    curr_df = curr_df[curr_df["count"] != 0]

    additional_plots.append(
        DetailsInfo(
            title="Current value counts (top 10)",
            info=table_data(column_names=["value", "count"], data=curr_df[:10].values),
        )
    )
    if ref_df is not None:
        ref_df = ref_df[ref_df["count"] != 0]
        additional_plots.append(
            DetailsInfo(
                title="Reference value counts (top 10)",
                info=table_data(column_names=["value", "count"], data=ref_df[:10].values),
            )
        )
    return additional_plots


def approx(value, relative=None, absolute=None):
    """Get approximate value for checking a value is equal to other within some tolerance"""
    return ApproxValue(value=value, relative=relative, absolute=absolute)


class ApproxValueNoDict(ApproxValue):
    def dict(self, *args, **kwargs):
        return self


# some monkeing for np asserts to work with ApproxValue
np.core.numeric.ScalarType = np.core.numeric.ScalarType + (ApproxValue, ApproxValueNoDict)  # type: ignore[attr-defined]


def approx_result(value, relative=None, absolute=None):
    """Get approximate value for checking a value is equal to other within some tolerance"""
    return ApproxValueNoDict(value=value, relative=relative, absolute=absolute)


def dataframes_to_table(
    current: pd.DataFrame,
    reference: Optional[pd.DataFrame],
    columns: List[str],
    table_id: str,
    sort_by: str = "curr",
    na_position: str = "first",
    asc: bool = False,
):
    display_columns = ["display"]
    if reference is not None:
        display_columns += ["ref_display"]
        df = pd.merge(
            current,
            reference.rename(columns={"value": "ref_value", "display": "ref_display"}),
            how="outer",
            left_index=True,
            right_index=True,
        )
        df["eq"] = (df["value"] == df["ref_value"]) | (df["value"].isna() & df["ref_value"].isna())
        if "ref_display" not in df.columns:
            df["ref_display"] = df["ref_value"].fillna("NA").astype(str)
    else:
        df = current
    if "display" not in df.columns:
        df["display"] = df["value"].fillna("NA").astype(str)
    if sort_by == "curr":
        df.sort_values("value", na_position=na_position, inplace=True, ascending=asc)
    elif sort_by == "diff" and reference is not None:
        df.sort_values("eq", inplace=True)

    df = df[display_columns].fillna("NA")
    return [
        DetailsInfo(
            id=table_id,
            title="",
            info=BaseWidgetInfo(
                title="",
                type="table",
                params={
                    "header": list(columns),
                    "data": [[idx] + list(df.loc[idx].values) for idx in df.index],
                },
                size=2,
            ),
        )
    ]


def plot_dicts_to_table(
    dict_curr: dict, dict_ref: Optional[dict], columns: list, id_prfx: str, sort_by: str = "curr", asc: bool = False
):
    return dataframes_to_table(
        pd.DataFrame.from_dict(dict_curr, orient="index", columns=["value"]),
        None if dict_ref is None else pd.DataFrame.from_dict(dict_ref, orient="index", columns=["value"]),
        columns=columns,
        table_id=id_prfx,
        sort_by=sort_by,
        na_position="first",
        asc=asc,
    )


def plot_correlations(current_correlations, reference_correlations):
    columns = current_correlations.columns
    heatmap_text = None
    heatmap_texttemplate = None

    if reference_correlations is not None:
        cols = 2
        subplot_titles = ["current", "reference"]
    else:
        cols = 1
        subplot_titles = [""]

    fig = make_subplots(rows=1, cols=cols, subplot_titles=subplot_titles, shared_yaxes=True)
    if len(columns) < 15:
        heatmap_text = np.round(current_correlations, 2).astype(str)
        heatmap_texttemplate = "%{text}"

    trace = go.Heatmap(
        z=current_correlations,
        x=columns,
        y=columns,
        text=heatmap_text,
        texttemplate=heatmap_texttemplate,
        coloraxis="coloraxis",
    )
    fig.add_trace(trace, 1, 1)

    if reference_correlations is not None:
        if len(columns) < 15:
            heatmap_text = np.round(reference_correlations, 2).astype(str)
            heatmap_texttemplate = "%{text}"

        trace = go.Heatmap(
            z=reference_correlations,
            x=columns,
            y=columns,
            text=heatmap_text,
            texttemplate=heatmap_texttemplate,
            coloraxis="coloraxis",
        )
        fig.add_trace(trace, 1, 2)
    fig.update_layout(coloraxis={"colorscale": "RdBu_r"})
    fig.update_yaxes(type="category")
    fig.update_xaxes(tickangle=-45)
    return fig


# todo typing: ConfusionMatrix
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
        x=list(map(str, curr_mtrx.labels)),
        y=list(map(str, curr_mtrx.labels)),
        text=np.array(curr_mtrx.values).astype(str),
        texttemplate="%{text}",
        coloraxis="coloraxis",
    )
    fig.add_trace(trace, 1, 1)

    if ref_mtrx is not None:
        trace = go.Heatmap(
            z=ref_mtrx.values,
            x=list(map(str, ref_mtrx.labels)),
            y=list(map(str, ref_mtrx.labels)),
            text=np.array(ref_mtrx.values).astype(str),
            texttemplate="%{text}",
            coloraxis="coloraxis",
        )
        fig.add_trace(trace, 1, 2)
    fig.update_layout(coloraxis={"colorscale": "RdBu_r"})
    return fig


def plot_roc_auc(
    *, curr_roc_curve: dict, ref_roc_curve: Optional[dict], color_options: ColorOptions
) -> List[Tuple[str, BaseWidgetInfo]]:
    additional_plots = []
    cols = 1
    subplot_titles = [""]
    current_color = color_options.get_current_data_color()
    reference_color = color_options.get_reference_data_color()

    if ref_roc_curve is not None:
        cols = 2
        subplot_titles = ["current", "reference"]

    for label in curr_roc_curve.keys():
        fig = make_subplots(rows=1, cols=cols, subplot_titles=subplot_titles, shared_yaxes=True)
        trace = go.Scatter(
            x=curr_roc_curve[label]["fpr"],
            y=curr_roc_curve[label]["tpr"],
            mode="lines",
            name="ROC",
            marker=dict(
                size=6,
                color=current_color,
            ),
        )
        fig.add_trace(trace, 1, 1)

        if ref_roc_curve is not None:
            trace = go.Scatter(
                x=ref_roc_curve[label]["fpr"],
                y=ref_roc_curve[label]["tpr"],
                mode="lines",
                name="ROC",
                marker=dict(
                    size=6,
                    color=reference_color,
                ),
            )
            fig.add_trace(trace, 1, 2)
        fig.update_layout(
            yaxis_title="True Positive Rate",
            xaxis_title="False Positive Rate",
            showlegend=True,
        )
        additional_plots.append((f"ROC Curve for label {label}", plotly_figure(title="", figure=fig)))

    return additional_plots


def plot_boxes(*, curr_for_plots: Boxes, ref_for_plots: Optional[Boxes], color_options: ColorOptions):
    current_color = color_options.get_current_data_color()
    reference_color = color_options.get_reference_data_color()
    fig = go.Figure()
    trace = go.Box(
        lowerfence=curr_for_plots.mins,
        q1=curr_for_plots.lowers,
        q3=curr_for_plots.uppers,
        median=curr_for_plots.means,
        upperfence=curr_for_plots.maxs,
        name="current",
        marker_color=current_color,
    )
    fig.add_trace(trace)
    if ref_for_plots is not None:
        trace = go.Box(
            lowerfence=curr_for_plots.mins,
            q1=ref_for_plots.lowers,
            q3=ref_for_plots.uppers,
            median=ref_for_plots.means,
            upperfence=ref_for_plots.maxs,
            name="reference",
            marker_color=reference_color,
        )
        fig.add_trace(trace)
        fig.update_layout(boxmode="group")

    fig.update_layout(
        yaxis_title="Prerdictions",
        xaxis_title="Class",
    )
    return fig


def plot_rates(
    *,
    curr_rate_plots_data: RatesPlotData,
    ref_rate_plots_data: Optional[RatesPlotData] = None,
    color_options: ColorOptions,
):
    if ref_rate_plots_data is not None:
        cols = 2
        subplot_titles = ["current", "reference"]
    else:
        cols = 1
        subplot_titles = [""]

    curr_df = pd.DataFrame(
        {
            "thrs": curr_rate_plots_data.thrs,
            "fpr": curr_rate_plots_data.fpr,
            "tpr": curr_rate_plots_data.tpr,
            "fnr": curr_rate_plots_data.fnr,
            "tnr": curr_rate_plots_data.tnr,
        }
    )
    curr_df = curr_df[curr_df.thrs <= 1]

    fig = make_subplots(rows=1, cols=cols, subplot_titles=subplot_titles, shared_yaxes=True)
    for i, metric in enumerate(["fpr", "tpr", "fnr", "tnr"]):
        fig.add_trace(
            go.Scatter(
                x=curr_df["thrs"],
                y=curr_df[metric],
                mode="lines",
                legendgroup=metric,
                name=metric,
                marker_color=color_options.color_sequence[i],
            ),
            1,
            1,
        )
    if ref_rate_plots_data is not None:
        ref_df = pd.DataFrame(
            {
                "thrs": ref_rate_plots_data.thrs,
                "fpr": ref_rate_plots_data.fpr,
                "tpr": ref_rate_plots_data.tpr,
                "fnr": ref_rate_plots_data.fnr,
                "tnr": ref_rate_plots_data.tnr,
            }
        )
        ref_df = ref_df[ref_df.thrs <= 1]
        for i, metric in enumerate(["fpr", "tpr", "fnr", "tnr"]):
            fig.add_trace(
                go.Scatter(
                    x=ref_df["thrs"],
                    y=ref_df[metric],
                    mode="lines",
                    legendgroup=metric,
                    name=metric,
                    showlegend=False,
                    marker_color=color_options.color_sequence[i],
                ),
                1,
                2,
            )
    fig.update_layout(
        xaxis_title="threshold",
    )

    return fig
