from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.metric_results import Histogram
from evidently.model.widget import BaseWidgetInfo
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import header_text
from evidently.utils.data_operations import process_columns
from evidently.utils.visualizations import make_hist_for_cat_plot
from evidently.utils.visualizations import plot_distr_with_perc_button


class ClassificationClassBalanceResult(MetricResult):
    class Config:
        dict_exclude_fields = {"plot_data"}
        pd_exclude_fields = {"plot_data"}

    plot_data: Histogram


class ClassificationClassBalance(Metric[ClassificationClassBalanceResult]):
    def calculate(self, data: InputData) -> ClassificationClassBalanceResult:
        dataset_columns = process_columns(data.current_data, data.column_mapping)
        target_name = dataset_columns.utility_columns.target
        prediction_name = dataset_columns.utility_columns.prediction
        if target_name is None or prediction_name is None:
            raise ValueError("The columns 'target' and 'prediction' columns should be present")
        curr_target = data.current_data[target_name]
        ref_target = None
        if data.reference_data is not None:
            ref_target = data.reference_data[target_name]
        target_names: Optional[Dict[Union[int, str], str]]
        if isinstance(dataset_columns.target_names, list):
            target_names = {idx: str(val) for idx, val in enumerate(dataset_columns.target_names)}
        else:
            target_names = dataset_columns.target_names
        if target_names is not None:
            curr_target = curr_target.map(target_names)
            if ref_target is not None:
                ref_target = ref_target.map(target_names)

        plot_data = make_hist_for_cat_plot(curr_target, ref_target)

        return ClassificationClassBalanceResult(plot_data=plot_data)


@default_renderer(wrap_type=ClassificationClassBalance)
class ClassificationClassBalanceRenderer(MetricRenderer):
    def render_html(self, obj: ClassificationClassBalance) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        current_plot_data = metric_result.plot_data.current
        reference_plot_data = metric_result.plot_data.reference

        fig = plot_distr_with_perc_button(
            hist_curr=current_plot_data,
            hist_ref=reference_plot_data,
            xaxis_name="Class",
            yaxis_name="Number Of Objects",
            yaxis_name_perc="Percent",
            same_color=True,
            color_options=self.color_options,
        )

        return [
            header_text(label="Class Representation"),
            BaseWidgetInfo(
                title="",
                size=2,
                type="big_graph",
                params={"data": fig["data"], "layout": fig["layout"]},
            ),
        ]
