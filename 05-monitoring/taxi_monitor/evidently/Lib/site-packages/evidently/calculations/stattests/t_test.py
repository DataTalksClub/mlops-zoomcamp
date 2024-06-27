"""T test of two samples.

Name: "t_test"

Import:

    >>> from evidently.calculations.stattests import t_test

Properties:
- only for numerical features
- returns p-value

Example:
    Using by object:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> from evidently.calculations.stattests import t_test
    >>> options = DataDriftOptions(all_features_stattest=t_test)

    Using by name:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> options = DataDriftOptions(all_features_stattest="t_test")
"""

from typing import Tuple

import pandas as pd
from scipy.stats import ttest_ind

from evidently.calculations.stattests.registry import StatTest
from evidently.calculations.stattests.registry import register_stattest
from evidently.core import ColumnType


def _t_test2samp(
    reference_data: pd.Series, current_data: pd.Series, feature_type: ColumnType, threshold: float
) -> Tuple[float, bool]:
    """Compute the two-sample t test between reference and current
    Args:
        reference_data: reference data
        current_data: current data
        feature_type: feature type
        threshold: level of significance (default will be 0.05)
    Returns:
        p_value: two-tailed p-value
        test_result: whether drift is detected
    """
    p_value = ttest_ind(reference_data, current_data)[1]
    return p_value, p_value < threshold


t_test = StatTest(
    name="t_test",
    display_name="t_test",
    allowed_feature_types=[ColumnType.Numerical],
)

register_stattest(t_test, _t_test2samp)
