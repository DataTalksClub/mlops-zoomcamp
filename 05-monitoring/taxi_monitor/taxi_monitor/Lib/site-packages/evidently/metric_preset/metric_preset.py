import abc
from typing import Any
from typing import Dict
from typing import Optional

from evidently.utils.data_preprocessing import DataDefinition


class MetricPreset:
    """Base class for metric presets"""

    def __init__(self):
        pass

    @abc.abstractmethod
    def generate_metrics(self, data_definition: DataDefinition, additional_data: Optional[Dict[str, Any]]):
        raise NotImplementedError()
