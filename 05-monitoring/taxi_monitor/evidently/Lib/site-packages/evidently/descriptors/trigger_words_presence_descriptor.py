from typing import List

from evidently.features import trigger_words_presence_feature
from evidently.features.generated_features import FeatureDescriptor
from evidently.features.generated_features import GeneratedFeature


class TriggerWordsPresence(FeatureDescriptor):
    words_list: List[str]
    lemmatize: bool = True

    def feature(self, column_name: str) -> GeneratedFeature:
        return trigger_words_presence_feature.TriggerWordsPresent(
            column_name,
            self.words_list,
            self.lemmatize,
            self.display_name,
        )

    def for_column(self, column_name: str):
        return trigger_words_presence_feature.TriggerWordsPresent(
            column_name,
            self.words_list,
            self.lemmatize,
            self.display_name,
        ).feature_name()
