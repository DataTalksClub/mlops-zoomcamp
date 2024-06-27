from typing import Dict
from typing import List
from typing import Optional

import numpy as np
import pandas as pd

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.calculations.recommender_systems import get_curr_and_ref_df
from evidently.core import IncludeTags
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer


class PrecisionRecallCalculationResult(MetricResult):
    class Config:
        pd_include = False
        field_tags = {"current": {IncludeTags.Current}, "reference": {IncludeTags.Reference}}

    current: Dict[str, list]
    reference: Optional[Dict[str, list]] = None


class PrecisionRecallCalculation(Metric[PrecisionRecallCalculationResult]):
    max_k: int
    min_rel_score: Optional[int]

    def __init__(self, max_k: int, min_rel_score: Optional[int] = None, options: AnyOptions = None) -> None:
        self.max_k = max_k
        self.min_rel_score = min_rel_score
        super().__init__(options=options)

    def get_precision_and_recall_dict(self, df, max_k):
        user_df = df.groupby("users").target.agg(["size", "sum"])
        user_df.columns = ["size", "all"]
        max_k = min(user_df["size"].max(), max_k)
        res = {}
        for k in range(1, max_k + 1):
            tp = df[df.preds <= k].groupby("users").target.agg(["sum", "last"])
            tp.columns = [f"tp_{k}", f"rel_{k}"]
            user_df = pd.concat([user_df, tp], axis=1).fillna(0)
            user_df[f"precision_{k}"] = user_df[f"tp_{k}"] / np.minimum(user_df["size"], k)
            user_df[f"recall_{k}"] = user_df[f"tp_{k}"] / user_df["all"]
        user_df.replace([np.inf, -np.inf, np.nan], 0, inplace=True)
        res["k"] = [k for k in range(1, max_k + 1)]
        res["precision_include_no_feedback"] = list(user_df[[f"precision_{k}" for k in range(1, k + 1)]].mean())
        res["precision"] = list(user_df.loc[user_df["all"] != 0, [f"precision_{k}" for k in range(1, k + 1)]].mean())
        res["map_include_no_feedback"] = list(
            user_df[[f"precision_{k}" for k in range(1, k + 1)]]
            .multiply(user_df[[f"rel_{k}" for k in range(1, k + 1)]].values)
            .expanding(axis=1)
            .sum()
            .divide(user_df["all"], axis=0)
            .fillna(0)
            .mean()
        )
        res["map"] = list(
            user_df.loc[user_df["all"] != 0, [f"precision_{k}" for k in range(1, k + 1)]]
            .multiply(user_df.loc[user_df["all"] != 0, [f"rel_{k}" for k in range(1, k + 1)]].values)
            .expanding(axis=1)
            .sum()
            .divide(user_df.loc[user_df["all"] != 0, "all"], axis=0)
            .fillna(0)
            .mean()
        )
        res["recall_include_no_feedback"] = list(user_df[[f"recall_{k}" for k in range(1, k + 1)]].mean())
        res["recall"] = list(user_df.loc[user_df["all"] != 0, [f"recall_{k}" for k in range(1, k + 1)]].mean())
        res["mar_include_no_feedback"] = list(
            user_df[[f"recall_{k}" for k in range(1, k + 1)]]
            .multiply(user_df[[f"rel_{k}" for k in range(1, k + 1)]].values)
            .expanding(axis=1)
            .sum()
            .divide(user_df["all"], axis=0)
            .fillna(0)
            .mean()
        )
        res["mar"] = list(
            user_df.loc[user_df["all"] != 0, [f"recall_{k}" for k in range(1, k + 1)]]
            .multiply(user_df.loc[user_df["all"] != 0, [f"rel_{k}" for k in range(1, k + 1)]].values)
            .expanding(axis=1)
            .sum()
            .divide(user_df.loc[user_df["all"] != 0, "all"], axis=0)
            .fillna(0)
            .mean()
        )
        return res

    def calculate(self, data: InputData) -> PrecisionRecallCalculationResult:
        curr, ref = get_curr_and_ref_df(data, self.min_rel_score, True, True)
        current = self.get_precision_and_recall_dict(curr, self.max_k)
        reference: Optional[dict] = None
        if ref is not None:
            reference = self.get_precision_and_recall_dict(ref, self.max_k)

        return PrecisionRecallCalculationResult(
            current=current,
            reference=reference,
        )


@default_renderer(wrap_type=PrecisionRecallCalculation)
class PrecisionTopKMetricRenderer(MetricRenderer):
    def render_html(self, obj: PrecisionRecallCalculation) -> List[BaseWidgetInfo]:
        return []
