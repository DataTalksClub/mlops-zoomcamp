from typing import List

from evidently.features.generated_features import GeneratedFeature
from evidently.features.generated_features import MultiColumnFeatureDescriptor
from evidently.features.semantic_similarity_feature import SemanticSimilarityFeature


class SemanticSimilarity(MultiColumnFeatureDescriptor):
    def feature(self, columns: List[str]) -> GeneratedFeature:
        return SemanticSimilarityFeature(columns=columns, display_name=self.display_name)
