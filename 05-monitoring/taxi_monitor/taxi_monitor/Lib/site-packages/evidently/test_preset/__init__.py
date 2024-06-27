"""Predefined Test Presets for Test Suite"""

from .classification_binary import BinaryClassificationTestPreset
from .classification_binary_topk import BinaryClassificationTopKTestPreset
from .classification_multiclass import MulticlassClassificationTestPreset
from .data_drift import DataDriftTestPreset
from .data_quality import DataQualityTestPreset
from .data_stability import DataStabilityTestPreset
from .no_target_performance import NoTargetPerformanceTestPreset
from .recsys import RecsysTestPreset
from .regression import RegressionTestPreset

__all__ = [
    "BinaryClassificationTestPreset",
    "BinaryClassificationTopKTestPreset",
    "MulticlassClassificationTestPreset",
    "DataDriftTestPreset",
    "DataQualityTestPreset",
    "DataStabilityTestPreset",
    "NoTargetPerformanceTestPreset",
    "RegressionTestPreset",
    "RecsysTestPreset",
]
