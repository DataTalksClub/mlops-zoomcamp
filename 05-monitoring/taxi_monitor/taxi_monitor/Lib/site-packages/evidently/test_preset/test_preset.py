import abc
from typing import Any
from typing import Dict
from typing import Optional

from evidently.utils.data_preprocessing import DataDefinition


class TestPreset:
    def __init__(self):
        pass

    @abc.abstractmethod
    def generate_tests(self, data_definition: DataDefinition, additional_data: Optional[Dict[str, Any]]):
        raise NotImplementedError()
