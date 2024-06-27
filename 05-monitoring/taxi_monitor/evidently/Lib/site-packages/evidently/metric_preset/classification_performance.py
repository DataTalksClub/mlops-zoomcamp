from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from evidently.metric_preset.metric_preset import MetricPreset
from evidently.metrics import ClassificationClassBalance
from evidently.metrics import ClassificationClassSeparationPlot
from evidently.metrics import ClassificationConfusionMatrix
from evidently.metrics import ClassificationPRCurve
from evidently.metrics import ClassificationProbDistribution
from evidently.metrics import ClassificationPRTable
from evidently.metrics import ClassificationQualityByClass
from evidently.metrics import ClassificationQualityByFeatureTable
from evidently.metrics import ClassificationQualityMetric
from evidently.metrics import ClassificationRocCurve
from evidently.utils.data_preprocessing import DataDefinition


class ClassificationPreset(MetricPreset):
    """
    Metrics preset for classification performance.

    Contains metrics:
    - ClassificationQualityMetric
    - ClassificationClassBalance
    - ClassificationConfusionMatrix
    - ClassificationQualityByClass
    """

    columns: Optional[List[str]]
    probas_threshold: Optional[float]
    k: Optional[int]

    def __init__(
        self, columns: Optional[List[str]] = None, probas_threshold: Optional[float] = None, k: Optional[int] = None
    ):
        super().__init__()
        self.columns = columns
        self.probas_threshold = probas_threshold
        self.k = k

    def generate_metrics(self, data_definition: DataDefinition, additional_data: Optional[Dict[str, Any]]):
        result = [
            ClassificationQualityMetric(probas_threshold=self.probas_threshold, k=self.k),
            ClassificationClassBalance(),
            ClassificationConfusionMatrix(probas_threshold=self.probas_threshold, k=self.k),
            ClassificationQualityByClass(probas_threshold=self.probas_threshold, k=self.k),
        ]

        columns = data_definition.get_prediction_columns()
        if columns is not None and columns.prediction_probas is not None:
            result.extend(
                [
                    ClassificationClassSeparationPlot(),
                    ClassificationProbDistribution(),
                    ClassificationRocCurve(),
                    ClassificationPRCurve(),
                    ClassificationPRTable(),
                ]
            )

        result.append(ClassificationQualityByFeatureTable(columns=self.columns))
        return result
