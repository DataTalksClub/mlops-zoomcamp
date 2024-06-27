from typing import List
from typing import Optional

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.core import IncludeTags
from evidently.model.widget import BaseWidgetInfo
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import CounterData
from evidently.renderers.html_widgets import counter
from evidently.renderers.html_widgets import header_text
from evidently.utils.data_operations import process_columns


class ConflictPredictionData(MetricResult):
    number_not_stable_prediction: int
    share_not_stable_prediction: float


class ConflictPredictionMetricResults(MetricResult):
    class Config:
        field_tags = {"current": {IncludeTags.Current}, "reference": {IncludeTags.Reference}}

    current: ConflictPredictionData
    reference: Optional[ConflictPredictionData]


class ConflictPredictionMetric(Metric[ConflictPredictionMetricResults]):
    def calculate(self, data: InputData) -> ConflictPredictionMetricResults:
        dataset_columns = process_columns(data.current_data, data.column_mapping)
        prediction_name = dataset_columns.utility_columns.prediction
        if prediction_name is None:
            raise ValueError("The prediction column should be presented")
        columns = dataset_columns.get_all_features_list()
        if len(columns) == 0:
            raise ValueError("Prediction conflict is not defined. No features provided")
        if isinstance(prediction_name, str):
            prediction_columns = [prediction_name]
        elif isinstance(prediction_name, list):
            prediction_columns = prediction_name
        duplicates = data.current_data[data.current_data.duplicated(subset=columns, keep=False)]
        number_not_stable_prediction = duplicates.drop(
            data.current_data[data.current_data.duplicated(subset=columns + prediction_columns, keep=False)].index
        ).shape[0]
        share_not_stable_prediction = round(number_not_stable_prediction / data.current_data.shape[0], 3)
        # reference
        reference = None
        if data.reference_data is not None:
            duplicates_ref = data.reference_data[data.reference_data.duplicated(subset=columns, keep=False)]
            number_not_stable_prediction_ref = duplicates_ref.drop(
                data.reference_data[
                    data.reference_data.duplicated(subset=columns + prediction_columns, keep=False)
                ].index
            ).shape[0]
            share_not_stable_prediction_ref = round(number_not_stable_prediction_ref / data.reference_data.shape[0], 3)
            reference = ConflictPredictionData(
                number_not_stable_prediction=number_not_stable_prediction_ref,
                share_not_stable_prediction=share_not_stable_prediction_ref,
            )
        return ConflictPredictionMetricResults(
            current=ConflictPredictionData(
                number_not_stable_prediction=number_not_stable_prediction,
                share_not_stable_prediction=share_not_stable_prediction,
            ),
            reference=reference,
        )


@default_renderer(wrap_type=ConflictPredictionMetric)
class ConflictPredictionMetricRenderer(MetricRenderer):
    def render_html(self, obj: ConflictPredictionMetric) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        counters = [
            CounterData(
                "number of conflicts (current)",
                self._get_string(
                    metric_result.current.number_not_stable_prediction,
                    metric_result.current.share_not_stable_prediction,
                ),
            )
        ]
        if metric_result.reference is not None:
            counters.append(
                CounterData(
                    "number of conflicts (reference)",
                    self._get_string(
                        metric_result.reference.number_not_stable_prediction,
                        metric_result.reference.share_not_stable_prediction,
                    ),
                )
            )
        result = [
            header_text(label="Conflicts in Prediction"),
            counter(counters=counters),
        ]
        return result

    @staticmethod
    def _get_string(number: int, ratio: float) -> str:
        return f"{number} ({ratio * 100}%)"
