"""Z-test test of two samples.

Name: "z"

Import:

    >>> from evidently.calculations.stattests import z_stat_test

Properties:
- only for numerical features
- returns p-value

Example:
    Using by object:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> from evidently.calculations.stattests import z_stat_test
    >>> options = DataDriftOptions(all_features_stattest=z_stat_test)

    Using by name:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> options = DataDriftOptions(all_features_stattest="z")
"""

from typing import Tuple

import numpy as np
import pandas as pd
from scipy.stats import norm

from evidently.calculations.stattests.registry import StatTest
from evidently.calculations.stattests.registry import register_stattest
from evidently.calculations.stattests.utils import get_unique_not_nan_values_list_from_series
from evidently.core import ColumnType


def proportions_diff_z_stat_ind(ref: pd.DataFrame, curr: pd.DataFrame):
    # pylint: disable=invalid-name
    n1 = len(ref)
    n2 = len(curr)

    p1 = float(sum(ref)) / n1
    p2 = float(sum(curr)) / n2
    P = float(p1 * n1 + p2 * n2) / (n1 + n2)

    return (p1 - p2) / np.sqrt(P * (1 - P) * (1.0 / n1 + 1.0 / n2))


def proportions_diff_z_test(z_stat, alternative="two-sided"):
    if alternative == "two-sided":
        return 2 * (1 - norm.cdf(np.abs(z_stat)))

    if alternative == "less":
        return norm.cdf(z_stat)

    if alternative == "greater":
        return 1 - norm.cdf(z_stat)

    raise ValueError("alternative not recognized\n" "should be 'two-sided', 'less' or 'greater'")


def _z_stat_test(
    reference_data: pd.Series, current_data: pd.Series, feature_type: ColumnType, threshold: float
) -> Tuple[float, bool]:
    """Compute the Z test between two arrays
    Args:
        reference_data: reference data
        current_data: current data
        feature_type: feature type
        threshold: all values above this threshold means data drift
    Returns:
        pvalue: the two-tailed p-value for the test
        test_result: whether the drift is detected
    """
    if (
        reference_data.nunique() == 1
        and current_data.nunique() == 1
        and reference_data.unique()[0] == current_data.unique()[0]
    ):
        p_value = 1
    else:
        keys = sorted(
            get_unique_not_nan_values_list_from_series(current_data=current_data, reference_data=reference_data)
        )
        p_value = proportions_diff_z_test(
            proportions_diff_z_stat_ind(
                reference_data.apply(lambda x, key=keys[0]: 0 if x == key else 1),
                current_data.apply(lambda x, key=keys[0]: 0 if x == key else 1),
            )
        )
    return p_value, p_value < threshold


z_stat_test = StatTest(
    name="z",
    display_name="Z-test p_value",
    allowed_feature_types=[ColumnType.Categorical],
)

register_stattest(z_stat_test, _z_stat_test)
