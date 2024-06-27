from typing import Callable
from typing import Union

import pandas as pd

from evidently.core import ColumnType
from evidently.features.custom_feature import CustomPairColumnFeature
from evidently.features.custom_feature import CustomSingleColumnFeature
from evidently.features.generated_features import FeatureDescriptor
from evidently.features.generated_features import GeneralDescriptor
from evidently.features.generated_features import GeneratedFeature


class CustomColumnEval(FeatureDescriptor):
    func: Callable[[pd.Series], pd.Series]
    display_name: str
    feature_type: Union[str, ColumnType]

    def feature(self, column_name: str) -> GeneratedFeature:
        return CustomSingleColumnFeature(
            func=self.func,
            column_name=column_name,
            display_name=self.display_name,
            feature_type=ColumnType(self.feature_type),
        )


class CustomPairColumnEval(GeneralDescriptor):
    func: Callable[[pd.Series, pd.Series], pd.Series]
    display_name: str
    first_column: str
    second_column: str
    feature_type: Union[str, ColumnType]

    def feature(self) -> GeneratedFeature:
        return CustomPairColumnFeature(
            func=self.func,
            first_column=self.first_column,
            second_column=self.second_column,
            display_name=self.display_name,
            feature_type=ColumnType(self.feature_type),
        )
