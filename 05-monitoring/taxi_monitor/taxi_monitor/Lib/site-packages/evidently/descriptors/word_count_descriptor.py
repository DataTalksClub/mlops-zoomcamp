from evidently.features import word_count_feature
from evidently.features.generated_features import FeatureDescriptor
from evidently.features.generated_features import GeneratedFeature


class WordCount(FeatureDescriptor):
    def feature(self, column_name: str) -> GeneratedFeature:
        return word_count_feature.WordCount(column_name, self.display_name)

    def for_column(self, column_name: str):
        return word_count_feature.WordCount(column_name, self.display_name).feature_name()
