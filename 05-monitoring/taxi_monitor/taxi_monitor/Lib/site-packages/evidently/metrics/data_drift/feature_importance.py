from typing import Dict
from typing import List
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OrdinalEncoder

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.core import ColumnType
from evidently.core import IncludeTags
from evidently.model.widget import BaseWidgetInfo
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.utils.data_preprocessing import DataDefinition

SAMPLE_SIZE = 5000


class FeatureImportanceMetricResult(MetricResult):
    class Config:
        field_tags = {"current": {IncludeTags.Current}, "reference": {IncludeTags.Reference}}

    current: Optional[Dict[str, float]] = None
    reference: Optional[Dict[str, float]] = None

    def get_pandas(self) -> pd.DataFrame:
        dfs = []
        for field in ["current", "reference"]:
            value = getattr(self, field)
            if value is None:
                continue
            df = pd.DataFrame([value])
            df["dataset"] = field
            dfs.append(df)
        return pd.concat(dfs)


class FeatureImportanceMetric(Metric[FeatureImportanceMetricResult]):
    def calculate(self, data: InputData) -> FeatureImportanceMetricResult:
        if data.additional_data.get("current_feature_importance") is not None:
            return FeatureImportanceMetricResult(
                current=data.additional_data.get("current_feature_importance"),
                reference=data.additional_data.get("reference_feature_importance"),
            )

        curr_sampled_data = data.current_data.sample(min(SAMPLE_SIZE, data.current_data.shape[0]), random_state=0)
        ref_sampled_data: Optional[pd.DataFrame] = None
        if data.reference_data is not None:
            ref_sampled_data = data.reference_data.sample(
                min(SAMPLE_SIZE, data.reference_data.shape[0]), random_state=0
            )

        return get_feature_importance_from_samples(data.data_definition, curr_sampled_data, ref_sampled_data)


def get_feature_importance_from_samples(
    data_definition: DataDefinition, curr_sampled_data: pd.DataFrame, ref_sampled_data: Optional[pd.DataFrame]
):
    num_cols = data_definition.get_columns(filter_def=ColumnType.Numerical, features_only=True)
    cat_cols = data_definition.get_columns(filter_def=ColumnType.Categorical, features_only=True)

    columns = [x.column_name for x in num_cols] + [x.column_name for x in cat_cols]

    for col in [x.column_name for x in cat_cols]:
        enc = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=np.nan)
        curr_sampled_data[col] = enc.fit_transform(curr_sampled_data[col].astype(str).values.reshape(-1, 1))
        if ref_sampled_data is not None:
            ref_sampled_data[col] = enc.fit_transform(ref_sampled_data[col].astype(str).values.reshape(-1, 1))

    task = data_definition.task
    target_column = data_definition.get_target_column()
    if target_column is None:
        return FeatureImportanceMetricResult(current=None, reference=None)
    target_name = target_column.column_name
    if task == "regression":
        model = RandomForestRegressor(min_samples_leaf=10)
    else:
        model = RandomForestClassifier(min_samples_leaf=10)

    model.fit(curr_sampled_data[columns].fillna(0), curr_sampled_data[target_name])
    current_fi = {x: np.round(y, 3) for x, y in zip(columns, model.feature_importances_)}

    reference_fi: Optional[Dict[str, float]] = None
    if ref_sampled_data is not None:
        model.fit(ref_sampled_data[columns].fillna(0), ref_sampled_data[target_name])
        reference_fi = {x: np.round(y, 3) for x, y in zip(columns, model.feature_importances_)}
    return FeatureImportanceMetricResult(current=current_fi, reference=reference_fi)


@default_renderer(wrap_type=FeatureImportanceMetric)
class FeatureImportanceRenderer(MetricRenderer):
    def render_html(self, obj: FeatureImportanceMetric) -> List[BaseWidgetInfo]:
        return []
