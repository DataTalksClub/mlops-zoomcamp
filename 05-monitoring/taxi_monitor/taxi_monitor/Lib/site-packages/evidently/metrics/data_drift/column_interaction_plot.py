import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import numpy as np
import pandas as pd

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.base_metric import UsesRawDataMixin
from evidently.calculations.utils import get_data_for_cat_cat_plot
from evidently.calculations.utils import get_data_for_num_num_plot
from evidently.calculations.utils import prepare_box_data
from evidently.calculations.utils import prepare_data_for_date_cat
from evidently.calculations.utils import prepare_data_for_date_num
from evidently.calculations.utils import relabel_data
from evidently.core import ColumnType
from evidently.core import IncludeTags
from evidently.metric_results import ColumnScatter
from evidently.metric_results import ContourData
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import header_text
from evidently.utils.visualizations import plot_boxes
from evidently.utils.visualizations import plot_cat_cat_rel
from evidently.utils.visualizations import plot_cat_feature_in_time
from evidently.utils.visualizations import plot_contour
from evidently.utils.visualizations import plot_num_feature_in_time
from evidently.utils.visualizations import plot_num_num_rel


class ColumnInteractionPlotResults(MetricResult):
    class Config:
        dict_include = False
        pd_include = False
        tags = {IncludeTags.Render}
        field_tags = {
            "current": {IncludeTags.Current},
            "reference": {IncludeTags.Reference},
            "current_scatter": {IncludeTags.Current},
            "current_contour": {IncludeTags.Current},
            "current_boxes": {IncludeTags.Current},
            "reference_scatter": {IncludeTags.Reference},
            "reference_contour": {IncludeTags.Reference},
            "reference_boxes": {IncludeTags.Reference},
        }

    y_type: ColumnType
    x_type: ColumnType
    current_scatter: Optional[ColumnScatter]
    current_contour: Optional[ContourData]
    current_boxes: Optional[Dict[str, Union[list, np.ndarray]]]
    current: Optional[pd.DataFrame]
    reference_scatter: Optional[ColumnScatter]
    reference_contour: Optional[ContourData]
    reference_boxes: Optional[Dict[str, Union[list, np.ndarray]]]
    reference: Optional[pd.DataFrame]
    prefix: Optional[str] = None


class ColumnInteractionPlot(UsesRawDataMixin, Metric[ColumnInteractionPlotResults]):
    x_column: str
    y_column: str

    def __init__(self, x_column: str, y_column: str, options: AnyOptions = None):
        self.x_column = x_column
        self.y_column = y_column
        super().__init__(options=options)

    def calculate(self, data: InputData) -> ColumnInteractionPlotResults:
        for col in [self.x_column, self.y_column]:
            if not data.has_column(col):
                raise ValueError(f"Column '{col}' not found in dataset.")

        x_type, x_curr, x_ref = data.get_data(self.x_column)
        y_type, y_curr, y_ref = data.get_data(self.y_column)
        for column in [x_curr, x_ref, y_curr, y_ref]:
            if column is not None:
                column.replace(to_replace=[np.inf, -np.inf], value=np.nan, inplace=True)
        if x_type == ColumnType.Categorical:
            x_curr, x_ref = relabel_data(x_curr, x_ref)
        if y_type == ColumnType.Categorical:
            y_curr, y_ref = relabel_data(y_curr, y_ref)

        agg_data = True
        if self.get_options().render_options.raw_data:
            agg_data = False
        if x_type == ColumnType.Numerical and y_type == ColumnType.Numerical:
            raw_plot, agg_plot = get_data_for_num_num_plot(
                agg_data,
                self.x_column,
                self.y_column,
                x_curr,
                y_curr,
                x_ref if x_ref is not None else None,
                y_ref if y_ref is not None else None,
            )
            if raw_plot is not None:
                return ColumnInteractionPlotResults(
                    x_type=x_type,
                    y_type=y_type,
                    current_scatter=raw_plot["current"],
                    reference_scatter=raw_plot.get("reference"),
                )
            return ColumnInteractionPlotResults(
                x_type=x_type,
                y_type=y_type,
                current_contour=agg_plot["current"],
                reference_contour=agg_plot.get("reference"),
            )
        if x_type == ColumnType.Categorical and y_type == ColumnType.Categorical:
            result = get_data_for_cat_cat_plot(
                self.x_column,
                self.y_column,
                x_curr,
                y_curr,
                x_ref if x_ref is not None else None,
                y_ref if y_ref is not None else None,
            )
            return ColumnInteractionPlotResults(
                x_type=x_type,
                y_type=y_type,
                current=result["current"],
                reference=result.get("reference"),
            )
        if (x_type == ColumnType.Categorical and y_type == ColumnType.Numerical) or (
            x_type == ColumnType.Numerical and y_type == ColumnType.Categorical
        ):
            curr_df = pd.DataFrame({self.x_column: x_curr, self.y_column: y_curr})
            ref_df = None
            if x_ref is not None and y_ref is not None:
                ref_df = pd.DataFrame({self.x_column: x_ref, self.y_column: y_ref})
            if x_type == ColumnType.Categorical:
                cat_name, num_name = self.x_column, self.y_column
            else:
                cat_name, num_name = self.y_column, self.x_column
            result = prepare_box_data(curr_df, ref_df, cat_name, num_name)
            return ColumnInteractionPlotResults(
                x_type=x_type,
                y_type=y_type,
                current_boxes=result["current"],
                reference_boxes=result.get("reference"),
            )
        if (x_type == ColumnType.Numerical and y_type == ColumnType.Datetime) or (
            x_type == ColumnType.Datetime and y_type == ColumnType.Numerical
        ):
            if x_type == ColumnType.Numerical:
                date_name, date_curr, date_ref = self.y_column, y_curr, y_ref
                num_name, num_curr, num_ref = self.x_column, x_curr, x_ref
            else:
                date_name, date_curr, date_ref = self.x_column, x_curr, x_ref
                num_name, num_curr, num_ref = self.y_column, y_curr, y_ref
            curr_res, ref_res, prefix = prepare_data_for_date_num(
                date_curr, date_ref, date_name, num_name, num_curr, num_ref
            )
            return ColumnInteractionPlotResults(
                x_type=x_type,
                y_type=y_type,
                current=curr_res,
                reference=ref_res,
                prefix=prefix,
            )
        if (x_type == ColumnType.Categorical and y_type == ColumnType.Datetime) or (
            x_type == ColumnType.Datetime and y_type == ColumnType.Categorical
        ):
            if x_type == ColumnType.Categorical:
                date_name, date_curr, date_ref = self.y_column, y_curr, y_ref
                cat_name, cat_curr, cat_ref = self.x_column, x_curr, x_ref
            else:
                date_name, date_curr, date_ref = self.x_column, x_curr, x_ref
                cat_name, cat_curr, cat_ref = self.y_column, y_curr, y_ref
            curr_res, ref_res, prefix = prepare_data_for_date_cat(
                date_curr, date_ref, date_name, cat_name, cat_curr, cat_ref
            )
            return ColumnInteractionPlotResults(
                x_type=x_type,
                y_type=y_type,
                current=curr_res,
                reference=ref_res,
                prefix=prefix,
            )
        raise ValueError(f"Combination of types {x_type} and {y_type} is not supported.")


@default_renderer(wrap_type=ColumnInteractionPlot)
class ColumnInteractionPlotRenderer(MetricRenderer):
    def render_html(self, obj: ColumnInteractionPlot) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        agg_data = not obj.get_options().render_options.raw_data
        if (
            metric_result.x_type == ColumnType.Numerical
            and metric_result.y_type == ColumnType.Numerical
            and (metric_result.current_scatter is not None or metric_result.current_contour is not None)
        ):
            if (
                isinstance(metric_result.current_scatter, Dict[str, List[Any]])
                and isinstance(metric_result.reference_scatter, Dict[str, List[Any]])
                and (not agg_data or metric_result.current_scatter is not None)
            ):
                fig = plot_num_num_rel(
                    metric_result.current_scatter,
                    metric_result.reference_scatter,
                    obj.y_column,
                    obj.x_column,
                    self.color_options,
                )
            elif metric_result.current_contour is not None:
                fig = plot_contour(
                    metric_result.current_contour,
                    metric_result.reference_contour,
                    obj.x_column,
                    obj.y_column,
                )
                fig = json.loads(fig.to_json())
        elif (
            metric_result.x_type == ColumnType.Categorical
            and metric_result.y_type == ColumnType.Categorical
            and metric_result.current is not None
        ):
            fig = plot_cat_cat_rel(
                metric_result.current,
                metric_result.reference,
                obj.y_column,
                obj.x_column,
                self.color_options,
            )
        elif (
            metric_result.x_type == ColumnType.Categorical
            and metric_result.y_type == ColumnType.Numerical
            and metric_result.current_boxes is not None
        ):
            fig = plot_boxes(
                metric_result.current_boxes,
                metric_result.reference_boxes,
                obj.y_column,
                obj.x_column,
                self.color_options,
            )
        elif (
            metric_result.x_type == ColumnType.Numerical
            and metric_result.y_type == ColumnType.Categorical
            and metric_result.current_boxes is not None
        ):
            fig = plot_boxes(
                metric_result.current_boxes,
                metric_result.reference_boxes,
                obj.x_column,
                obj.y_column,
                self.color_options,
                True,
            )
        elif (
            metric_result.x_type == ColumnType.Datetime
            and metric_result.y_type == ColumnType.Numerical
            and metric_result.current is not None
            and metric_result.prefix is not None
        ):
            fig = plot_num_feature_in_time(
                metric_result.current,
                metric_result.reference,
                obj.y_column,
                obj.x_column,
                metric_result.prefix,
                self.color_options,
            )
        elif (
            metric_result.y_type == ColumnType.Datetime
            and metric_result.x_type == ColumnType.Numerical
            and metric_result.current is not None
            and metric_result.prefix is not None
        ):
            fig = plot_num_feature_in_time(
                metric_result.current,
                metric_result.reference,
                obj.x_column,
                obj.y_column,
                metric_result.prefix,
                self.color_options,
                True,
            )
        elif (
            metric_result.x_type == ColumnType.Datetime
            and metric_result.y_type == ColumnType.Categorical
            and metric_result.current is not None
            and metric_result.prefix is not None
        ):
            fig = plot_cat_feature_in_time(
                metric_result.current,
                metric_result.reference,
                obj.y_column,
                obj.x_column,
                metric_result.prefix,
                self.color_options,
            )
        elif (
            metric_result.y_type == ColumnType.Datetime
            and metric_result.x_type == ColumnType.Categorical
            and metric_result.current is not None
            and metric_result.prefix is not None
        ):
            fig = plot_cat_feature_in_time(
                metric_result.current,
                metric_result.reference,
                obj.x_column,
                obj.y_column,
                metric_result.prefix,
                self.color_options,
                True,
            )
        return [
            header_text(label=f"Interactions between '{obj.x_column}' and '{obj.y_column}'"),
            BaseWidgetInfo(
                title="",
                size=2,
                type="big_graph",
                params={"data": fig["data"], "layout": fig["layout"]},
            ),
        ]
