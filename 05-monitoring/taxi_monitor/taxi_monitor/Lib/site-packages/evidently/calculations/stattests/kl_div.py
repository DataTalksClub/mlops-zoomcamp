"""Kullback-Leibler divergence of two samples.

Name: "kl_div"

Import:

    >>> from evidently.calculations.stattests import kl_div_stat_test

Properties:
- only for categorical and numerical features
- returns divergence

Example:
    Using by object:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> from evidently.calculations.stattests import kl_div_stat_test
    >>> options = DataDriftOptions(all_features_stattest=kl_div_stat_test)

    Using by name:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> options = DataDriftOptions(all_features_stattest="kl_div")
"""

from typing import Tuple

import pandas as pd
from scipy import stats

from evidently.calculations.stattests.registry import StatTest
from evidently.calculations.stattests.registry import register_stattest
from evidently.calculations.stattests.utils import get_binned_data
from evidently.core import ColumnType


def _kl_div(
    reference_data: pd.Series, current_data: pd.Series, feature_type: ColumnType, threshold: float, n_bins: int = 30
) -> Tuple[float, bool]:
    """Compute the Kullback-Leibler divergence between two arrays
    Args:
        reference_data: reference data
        current_data: current data
        feature_type: feature type
        threshold: all values above this threshold means data drift
        n_bins: number of bins
    Returns:
        kl_div: calculated Kullback-Leibler divergence value
        test_result: whether the drift is detected
    """
    reference_percents, current_percents = get_binned_data(reference_data, current_data, feature_type, n_bins)
    kl_div_value = stats.entropy(reference_percents, current_percents)
    return kl_div_value, kl_div_value >= threshold


kl_div_stat_test = StatTest(
    name="kl_div",
    display_name="Kullback-Leibler divergence",
    allowed_feature_types=[ColumnType.Categorical, ColumnType.Numerical],
    default_threshold=0.1,
)

register_stattest(kl_div_stat_test, _kl_div)
