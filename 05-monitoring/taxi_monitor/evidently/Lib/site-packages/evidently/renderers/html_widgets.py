import dataclasses
from enum import Enum
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union
from uuid import uuid4

import numpy as np
import pandas as pd
from plotly import graph_objs as go
from plotly.subplots import make_subplots

from evidently.metric_results import Distribution
from evidently.metric_results import HistogramData
from evidently.metric_results import LiftCurve
from evidently.metric_results import PRCurve
from evidently.metric_results import ROCCurve
from evidently.model.widget import BaseWidgetInfo
from evidently.model.widget import PlotlyGraphInfo
from evidently.model.widget import TabInfo
from evidently.model.widget import WidgetType
from evidently.options import ColorOptions


class WidgetSize(int, Enum):
    HALF = 1
    FULL = 2


class GraphData:
    title: str
    data: dict
    layout: dict

    def __init__(self, title: str, data: dict, layout: dict):
        """
        create GraphData object for usage in plotly_graph_tabs or plotly_data.

        Args:
            title: title of graph
            data: plotly figure data
            layout: plotly figure layout
        """
        self.title = title
        self.data = data
        self.layout = layout

    @staticmethod
    def figure(title: str, figure: go.Figure):
        """
        create GraphData from plotly figure itself
        Args:
            title: title of graph
            figure: plotly figure for getting data from
        """
        data = figure.to_plotly_json()
        return GraphData(title, data["data"], data["layout"])


def plotly_graph(*, graph_data: GraphData, size: WidgetSize = WidgetSize.FULL) -> BaseWidgetInfo:
    """
    generate plotly plot with given GraphData object.

    Args:
        graph_data: plot data for widget
        size: size of widget to render

    Example:
        >>> figure = go.Figure(go.Bar(name="Bar plot", x=[1, 2, 3, 4], y=[10, 11, 20, 11]))
        >>> f_dict = figure.to_plotly_json()
        >>> bar_graph_data = GraphData(title="Some plot title", data=f_dict["data"], layout=f_dict["layout"])
        >>> widget_info = plotly_graph(graph_data=bar_graph_data, size=WidgetSize.FULL)
    """
    return BaseWidgetInfo(
        title=graph_data.title,
        type=WidgetType.BIG_GRAPH.value,
        size=size.value,
        params={"data": graph_data.data, "layout": graph_data.layout},
    )


def plotly_data(*, title: str, data: dict, layout: dict, size: WidgetSize = WidgetSize.FULL) -> BaseWidgetInfo:
    """
    generate plotly plot with given data and layout (can be generated from plotly).

    Args:
        title: widget title
        data: plotly figure data
        layout: plotly figure layout
        size: widget size

    Example:
        >>> figure = go.Figure(go.Bar(name="Bar plot", x=[1, 2, 3, 4], y=[10, 11, 20, 11]))
        >>> f_dict = figure.to_plotly_json()
        >>> widget_info = plotly_data(title="Some plot title", data=f_dict["data"], layout=f_dict["layout"])
    """
    return plotly_graph(graph_data=GraphData(title, data, layout), size=size)


def plotly_figure(*, title: str, figure: go.Figure, size: WidgetSize = WidgetSize.FULL) -> BaseWidgetInfo:
    """
    generate plotly plot based on given plotly figure object.

    Args:
        title: title of widget
        figure: plotly figure which should be rendered as widget
        size: size of widget, default to WidgetSize.FULL

    Example:
        >>> bar_figure = go.Figure(go.Bar(name="Bar plot", x=[1, 2, 3, 4], y=[10, 11, 20, 11]))
        >>> widget_info = plotly_figure(title="Bar plot widget", figure=bar_figure, size=WidgetSize.FULL)
    """
    return plotly_graph(graph_data=GraphData.figure(title=title, figure=figure), size=size)


def plotly_graph_tabs(*, title: str, figures: List[GraphData], size: WidgetSize = WidgetSize.FULL) -> BaseWidgetInfo:
    """
    generate Tab widget with multiple graphs

    Args:
        title: widget title
        figures: list of graphs with tab titles
        size: widget size

    Example:
        >>> bar_figure = go.Figure(go.Bar(name="Bar plot", x=[1, 2, 3, 4], y=[10, 11, 20, 11]))
        >>> line_figure = go.Figure(go.Line(name="Bar plot", x=[1, 2, 3, 4], y=[10, 11, 20, 11]))
        >>> widget_info = plotly_graph_tabs(
        ...     title="Tabbed widget",
        ...     figures=[GraphData.figure("Bar", bar_figure), GraphData.figure("Line", line_figure)],
        ... )
    """
    return BaseWidgetInfo(
        title=title,
        type=WidgetType.TABBED_GRAPH.value,
        size=size.value,
        params={
            "graphs": [
                {
                    "id": str(uuid4()),
                    "title": graph.title,
                    "graph": {
                        "data": graph.data,
                        "layout": graph.layout,
                    },
                }
                for graph in figures
            ]
        },
    )


class CounterData:
    label: str
    value: str

    def __init__(self, label: str, value: str):
        """
        creates CounterData for counter widget with given label and value.

        Args:
            label: counter label
            value: counter value
        """
        self.label = label
        self.value = value

    @staticmethod
    def float(label: str, value: float, precision: int) -> "CounterData":
        """
        create CounterData for float value with given precision.

        Args:
            label: counter label
            value: float value of counter
            precision: decimal precision
        """
        return CounterData(label, f"{value:.{precision}}")

    @staticmethod
    def string(label: str, value: str) -> "CounterData":
        """
        create CounterData for string value with given precision.

        Args:
            label: counter label
            value: string value of counter
        """
        return CounterData(label, f"{value}")

    @staticmethod
    def int(label: str, value: int) -> "CounterData":
        """
        create CounterData for int value.

        Args:
            label: counter label
            value: int value
        """
        return CounterData(label, f"{value}")


def counter(*, counters: List[CounterData], title: str = "", size: WidgetSize = WidgetSize.FULL) -> BaseWidgetInfo:
    """
    generate widget with given counters

    Args:
        title: widget title
        counters: list of counters in widget
        size: widget size

    Example:
        >>> display_counters = [CounterData("value1", "some value"), CounterData.float("float", 0.111, 2)]
        >>> widget_info = counter(counters=display_counters, title="counters example")
    """
    return BaseWidgetInfo(
        title=title,
        type=WidgetType.COUNTER.value,
        size=size.value,
        params={"counters": [{"value": item.value, "label": item.label} for item in counters]},
    )


def header_text(*, label: str, title: str = "", size: WidgetSize = WidgetSize.FULL):
    """
    generate widget with some text as header

    Args:
        label: text to display
        title: widget title
        size: widget size
    """
    return BaseWidgetInfo(
        title=title,
        type=WidgetType.COUNTER.value,
        size=size.value,
        params={"counters": [{"value": "", "label": label}]},
    )


def text_widget(*, text: str, title: str = "", size: WidgetSize = WidgetSize.FULL):
    """
    generate widget with markdown text
    Args:
        text: markdown formatted text
        title: widget title
        size: widget size
    """
    return BaseWidgetInfo(title=title, type="text", size=size.value, params={"text": text})


def table_data(
    *, column_names: Iterable[str], data: Iterable[Iterable], title: str = "", size: WidgetSize = WidgetSize.FULL
) -> BaseWidgetInfo:
    """
    generate simple table with given columns and data

    Args:
        column_names: list of column names in display order
        data: list of data rows (lists of object to show in table in order of columns), object will be converted to str
        title: widget title
        size: widget size

    Example:
        >>> columns = ["Column A", "Column B"]
        >>> in_table_data = [[1, 2], [3, 4]]
        >>> widget_info = table_data(column_names=columns, data=in_table_data, title="Table")
    """
    return BaseWidgetInfo(
        title=title,
        type=WidgetType.TABLE.value,
        params={
            "header": column_names,
            "data": [[str(item) for item in row] for row in data],
        },
        size=size.value,
    )


class ColumnType(Enum):
    STRING = "string"
    LINE = "line"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"


class SortDirection(Enum):
    ASC = "asc"
    DESC = "desc"


@dataclasses.dataclass
class ColumnDefinition:
    title: str
    field_name: str
    type: ColumnType = ColumnType.STRING
    sort: Optional[SortDirection] = None
    options: Optional[dict] = None

    def as_dict(self) -> dict:
        result: dict = {"title": self.title, "field": self.field_name}
        if self.type != ColumnType.STRING:
            result["type"] = self.type.value
        if self.sort is not None:
            result["sort"] = self.sort.value
        if self.options is not None:
            result["options"] = self.options
        return result


@dataclasses.dataclass
class TabData:
    title: str
    widget: BaseWidgetInfo


def widget_tabs(*, title: str = "", size: WidgetSize = WidgetSize.FULL, tabs: List[TabData]) -> BaseWidgetInfo:
    """
    generate widget with tabs which can contain any other widget.

    Args:
        title: widget title
        size: widget size
        tabs: list of TabData with widgets to include

    Example:
        >>> columns = ["Column A", "Column B"]
        >>> in_table_data = [[1, 2], [3, 4]]
        >>> tab_data = [
        ...     TabData("Counters", counter(counters=[CounterData("counter", "value")], title="Counter")),
        ...     TabData("Table", table_data(column_names=columns, data=in_table_data, title="Table")),
        ... ]
        >>> widget_info = widget_tabs(title="Tabs", tabs=tab_data)
    """
    return BaseWidgetInfo(
        title=title,
        type=WidgetType.TABS.value,
        size=size.value,
        tabs=[TabInfo(str(uuid4()), tab.title, tab.widget) for tab in tabs],
    )


def widget_tabs_for_more_than_one(
    *, title: str = "", size: WidgetSize = WidgetSize.FULL, tabs: List[TabData]
) -> Optional[BaseWidgetInfo]:
    """Draw tabs widget only if there is more than one tab, otherwise just draw one widget"""
    if len(tabs) > 1:
        return widget_tabs(title=title, size=size, tabs=tabs)

    elif len(tabs) < 1:
        return None

    else:
        return tabs[0].widget


class DetailsPartInfo:
    title: str
    info: Union[BaseWidgetInfo, PlotlyGraphInfo]

    def __init__(self, title: str, info: Union[BaseWidgetInfo, PlotlyGraphInfo]):
        self.title = title
        self.info = info


class RowDetails:
    parts: List[DetailsPartInfo]

    def __init__(self, parts: Optional[List[DetailsPartInfo]] = None):
        if parts is None:
            parts = []
        self.parts = parts

    def with_part(self, title: str, info: Union[BaseWidgetInfo, PlotlyGraphInfo]):
        self.parts.append(DetailsPartInfo(title, info))
        return self


class RichTableDataRow:
    details: Optional[RowDetails]
    fields: dict

    def __init__(self, fields: dict, details: Optional[RowDetails] = None):
        self.fields = fields
        self.details = details


def rich_table_data(
    *,
    title: str = "",
    size: WidgetSize = WidgetSize.FULL,
    rows_per_page: int = 10,
    columns: List[ColumnDefinition],
    data: List[RichTableDataRow],
) -> BaseWidgetInfo:
    """
    generate widget with rich table: with additional column types and details for rows

    Args:
         title: widget title
         size: widget size
         rows_per_page: maximum number per page to show
         columns: list of columns in table
         data: list of dicts with data (key-value pairs, keys is according to ColumnDefinition.field_name)

    Example:
        >>> columns_def = [
        ...     ColumnDefinition("Column A", "field_1"),
        ...     ColumnDefinition("Column B", "field_2", ColumnType.HISTOGRAM,
        ...                      options={"xField": "x", "yField": "y", "color": "#ed0400"}),
        ...     ColumnDefinition("Column C", "field_3", sort=SortDirection.ASC),
        ... ]
        >>> in_table_data = [
        ...     RichTableDataRow(fields=dict(field_1="a", field_2=dict(x=[1, 2, 3], y=[10, 11, 3]), field_3="2")),
        ...     RichTableDataRow(
        ...         fields=dict(field_1="b", field_2=dict(x=[1, 2, 3], y=[10, 11, 3]), field_3="1"),
        ...         details=RowDetails()
        ...             .with_part("Some details", counter(counters=[CounterData("counter 1", "value")])
        ...         )
        ...     )
        ... ]
        >>> widget_info = rich_table_data(title="Rich table", rows_per_page=10, columns=columns_def, data=in_table_data)
    """
    additional_graphs = []

    converted_data = []
    for row in data:
        if row.details is None or row.details.parts is None or len(row.details.parts) == 0:
            converted_data.append(dict(**row.fields))
            continue
        parts = []
        for part in row.details.parts:
            parts.append(
                dict(
                    title=part.title,
                    id=part.info.id,
                    type="widget" if isinstance(part.info, BaseWidgetInfo) else "graph",
                )
            )
            additional_graphs.append(part.info)
        converted_data.append(dict(details={"parts": parts}, **row.fields))

    return BaseWidgetInfo(
        title=title,
        type=WidgetType.BIG_TABLE.value,
        details="",
        alerts=[],
        alertsPosition="row",
        insights=[],
        size=size.value,
        params={
            "rowsPerPage": min(len(data), rows_per_page),
            "columns": [column.as_dict() for column in columns],
            "data": converted_data,
        },
        additionalGraphs=additional_graphs,
    )


def get_histogram_figure(
    *,
    primary_hist: HistogramData,
    secondary_hist: Optional[HistogramData] = None,
    color_options: ColorOptions,
    orientation: str = "v",
) -> go.Figure:
    figure = go.Figure()
    curr_bar = go.Bar(
        name=primary_hist.name,
        x=primary_hist.x,
        y=primary_hist.count,
        marker_color=color_options.get_current_data_color(),
        orientation=orientation,
    )
    figure.add_trace(curr_bar)

    if secondary_hist is not None:
        ref_bar = go.Bar(
            name=secondary_hist.name,
            x=secondary_hist.x,
            y=secondary_hist.count,
            marker_color=color_options.get_reference_data_color(),
            orientation=orientation,
        )
        figure.add_trace(ref_bar)

    return figure


def histogram(
    *,
    title: str,
    primary_hist: HistogramData,
    secondary_hist: Optional[HistogramData] = None,
    color_options: ColorOptions,
    orientation: str = "v",
    size: WidgetSize = WidgetSize.FULL,
    xaxis_title: Optional[str] = None,
    yaxis_title: Optional[str] = None,
) -> BaseWidgetInfo:
    """
    generate widget with one or two histogram

    Args:
        title: widget title
        primary_hist: first histogram to show in widget
        secondary_hist: optional second histogram to show in widget
        orientation: bars orientation in histograms
        color_options: color options to use for widgets
        size: widget size
        xaxis_title: title for x-axis
        yaxis_title: title for y-axis
    Example:
        >>> ref_hist = HistogramData(name="Histogram 1", x=pd.Series(["a", "b", "c"]), count=pd.Series([1, 2, 3]))
        >>> curr_hist = HistogramData(name="Histogram 2", x=pd.Series(["a", "b", "c"]), count=pd.Series([3, 2 ,1]))
        >>> widget_info = histogram(
        >>>     title="Histogram example",
        >>>     primary_hist=ref_hist,
        >>>     secondary_hist=curr_hist,
        >>>     color_options=color_options
        >>> )
    """
    figure = get_histogram_figure(
        primary_hist=primary_hist,
        secondary_hist=secondary_hist,
        color_options=color_options,
        orientation=orientation,
    )
    if xaxis_title is not None:
        figure.update_layout(
            xaxis_title=xaxis_title,
        )

    if yaxis_title is not None:
        figure.update_layout(
            yaxis_title=yaxis_title,
        )

    return plotly_figure(title=title, figure=figure, size=size)


def get_histogram_for_distribution(
    *,
    current_distribution: Distribution,
    reference_distribution: Optional[Distribution] = None,
    title: str = "",
    xaxis_title: Optional[str] = None,
    yaxis_title: Optional[str] = None,
    color_options: ColorOptions,
):
    current_histogram = HistogramData(
        name="current",
        x=pd.Series(current_distribution.x),
        count=pd.Series(current_distribution.y),
    )

    if reference_distribution is not None:
        reference_histogram: Optional[HistogramData] = HistogramData(
            name="reference",
            x=pd.Series(reference_distribution.x),
            count=pd.Series(reference_distribution.y),
        )

    else:
        reference_histogram = None

    return histogram(
        title=title,
        primary_hist=current_histogram,
        secondary_hist=reference_histogram,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        color_options=color_options,
    )


@dataclasses.dataclass
class HeatmapData:
    name: str
    matrix: pd.DataFrame


def get_heatmaps_widget(
    *,
    title: str = "",
    primary_data: HeatmapData,
    secondary_data: Optional[HeatmapData] = None,
    size: WidgetSize = WidgetSize.FULL,
    color_options: ColorOptions,
) -> BaseWidgetInfo:
    """
    Create a widget with heatmap(s)
    """

    if secondary_data is not None:
        subplot_titles = [primary_data.name, secondary_data.name]
        heatmaps_count = 2

    else:
        subplot_titles = [""]
        heatmaps_count = 1

    figure = make_subplots(rows=1, cols=heatmaps_count, subplot_titles=subplot_titles, shared_yaxes=True)

    for idx, heatmap_data in enumerate([primary_data, secondary_data]):
        if heatmap_data is None:
            continue
        data = heatmap_data.matrix
        columns = heatmap_data.matrix.columns

        # show values if thw heatmap is small
        if len(columns) < 15:
            heatmap_text = np.round(data, 2).astype(str)
            heatmap_text_template: Optional[str] = "%{text}"

        else:
            heatmap_text = None
            heatmap_text_template = None

        figure.add_trace(
            go.Heatmap(
                z=data,
                x=columns,
                y=columns,
                text=heatmap_text,
                texttemplate=heatmap_text_template,
                coloraxis="coloraxis",
            ),
            1,
            idx + 1,
        )

    figure.update_layout(coloraxis={"colorscale": color_options.heatmap})
    figure.update_yaxes(type="category")
    figure.update_xaxes(tickangle=-45)
    return plotly_figure(title=title, figure=figure, size=size)


def get_roc_auc_tab_data(
    curr_roc_curve: ROCCurve, ref_roc_curve: Optional[ROCCurve], color_options: ColorOptions
) -> List[Tuple[str, BaseWidgetInfo]]:
    additional_plots = []
    cols = 1
    subplot_titles = [""]
    if ref_roc_curve is not None:
        cols = 2
        subplot_titles = ["current", "reference"]
    for label in curr_roc_curve.keys():
        fig = make_subplots(rows=1, cols=cols, subplot_titles=subplot_titles, shared_yaxes=True)
        trace = go.Scatter(
            x=curr_roc_curve[label].fpr,
            y=curr_roc_curve[label].tpr,
            mode="lines",
            name="ROC",
            legendgroup="ROC",
            marker=dict(
                size=6,
                color=color_options.get_current_data_color(),
            ),
        )
        fig.add_trace(trace, 1, 1)
        fig.update_xaxes(title_text="False Positive Rate", row=1, col=1)
        if ref_roc_curve is not None:
            trace = go.Scatter(
                x=ref_roc_curve[label].fpr,
                y=ref_roc_curve[label].tpr,
                mode="lines",
                name="ROC",
                legendgroup="ROC",
                showlegend=False,
                marker=dict(
                    size=6,
                    color=color_options.get_current_data_color(),
                ),
            )
            fig.add_trace(trace, 1, 2)
            fig.update_xaxes(title_text="False Positive Rate", row=1, col=2)
        fig.update_layout(yaxis_title="True Positive Rate", showlegend=True)

        additional_plots.append((str(label), plotly_figure(title="", figure=fig)))
    return additional_plots


def get_pr_rec_plot_data(
    current_pr_curve: PRCurve, reference_pr_curve: Optional[PRCurve], color_options: ColorOptions
) -> List[Tuple[str, BaseWidgetInfo]]:
    additional_plots = []
    cols = 1
    subplot_titles = [""]
    if reference_pr_curve is not None:
        cols = 2
        subplot_titles = ["current", "reference"]
    for label in current_pr_curve.keys():
        fig = make_subplots(rows=1, cols=cols, subplot_titles=subplot_titles, shared_yaxes=True)
        trace = go.Scatter(
            x=current_pr_curve[label].rcl,
            y=current_pr_curve[label].pr,
            mode="lines",
            name="PR",
            legendgroup="PR",
            marker=dict(
                size=6,
                color=color_options.get_current_data_color(),
            ),
        )
        fig.add_trace(trace, 1, 1)
        fig.update_xaxes(title_text="Recall", row=1, col=1)
        if reference_pr_curve is not None:
            trace = go.Scatter(
                x=reference_pr_curve[label].rcl,
                y=reference_pr_curve[label].pr,
                mode="lines",
                name="PR",
                legendgroup="PR",
                showlegend=False,
                marker=dict(
                    size=6,
                    color=color_options.get_current_data_color(),
                ),
            )
            fig.add_trace(trace, 1, 2)
            fig.update_xaxes(title_text="Recall", row=1, col=2)
        fig.update_layout(yaxis_title="Precision", showlegend=True)

        additional_plots.append((str(label), plotly_figure(title="", figure=fig)))
    return additional_plots


def get_lift_plot_data(
    current_lift_curve: LiftCurve,
    reference_lift_curve: Optional[PRCurve],
    color_options: ColorOptions,
) -> List[Tuple[str, BaseWidgetInfo]]:
    """
    Forms plot data for lift metric visualization

    Parameters
    ----------
    current_lift_curve: dict
        Calculated lift table data for current sample
    reference_lift_curve: Optional[dict]
        Calculated lift table data for reference sample
    color_options: ColorOptions
        Standard Evidently class-collection of colors for data visualization

    Return values
    -------------
    additional_plots: List[Tuple[str, BaseWidgetInfo]]
        Plot objects within List
    """
    additional_plots = []
    cols = 1
    subplot_titles = [""]
    if reference_lift_curve is not None:
        cols = 2
        subplot_titles = ["current", "reference"]
    for label in current_lift_curve.keys():
        fig = make_subplots(rows=1, cols=cols, subplot_titles=subplot_titles, shared_yaxes=True)
        trace = go.Scatter(
            x=current_lift_curve[label].top,
            y=current_lift_curve[label].lift,
            mode="lines+markers",
            name="Lift",
            hoverinfo="text",
            text=[
                f"top: {str(int(current_lift_curve[label].top[i]))}, " f"lift={str(current_lift_curve[label].lift[i])}"
                for i in range(100)
            ],
            legendgroup="Lift",
            marker=dict(
                size=6,
                color=color_options.get_current_data_color(),
            ),
        )
        fig.add_trace(trace, 1, 1)
        fig.update_xaxes(title_text="Top", row=1, col=1)
        if reference_lift_curve is not None:
            trace = go.Scatter(
                x=reference_lift_curve[label].top,
                y=reference_lift_curve[label].lift,
                mode="lines+markers",
                name="Lift",
                hoverinfo="text",
                text=[
                    f"top: {str(int(reference_lift_curve[label].top[i]))}, "
                    f"lift={str(reference_lift_curve[label].lift[i])}"
                    for i in range(100)
                ],
                legendgroup="Lift",
                showlegend=False,
                marker=dict(
                    size=6,
                    color=color_options.get_current_data_color(),
                ),
            )
            fig.add_trace(trace, 1, 2)
            fig.update_xaxes(title_text="Top", row=1, col=2)
        fig.update_layout(yaxis_title="Lift", showlegend=True)

        additional_plots.append((str(label), plotly_figure(title="", figure=fig)))
    return additional_plots


def class_separation_traces_raw(df, label, target_name, color_options):
    traces = []
    traces.append(
        go.Scatter(
            x=np.random.random(df[df[target_name] == label].shape[0]),
            y=df[df[target_name] == label][label],
            mode="markers",
            name=str(label),
            legendgroup=str(label),
            marker=dict(size=6, color=color_options.primary_color),
        )
    )
    traces.append(
        go.Scatter(
            x=np.random.random(df[df[target_name] != label].shape[0]),
            y=df[df[target_name] != label][label],
            mode="markers",
            name="other",
            legendgroup="other",
            marker=dict(size=6, color=color_options.secondary_color),
        )
    )
    return traces


def class_separation_traces_agg(df, label, color_options):
    traces = []
    df_name = df[df["values"] == label]
    traces.append(
        go.Box(
            lowerfence=df_name["mins"],
            q1=df_name["lowers"],
            q3=df_name["uppers"],
            median=df_name["means"],
            upperfence=df_name["maxs"],
            x=df_name["values"].astype(str),
            marker_color=color_options.get_current_data_color(),
        )
    )
    df_name = df[df["values"] == "others"]
    traces.append(
        go.Box(
            lowerfence=df_name["mins"],
            q1=df_name["lowers"],
            q3=df_name["uppers"],
            median=df_name["means"],
            upperfence=df_name["maxs"],
            x=df_name["values"],
            marker_color=color_options.get_reference_data_color(),
        )
    )
    return traces


def get_class_separation_plot_data(
    current_plot: pd.DataFrame, reference_plot: Optional[pd.DataFrame], target_name: str, color_options: ColorOptions
) -> List[Tuple[str, BaseWidgetInfo]]:
    additional_plots = []
    cols = 1
    subplot_titles = [""]
    if reference_plot is not None:
        cols = 2
        subplot_titles = ["current", "reference"]
    for label in current_plot.columns.drop(target_name):
        fig = make_subplots(rows=1, cols=cols, subplot_titles=subplot_titles, shared_yaxes=True)
        traces = class_separation_traces_raw(current_plot, label, target_name, color_options)
        for trace in traces:
            fig.add_trace(trace, 1, 1)
        fig.update_xaxes(dict(range=(-2, 3), showticklabels=False), row=1, col=1)

        if reference_plot is not None:
            traces = class_separation_traces_raw(reference_plot, label, target_name, color_options)
            for trace in traces:
                fig.add_trace(trace, 1, 2)
            fig.update_xaxes(dict(range=(-2, 3), showticklabels=False), row=1, col=2)

        fig.update_layout(yaxis_title="Probability", showlegend=True)

        additional_plots.append((str(label), plotly_figure(title="", figure=fig)))
    return additional_plots


def get_class_separation_plot_data_agg(
    current_plot: Dict[Union[int, str], pd.DataFrame],
    reference_plot: Optional[Dict[Union[int, str], pd.DataFrame]],
    target_name: str,
    color_options: ColorOptions,
) -> List[Tuple[str, BaseWidgetInfo]]:
    additional_plots = []
    cols = 1
    subplot_titles = [""]
    if reference_plot is not None:
        cols = 2
        subplot_titles = ["current", "reference"]
    for label in current_plot.keys():
        fig = make_subplots(rows=1, cols=cols, subplot_titles=subplot_titles, shared_yaxes=True)
        traces = class_separation_traces_agg(current_plot[label], label, color_options)
        for trace in traces:
            fig.add_trace(trace, 1, 1)

        if reference_plot is not None:
            traces = class_separation_traces_agg(reference_plot[label], label, color_options)
            for trace in traces:
                fig.add_trace(trace, 1, 2)

        fig.update_layout(yaxis_title="Probability", showlegend=False)

        additional_plots.append((str(label), plotly_figure(title="", figure=fig)))
    return additional_plots
