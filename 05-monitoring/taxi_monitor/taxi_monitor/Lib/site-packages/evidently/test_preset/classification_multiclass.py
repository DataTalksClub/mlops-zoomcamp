from typing import Any
from typing import Dict
from typing import Optional

from evidently.calculations.stattests import PossibleStatTestType
from evidently.test_preset.test_preset import TestPreset
from evidently.tests import TestAccuracyScore
from evidently.tests import TestColumnDrift
from evidently.tests import TestF1Score
from evidently.tests import TestLogLoss
from evidently.tests import TestNumberOfRows
from evidently.tests import TestPrecisionByClass
from evidently.tests import TestRecallByClass
from evidently.tests import TestRocAuc
from evidently.utils.data_preprocessing import DataDefinition


class MulticlassClassificationTestPreset(TestPreset):
    """
    Multiclass Classification tests.

    Args:
        stattest: statistical test for target drift test.
        stattest_threshold: threshold for statistical test for target drift test.

    Contains tests:
    - `TestAccuracyScore`
    - `TestF1Score`
    - `TestPrecisionByClass` for each class in data
    - `TestRecallByClass` for each class in data
    - `TestNumberOfRows`
    - `TestColumnValueDrift`
    - `TestRocAuc`
    - `TestLogLoss`
    """

    stattest: Optional[PossibleStatTestType]
    stattest_threshold: Optional[float]

    def __init__(
        self,
        stattest: Optional[PossibleStatTestType] = None,
        stattest_threshold: Optional[float] = None,
    ):
        super().__init__()

        self.stattest = stattest
        self.stattest_threshold = stattest_threshold

    def generate_tests(self, data_definition: DataDefinition, additional_data: Optional[Dict[str, Any]]):
        target = data_definition.get_target_column()

        if target is None:
            raise ValueError("Target column should be set in mapping and be present in data")

        classification_labels = data_definition.classification_labels
        if classification_labels is None:
            labels = set()
        else:
            labels = set(
                classification_labels if isinstance(classification_labels, list) else classification_labels.values()
            )

        tests = [
            TestAccuracyScore(),
            TestF1Score(),
            *[TestPrecisionByClass(label) for label in labels],
            *[TestRecallByClass(label) for label in labels],
            TestNumberOfRows(),
            TestColumnDrift(
                column_name=target.column_name,
                stattest=self.stattest,
                stattest_threshold=self.stattest_threshold,
            ),
        ]

        prediction_columns = data_definition.get_prediction_columns()
        if prediction_columns is None or prediction_columns.prediction_probas is None:
            return tests
        else:
            return tests + [TestRocAuc(), TestLogLoss()]
