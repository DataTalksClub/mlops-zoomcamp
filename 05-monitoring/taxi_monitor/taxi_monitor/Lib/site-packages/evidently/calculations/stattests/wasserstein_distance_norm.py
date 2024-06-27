"""Wasserstein distance of two samples.

Name: "wasserstein"

Import:

    >>> from evidently.calculations.stattests import wasserstein_stat_test

Properties:
- only for numerical features
- returns p-value

Example:
    Using by object:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> from evidently.calculations.stattests import wasserstein_stat_test
    >>> options = DataDriftOptions(all_features_stattest=wasserstein_stat_test)

    Using by name:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> options = DataDriftOptions(all_features_stattest="wasserstein")
"""

from typing import Tuple

import numpy as np
import pandas as pd
from scipy import stats

from evidently.calculations.stattests.registry import StatTest
from evidently.calculations.stattests.registry import register_stattest
from evidently.core import ColumnType


def _wasserstein_distance_norm(
    reference_data: pd.Series, current_data: pd.Series, feature_type: ColumnType, threshold: float
) -> Tuple[float, bool]:
    """Compute the first Wasserstein distance between two arrays normed by std of reference data
    Args:
        reference_data: reference data
        current_data: current data
        feature_type: feature type
        threshold: all values above this threshold means data drift
    Returns:
        wasserstein_distance_norm: normed Wasserstein distance
        test_result: whether the drift is detected
    """
    norm = max(np.std(reference_data), 0.001)
    wd_norm_value = stats.wasserstein_distance(reference_data, current_data) / norm
    return wd_norm_value, wd_norm_value >= threshold


wasserstein_stat_test = StatTest(
    name="wasserstein",
    display_name="Wasserstein distance (normed)",
    allowed_feature_types=[ColumnType.Numerical],
    default_threshold=0.1,
)

register_stattest(wasserstein_stat_test, _wasserstein_distance_norm)
