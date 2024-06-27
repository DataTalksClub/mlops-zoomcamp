"""Hellinger distance of two samples.

Name: "hellinger"

Import:

    >>> from evidently.calculations.stattests import hellinger_stat_test

Properties:
- only for categorical and numerical features
- returns distance

Example:
    Using by object:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> from evidently.calculations.stattests import hellinger_stat_test
    >>> options = DataDriftOptions(all_features_stattest=hellinger_stat_test)

    Using by name:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> options = DataDriftOptions(all_features_stattest="hellinger")
"""

from collections import defaultdict
from math import sqrt
from typing import DefaultDict
from typing import Tuple

import numpy as np
import pandas as pd

from evidently.calculations.stattests.registry import StatTest
from evidently.calculations.stattests.registry import register_stattest
from evidently.core import ColumnType


def _hellinger_distance(
    reference_data: pd.Series,
    current_data: pd.Series,
    feature_type: ColumnType,
    threshold: float,
) -> Tuple[float, bool]:
    """Compute the Hellinger distance between two arrays
    Args:
        reference_data: reference data
        current_data: current data
        feature_type: feature type
        threshold: all values above this threshold means data drift
    Returns:
        hellinger_distance: normed Hellinger distance
        test_result: whether the drift is detected
    """
    reference_data.dropna(inplace=True)
    current_data.dropna(inplace=True)

    keys = list((set(reference_data.unique()) | set(current_data.unique())))

    if feature_type == ColumnType.Categorical:
        dd: DefaultDict[int, int] = defaultdict(int)
        ref = (reference_data.value_counts() / len(reference_data)).to_dict(dd)
        curr = (current_data.value_counts() / len(current_data)).to_dict(dd)

        hellinger_distance = 0.0
        for key in keys:
            p1 = ref[key]
            p2 = curr[key]
            hellinger_distance += sqrt(p1 * p2)

        hellinger_distance = np.clip(hellinger_distance, 0, 1)
        hellinger_distance = sqrt(1 - hellinger_distance)

    else:
        bins = np.histogram_bin_edges(keys, bins="sturges")
        h1 = np.histogram(reference_data.values, bins=bins, density=True)[0]
        h2 = np.histogram(current_data.values, bins=bins, density=True)[0]

        bin_width = (max(bins) - min(bins)) / (len(bins) - 1)

        hellinger_distance = 0.0
        for i in range(len(h1)):
            p1 = h1[i]
            p2 = h2[i]
            hellinger_distance += sqrt(p1 * p2) * bin_width

        hellinger_distance = np.clip(hellinger_distance, 0, 1)
        hellinger_distance = sqrt(1 - hellinger_distance)

    return hellinger_distance, hellinger_distance >= threshold


hellinger_stat_test = StatTest(
    name="hellinger",
    display_name="Hellinger distance",
    allowed_feature_types=[ColumnType.Categorical, ColumnType.Numerical],
    default_threshold=0.1,
)

register_stattest(hellinger_stat_test, _hellinger_distance)
