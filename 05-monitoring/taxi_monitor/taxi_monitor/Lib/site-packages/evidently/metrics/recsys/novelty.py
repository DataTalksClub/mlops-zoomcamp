from typing import List
from typing import Optional

import numpy as np
import pandas as pd

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.calculations.recommender_systems import get_prediciton_name
from evidently.core import IncludeTags
from evidently.metric_results import Distribution
from evidently.metric_results import HistogramData
from evidently.metrics.recsys.train_stats import TrainStats
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.pipeline.column_mapping import RecomType
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import CounterData
from evidently.renderers.html_widgets import counter
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import plotly_figure
from evidently.utils.visualizations import get_distribution_for_column
from evidently.utils.visualizations import plot_distr_with_perc_button


class NoveltyMetricResult(MetricResult):
    class Config:
        field_tags = {
            "k": {IncludeTags.Parameter},
            "current_value": {IncludeTags.Current},
            "current_distr": {IncludeTags.Current},
            "reference_value": {IncludeTags.Reference},
            "reference_distr": {IncludeTags.Reference},
        }

    k: int
    current_value: float
    current_distr: Distribution
    reference_value: Optional[float] = None
    reference_distr: Optional[Distribution] = None


class NoveltyMetric(Metric[NoveltyMetricResult]):
    """Mean Inverse User Frequency"""

    k: int
    _train_stats: TrainStats

    def __init__(self, k: int, options: AnyOptions = None) -> None:
        self.k = k
        self._train_stats = TrainStats()
        super().__init__(options=options)

    def get_miuf(
        self, df, k, recommendations_type: Optional[RecomType], user_name, item_name, prediction_name, interactions
    ):
        data = df.copy()
        if recommendations_type == RecomType.SCORE:
            data[prediction_name] = data.groupby(user_name)[prediction_name].transform("rank", ascending=False)
        data = data[data[prediction_name] <= k]
        data["miuf"] = -np.log2(data[item_name].map(interactions)).replace([np.inf, -np.inf], np.nan)
        data = data[~data.miuf.isna()]
        distr = data.groupby(user_name).miuf.mean()
        value = distr.mean()
        return distr, value

    def calculate(self, data: InputData) -> NoveltyMetricResult:
        train_result = self._train_stats.get_result()
        curr_user_interacted = train_result.current
        ref_user_interacted = train_result.reference
        current_n_users = train_result.current_n_users
        reference_n_users = train_result.reference_n_users
        user_id = data.column_mapping.user_id
        item_id = data.column_mapping.item_id

        curr_interactions = curr_user_interacted / current_n_users
        prediction_name = get_prediciton_name(data)
        curr_distr_data, curr_value = self.get_miuf(
            data.current_data,
            self.k,
            data.column_mapping.recom_type,
            user_id,
            item_id,
            prediction_name,
            curr_interactions,
        )
        ref_distr_data: Optional[pd.Series] = None
        ref_value: Optional[float] = None
        if data.reference_data is not None:
            ref_interactions = curr_interactions
            if ref_user_interacted is not None and reference_n_users is not None:
                ref_interactions = ref_user_interacted / reference_n_users
            ref_distr_data, ref_value = self.get_miuf(
                data.reference_data,
                self.k,
                data.column_mapping.recom_type,
                user_id,
                item_id,
                prediction_name,
                ref_interactions,
            )
        curr_distr, ref_distr = get_distribution_for_column(
            column_type="num", current=curr_distr_data, reference=ref_distr_data
        )
        return NoveltyMetricResult(
            k=self.k,
            current_value=curr_value,
            current_distr=curr_distr,
            reference_value=ref_value,
            reference_distr=ref_distr,
        )


@default_renderer(wrap_type=NoveltyMetric)
class NoveltyMetricRenderer(MetricRenderer):
    def render_html(self, obj: NoveltyMetric) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        counters = [CounterData.float(label="current", value=metric_result.current_value, precision=4)]
        if metric_result.reference_value is not None:
            counters.append(CounterData.float(label="reference", value=metric_result.reference_value, precision=4))

        distr_fig = plot_distr_with_perc_button(
            hist_curr=HistogramData.from_distribution(metric_result.current_distr),
            hist_ref=HistogramData.from_distribution(metric_result.reference_distr),
            xaxis_name="novelty by user",
            yaxis_name="Count",
            yaxis_name_perc="Percent",
            same_color=False,
            color_options=self.color_options,
            subplots=False,
            to_json=False,
        )

        return [
            header_text(label=f"Novelty (top-{metric_result.k})"),
            counter(counters=counters),
            plotly_figure(title="", figure=distr_fig),
        ]
