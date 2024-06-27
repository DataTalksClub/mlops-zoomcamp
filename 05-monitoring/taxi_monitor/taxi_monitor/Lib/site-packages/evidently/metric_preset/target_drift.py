from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence

from evidently.base_metric import Metric
from evidently.calculations.stattests import PossibleStatTestType
from evidently.metric_preset.metric_preset import MetricPreset
from evidently.metrics import ColumnCorrelationsMetric
from evidently.metrics import ColumnDriftMetric
from evidently.metrics import ColumnValuePlot
from evidently.metrics import TargetByFeaturesTable
from evidently.pipeline.column_mapping import TaskType
from evidently.utils.data_drift_utils import resolve_stattest_threshold
from evidently.utils.data_preprocessing import DataDefinition


class TargetDriftPreset(MetricPreset):
    """Metric preset for Target Drift analysis.

    Contains metrics:
    - ColumnDriftMetric - for target and prediction if present in datasets.
    - ColumnValuePlot - if task is regression.
    - ColumnCorrelationsMetric - for target and prediction if present in datasets.
    - TargetByFeaturesTable
    """

    columns: Optional[List[str]]
    stattest: Optional[PossibleStatTestType]
    cat_stattest: Optional[PossibleStatTestType]
    num_stattest: Optional[PossibleStatTestType]
    text_stattest: Optional[PossibleStatTestType]
    per_column_stattest: Optional[Dict[str, PossibleStatTestType]]
    stattest_threshold: Optional[float]
    cat_stattest_threshold: Optional[float]
    num_stattest_threshold: Optional[float]
    text_stattest_threshold: Optional[float]
    per_column_stattest_threshold: Optional[Dict[str, float]]

    def __init__(
        self,
        columns: Optional[List[str]] = None,
        stattest: Optional[PossibleStatTestType] = None,
        cat_stattest: Optional[PossibleStatTestType] = None,
        num_stattest: Optional[PossibleStatTestType] = None,
        text_stattest: Optional[PossibleStatTestType] = None,
        per_column_stattest: Optional[Dict[str, PossibleStatTestType]] = None,
        stattest_threshold: Optional[float] = None,
        cat_stattest_threshold: Optional[float] = None,
        num_stattest_threshold: Optional[float] = None,
        text_stattest_threshold: Optional[float] = None,
        per_column_stattest_threshold: Optional[Dict[str, float]] = None,
    ):
        super().__init__()
        self.columns = columns
        self.stattest = stattest
        self.cat_stattest = cat_stattest
        self.num_stattest = num_stattest
        self.text_stattest = text_stattest
        self.per_column_stattest = per_column_stattest
        self.stattest_threshold = stattest_threshold
        self.cat_stattest_threshold = cat_stattest_threshold
        self.num_stattest_threshold = num_stattest_threshold
        self.text_stattest_threshold = text_stattest_threshold
        self.per_column_stattest_threshold = per_column_stattest_threshold

    def generate_metrics(
        self, data_definition: DataDefinition, additional_data: Optional[Dict[str, Any]]
    ) -> Sequence[Metric]:
        target = data_definition.get_target_column()
        prediction = data_definition.get_prediction_columns()
        result: List[Metric] = []
        columns_by_target = []

        if target is not None:
            columns_by_target.append(target.column_name)

            stattest, threshold = resolve_stattest_threshold(
                target.column_name,
                "cat" if data_definition.task == TaskType.CLASSIFICATION_TASK else "num",
                self.stattest,
                self.cat_stattest,
                self.num_stattest,
                self.text_stattest,
                self.per_column_stattest,
                self.stattest_threshold,
                self.cat_stattest_threshold,
                self.num_stattest_threshold,
                self.text_stattest_threshold,
                self.per_column_stattest_threshold,
            )
            result.append(
                ColumnDriftMetric(
                    column_name=target.column_name,
                    stattest=stattest,
                    stattest_threshold=threshold,
                )
            )

            if data_definition.task == TaskType.REGRESSION_TASK:
                result.append(ColumnValuePlot(column_name=target.column_name))

            result.append(ColumnCorrelationsMetric(column_name=target.column_name))

        if prediction is not None and prediction.predicted_values is not None:
            columns_by_target.append(prediction.predicted_values.column_name)
            stattest, threshold = resolve_stattest_threshold(
                prediction.predicted_values.column_name,
                "cat" if data_definition.task == TaskType.CLASSIFICATION_TASK else "num",
                self.stattest,
                self.cat_stattest,
                self.num_stattest,
                self.text_stattest,
                self.per_column_stattest,
                self.stattest_threshold,
                self.cat_stattest_threshold,
                self.num_stattest_threshold,
                self.text_stattest_threshold,
                self.per_column_stattest_threshold,
            )
            result.append(
                ColumnDriftMetric(
                    column_name=prediction.predicted_values.column_name,
                    stattest=stattest,
                    stattest_threshold=threshold,
                )
            )

            if prediction.prediction_probas is not None:
                for prob_column in prediction.prediction_probas:
                    stattest, threshold = resolve_stattest_threshold(
                        prob_column.column_name,
                        "num",
                        self.stattest,
                        self.cat_stattest,
                        self.num_stattest,
                        self.text_stattest,
                        self.per_column_stattest,
                        self.stattest_threshold,
                        self.cat_stattest_threshold,
                        self.num_stattest_threshold,
                        self.text_stattest_threshold,
                        self.per_column_stattest_threshold,
                    )
                    result.append(
                        ColumnDriftMetric(
                            column_name=prob_column.column_name,
                            stattest=stattest,
                            stattest_threshold=threshold,
                        )
                    )

            result.append(ColumnCorrelationsMetric(column_name=prediction.predicted_values.column_name))

        if columns_by_target:
            result.append(TargetByFeaturesTable())

        return result
