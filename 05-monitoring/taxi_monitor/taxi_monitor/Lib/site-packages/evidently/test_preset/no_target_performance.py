from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import numpy as np

from evidently.calculations.stattests import PossibleStatTestType
from evidently.metrics.data_drift.embedding_drift_methods import DriftMethod
from evidently.pipeline.column_mapping import TaskType
from evidently.test_preset.test_preset import TestPreset
from evidently.tests import TestAllColumnsShareOfMissingValues
from evidently.tests import TestCatColumnsOutOfListValues
from evidently.tests import TestColumnDrift
from evidently.tests import TestColumnsType
from evidently.tests import TestEmbeddingsDrift
from evidently.tests import TestNumColumnsMeanInNSigmas
from evidently.tests import TestNumColumnsOutOfRangeValues
from evidently.tests import TestShareOfDriftedColumns
from evidently.utils.data_drift_utils import add_emb_drift_to_reports
from evidently.utils.data_drift_utils import resolve_stattest_threshold
from evidently.utils.data_preprocessing import DataDefinition


class NoTargetPerformanceTestPreset(TestPreset):
    """
    No Target Performance tests.

    Args:
        columns: list of columns include to tests

    Contains tests:
    - `TestColumnValueDrift`
    - `TestShareOfDriftedColumns`
    - `TestColumnsType`
    - `TestAllColumnsShareOfMissingValues`
    - `TestNumColumnsOutOfRangeValues`
    - `TestCatColumnsOutOfListValues`
    - `TestNumColumnsMeanInNSigmas`
    - `TestCustomFeaturesValueDrift`
    - 'TestEmbeddingsDrift'
    """

    columns: Optional[List[str]]
    embeddings: Optional[List[str]]
    embeddings_drift_method: Optional[Dict[str, DriftMethod]]
    drift_share: Optional[float]
    stattest: Optional[PossibleStatTestType] = None
    cat_stattest: Optional[PossibleStatTestType] = None
    num_stattest: Optional[PossibleStatTestType] = None
    text_stattest: Optional[PossibleStatTestType] = None
    per_column_stattest: Optional[Dict[str, PossibleStatTestType]] = None
    stattest_threshold: Optional[float] = None
    cat_stattest_threshold: Optional[float] = None
    num_stattest_threshold: Optional[float] = None
    text_stattest_threshold: Optional[float] = None
    per_column_stattest_threshold: Optional[Dict[str, float]] = None

    def __init__(
        self,
        columns: Optional[List[str]] = None,
        embeddings: Optional[List[str]] = None,
        embeddings_drift_method: Optional[Dict[str, DriftMethod]] = None,
        drift_share: Optional[float] = None,
        stattest: Optional[PossibleStatTestType] = None,
        cat_stattest: Optional[PossibleStatTestType] = None,
        num_stattest: Optional[PossibleStatTestType] = None,
        text_stattest: Optional[PossibleStatTestType] = None,
        per_column_stattest: Optional[Dict[str, PossibleStatTestType]] = None,
        stattest_threshold: Optional[float] = None,
        cat_stattest_threshold: Optional[float] = None,
        num_stattest_threshold: Optional[float] = None,
        text_stattest_threshold: Optional[float] = None,
        per_column_stattest_threshold: Optional[Dict[str, float]] = None,
    ):
        super().__init__()
        self.columns = columns
        self.embeddings = embeddings
        self.embeddings_drift_method = embeddings_drift_method
        self.drift_share = drift_share
        self.stattest = stattest
        self.cat_stattest = cat_stattest
        self.num_stattest = num_stattest
        self.text_stattest = text_stattest
        self.per_column_stattest = per_column_stattest
        self.stattest_threshold = stattest_threshold
        self.cat_stattest_threshold = cat_stattest_threshold
        self.num_stattest_threshold = num_stattest_threshold
        self.text_stattest_threshold = text_stattest_threshold
        self.per_feature_threshold = per_column_stattest_threshold

    def generate_tests(self, data_definition: DataDefinition, additional_data: Optional[Dict[str, Any]]):
        embeddings_data = data_definition.embeddings
        if embeddings_data is not None:
            embs = list(set(v for values in embeddings_data.values() for v in values))
            if self.columns is None:
                self.columns = list(
                    np.setdiff1d(
                        [column.column_name for column in data_definition.get_columns(features_only=True)],
                        embs,
                    )
                )
            else:
                self.columns = list(np.setdiff1d(self.columns, embs))

        preset_tests: List = []

        prediction_columns = data_definition.get_prediction_columns()
        if prediction_columns is not None and prediction_columns.predicted_values is not None:
            stattest, threshold = resolve_stattest_threshold(
                prediction_columns.predicted_values.column_name,
                "cat" if data_definition.task == TaskType.CLASSIFICATION_TASK else "num",
                self.stattest,
                self.cat_stattest,
                self.num_stattest,
                self.text_stattest,
                self.per_column_stattest,
                self.stattest_threshold,
                self.cat_stattest_threshold,
                self.num_stattest_threshold,
                self.text_stattest_threshold,
                self.per_column_stattest_threshold,
            )
            preset_tests.append(
                TestColumnDrift(
                    column_name=prediction_columns.predicted_values.column_name,
                    stattest=stattest,
                    stattest_threshold=threshold,
                )
            )
        preset_tests.append(
            TestShareOfDriftedColumns(
                lt=0.3 if self.drift_share is None else self.drift_share,
                stattest=self.stattest,
                cat_stattest=self.cat_stattest,
                num_stattest=self.num_stattest,
                text_stattest=self.text_stattest,
                per_column_stattest=self.per_column_stattest,
                stattest_threshold=self.stattest_threshold,
                cat_stattest_threshold=self.cat_stattest_threshold,
                num_stattest_threshold=self.num_stattest_threshold,
                text_stattest_threshold=self.text_stattest_threshold,
                per_column_stattest_threshold=self.per_feature_threshold,
            )
        )
        preset_tests.append(TestColumnsType())
        preset_tests.append(TestAllColumnsShareOfMissingValues(columns=self.columns))
        preset_tests.append(TestNumColumnsOutOfRangeValues(columns=self.columns))
        preset_tests.append(TestCatColumnsOutOfListValues(columns=self.columns))
        preset_tests.append(TestNumColumnsMeanInNSigmas(columns=self.columns))

        if embeddings_data is None:
            return preset_tests
        preset_tests = add_emb_drift_to_reports(
            preset_tests,
            embeddings_data,
            self.embeddings,
            self.embeddings_drift_method,
            TestEmbeddingsDrift,
        )
        return preset_tests
