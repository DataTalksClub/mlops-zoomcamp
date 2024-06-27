from typing import Optional

import numpy as np
import pandas as pd

from evidently.base_metric import ColumnName
from evidently.base_metric import additional_feature
from evidently.features.generated_features import GeneratedFeature
from evidently.utils.data_preprocessing import DataDefinition


class TextLength(GeneratedFeature):
    column_name: str

    def __init__(self, column_name: str, display_name: Optional[str] = None):
        self.column_name = column_name
        self.display_name = display_name
        super().__init__()

    def generate_feature(self, data: pd.DataFrame, data_definition: DataDefinition) -> pd.DataFrame:
        def text_len(s):
            if s is None or (isinstance(s, float) and np.isnan(s)):
                return 0
            return len(s)

        return pd.DataFrame(dict([(self.column_name, data[self.column_name].apply(text_len))]))

    def feature_name(self) -> ColumnName:
        return additional_feature(self, self.column_name, self.display_name or f"Text Length for {self.column_name}")
