from evidently.features import non_letter_character_percentage_feature
from evidently.features.generated_features import FeatureDescriptor
from evidently.features.generated_features import GeneratedFeature


class NonLetterCharacterPercentage(FeatureDescriptor):
    def feature(self, column_name: str) -> GeneratedFeature:
        return non_letter_character_percentage_feature.NonLetterCharacterPercentage(column_name, self.display_name)

    def for_column(self, column_name: str):
        return non_letter_character_percentage_feature.NonLetterCharacterPercentage(
            column_name,
            self.display_name,
        ).feature_name()
