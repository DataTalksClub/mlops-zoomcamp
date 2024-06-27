from typing import Any
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
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.pipeline.column_mapping import RecomType
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import CounterData
from evidently.renderers.html_widgets import TabData
from evidently.renderers.html_widgets import counter
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import table_data
from evidently.renderers.html_widgets import widget_tabs


class PersonalizationMetricResult(MetricResult):
    class Config:
        pd_include = False

        field_tags = {
            "k": {IncludeTags.Parameter},
            "current_value": {IncludeTags.Current},
            "current_table": {IncludeTags.Current, IncludeTags.Extra},
            "reference_value": {IncludeTags.Reference},
            "reference_table": {IncludeTags.Reference, IncludeTags.Extra},
        }

    k: int
    current_value: float
    current_table: Dict[str, int]
    reference_value: Optional[float] = None
    reference_table: Optional[Dict[str, int]] = None


class PersonalizationMetric(Metric[PersonalizationMetricResult]):
    """Mean Inter List"""

    k: int

    def __init__(self, k: int, options: AnyOptions = None) -> None:
        self.k = k
        super().__init__(options=options)

    def get_diversity(
        self,
        df: pd.DataFrame,
        user_id: str,
        item_id: str,
        prediction_name: str,
        k: int,
        recommendations_type: RecomType,
    ):
        df = df.copy()
        table = dict(df[item_id].value_counts()[:10])
        if recommendations_type == RecomType.SCORE:
            df[prediction_name] = df.groupby(user_id)[prediction_name].transform("rank", ascending=False)
        df = df[df[prediction_name] <= k]
        recommended_counter = df[item_id].value_counts()
        n_users = df[user_id].nunique()
        cooccurrences_cumulative = np.sum(recommended_counter**2) - n_users * k
        all_user_couples_count = n_users**2 - n_users
        diversity_cumulative = all_user_couples_count - cooccurrences_cumulative / k

        diversity = diversity_cumulative / all_user_couples_count
        recommended_counter.index = recommended_counter.index.astype(str)
        return diversity, table

    def calculate(self, data: InputData) -> PersonalizationMetricResult:
        prediction_name = get_prediciton_name(data)
        user_id = data.data_definition.get_user_id_column()
        item_id = data.data_definition.get_item_id_column()
        recommendations_type = data.column_mapping.recom_type
        if user_id is None or item_id is None or recommendations_type is None:
            raise ValueError("user_id and item_id and recommendations_type should be specified")
        curr_value, curr_table = self.get_diversity(
            data.current_data,
            user_id=user_id.column_name,
            item_id=item_id.column_name,
            prediction_name=prediction_name,
            k=self.k,
            recommendations_type=recommendations_type,
        )

        ref_table: Optional[Dict[Any, int]] = None
        ref_value: Optional[float] = None
        if data.reference_data is not None:
            ref_value, ref_table = self.get_diversity(
                data.reference_data,
                user_id=user_id.column_name,
                item_id=item_id.column_name,
                prediction_name=prediction_name,
                k=self.k,
                recommendations_type=recommendations_type,
            )
        return PersonalizationMetricResult(
            k=self.k,
            current_value=curr_value,
            current_table=curr_table,
            reference_value=ref_value,
            reference_table=ref_table,
        )


@default_renderer(wrap_type=PersonalizationMetric)
class PersonalizationMetricRenderer(MetricRenderer):
    @staticmethod
    def _get_table_stat(dataset_name: str, curr_table: dict, ref_table: Optional[dict]) -> BaseWidgetInfo:
        matched_stat_headers = ["Value", "Count"]
        tabs = [
            TabData(
                title="CURRENT: Top 10 popular items",
                widget=table_data(
                    title="",
                    column_names=matched_stat_headers,
                    data=[(k, v) for k, v in curr_table.items() if v > 0][:10],
                ),
            ),
        ]
        if ref_table is not None:
            tabs.append(
                TabData(
                    title="REFERENCE: Top 10 popular items",
                    widget=table_data(
                        title="",
                        column_names=matched_stat_headers,
                        data=[(k, v) for k, v in ref_table.items() if v > 0][:10],
                    ),
                ),
            )
        return widget_tabs(title="", tabs=tabs)

    def render_html(self, obj: PersonalizationMetric) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()

        counters = [CounterData.float(label="current", value=metric_result.current_value, precision=4)]
        if metric_result.reference_value is not None:
            counters.append(CounterData.float(label="reference", value=metric_result.reference_value, precision=4))

        result = [
            header_text(label=f"Personalization (top-{metric_result.k})"),
            counter(counters=counters),
            self._get_table_stat("", metric_result.current_table, metric_result.reference_table),
        ]

        return result
