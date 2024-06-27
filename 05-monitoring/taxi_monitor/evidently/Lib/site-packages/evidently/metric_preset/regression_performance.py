from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from evidently.metric_preset.metric_preset import MetricPreset
from evidently.metrics import RegressionAbsPercentageErrorPlot
from evidently.metrics import RegressionErrorBiasTable
from evidently.metrics import RegressionErrorDistribution
from evidently.metrics import RegressionErrorNormality
from evidently.metrics import RegressionErrorPlot
from evidently.metrics import RegressionPredictedVsActualPlot
from evidently.metrics import RegressionPredictedVsActualScatter
from evidently.metrics import RegressionQualityMetric
from evidently.metrics import RegressionTopErrorMetric
from evidently.utils.data_preprocessing import DataDefinition


class RegressionPreset(MetricPreset):
    """Metric preset for Regression performance analysis.

    Contains metrics:
    - RegressionQualityMetric
    - RegressionPredictedVsActualScatter
    - RegressionPredictedVsActualPlot
    - RegressionErrorPlot
    - RegressionAbsPercentageErrorPlot
    - RegressionErrorDistribution
    - RegressionErrorNormality
    - RegressionTopErrorMetric
    - RegressionErrorBiasTable
    """

    columns: Optional[List[str]]

    def __init__(self, columns: Optional[List[str]] = None):
        super().__init__()
        self.columns = columns

    def generate_metrics(self, data_definition: DataDefinition, additional_data: Optional[Dict[str, Any]]):
        return [
            RegressionQualityMetric(),
            RegressionPredictedVsActualScatter(),
            RegressionPredictedVsActualPlot(),
            RegressionErrorPlot(),
            RegressionAbsPercentageErrorPlot(),
            RegressionErrorDistribution(),
            RegressionErrorNormality(),
            RegressionTopErrorMetric(),
            RegressionErrorBiasTable(columns=self.columns),
        ]
