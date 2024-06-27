"""Available tests for TestSuite reports.
Tests grouped into modules.
For detailed information see module documentation.
"""

from .classification_performance_tests import TestAccuracyScore
from .classification_performance_tests import TestF1ByClass
from .classification_performance_tests import TestF1Score
from .classification_performance_tests import TestFNR
from .classification_performance_tests import TestFPR
from .classification_performance_tests import TestLogLoss
from .classification_performance_tests import TestPrecisionByClass
from .classification_performance_tests import TestPrecisionScore
from .classification_performance_tests import TestRecallByClass
from .classification_performance_tests import TestRecallScore
from .classification_performance_tests import TestRocAuc
from .classification_performance_tests import TestTNR
from .classification_performance_tests import TestTPR
from .data_drift_tests import TestAllFeaturesValueDrift
from .data_drift_tests import TestColumnDrift
from .data_drift_tests import TestCustomFeaturesValueDrift
from .data_drift_tests import TestEmbeddingsDrift
from .data_drift_tests import TestNumberOfDriftedColumns
from .data_drift_tests import TestShareOfDriftedColumns
from .data_integrity_tests import TestAllColumnsShareOfMissingValues
from .data_integrity_tests import TestColumnAllConstantValues
from .data_integrity_tests import TestColumnAllUniqueValues
from .data_integrity_tests import TestColumnNumberOfDifferentMissingValues
from .data_integrity_tests import TestColumnNumberOfMissingValues
from .data_integrity_tests import TestColumnRegExp
from .data_integrity_tests import TestColumnShareOfMissingValues
from .data_integrity_tests import TestColumnsType
from .data_integrity_tests import TestNumberOfColumns
from .data_integrity_tests import TestNumberOfColumnsWithMissingValues
from .data_integrity_tests import TestNumberOfConstantColumns
from .data_integrity_tests import TestNumberOfDifferentMissingValues
from .data_integrity_tests import TestNumberOfDuplicatedColumns
from .data_integrity_tests import TestNumberOfDuplicatedRows
from .data_integrity_tests import TestNumberOfEmptyColumns
from .data_integrity_tests import TestNumberOfEmptyRows
from .data_integrity_tests import TestNumberOfMissingValues
from .data_integrity_tests import TestNumberOfRows
from .data_integrity_tests import TestNumberOfRowsWithMissingValues
from .data_integrity_tests import TestShareOfColumnsWithMissingValues
from .data_integrity_tests import TestShareOfMissingValues
from .data_integrity_tests import TestShareOfRowsWithMissingValues
from .data_quality_tests import TestAllColumnsMostCommonValueShare
from .data_quality_tests import TestCatColumnsOutOfListValues
from .data_quality_tests import TestCategoryCount
from .data_quality_tests import TestCategoryShare
from .data_quality_tests import TestColumnQuantile
from .data_quality_tests import TestColumnValueMax
from .data_quality_tests import TestColumnValueMean
from .data_quality_tests import TestColumnValueMedian
from .data_quality_tests import TestColumnValueMin
from .data_quality_tests import TestColumnValueStd
from .data_quality_tests import TestConflictPrediction
from .data_quality_tests import TestConflictTarget
from .data_quality_tests import TestCorrelationChanges
from .data_quality_tests import TestHighlyCorrelatedColumns
from .data_quality_tests import TestMeanInNSigmas
from .data_quality_tests import TestMostCommonValueShare
from .data_quality_tests import TestNumberOfOutListValues
from .data_quality_tests import TestNumberOfOutRangeValues
from .data_quality_tests import TestNumberOfUniqueValues
from .data_quality_tests import TestNumColumnsMeanInNSigmas
from .data_quality_tests import TestNumColumnsOutOfRangeValues
from .data_quality_tests import TestPredictionFeaturesCorrelations
from .data_quality_tests import TestShareOfOutListValues
from .data_quality_tests import TestShareOfOutRangeValues
from .data_quality_tests import TestTargetFeaturesCorrelations
from .data_quality_tests import TestTargetPredictionCorrelation
from .data_quality_tests import TestUniqueValuesShare
from .data_quality_tests import TestValueList
from .data_quality_tests import TestValueRange
from .recsys_tests import TestARP
from .recsys_tests import TestCoverage
from .recsys_tests import TestDiversity
from .recsys_tests import TestFBetaTopK
from .recsys_tests import TestGiniIndex
from .recsys_tests import TestHitRateK
from .recsys_tests import TestMAPK
from .recsys_tests import TestMARK
from .recsys_tests import TestMRRK
from .recsys_tests import TestNDCGK
from .recsys_tests import TestNovelty
from .recsys_tests import TestPersonalization
from .recsys_tests import TestPrecisionTopK
from .recsys_tests import TestRecallTopK
from .recsys_tests import TestScoreEntropy
from .recsys_tests import TestSerendipity
from .regression_performance_tests import TestValueAbsMaxError
from .regression_performance_tests import TestValueMAE
from .regression_performance_tests import TestValueMAPE
from .regression_performance_tests import TestValueMeanError
from .regression_performance_tests import TestValueR2Score
from .regression_performance_tests import TestValueRMSE

__all__ = [
    "TestAccuracyScore",
    "TestF1ByClass",
    "TestF1Score",
    "TestFNR",
    "TestFPR",
    "TestLogLoss",
    "TestPrecisionByClass",
    "TestPrecisionScore",
    "TestRecallByClass",
    "TestRecallScore",
    "TestRocAuc",
    "TestTNR",
    "TestTPR",
    "TestAllFeaturesValueDrift",
    "TestCategoryCount",
    "TestCategoryShare",
    "TestColumnDrift",
    "TestCustomFeaturesValueDrift",
    "TestEmbeddingsDrift",
    "TestNumberOfDriftedColumns",
    "TestShareOfDriftedColumns",
    "TestAllColumnsShareOfMissingValues",
    "TestColumnAllConstantValues",
    "TestColumnAllUniqueValues",
    "TestColumnNumberOfDifferentMissingValues",
    "TestColumnNumberOfMissingValues",
    "TestColumnRegExp",
    "TestColumnShareOfMissingValues",
    "TestColumnsType",
    "TestNumberOfColumns",
    "TestNumberOfColumnsWithMissingValues",
    "TestNumberOfConstantColumns",
    "TestNumberOfDifferentMissingValues",
    "TestNumberOfDuplicatedColumns",
    "TestNumberOfDuplicatedRows",
    "TestNumberOfEmptyColumns",
    "TestNumberOfEmptyRows",
    "TestNumberOfMissingValues",
    "TestNumberOfRows",
    "TestNumberOfRowsWithMissingValues",
    "TestShareOfColumnsWithMissingValues",
    "TestShareOfMissingValues",
    "TestShareOfRowsWithMissingValues",
    "TestAllColumnsMostCommonValueShare",
    "TestCatColumnsOutOfListValues",
    "TestColumnQuantile",
    "TestColumnValueMax",
    "TestColumnValueMean",
    "TestColumnValueMedian",
    "TestColumnValueMin",
    "TestColumnValueStd",
    "TestConflictPrediction",
    "TestConflictTarget",
    "TestCorrelationChanges",
    "TestHighlyCorrelatedColumns",
    "TestMeanInNSigmas",
    "TestMostCommonValueShare",
    "TestNumberOfOutListValues",
    "TestNumberOfOutRangeValues",
    "TestNumberOfUniqueValues",
    "TestNumColumnsMeanInNSigmas",
    "TestNumColumnsOutOfRangeValues",
    "TestPredictionFeaturesCorrelations",
    "TestShareOfOutListValues",
    "TestShareOfOutRangeValues",
    "TestTargetFeaturesCorrelations",
    "TestTargetPredictionCorrelation",
    "TestUniqueValuesShare",
    "TestValueList",
    "TestValueRange",
    "TestValueAbsMaxError",
    "TestValueMAE",
    "TestValueMAPE",
    "TestValueMeanError",
    "TestValueR2Score",
    "TestValueRMSE",
    "TestFBetaTopK",
    "TestHitRateK",
    "TestMAPK",
    "TestMRRK",
    "TestMARK",
    "TestNDCGK",
    "TestPrecisionTopK",
    "TestRecallTopK",
    "TestNovelty",
    "TestPersonalization",
    "TestSerendipity",
    "TestDiversity",
    "TestARP",
    "TestGiniIndex",
    "TestCoverage",
    "TestScoreEntropy",
]
