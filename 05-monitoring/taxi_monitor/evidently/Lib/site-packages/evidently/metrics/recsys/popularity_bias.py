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


class PopularityBiasResult(MetricResult):
    class Config:
        field_tags = {
            "k": {IncludeTags.Parameter},
            "normalize_arp": {IncludeTags.Parameter},
            "current_apr": {IncludeTags.Current},
            "current_coverage": {IncludeTags.Current},
            "current_gini": {IncludeTags.Current},
            "current_distr": {IncludeTags.Current},
            "reference_apr": {IncludeTags.Reference},
            "reference_coverage": {IncludeTags.Reference},
            "reference_gini": {IncludeTags.Reference},
            "reference_distr": {IncludeTags.Reference},
        }

    k: int
    normalize_arp: bool
    current_apr: float
    current_coverage: float
    current_gini: float
    current_distr: Distribution
    reference_apr: Optional[float] = None
    reference_coverage: Optional[float] = None
    reference_gini: Optional[float] = None
    reference_distr: Optional[Distribution] = None


class PopularityBias(Metric[PopularityBiasResult]):
    """
    Average Recommendation Popularity
    Aggregate Diversity
    Gini
    """

    k: int
    _train_stats: TrainStats
    normalize_arp: bool

    def __init__(self, k: int, normalize_arp: bool = False, options: AnyOptions = None) -> None:
        self.k = k
        self.normalize_arp = normalize_arp
        self._train_stats = TrainStats()
        super().__init__(options=options)

    def get_apr(
        self,
        k: int,
        df: pd.DataFrame,
        train_stats: pd.Series,
        normalize_arp: bool,
        prediction_name: str,
        user_name: str,
        item_name: str,
    ):
        data = df.copy()
        data = data[data[prediction_name] <= k]
        data["popularity"] = data[item_name].map(train_stats).replace([np.inf, -np.inf], np.nan)
        if normalize_arp:
            data["popularity"] = data["popularity"] / train_stats.max()
        data = data[~data.popularity.isna()]
        value = data.groupby(user_name).popularity.mean().mean()
        distr_data = data.popularity
        return value, distr_data

    def get_gini(
        self,
        k: int,
        df: pd.DataFrame,
        prediction_name: str,
        item_name: str,
    ):
        data = df.copy()
        data = data[data[prediction_name] <= k]
        recommended_counter_sorted = data[item_name].value_counts(ascending=True)
        n_items = len(recommended_counter_sorted)
        index = np.arange(1, n_items + 1)
        return (np.sum((2 * index - n_items - 1) * recommended_counter_sorted)) / (
            (n_items - 1) * np.sum(recommended_counter_sorted)
        )

    def get_coverage(
        self,
        k: int,
        df: pd.DataFrame,
        train_stats: pd.Series,
        prediction_name: str,
        item_name: str,
    ):
        return len(np.intersect1d(df[df[prediction_name] <= k][item_name].unique(), train_stats.index)) / len(
            train_stats
        )

    def calculate(self, data: InputData) -> PopularityBiasResult:
        train_result = self._train_stats.get_result()
        curr_user_interacted = train_result.current
        ref_user_interacted = train_result.reference
        prediction_name = get_prediciton_name(data)
        col_user_id = data.data_definition.get_user_id_column()
        col_item_id = data.data_definition.get_item_id_column()
        recommendations_type = data.column_mapping.recom_type
        if col_user_id is None or col_item_id is None or recommendations_type is None:
            raise ValueError("user_id and item_id and recommendations_type should be specified")
        user_id = col_user_id.column_name
        item_id = col_item_id.column_name

        current_data = data.current_data.copy()
        if recommendations_type == RecomType.SCORE:
            current_data[prediction_name] = current_data.groupby(user_id)[prediction_name].transform(
                "rank", ascending=False
            )

        current_apr, current_distr_data = self.get_apr(
            self.k,
            current_data,
            curr_user_interacted,
            self.normalize_arp,
            prediction_name,
            user_id,
            item_id,
        )
        curr_coverage = self.get_coverage(self.k, current_data, curr_user_interacted, prediction_name, item_id)

        curr_gini = self.get_gini(self.k, current_data, prediction_name, item_id)

        reference_apr: Optional[float] = None
        ref_coverage: Optional[float] = None
        ref_gini: Optional[float] = None
        reference_distr_data: Optional[pd.Series] = None
        if data.reference_data is not None:
            reference_data = data.reference_data.copy()
            if recommendations_type == RecomType.SCORE:
                reference_data[prediction_name] = reference_data.groupby(user_id)[prediction_name].transform(
                    "rank", ascending=False
                )
            if ref_user_interacted is None:
                ref_user_interacted = curr_user_interacted

            reference_apr, reference_distr_data = self.get_apr(
                self.k,
                reference_data,
                ref_user_interacted,
                self.normalize_arp,
                prediction_name,
                user_id,
                item_id,
            )

            ref_coverage = reference_data[item_id].nunique() / len(ref_user_interacted)

            ref_gini = self.get_gini(self.k, reference_data, prediction_name, item_id)
        current_distr, reference_distr = get_distribution_for_column(
            column_type="num",
            current=current_distr_data,
            reference=reference_distr_data,
        )

        return PopularityBiasResult(
            k=self.k,
            normalize_arp=self.normalize_arp,
            current_apr=current_apr,
            current_coverage=curr_coverage,
            current_gini=curr_gini,
            current_distr=current_distr,
            reference_apr=reference_apr,
            reference_coverage=ref_coverage,
            reference_distr=reference_distr,
            reference_gini=ref_gini,
        )


@default_renderer(wrap_type=PopularityBias)
class PopularityBiasRenderer(MetricRenderer):
    def render_html(self, obj: PopularityBias) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        is_normed = ""
        if metric_result.normalize_arp:
            is_normed = " normilized"
        result = [header_text(label=f"Popularity bias (top-{metric_result.k})")]
        counters = [
            CounterData.float(
                label="current ARP" + is_normed,
                value=metric_result.current_apr,
                precision=4,
            ),
            CounterData.float(
                label="current coverage",
                value=metric_result.current_coverage,
                precision=4,
            ),
            CounterData.float(
                label="current gini index",
                value=metric_result.current_gini,
                precision=4,
            ),
        ]
        result.append(counter(counters=counters))
        if (
            metric_result.reference_apr is not None
            and metric_result.reference_coverage is not None
            and metric_result.reference_gini is not None
        ):
            counters = [
                CounterData.float(
                    label="reference ARP" + is_normed,
                    value=metric_result.reference_apr,
                    precision=4,
                ),
                CounterData.float(
                    label="reference coverage",
                    value=metric_result.reference_coverage,
                    precision=4,
                ),
                CounterData.float(
                    label="reference gini index",
                    value=metric_result.reference_gini,
                    precision=4,
                ),
            ]
            result.append(counter(counters=counters))

        distr_fig = plot_distr_with_perc_button(
            hist_curr=HistogramData.from_distribution(metric_result.current_distr),
            hist_ref=HistogramData.from_distribution(metric_result.reference_distr),
            xaxis_name="item popularity" + is_normed,
            yaxis_name="Count",
            yaxis_name_perc="Percent",
            same_color=False,
            color_options=self.color_options,
            subplots=False,
            to_json=False,
        )
        result.append(plotly_figure(title="", figure=distr_fig))

        return result
