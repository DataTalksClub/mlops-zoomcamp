from typing import List
from typing import Optional

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.calculations.recommender_systems import get_prediciton_name
from evidently.core import ColumnType
from evidently.core import IncludeTags
from evidently.metric_results import Distribution
from evidently.metric_results import HistogramData
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.pipeline.column_mapping import RecomType
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import plotly_figure
from evidently.utils.visualizations import get_distribution_for_column
from evidently.utils.visualizations import plot_bias


class ItemBiasMetricResult(MetricResult):
    class Config:
        field_tags = {
            "k": {IncludeTags.Parameter},
            "column_name": {IncludeTags.Parameter},
            "current_train_distr": {IncludeTags.Current},
            "current_distr": {IncludeTags.Current},
            "reference_train_distr": {IncludeTags.Reference},
            "reference_distr": {IncludeTags.Reference},
        }

    k: int
    column_name: str
    current_train_distr: Distribution
    current_distr: Distribution
    reference_train_distr: Optional[Distribution] = None
    reference_distr: Optional[Distribution] = None


class ItemBiasMetric(Metric[ItemBiasMetricResult]):
    k: int
    column_name: str

    def __init__(self, k: int, column_name: str, options: AnyOptions = None) -> None:
        self.k = k
        self.column_name = column_name
        super().__init__(options=options)

    def calculate(self, data: InputData) -> ItemBiasMetricResult:
        column = data.data_definition.get_column(self.column_name)
        prediction_name = get_prediciton_name(data)
        current_train_data = data.additional_data.get("current_train_data")
        reference_train_data = data.additional_data.get("reference_train_data")
        if current_train_data is None:
            raise ValueError(
                """current_train_data should be presented in additional_data with key "current_train_data":
                report.run(reference_data=reference_df, current_data=current_df, column_mapping=column_mapping,
                additional_data={"current_train_data": current_train_df})"""
            )
        col_item_id = data.data_definition.get_item_id_column()
        col_user_id = data.data_definition.get_user_id_column()
        recommendations_type = data.column_mapping.recom_type
        if col_item_id is None or recommendations_type is None or col_user_id is None:
            raise ValueError("item_id, user_id and recommendations_type should be specified")
        if column.column_type not in [ColumnType.Categorical, ColumnType.Numerical]:
            raise ValueError(f"{column.column_name} expected to be numerical or categorical")

        curr_train = current_train_data.drop_duplicates(subset=[col_item_id.column_name], keep="last")
        curr = data.current_data.copy()
        if recommendations_type == RecomType.SCORE:
            curr[prediction_name] = curr.groupby(col_user_id.column_name)[prediction_name].transform(
                "rank", ascending=False
            )
        curr = curr[curr[prediction_name] <= self.k]

        if column.column_name not in current_train_data.columns:
            raise ValueError(f"{column.column_name} expected to be in current_train_data")
        column_type = "num"
        if column.column_type == ColumnType.Categorical:
            column_type = "cat"
        current_distr, current_train_distr = get_distribution_for_column(
            column_type=column_type, current=curr[column.column_name], reference=curr_train[column.column_name]
        )
        reference_train_distr: Optional[Distribution] = None
        reference_distr: Optional[Distribution] = None
        if data.reference_data is not None:
            ref_train = curr_train
            ref = data.reference_data.copy()
            if recommendations_type == RecomType.SCORE:
                ref[prediction_name] = ref.groupby(col_user_id.column_name)[prediction_name].transform(
                    "rank", ascending=False
                )
            ref = ref[ref[prediction_name] <= self.k]
            if reference_train_data is not None:
                if column.column_name not in reference_train_data.columns:
                    raise ValueError(f"{column.column_name} expected to be in reference_train_data")
                ref_train = reference_train_data.drop_duplicates(subset=[col_user_id.column_name], keep="last")
            reference_distr, reference_train_distr = get_distribution_for_column(
                column_type=column_type, current=ref[column.column_name], reference=ref_train[column.column_name]
            )
        return ItemBiasMetricResult(
            k=self.k,
            column_name=self.column_name,
            current_train_distr=current_train_distr,
            current_distr=current_distr,
            reference_train_distr=reference_train_distr,
            reference_distr=reference_distr,
        )


@default_renderer(wrap_type=ItemBiasMetric)
class ItemBiasMetricRenderer(MetricRenderer):
    def render_html(self, obj: ItemBiasMetric) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        distr_fig = plot_bias(
            curr=HistogramData.from_distribution(metric_result.current_distr),
            curr_train=HistogramData.from_distribution(metric_result.current_train_distr),
            ref=HistogramData.from_distribution(metric_result.reference_distr),
            ref_train=HistogramData.from_distribution(metric_result.reference_train_distr),
            xaxis_name=metric_result.column_name,
        )

        return [
            header_text(label=f"Item bias by '{metric_result.column_name}'"),
            plotly_figure(title="", figure=distr_fig),
        ]
