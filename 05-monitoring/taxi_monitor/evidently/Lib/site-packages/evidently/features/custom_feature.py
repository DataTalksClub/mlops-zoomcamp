from typing import Callable

import pandas as pd

from evidently.base_metric import ColumnName
from evidently.base_metric import additional_feature
from evidently.features.generated_features import GeneratedFeature
from evidently.utils.data_preprocessing import DataDefinition


class CustomFeature(GeneratedFeature):
    display_name: str
    func: Callable[[pd.DataFrame, DataDefinition], pd.Series]

    def generate_feature(self, data: pd.DataFrame, data_definition: DataDefinition) -> pd.DataFrame:
        result = self.func(data, data_definition)
        return pd.DataFrame(dict([(str(self.feature_id), result)]))

    def feature_name(self) -> "ColumnName":
        return additional_feature(self, str(self.feature_id), self.display_name)


class CustomSingleColumnFeature(GeneratedFeature):
    display_name: str
    func: Callable[[pd.Series], pd.Series]
    column_name: str

    def generate_feature(self, data: pd.DataFrame, data_definition: DataDefinition) -> pd.DataFrame:
        result = self.func(data[self.column_name])
        return pd.DataFrame(dict([(str(self.feature_id), result)]), index=data.index)

    def feature_name(self) -> "ColumnName":
        return additional_feature(self, str(self.feature_id), self.display_name)


class CustomPairColumnFeature(GeneratedFeature):
    display_name: str
    func: Callable[[pd.Series, pd.Series], pd.Series]
    first_column: str
    second_column: str

    def generate_feature(self, data: pd.DataFrame, data_definition: DataDefinition) -> pd.DataFrame:
        result = self.func(data[self.first_column], data[self.second_column])
        return pd.DataFrame(dict([(str(self.feature_id), result)]))

    def feature_name(self) -> "ColumnName":
        return additional_feature(self, str(self.feature_id), self.display_name)
