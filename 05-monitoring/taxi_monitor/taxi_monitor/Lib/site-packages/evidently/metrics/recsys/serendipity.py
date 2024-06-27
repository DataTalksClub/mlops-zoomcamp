from itertools import product
from typing import Dict
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
from evidently.metrics.recsys.pairwise_distance import PairwiseDistance
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


class SerendipityMetricResult(MetricResult):
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


class SerendipityMetric(Metric[SerendipityMetricResult]):
    """unusualness * relevance"""

    _pairwise_distance: PairwiseDistance
    k: int
    item_features: List[str]
    min_rel_score: Optional[int]

    def __init__(
        self, k: int, item_features: List[str], min_rel_score: Optional[int] = None, options: AnyOptions = None
    ) -> None:
        self.k = k
        self.item_features = item_features
        self.min_rel_score = min_rel_score
        self._pairwise_distance = PairwiseDistance(k=k, item_features=item_features)
        super().__init__(options=options)

    def get_serendipity(
        self,
        k: int,
        df: pd.DataFrame,
        recommendations_type: RecomType,
        train_df: pd.DataFrame,
        dist_matrix: np.ndarray,
        prediction_name: str,
        target_name: str,
        user_id: str,
        item_id: str,
        name_dict: Dict,
        min_rel_score: Optional[int],
    ):
        df = df.copy()
        if min_rel_score is not None:
            df[target_name] = (df[target_name] >= min_rel_score).astype(int)
        if recommendations_type == RecomType.SCORE:
            df[prediction_name] = df.groupby(user_id)[prediction_name].transform("rank", ascending=False)
        df = df.loc[(df[target_name] > 0) & (df[prediction_name] <= k), [user_id, item_id]]
        all_users = df[user_id].unique()
        all_users = np.intersect1d(all_users, train_df[user_id].unique())
        user_res = []
        for user in all_users:
            user_train = train_df.loc[train_df[user_id] == user, item_id]
            user_df = df.loc[df[user_id] == user, item_id]
            res = 0
            for i, j in product(user_train, user_df):
                res += 1 - dist_matrix[name_dict[i], name_dict[j]]
            user_res.append(1 - res / len(user_train))
        distr_data = pd.Series(user_res)
        value = np.mean(user_res)
        return distr_data, value

    def calculate(self, data: InputData) -> SerendipityMetricResult:
        result = self._pairwise_distance.get_result()
        dist_matrix = result.dist_matrix
        name_dict = result.name_dict
        target = data.data_definition.get_target_column()
        user_id = data.data_definition.get_user_id_column()
        item_id = data.data_definition.get_item_id_column()
        recommendations_type = data.column_mapping.recom_type
        if user_id is None or item_id is None or recommendations_type is None or target is None:
            raise ValueError("user_id, item_id, recommendations_type and target should be specified")
        current_train_data = data.additional_data.get("current_train_data")
        reference_train_data = data.additional_data.get("reference_train_data")
        if current_train_data is None:
            raise ValueError(
                """current_train_data should be presented in additional_data with key "current_train_data":
                report.run(reference_data=reference_df, current_data=current_df, column_mapping=column_mapping,
                additional_data={"current_train_data": current_train_df})"""
            )
        prediction_name = get_prediciton_name(data)
        curr_distr_data, curr_value = self.get_serendipity(
            df=data.current_data,
            train_df=current_train_data,
            k=self.k,
            recommendations_type=recommendations_type,
            user_id=user_id.column_name,
            item_id=item_id.column_name,
            prediction_name=prediction_name,
            target_name=target.column_name,
            dist_matrix=dist_matrix,
            name_dict=name_dict,
            min_rel_score=self.min_rel_score,
        )

        ref_distr_data: Optional[pd.Series] = None
        ref_value: Optional[float] = None
        if data.reference_data is not None:
            reference_train = current_train_data
            if reference_train_data is not None:
                reference_train = reference_train_data
            ref_distr_data, ref_value = self.get_serendipity(
                df=data.reference_data,
                train_df=reference_train,
                k=self.k,
                recommendations_type=recommendations_type,
                user_id=user_id.column_name,
                item_id=item_id.column_name,
                prediction_name=prediction_name,
                target_name=target.column_name,
                dist_matrix=dist_matrix,
                name_dict=name_dict,
                min_rel_score=self.min_rel_score,
            )
        curr_distr, ref_distr = get_distribution_for_column(
            column_type="num", current=curr_distr_data, reference=ref_distr_data
        )
        return SerendipityMetricResult(
            k=self.k,
            current_value=curr_value,
            current_distr=curr_distr,
            reference_value=ref_value,
            reference_distr=ref_distr,
        )


@default_renderer(wrap_type=SerendipityMetric)
class SerendipityMetricRenderer(MetricRenderer):
    def render_html(self, obj: SerendipityMetric) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        counters = [CounterData.float(label="current", value=metric_result.current_value, precision=4)]
        if metric_result.reference_value is not None:
            counters.append(CounterData.float(label="reference", value=metric_result.reference_value, precision=4))

        distr_fig = plot_distr_with_perc_button(
            hist_curr=HistogramData.from_distribution(metric_result.current_distr),
            hist_ref=HistogramData.from_distribution(metric_result.reference_distr),
            xaxis_name="serendipity by user",
            yaxis_name="Count",
            yaxis_name_perc="Percent",
            same_color=False,
            color_options=self.color_options,
            subplots=False,
            to_json=False,
        )

        return [
            header_text(label=f"Serendipity (top-{metric_result.k})"),
            counter(counters=counters),
            plotly_figure(title="", figure=distr_fig),
        ]
