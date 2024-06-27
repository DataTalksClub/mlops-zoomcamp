from typing import Any
from typing import Dict
from typing import Optional

from evidently.test_preset.test_preset import TestPreset
from evidently.tests import TestHitRateK
from evidently.tests import TestMAPK
from evidently.tests import TestNDCGK
from evidently.tests import TestPrecisionTopK
from evidently.tests import TestRecallTopK
from evidently.utils.data_preprocessing import DataDefinition


class RecsysTestPreset(TestPreset):
    """
    Recsys performance tests.

    Contains tests:
    - `TestPrecisionTopK`
    - `TestRecallTopK`
    - `TestMAPK`
    - `TestNDCGK`
    - `TestHitRateK`
    """

    k: int
    min_rel_score: Optional[int]
    no_feedback_users: bool

    def __init__(self, k: int, min_rel_score: Optional[int] = None, no_feedback_users: bool = False):
        super().__init__()
        self.k = k
        self.min_rel_score = min_rel_score
        self.no_feedback_users = no_feedback_users

    def generate_tests(self, data_definition: DataDefinition, additional_data: Optional[Dict[str, Any]]):
        return [
            TestPrecisionTopK(k=self.k, min_rel_score=self.min_rel_score, no_feedback_users=self.no_feedback_users),
            TestRecallTopK(k=self.k, min_rel_score=self.min_rel_score, no_feedback_users=self.no_feedback_users),
            TestMAPK(k=self.k, min_rel_score=self.min_rel_score, no_feedback_users=self.no_feedback_users),
            TestNDCGK(k=self.k, min_rel_score=self.min_rel_score, no_feedback_users=self.no_feedback_users),
            TestHitRateK(k=self.k, min_rel_score=self.min_rel_score, no_feedback_users=self.no_feedback_users),
        ]
