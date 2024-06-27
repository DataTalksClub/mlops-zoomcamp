from typing import Optional

import pandas as pd

from evidently.base_metric import ColumnName
from evidently.base_metric import additional_feature
from evidently.core import ColumnType
from evidently.features.generated_features import GeneratedFeature
from evidently.utils.data_preprocessing import DataDefinition


class BeginsWith(GeneratedFeature):
    column_name: str
    case_sensitive: bool
    prefix: str

    def __init__(
        self,
        column_name: str,
        prefix: str,
        case_sensitive: bool = True,
        display_name: Optional[str] = None,
    ):
        self.feature_type = ColumnType.Categorical
        self.column_name = column_name
        self.display_name = display_name
        self.case_sensitive = case_sensitive
        self.prefix = prefix
        super().__init__()

    def _feature_column_name(self) -> str:
        return f"{self.column_name}.{self.prefix}.{self.case_sensitive}"

    def generate_feature(self, data: pd.DataFrame, data_definition: DataDefinition) -> pd.DataFrame:
        data = data[self.column_name]
        substr = self.prefix
        if not self.case_sensitive:
            data = data.str.casefold()
            substr = substr.casefold()
        calculated = data.str.startswith(substr)
        return pd.DataFrame(dict([(self._feature_column_name(), calculated)]))

    def feature_name(self) -> ColumnName:
        return additional_feature(
            self,
            self._feature_column_name(),
            self.display_name or f"Text Begins with [{self.prefix}] for {self.column_name}",
        )


class EndsWith(GeneratedFeature):
    column_name: str
    case_sensitive: bool
    suffix: str

    def __init__(
        self,
        column_name: str,
        suffix: str,
        case_sensitive: bool = True,
        display_name: Optional[str] = None,
    ):
        self.feature_type = ColumnType.Categorical
        self.column_name = column_name
        self.display_name = display_name
        self.case_sensitive = case_sensitive
        self.suffix = suffix
        super().__init__()

    def _feature_column_name(self) -> str:
        return f"{self.column_name}.{self.suffix}.{self.case_sensitive}"

    def generate_feature(self, data: pd.DataFrame, data_definition: DataDefinition) -> pd.DataFrame:
        data = data[self.column_name]
        substr = self.suffix
        if not self.case_sensitive:
            data = data.str.casefold()
            substr = substr.casefold()
        calculated = data.str.endswith(substr)
        return pd.DataFrame(
            dict(
                [
                    (
                        self._feature_column_name(),
                        calculated,
                    )
                ]
            )
        )

    def feature_name(self) -> ColumnName:
        return additional_feature(
            self,
            self._feature_column_name(),
            self.display_name or f"Text Ends with [{self.suffix}] for {self.column_name}",
        )
