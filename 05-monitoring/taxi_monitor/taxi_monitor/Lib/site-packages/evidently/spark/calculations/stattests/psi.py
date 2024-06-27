import numpy as np

from evidently.calculations.stattests import psi_stat_test
from evidently.calculations.stattests.registry import StatTestFuncReturns
from evidently.core import ColumnType

from .base import SparkStatTestImpl
from .base import SpartStatTestData
from .utils import get_binned_data


class SparkPSI(SparkStatTestImpl):
    base_stat_test = psi_stat_test

    def __call__(self, data: SpartStatTestData, feature_type: ColumnType, threshold: float) -> StatTestFuncReturns:
        cur = data.current_data
        ref = data.reference_data
        column_name = data.column_name
        reference_percents, current_percents = get_binned_data(ref, cur, column_name, feature_type)

        psi_values = (reference_percents - current_percents) * np.log(reference_percents / current_percents)
        psi_value = np.sum(psi_values)

        return psi_value, psi_value >= threshold
