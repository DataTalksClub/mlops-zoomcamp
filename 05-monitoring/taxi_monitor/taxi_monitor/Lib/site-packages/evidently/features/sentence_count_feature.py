import re
from typing import Optional

import numpy as np
import pandas as pd

from evidently.base_metric import ColumnName
from evidently.base_metric import additional_feature
from evidently.features.generated_features import GeneratedFeature
from evidently.utils.data_preprocessing import DataDefinition


class SentenceCount(GeneratedFeature):
    column_name: str

    def __init__(self, column_name: str, display_name: Optional[str] = None):
        self.column_name = column_name
        self.display_name = display_name
        super().__init__()

    def generate_feature(self, data: pd.DataFrame, data_definition: DataDefinition) -> pd.DataFrame:
        def sentence_count_f(s):
            if s is None or (isinstance(s, float) and np.isnan(s)):
                return 0
            number = len(re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", s))
            return max(1, number)

        return pd.DataFrame(dict([(self.column_name, data[self.column_name].apply(sentence_count_f))]))

    def feature_name(self) -> ColumnName:
        return additional_feature(self, self.column_name, self.display_name or f"Sentence Count for {self.column_name}")
