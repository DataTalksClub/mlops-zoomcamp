from typing import List
from typing import Optional

from evidently.base_metric import InputData
from evidently.base_metric import MetricResult
from evidently.calculations.classification_performance import calculate_metrics
from evidently.core import IncludeTags
from evidently.metric_results import DatasetClassificationQuality
from evidently.metrics.classification_performance.base_classification_metric import ThresholdClassificationMetric
from evidently.metrics.classification_performance.confusion_matrix_metric import ClassificationConfusionMatrix
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import CounterData
from evidently.renderers.html_widgets import counter
from evidently.renderers.html_widgets import header_text
from evidently.utils.data_operations import process_columns


class ClassificationQualityMetricResult(MetricResult):
    class Config:
        field_tags = {
            "current": {IncludeTags.Current},
            "reference": {IncludeTags.Reference},
            "target_name": {IncludeTags.Parameter},
        }

    current: DatasetClassificationQuality
    reference: Optional[DatasetClassificationQuality]
    target_name: str


class ClassificationQualityMetric(ThresholdClassificationMetric[ClassificationQualityMetricResult]):
    _confusion_matrix_metric: ClassificationConfusionMatrix

    def __init__(
        self,
        probas_threshold: Optional[float] = None,
        k: Optional[int] = None,
        options: AnyOptions = None,
    ):
        self._confusion_matrix_metric = ClassificationConfusionMatrix(probas_threshold=probas_threshold, k=k)
        super().__init__(probas_threshold=probas_threshold, k=k, options=options)

    def calculate(self, data: InputData) -> ClassificationQualityMetricResult:
        dataset_columns = process_columns(data.current_data, data.column_mapping)
        target_name = dataset_columns.utility_columns.target
        prediction_name = dataset_columns.utility_columns.prediction
        if target_name is None or prediction_name is None:
            raise ValueError("The columns 'target' and 'prediction' columns should be present")
        target, prediction = self.get_target_prediction_data(data.current_data, data.column_mapping)
        current = calculate_metrics(
            data.column_mapping,
            self._confusion_matrix_metric.get_result().current_matrix,
            target,
            prediction,
        )

        reference = None
        if data.reference_data is not None:
            ref_matrix = self._confusion_matrix_metric.get_result().reference_matrix
            if ref_matrix is None:
                raise ValueError(f"Dependency {self._confusion_matrix_metric.__class__} should have reference data")
            target, prediction = self.get_target_prediction_data(data.reference_data, data.column_mapping)
            reference = calculate_metrics(
                data.column_mapping,
                ref_matrix,
                target,
                prediction,
            )

        result = ClassificationQualityMetricResult(current=current, reference=reference, target_name=target_name)

        return result


@default_renderer(wrap_type=ClassificationQualityMetric)
class ClassificationQualityMetricRenderer(MetricRenderer):
    def render_html(self, obj: ClassificationQualityMetric) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        target_name = metric_result.target_name
        result = []
        counters = [
            CounterData("Accuracy", f"{round(metric_result.current.accuracy, 3)}"),
            CounterData("Precision", f"{round(metric_result.current.precision, 3)}"),
            CounterData("Recall", f"{round(metric_result.current.recall, 3)}"),
            CounterData("F1", f"{round(metric_result.current.f1, 3)}"),
        ]
        if metric_result.current.roc_auc is not None and metric_result.current.log_loss is not None:
            counters.extend(
                [
                    CounterData("ROC AUC", f"{round(metric_result.current.roc_auc, 3)}"),
                    CounterData("LogLoss", f"{round(metric_result.current.log_loss, 3)}"),
                ]
            )
        result.append(header_text(label=f"Classification Model Performance. Target: '{target_name}’"))
        result.append(counter(title="Current: Model Quality Metrics", counters=counters))

        if metric_result.reference is not None:
            counters = [
                CounterData("Accuracy", f"{round(metric_result.reference.accuracy, 3)}"),
                CounterData("Precision", f"{round(metric_result.reference.precision, 3)}"),
                CounterData("Recall", f"{round(metric_result.reference.recall, 3)}"),
                CounterData("F1", f"{round(metric_result.reference.f1, 3)}"),
            ]
            if metric_result.reference.roc_auc is not None and metric_result.reference.log_loss is not None:
                counters.extend(
                    [
                        CounterData("ROC AUC", f"{round(metric_result.reference.roc_auc, 3)}"),
                        CounterData("LogLoss", f"{round(metric_result.reference.log_loss, 3)}"),
                    ]
                )
            result.append(counter(title="Reference: Model Quality Metrics", counters=counters))
        return result
