"""Jensen-Shannon distance of two samples.

Name: "jensenshannon"

Import:

    >>> from evidently.calculations.stattests import jensenshannon_stat_test

Properties:
- only for categorical and numerical features
- returns distance

Example:
    Using by object:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> from evidently.calculations.stattests import jensenshannon_stat_test
    >>> options = DataDriftOptions(all_features_stattest=jensenshannon_stat_test)

    Using by name:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> options = DataDriftOptions(all_features_stattest="jensenshannon")
"""

from typing import Optional
from typing import Tuple

import pandas as pd
from scipy.spatial import distance

from evidently.calculations.stattests.registry import StatTest
from evidently.calculations.stattests.registry import register_stattest
from evidently.calculations.stattests.utils import get_binned_data
from evidently.core import ColumnType


def _jensenshannon(
    reference_data: pd.Series,
    current_data: pd.Series,
    feature_type: ColumnType,
    threshold: float,
    n_bins: int = 30,
    base: Optional[float] = None,
) -> Tuple[float, bool]:
    """Compute the Jensen-Shannon distance between two arrays
    Args:
        reference_data: reference data
        current_data: current data
        feature_type: feature type
        threshold: all values above this threshold means data drift
        n_bins: number of bins
        base: the base of the logarithm used to compute the output
    Returns:
        jensenshannon: calculated Jensen-Shannon distance
        test_result: whether the drift is detected
    """
    reference_percents, current_percents = get_binned_data(reference_data, current_data, feature_type, n_bins, False)
    jensenshannon_value = distance.jensenshannon(reference_percents, current_percents, base)
    return jensenshannon_value, jensenshannon_value >= threshold


jensenshannon_stat_test = StatTest(
    name="jensenshannon",
    display_name="Jensen-Shannon distance",
    allowed_feature_types=[ColumnType.Categorical, ColumnType.Numerical],
    default_threshold=0.1,
)

register_stattest(jensenshannon_stat_test, _jensenshannon)
