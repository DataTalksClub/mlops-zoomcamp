"""G-test of two samples.

Name: "g_test"

Import:

    >>> from evidently.calculations.stattests import g_test

Properties:
- only for categorical features
- returns p-value

Example:
    Using by object:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> from evidently.calculations.stattests import g_test
    >>> options = DataDriftOptions(all_features_stattest=g_test)

    Using by name:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> options = DataDriftOptions(all_features_stattest="g_test")
"""

from typing import Tuple

import pandas as pd
from scipy.stats import power_divergence

from evidently.calculations.stattests.registry import StatTest
from evidently.calculations.stattests.registry import register_stattest
from evidently.calculations.stattests.utils import get_unique_not_nan_values_list_from_series
from evidently.core import ColumnType


def _g_stat_test(
    reference_data: pd.Series, current_data: pd.Series, feature_type: ColumnType, threshold: float
) -> Tuple[float, bool]:
    """Compute the G test between two arrays
    Args:
        reference_data: reference data
        current_data: current data
        feature_type: feature type
        threshold: level of significance
    Returns:
        p_value: calculated p_value value
        test_result: whether the drift is detected
    """
    keys = get_unique_not_nan_values_list_from_series(current_data=current_data, reference_data=reference_data)
    ref_feature_dict = {**dict.fromkeys(keys, 0), **dict(reference_data.value_counts())}
    current_feature_dict = {
        **dict.fromkeys(keys, 0),
        **dict(current_data.value_counts()),
    }
    f_exp = [ref_feature_dict[key] for key in keys]
    f_obs = [current_feature_dict[key] for key in keys]
    p_value = power_divergence(f_obs, f_exp, lambda_="log-likelihood")[1]
    return p_value, p_value < threshold


g_test = StatTest(
    name="g_test",
    display_name="g_test",
    allowed_feature_types=[ColumnType.Categorical],
    default_threshold=0.1,
)

register_stattest(g_test, _g_stat_test)
