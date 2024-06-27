import abc
from typing import List
from typing import Optional

import pandas as pd

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.core import IncludeTags
from evidently.metrics.recsys.precision_recall_k import PrecisionRecallCalculation
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import CounterData
from evidently.renderers.html_widgets import counter
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import plotly_figure
from evidently.utils.visualizations import plot_metric_k


class TopKMetricResult(MetricResult):
    class Config:
        field_tags = {
            "current": {IncludeTags.Current},
            "reference": {IncludeTags.Reference},
            "k": {IncludeTags.Parameter},
        }

    k: int
    current: pd.Series
    reference: Optional[pd.Series] = None


class TopKMetric(Metric[TopKMetricResult], abc.ABC):
    _precision_recall_calculation: PrecisionRecallCalculation
    k: int
    min_rel_score: Optional[int]
    no_feedback_users: bool

    def __init__(
        self, k: int, min_rel_score: Optional[int] = None, no_feedback_users: bool = False, options: AnyOptions = None
    ) -> None:
        self.k = k
        self.min_rel_score = min_rel_score
        self.no_feedback_users = no_feedback_users
        self._precision_recall_calculation = PrecisionRecallCalculation(max(k, 10), min_rel_score)
        super().__init__(options=options)

    def calculate(self, data: InputData) -> TopKMetricResult:
        result = self._precision_recall_calculation.get_result()
        key = self.key()
        if key is None:
            raise ValueError("Key should be specified")
        if self.no_feedback_users:
            key = f"{self.key()}_include_no_feedback"

        current = pd.Series(index=result.current["k"], data=result.current[key])
        ref_data = result.reference
        reference: Optional[pd.Series] = None
        if ref_data is not None:
            reference = pd.Series(index=ref_data["k"], data=ref_data[key])
        return TopKMetricResult(k=self.k, reference=reference, current=current)

    @abc.abstractmethod
    def key(self) -> str:
        raise NotImplementedError()


@default_renderer(wrap_type=TopKMetric)
class TopKMetricRenderer(MetricRenderer):
    yaxis_name: str
    header: str

    def render_html(self, obj: TopKMetric) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        k = metric_result.k
        counters = [CounterData.float(label="current", value=metric_result.current[k], precision=3)]
        if metric_result.reference is not None:
            counters.append(CounterData.float(label="reference", value=metric_result.reference[k], precision=3))
        fig = plot_metric_k(metric_result.current, metric_result.reference, self.yaxis_name)
        header_part = " No feedback users included."
        if not obj.no_feedback_users:
            header_part = " No feedback users excluded."

        return [
            header_text(label=self.header + f" (top-{k})." + header_part),
            counter(counters=counters),
            plotly_figure(title="", figure=fig),
        ]
