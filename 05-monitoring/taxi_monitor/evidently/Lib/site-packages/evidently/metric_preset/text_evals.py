from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from evidently.descriptors import OOV
from evidently.descriptors import NonLetterCharacterPercentage
from evidently.descriptors import SentenceCount
from evidently.descriptors import Sentiment
from evidently.descriptors import TextLength
from evidently.features.generated_features import FeatureDescriptor
from evidently.metric_preset.metric_preset import MetricPreset
from evidently.metrics import ColumnSummaryMetric
from evidently.utils.data_preprocessing import DataDefinition


class TextEvals(MetricPreset):
    def __init__(self, column_name: str, descriptors: Optional[List[FeatureDescriptor]] = None):
        super().__init__()
        self.column_name: str = column_name
        self.descriptors: Optional[List[FeatureDescriptor]] = descriptors

    def generate_metrics(self, data_definition: DataDefinition, additional_data: Optional[Dict[str, Any]]):
        descriptors = self.descriptors or [
            TextLength(),
            SentenceCount(),
            Sentiment(),
            OOV(),
            NonLetterCharacterPercentage(),
        ]
        return [ColumnSummaryMetric(desc.on(self.column_name)) for desc in descriptors]
