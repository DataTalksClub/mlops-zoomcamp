from typing import Optional

import pandas as pd

from evidently.base_metric import additional_feature
from evidently.core import ColumnType
from evidently.features.generated_features import GeneratedFeature
from evidently.utils.data_preprocessing import DataDefinition


class RegExp(GeneratedFeature):
    column_name: str
    reg_exp: str

    def __init__(self, column_name: str, reg_exp: str, display_name: Optional[str] = None):
        self.feature_type = ColumnType.Categorical
        self.column_name = column_name
        self.reg_exp = reg_exp
        self.display_name = display_name
        super().__init__()

    def generate_feature(self, data: pd.DataFrame, data_definition: DataDefinition) -> pd.DataFrame:
        result = data[self.column_name].astype(str).str.fullmatch(self.reg_exp).astype(int)
        return pd.DataFrame(dict([(self.column_name + "_" + self.reg_exp, result)]))

    def feature_name(self):
        return additional_feature(
            self,
            self.column_name + "_" + self.reg_exp,
            self.display_name or f"RegExp '{self.reg_exp}' Match for column {self.column_name}",
        )

    def get_parameters(self):
        return self.column_name, self.reg_exp
