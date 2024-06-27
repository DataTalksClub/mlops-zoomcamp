import numpy as np
from pyspark.sql import functions as sf

from evidently.calculations.stattests import wasserstein_stat_test
from evidently.calculations.stattests.registry import StatTestFuncReturns
from evidently.core import ColumnType

from ...utils import calculate_stats
from ..histogram import get_histogram
from .base import SparkStatTestImpl
from .base import SpartStatTestData

APPROX_WASSERSTEIN_BINS = 1000


class SparkWasserstein(SparkStatTestImpl):
    base_stat_test = wasserstein_stat_test

    def __call__(self, data: SpartStatTestData, feature_type: ColumnType, threshold: float) -> StatTestFuncReturns:
        cur = data.current_data
        ref = data.reference_data
        column_name = data.column_name
        from scipy.stats import wasserstein_distance

        std = calculate_stats(ref, column_name, sf.stddev_pop)
        norm = max(std, 0.001)

        (w1, vals1) = get_histogram(cur, column_name, APPROX_WASSERSTEIN_BINS, False)
        (w2, vals2) = get_histogram(ref, column_name, APPROX_WASSERSTEIN_BINS, False)

        centers1 = np.diff(vals1) / 2 + vals1[:-1]
        centers2 = np.diff(vals2) / 2 + vals2[:-1]

        wd_norm_value = wasserstein_distance(centers1, centers2, w1, w2) / norm

        return wd_norm_value, wd_norm_value >= threshold
