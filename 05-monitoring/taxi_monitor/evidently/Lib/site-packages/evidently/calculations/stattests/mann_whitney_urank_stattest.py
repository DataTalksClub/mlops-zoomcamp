"""Mann-Whitney U-rank test of two samples.

Name: "mannw"

Import:

    >>> from evidently.calculations.stattests import mann_whitney_u_stat_test

Properties:
- only for numerical features
- returns p-value

Example:
    Using by object:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> from evidently.calculations.stattests import mann_whitney_u_stat_test
    >>> options = DataDriftOptions(all_features_stattest=mann_whitney_u_stat_test)

    Using by name:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> options = DataDriftOptions(all_features_stattest="mannw")
"""

from typing import Tuple

import pandas as pd
from scipy.stats import mannwhitneyu

from evidently.calculations.stattests.registry import StatTest
from evidently.calculations.stattests.registry import register_stattest
from evidently.core import ColumnType


def _mannwhitneyu_rank(
    reference_data: pd.Series,
    current_data: pd.Series,
    feature_type: ColumnType,
    threshold: float,
) -> Tuple[float, bool]:
    """Perform the Mann-Whitney U-rank test between two arrays
    Args:
        reference_data: reference data
        current_data: current data
        feature_type: feature type
        threshold: all values above this threshold means data drift
    Returns:
        pvalue: the two-tailed p-value for the test depending on alternative and method
        test_result: whether the drift is detected
    """
    p_value = mannwhitneyu(x=reference_data, y=current_data, alternative="less")[1]
    return p_value, p_value < threshold


mann_whitney_u_stat_test = StatTest(
    name="mannw",
    display_name="Mann-Whitney U-rank test",
    allowed_feature_types=[ColumnType.Numerical],
    default_threshold=0.05,
)

register_stattest(mann_whitney_u_stat_test, _mannwhitneyu_rank)
