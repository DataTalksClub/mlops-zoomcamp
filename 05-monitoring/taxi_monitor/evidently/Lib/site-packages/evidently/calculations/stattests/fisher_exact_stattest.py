"""Fisher's exact test of two samples.

Name: "fisher_exact"

Import:

    >>> from evidently.calculations.stattests import fisher_exact_test

Properties:
- only for categorical features
- returns p-value

Example:
    Using by object:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> from evidently.calculations.stattests import fisher_exact_test
    >>> options = DataDriftOptions(all_features_stattest=fisher_exact_test)

    Using by name:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> options = DataDriftOptions(all_features_stattest="fisher_exact")
"""

from typing import Tuple

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact

from evidently.calculations.stattests.registry import StatTest
from evidently.calculations.stattests.registry import register_stattest

from ...core import ColumnType
from .utils import generate_fisher2x2_contingency_table


def _fisher_exact_stattest(
    reference_data: pd.Series, current_data: pd.Series, feature_type: ColumnType, threshold: float
) -> Tuple[float, bool]:
    """Calculate the p-value of Fisher's exact test between two arrays
    Args:
        reference_data: reference data
        current_data: current data
        feature_type: feature type
        threshold: all values above this threshold means data drift
    Raises:
        ValueError: If null or inf values is found in either reference_data or current_data
        ValueError: If reference_data or current_data is not binary(unique values exceeds 2)
    Returns:
        p_value: two-tailed p-value
        test_result: whether the drift is detected
    """

    if (
        (reference_data.isnull().values.any())
        or (current_data.isnull().values.any())
        or (reference_data.isin([np.inf, -np.inf]).any())
        or (current_data.isin([np.inf, -np.inf]).any())
    ):
        raise ValueError(
            "Null or inf values found in either reference_data or current_data. Please ensure that no null or inf values are present"
        )

    if (reference_data.nunique() > 2) or (current_data.nunique() > 2):
        raise ValueError("Expects binary data for both reference and current, but found unique categories > 2")

    contingency_matrix = generate_fisher2x2_contingency_table(reference_data, current_data)
    _, p_value = fisher_exact(contingency_matrix)
    return p_value, p_value < threshold


fisher_exact_test = StatTest(
    name="fisher_exact",
    display_name="Fisher's Exact test",
    allowed_feature_types=[ColumnType.Categorical],
    default_threshold=0.1,
)

register_stattest(fisher_exact_test, _fisher_exact_stattest)
