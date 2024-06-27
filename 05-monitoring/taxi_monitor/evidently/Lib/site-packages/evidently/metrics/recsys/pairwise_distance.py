from typing import Dict
from typing import List
from typing import Union

import numpy as np
import pandas as pd
from sklearn.metrics import pairwise_distances

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


class PairwiseDistanceResult(MetricResult):
    class Config:
        pd_include = False
        field_tags = {"dist_matrix": {IncludeTags.Extra}}

    dist_matrix: np.ndarray
    name_dict: Dict[Union[int, str], int]


class PairwiseDistance(Metric[PairwiseDistanceResult]):
    k: int
    item_features: List[str]

    def __init__(self, k: int, item_features: List[str], options: AnyOptions = None) -> None:
        self.k = k
        self.item_features = item_features
        super().__init__(options=options)

    def calculate(self, data: InputData) -> PairwiseDistanceResult:
        curr = data.current_data
        ref = data.reference_data
        prediction_name = get_prediciton_name(data)
        recommendations_type = data.column_mapping.recom_type
        user_id = data.data_definition.get_user_id_column()
        item_id = data.data_definition.get_item_id_column()
        current_train_data = data.additional_data.get("current_train_data")
        reference_train_data = data.additional_data.get("reference_train_data")
        if recommendations_type is None or user_id is None or item_id is None:
            raise ValueError("recommendations_type, user_id, item_id must be provided in the column mapping.")

        all_items = curr.copy()
        if ref is not None:
            all_items = pd.concat([curr, ref])
        if recommendations_type == RecomType.SCORE:
            all_items[prediction_name] = all_items.groupby(user_id.column_name)[prediction_name].transform(
                "rank", ascending=False
            )
        all_items = all_items[all_items[prediction_name] <= self.k + 1]
        all_items = all_items[[item_id.column_name] + self.item_features]
        if current_train_data is not None:
            if not np.in1d(self.item_features, current_train_data.columns).all():
                raise ValueError("current_train_data must contain item_features.")
            all_items = pd.concat([all_items, current_train_data[[item_id.column_name] + self.item_features]])
        if reference_train_data is not None:
            if not np.in1d(self.item_features, reference_train_data.columns).all():
                raise ValueError("reference_train_data must contain item_features.")
            all_items = pd.concat([all_items, reference_train_data[[item_id.column_name] + self.item_features]])

        all_items.drop_duplicates(subset=[item_id.column_name], inplace=True)
        name_dict = {i: j for i, j in zip(all_items[item_id.column_name], range(all_items.shape[0]))}
        return PairwiseDistanceResult(
            dist_matrix=pairwise_distances(all_items[self.item_features], metric="cosine"), name_dict=name_dict
        )


@default_renderer(wrap_type=PairwiseDistance)
class PairwiseDistanceRenderer(MetricRenderer):
    def render_html(self, obj: PairwiseDistance) -> List[BaseWidgetInfo]:
        return []
