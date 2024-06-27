from pyspark.sql.functions import col

from evidently.calculations.stattests import chi_stat_test
from evidently.calculations.stattests.registry import StatTestFuncReturns
from evidently.core import ColumnType

from .base import SparkStatTestImpl
from .base import SpartStatTestData


class SparkChiSquare(SparkStatTestImpl):
    base_stat_test = chi_stat_test

    def __call__(self, data: SpartStatTestData, feature_type: ColumnType, threshold: float) -> StatTestFuncReturns:
        cur = data.current_data
        ref = data.reference_data
        column_name = data.column_name

        from scipy.stats import chisquare

        cur_vc = cur.groupby(column_name).count()
        cur_count = cur.count()
        ref_count = ref.count()
        k_norm = cur_count / ref_count
        ref_vc = ref.groupby(column_name).count().withColumn("count", col("count") * k_norm)

        ref_d = {r[column_name]: r["count"] for r in ref_vc.collect()}
        cur_d = {r[column_name]: r["count"] for r in cur_vc.collect()}
        keys = set(cur_d.keys()) | set(ref_d.keys())
        p_val = chisquare([cur_d.get(k, 0) for k in keys], [ref_d.get(k, 0) for k in keys])[1]

        return p_val, p_val < threshold
