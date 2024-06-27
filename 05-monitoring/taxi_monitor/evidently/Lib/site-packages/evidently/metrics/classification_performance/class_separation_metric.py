from typing import List
from typing import Optional

import numpy as np
import pandas as pd

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.base_metric import UsesRawDataMixin
from evidently.calculations.classification_performance import get_prediction_data
from evidently.core import IncludeTags
from evidently.metric_results import ColumnAggScatter
from evidently.metric_results import ColumnScatter
from evidently.metric_results import ColumnScatterOrAgg
from evidently.metric_results import column_scatter_from_df
from evidently.metric_results import df_from_column_scatter
from evidently.metric_results import raw_agg_properties
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import TabData
from evidently.renderers.html_widgets import get_class_separation_plot_data
from evidently.renderers.html_widgets import get_class_separation_plot_data_agg
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import widget_tabs
from evidently.utils.data_operations import process_columns


class ClassificationClassSeparationPlotResults(MetricResult):
    class Config:
        dict_exclude_fields = {"current", "reference"}
        pd_exclude_fields = {"current", "reference"}
        field_tags = {
            "current": {IncludeTags.Current, IncludeTags.Extra},
            "reference": {IncludeTags.Reference, IncludeTags.Extra},
            "target_name": {IncludeTags.Parameter},
        }

    target_name: str

    current: Optional[ColumnScatterOrAgg] = None
    current_raw, current_agg = raw_agg_properties("current", ColumnScatter, ColumnAggScatter, True)

    reference: Optional[ColumnScatterOrAgg] = None
    reference_raw, reference_agg = raw_agg_properties("reference", ColumnScatter, ColumnAggScatter, True)


def prepare_box_data(df: pd.DataFrame, target_name: str, prediction_names: List[str]):
    res = {}
    for name in prediction_names:
        df_name = df.copy()
        df_name[target_name] = (df_name[target_name] == name).astype(int)
        df_for_plot = df_name.groupby(target_name)[name].quantile([0, 0.25, 0.5, 0.75, 1]).reset_index()
        df_for_plot.columns = [target_name, "q", name]
        res_df = pd.DataFrame()
        values = df_for_plot[target_name].unique()

        def _quantiles(qdf, value):
            return qdf[df_for_plot.q == value].set_index(target_name).loc[values, name].tolist()

        res_df["mins"] = _quantiles(df_for_plot, 0)
        res_df["lowers"] = _quantiles(df_for_plot, 0.25)
        res_df["means"] = _quantiles(df_for_plot, 0.5)
        res_df["uppers"] = _quantiles(df_for_plot, 0.75)
        res_df["maxs"] = _quantiles(df_for_plot, 1)
        res_df["values"] = values
        res_df["values"] = res_df["values"].map({1: name, 0: "others"})
        res[name] = res_df
    return res


class ClassificationClassSeparationPlot(UsesRawDataMixin, Metric[ClassificationClassSeparationPlotResults]):
    def __init__(self, options: AnyOptions = None):
        super().__init__(options=options)

    def calculate(self, data: InputData) -> ClassificationClassSeparationPlotResults:
        dataset_columns = process_columns(data.current_data, data.column_mapping)
        target_name = dataset_columns.utility_columns.target
        prediction_name = dataset_columns.utility_columns.prediction
        if target_name is None or prediction_name is None:
            raise ValueError("The columns 'target' and 'prediction' columns should be present")
        curr_predictions = get_prediction_data(data.current_data, dataset_columns, data.column_mapping.pos_label)
        if curr_predictions.prediction_probas is None:
            raise ValueError(
                "ClassificationClassSeparationPlot can be calculated only on binary probabilistic predictions"
            )
        current_plot = curr_predictions.prediction_probas.copy()
        prediction_names = current_plot.columns
        current_plot[target_name] = data.current_data[target_name]
        reference_plot = None
        if data.reference_data is not None:
            ref_predictions = get_prediction_data(data.reference_data, dataset_columns, data.column_mapping.pos_label)
            if ref_predictions.prediction_probas is None:
                raise ValueError(
                    "ClassificationClassSeparationPlot can be calculated only on binary probabilistic predictions"
                )
            reference_plot = ref_predictions.prediction_probas.copy()
            reference_plot[target_name] = data.reference_data[target_name]
        if self.get_options().render_options.raw_data:
            return ClassificationClassSeparationPlotResults(
                current=column_scatter_from_df(current_plot, True),
                reference=column_scatter_from_df(reference_plot, True),
                target_name=target_name,
            )
        current_plot = prepare_box_data(current_plot, target_name, prediction_names)
        if reference_plot is not None:
            reference_plot = prepare_box_data(reference_plot, target_name, prediction_names)
        return ClassificationClassSeparationPlotResults(
            current=current_plot,
            reference=reference_plot,
            target_name=target_name,
        )


@default_renderer(wrap_type=ClassificationClassSeparationPlot)
class ClassificationClassSeparationPlotRenderer(MetricRenderer):
    def render_html(self, obj: ClassificationClassSeparationPlot) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        target_name = metric_result.target_name
        agg_data = not obj.get_options().render_options.raw_data
        if metric_result.current is None:
            return []
        if not agg_data:
            assert metric_result.current_raw is not None  # checked before
            # todo changing data here, consider doing this in calculation
            current_df = df_from_column_scatter(metric_result.current_raw)
            current_df.replace([np.inf, -np.inf], np.nan, inplace=True)
            reference_df = None
            reference_plot = metric_result.reference_raw
            if reference_plot is not None:
                reference_df = df_from_column_scatter(reference_plot)
                reference_df.replace([np.inf, -np.inf], np.nan, inplace=True)
            tab_data = get_class_separation_plot_data(
                current_df,
                reference_df,
                target_name,
                color_options=self.color_options,
            )
        else:
            assert metric_result.current_agg is not None  # checked before
            tab_data = get_class_separation_plot_data_agg(
                metric_result.current_agg,
                metric_result.reference_agg,
                target_name,
                color_options=self.color_options,
            )
        tabs = [TabData(name, widget) for name, widget in tab_data]
        return [
            header_text(label="Class Separation Quality"),
            widget_tabs(title="", tabs=tabs),
        ]
