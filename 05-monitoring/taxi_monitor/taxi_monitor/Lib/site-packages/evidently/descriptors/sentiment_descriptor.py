from evidently.features import sentiment_feature
from evidently.features.generated_features import FeatureDescriptor
from evidently.features.generated_features import GeneratedFeature


class Sentiment(FeatureDescriptor):
    def feature(self, column_name: str) -> GeneratedFeature:
        return sentiment_feature.Sentiment(column_name, self.display_name)

    def for_column(self, column_name: str):
        return sentiment_feature.Sentiment(column_name, self.display_name).feature_name()
