from scipy.spatial import distance

from evidently.calculations.stattests import jensenshannon_stat_test
from evidently.calculations.stattests.registry import StatTestFuncReturns
from evidently.core import ColumnType

from .base import SparkStatTestImpl
from .base import SpartStatTestData
from .utils import get_binned_data


class SparkJensenShannon(SparkStatTestImpl):
    base_stat_test = jensenshannon_stat_test

    def __call__(self, data: SpartStatTestData, feature_type: ColumnType, threshold: float) -> StatTestFuncReturns:
        cur = data.current_data
        ref = data.reference_data
        column_name = data.column_name
        reference_percents, current_percents = get_binned_data(ref, cur, column_name, feature_type, False)
        jensenshannon_value = distance.jensenshannon(reference_percents, current_percents, base=None)
        return jensenshannon_value, jensenshannon_value >= threshold
