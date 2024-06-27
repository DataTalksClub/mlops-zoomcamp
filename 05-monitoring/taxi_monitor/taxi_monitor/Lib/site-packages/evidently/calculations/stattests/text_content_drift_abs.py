from typing import Tuple

import pandas as pd

from evidently.calculations.stattests.registry import StatTest
from evidently.calculations.stattests.registry import register_stattest
from evidently.core import ColumnType
from evidently.utils.data_drift_utils import calculate_text_drift_score


def _abs_text_content_drift(
    reference_data: pd.Series, current_data: pd.Series, feature_type: ColumnType, threshold: float
) -> Tuple[float, bool]:
    return calculate_text_drift_score(reference_data, current_data, bootstrap=False, threshold=threshold)


abs_text_content_drift_stat_test = StatTest(
    name="abs_text_content_drift",
    display_name="Absolute text content drift",
    allowed_feature_types=[ColumnType.Text],
    default_threshold=0.55,
)

register_stattest(abs_text_content_drift_stat_test, _abs_text_content_drift)
