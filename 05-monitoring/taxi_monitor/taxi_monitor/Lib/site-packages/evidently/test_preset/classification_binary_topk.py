from typing import Any
from typing import Dict
from typing import Optional

from evidently.calculations.stattests import PossibleStatTestType
from evidently.test_preset.test_preset import TestPreset
from evidently.tests import TestAccuracyScore
from evidently.tests import TestColumnDrift
from evidently.tests import TestF1Score
from evidently.tests import TestLogLoss
from evidently.tests import TestPrecisionScore
from evidently.tests import TestRecallScore
from evidently.tests import TestRocAuc
from evidently.utils.data_preprocessing import DataDefinition


class BinaryClassificationTopKTestPreset(TestPreset):
    """
    Binary Classification Tests for Top K threshold.
    Args:
        stattest: stattest for `TestColumnDrift`
        stattest_threshold: threshold for stattest

    Contains:
    - `TestColumnDrift` for target
    - `TestPrecisionScore`
    - `TestRecallScore`
    - `TestF1Score`
    - `TestAccuracyScore`
    """

    stattest: Optional[PossibleStatTestType]
    stattest_threshold: Optional[float]

    def __init__(
        self,
        k: int,
        stattest: Optional[PossibleStatTestType] = None,
        stattest_threshold: Optional[float] = None,
    ):
        super().__init__()
        self.k = k
        self.stattest = stattest
        self.stattest_threshold = stattest_threshold

    def generate_tests(self, data_definition: DataDefinition, additional_data: Optional[Dict[str, Any]]):
        target = data_definition.get_target_column()
        if target is None:
            raise ValueError("Target column should be set in mapping and be present in data")
        return [
            TestAccuracyScore(k=self.k),
            TestPrecisionScore(k=self.k),
            TestRecallScore(k=self.k),
            TestF1Score(k=self.k),
            TestColumnDrift(
                column_name=target.column_name,
                stattest=self.stattest,
                stattest_threshold=self.stattest_threshold,
            ),
            TestRocAuc(),
            TestLogLoss(),
        ]
