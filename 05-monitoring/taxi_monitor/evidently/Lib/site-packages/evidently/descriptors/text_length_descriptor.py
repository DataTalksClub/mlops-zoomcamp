from evidently.features import text_length_feature
from evidently.features.generated_features import FeatureDescriptor
from evidently.features.generated_features import GeneratedFeature


class TextLength(FeatureDescriptor):
    def feature(self, column_name: str) -> GeneratedFeature:
        return text_length_feature.TextLength(column_name, self.display_name)

    def for_column(self, column_name: str):
        return text_length_feature.TextLength(column_name, self.display_name).feature_name()
