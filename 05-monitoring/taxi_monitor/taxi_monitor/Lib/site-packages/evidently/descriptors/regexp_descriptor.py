from evidently.features import regexp_feature
from evidently.features.generated_features import FeatureDescriptor
from evidently.features.generated_features import GeneratedFeature


class RegExp(FeatureDescriptor):
    reg_exp: str

    def feature(self, column_name: str) -> GeneratedFeature:
        return regexp_feature.RegExp(column_name, self.reg_exp, self.display_name)

    def for_column(self, column_name: str):
        return regexp_feature.RegExp(column_name, self.reg_exp, self.display_name).feature_name()
