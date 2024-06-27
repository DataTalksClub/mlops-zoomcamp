from typing import Dict
from typing import List
from typing import Optional
from typing import overload

import pandas as pd
from pandas import Interval

from evidently.base_metric import MetricResult
from evidently.core import IncludeTags
from evidently.metric_results import ScatterData


class PredActualScatter(MetricResult):
    predicted: ScatterData
    actual: ScatterData


@overload
def scatter_as_dict(scatter: PredActualScatter) -> Dict[str, ScatterData]: ...


@overload
def scatter_as_dict(scatter: Optional[PredActualScatter]) -> Optional[Dict[str, ScatterData]]: ...


def scatter_as_dict(scatter: Optional[PredActualScatter]) -> Optional[Dict[str, ScatterData]]:
    if scatter is None:
        return None
    return scatter.dict()


class RegressionScatter(MetricResult):
    underestimation: PredActualScatter
    majority: PredActualScatter
    overestimation: PredActualScatter


class IntervalSeries(MetricResult):
    class Config:
        underscore_attrs_are_private = True

    bins: List[float]
    values: List[float]

    _data: pd.Series

    @property
    def data(self):
        if not hasattr(self, "_data"):
            self._data = pd.Series(
                self.values, index=[Interval(a, b, closed="right") for a, b in zip(self.bins, self.bins[1:])]
            )
        return self._data

    @classmethod
    def from_data(cls, data: pd.Series):
        index = list(data.index)
        interval_series = cls(values=list(data), bins=[i.left for i in index] + [index[-1].right])
        interval_series._data = data
        return interval_series

    def __mul__(self, other: float):
        series = IntervalSeries(bins=self.bins, values=[v * other for v in self.values])
        if hasattr(self, "_data"):
            series._data = self._data * other
        return series


class RegressionMetricScatter(MetricResult):
    class Config:
        smart_union = True
        field_tags = {"current": {IncludeTags.Current}, "reference": {IncludeTags.Reference}}

    current: IntervalSeries
    reference: Optional[IntervalSeries] = None

    def __mul__(self, other: float):
        return RegressionMetricScatter(
            current=self.current * other, reference=self.reference * other if self.reference is not None else None
        )


class RegressionMetricsScatter(MetricResult):
    r2_score: RegressionMetricScatter
    rmse: RegressionMetricScatter
    mean_abs_error: RegressionMetricScatter
    mean_abs_perc_error: RegressionMetricScatter
