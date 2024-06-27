from typing import Optional

import numpy as np
import pandas as pd

from evidently.base_metric import InputData
from evidently.metrics.recsys.base_top_k import TopKMetric
from evidently.metrics.recsys.base_top_k import TopKMetricRenderer
from evidently.metrics.recsys.base_top_k import TopKMetricResult
from evidently.metrics.recsys.precision_recall_k import PrecisionRecallCalculation
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import default_renderer


class FBetaTopKMetric(TopKMetric):
    k: int
    beta: Optional[float]
    min_rel_score: Optional[int]
    no_feedback_users: bool
    _precision_recall_calculation: PrecisionRecallCalculation

    def __init__(
        self,
        k: int,
        beta: Optional[float] = 1.0,
        min_rel_score: Optional[int] = None,
        no_feedback_users: bool = False,
        options: AnyOptions = None,
    ) -> None:
        self.k = k
        self.beta = beta
        self.min_rel_score = min_rel_score
        self.no_feedback_users = no_feedback_users
        self._precision_recall_calculation = PrecisionRecallCalculation(max(k, 10), min_rel_score)
        super().__init__(
            options=options,
            k=k,
            min_rel_score=min_rel_score,
            no_feedback_users=no_feedback_users,
        )

    def calculate(self, data: InputData) -> TopKMetricResult:
        if self.no_feedback_users:
            pr_key = "precision_include_no_feedback"
            rc_key = "recall_include_no_feedback"
        else:
            pr_key = "precision"
            rc_key = "recall"
        result = self._precision_recall_calculation.get_result()
        current = pd.Series(index=result.current["k"], data=self.fbeta(result.current[pr_key], result.current[rc_key]))
        ref_data = result.reference
        reference: Optional[pd.Series] = None
        if ref_data is not None:
            reference = pd.Series(index=ref_data["k"], data=self.fbeta(ref_data[pr_key], ref_data[rc_key]))
        return TopKMetricResult(k=self.k, reference=reference, current=current)

    def fbeta(self, precision, recall):
        beta_sqr = self.beta**2
        precision_arr = np.array(precision)
        recall_arr = np.array(recall)
        return (1 + beta_sqr) * precision_arr * recall_arr / (beta_sqr * precision_arr + recall_arr)

    def key(self) -> str:
        return ""


@default_renderer(wrap_type=FBetaTopKMetric)
class FBetaTopKMetricRenderer(TopKMetricRenderer):
    yaxis_name = "f_beta@k"
    header = "F_beta"
