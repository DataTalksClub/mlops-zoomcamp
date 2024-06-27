from typing import List

from evidently.features import text_contains_feature
from evidently.features.generated_features import FeatureDescriptor
from evidently.features.generated_features import GeneratedFeature


class Contains(FeatureDescriptor):
    items: List[str]
    mode: str = "any"
    case_sensitive: bool = True

    def feature(self, column_name: str) -> GeneratedFeature:
        return text_contains_feature.Contains(
            column_name,
            self.items,
            self.case_sensitive,
            self.mode,
            self.display_name,
        )

    def for_column(self, column_name: str):
        return text_contains_feature.Contains(
            column_name,
            self.items,
            self.case_sensitive,
            self.mode,
            self.display_name,
        ).feature_name()


class DoesNotContain(FeatureDescriptor):
    items: List[str]
    mode: str = "all"
    case_sensitive: bool = True

    def feature(self, column_name: str) -> GeneratedFeature:
        return text_contains_feature.DoesNotContain(
            column_name,
            self.items,
            self.case_sensitive,
            self.mode,
            self.display_name,
        )

    def for_column(self, column_name: str):
        return text_contains_feature.DoesNotContain(
            column_name,
            self.items,
            self.case_sensitive,
            self.mode,
            self.display_name,
        ).feature_name()
