from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from evidently.metric_preset.metric_preset import MetricPreset
from evidently.metrics import ColumnSummaryMetric
from evidently.metrics import DatasetCorrelationsMetric
from evidently.metrics import DatasetSummaryMetric
from evidently.metrics.base_metric import generate_column_metrics
from evidently.metrics.data_integrity.dataset_missing_values_metric import DatasetMissingValuesMetric
from evidently.utils.data_preprocessing import DataDefinition


class DataQualityPreset(MetricPreset):
    """Metric preset for Data Quality analysis.

    Contains metrics:
    - DatasetSummaryMetric
    - ColumnSummaryMetric for each column
    - DatasetMissingValuesMetric
    - DatasetCorrelationsMetric

    Args:
        columns: list of columns for analysis.
    """

    columns: Optional[List[str]]

    def __init__(self, columns: Optional[List[str]] = None):
        super().__init__()
        self.columns = columns

    def generate_metrics(self, data_definition: DataDefinition, additional_data: Optional[Dict[str, Any]]):
        return [
            DatasetSummaryMetric(),
            generate_column_metrics(ColumnSummaryMetric, columns=self.columns, skip_id_column=True),
            DatasetMissingValuesMetric(),
            DatasetCorrelationsMetric(),
        ]
