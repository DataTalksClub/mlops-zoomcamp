from typing import Any
from typing import Dict
from typing import Optional

from evidently.test_preset.test_preset import TestPreset
from evidently.tests import TestValueMAE
from evidently.tests import TestValueMAPE
from evidently.tests import TestValueMeanError
from evidently.tests import TestValueRMSE
from evidently.utils.data_preprocessing import DataDefinition


class RegressionTestPreset(TestPreset):
    """
    Regression performance tests.

    Contains tests:
    - `TestValueMeanError`
    - `TestValueMAE`
    - `TestValueRMSE`
    - `TestValueMAPE`
    """

    def generate_tests(self, data_definition: DataDefinition, additional_data: Optional[Dict[str, Any]]):
        return [
            TestValueMeanError(),
            TestValueMAE(),
            TestValueRMSE(),
            TestValueMAPE(),
        ]
