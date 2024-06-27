from typing import List

from evidently.features import words_feature
from evidently.features.generated_features import FeatureDescriptor
from evidently.features.generated_features import GeneratedFeature


class ExcludesWords(FeatureDescriptor):
    words_list: List[str]
    mode: str = "all"
    lemmatize: bool = True

    def feature(self, column_name: str) -> GeneratedFeature:
        return words_feature.ExcludesWords(
            column_name,
            self.words_list,
            self.mode,
            self.lemmatize,
            self.display_name,
        )


class IncludesWords(FeatureDescriptor):
    words_list: List[str]
    mode: str = "any"
    lemmatize: bool = True

    def feature(self, column_name: str) -> GeneratedFeature:
        return words_feature.IncludesWords(
            column_name,
            self.words_list,
            self.mode,
            self.lemmatize,
            self.display_name,
        )
