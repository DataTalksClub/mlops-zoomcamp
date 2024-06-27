"""
Available metrics for Reports and Tests.
All metrics is grouped into modules.
For specific group see module documentation.
"""

from .classification_performance.class_balance_metric import ClassificationClassBalance
from .classification_performance.class_separation_metric import ClassificationClassSeparationPlot
from .classification_performance.classification_dummy_metric import ClassificationDummyMetric
from .classification_performance.classification_quality_metric import ClassificationQualityMetric
from .classification_performance.confusion_matrix_metric import ClassificationConfusionMatrix
from .classification_performance.lift_curve_metric import ClassificationLiftCurve
from .classification_performance.lift_table_metric import ClassificationLiftTable
from .classification_performance.pr_curve_metric import ClassificationPRCurve
from .classification_performance.pr_table_metric import ClassificationPRTable
from .classification_performance.probability_distribution_metric import ClassificationProbDistribution
from .classification_performance.quality_by_class_metric import ClassificationQualityByClass
from .classification_performance.quality_by_feature_table import ClassificationQualityByFeatureTable
from .classification_performance.roc_curve_metric import ClassificationRocCurve
from .data_drift.column_drift_metric import ColumnDriftMetric
from .data_drift.column_interaction_plot import ColumnInteractionPlot
from .data_drift.column_value_plot import ColumnValuePlot
from .data_drift.data_drift_table import DataDriftTable
from .data_drift.dataset_drift_metric import DatasetDriftMetric
from .data_drift.embeddings_drift import EmbeddingsDriftMetric
from .data_drift.target_by_features_table import TargetByFeaturesTable
from .data_drift.text_descriptors_drift_metric import TextDescriptorsDriftMetric
from .data_drift.text_metric import Comment
from .data_integrity.column_missing_values_metric import ColumnMissingValuesMetric
from .data_integrity.column_regexp_metric import ColumnRegExpMetric
from .data_integrity.column_summary_metric import ColumnSummaryMetric
from .data_integrity.dataset_missing_values_metric import DatasetMissingValuesMetric
from .data_integrity.dataset_summary_metric import DatasetSummaryMetric
from .data_quality.column_category_metric import ColumnCategoryMetric
from .data_quality.column_correlations_metric import ColumnCorrelationsMetric
from .data_quality.column_distribution_metric import ColumnDistributionMetric
from .data_quality.column_quantile_metric import ColumnQuantileMetric
from .data_quality.column_value_list_metric import ColumnValueListMetric
from .data_quality.column_value_range_metric import ColumnValueRangeMetric
from .data_quality.conflict_prediction_metric import ConflictPredictionMetric
from .data_quality.conflict_target_metric import ConflictTargetMetric
from .data_quality.dataset_correlations_metric import DatasetCorrelationsMetric
from .data_quality.stability_metric import DataQualityStabilityMetric
from .data_quality.text_descriptors_correlation_metric import TextDescriptorsCorrelationMetric
from .data_quality.text_descriptors_distribution import TextDescriptorsDistribution
from .recsys.diversity import DiversityMetric
from .recsys.f_beta_top_k import FBetaTopKMetric
from .recsys.hit_rate_k import HitRateKMetric
from .recsys.item_bias import ItemBiasMetric
from .recsys.map_k import MAPKMetric
from .recsys.mar_k import MARKMetric
from .recsys.mrr import MRRKMetric
from .recsys.ndcg_k import NDCGKMetric
from .recsys.novelty import NoveltyMetric
from .recsys.personalisation import PersonalizationMetric
from .recsys.popularity_bias import PopularityBias
from .recsys.precision_top_k import PrecisionTopKMetric
from .recsys.rec_examples import RecCasesTable
from .recsys.recall_top_k import RecallTopKMetric
from .recsys.scores_distribution import ScoreDistribution
from .recsys.serendipity import SerendipityMetric
from .recsys.user_bias import UserBiasMetric
from .regression_performance.abs_perc_error_in_time import RegressionAbsPercentageErrorPlot
from .regression_performance.error_bias_table import RegressionErrorBiasTable
from .regression_performance.error_distribution import RegressionErrorDistribution
from .regression_performance.error_in_time import RegressionErrorPlot
from .regression_performance.error_normality import RegressionErrorNormality
from .regression_performance.predicted_and_actual_in_time import RegressionPredictedVsActualPlot
from .regression_performance.predicted_vs_actual import RegressionPredictedVsActualScatter
from .regression_performance.regression_dummy_metric import RegressionDummyMetric
from .regression_performance.regression_performance_metrics import RegressionPerformanceMetrics
from .regression_performance.regression_quality import RegressionQualityMetric
from .regression_performance.top_error import RegressionTopErrorMetric

__all__ = [
    "ClassificationClassBalance",
    "ClassificationClassSeparationPlot",
    "ClassificationDummyMetric",
    "ClassificationQualityMetric",
    "ClassificationConfusionMatrix",
    "ClassificationPRCurve",
    "ClassificationPRTable",
    "ClassificationProbDistribution",
    "ClassificationQualityByClass",
    "ClassificationQualityByFeatureTable",
    "ClassificationRocCurve",
    "ClassificationLiftCurve",
    "ClassificationLiftTable",
    "ColumnDriftMetric",
    "ColumnValuePlot",
    "DataDriftTable",
    "DatasetDriftMetric",
    "EmbeddingsDriftMetric",
    "TargetByFeaturesTable",
    "TextDescriptorsDriftMetric",
    "ColumnMissingValuesMetric",
    "ColumnRegExpMetric",
    "ColumnSummaryMetric",
    "DatasetMissingValuesMetric",
    "DatasetSummaryMetric",
    "ColumnCategoryMetric",
    "ColumnCorrelationsMetric",
    "ColumnDistributionMetric",
    "ColumnInteractionPlot",
    "ColumnQuantileMetric",
    "ColumnValueListMetric",
    "ColumnValueRangeMetric",
    "Comment",
    "ConflictPredictionMetric",
    "ConflictTargetMetric",
    "DatasetCorrelationsMetric",
    "DataQualityStabilityMetric",
    "TextDescriptorsCorrelationMetric",
    "TextDescriptorsDistribution",
    "RegressionAbsPercentageErrorPlot",
    "RegressionErrorBiasTable",
    "RegressionErrorDistribution",
    "RegressionErrorPlot",
    "RegressionErrorNormality",
    "RegressionPredictedVsActualPlot",
    "RegressionPredictedVsActualScatter",
    "RegressionDummyMetric",
    "RegressionPerformanceMetrics",
    "RegressionQualityMetric",
    "RegressionTopErrorMetric",
    "PrecisionTopKMetric",
    "RecallTopKMetric",
    "FBetaTopKMetric",
    "MAPKMetric",
    "MARKMetric",
    "NDCGKMetric",
    "DiversityMetric",
    "PersonalizationMetric",
    "NoveltyMetric",
    "PopularityBias",
    "UserBiasMetric",
    "ItemBiasMetric",
    "SerendipityMetric",
    "HitRateKMetric",
    "ScoreDistribution",
    "MRRKMetric",
    "RecCasesTable",
]
