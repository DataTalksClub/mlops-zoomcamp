from abc import ABC
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import numpy as np
import pandas as pd

from evidently.base_metric import ColumnName
from evidently.calculations.data_drift import ColumnDataDriftMetrics
from evidently.calculations.stattests import PossibleStatTestType
from evidently.core import ColumnType
from evidently.metric_results import HistogramData
from evidently.metrics import ColumnDriftMetric
from evidently.metrics import DataDriftTable
from evidently.metrics import EmbeddingsDriftMetric
from evidently.metrics.data_drift.base import WithDriftOptionsFields
from evidently.metrics.data_drift.data_drift_table import DataDriftTableResults
from evidently.metrics.data_drift.embedding_drift_methods import DriftMethod
from evidently.model.widget import BaseWidgetInfo
from evidently.renderers.base_renderer import DetailsInfo
from evidently.renderers.base_renderer import TestHtmlInfo
from evidently.renderers.base_renderer import TestRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import plotly_figure
from evidently.renderers.html_widgets import table_data
from evidently.tests.base_test import BaseCheckValueTest
from evidently.tests.base_test import ConditionTestParameters
from evidently.tests.base_test import ExcludeNoneMixin
from evidently.tests.base_test import GroupData
from evidently.tests.base_test import GroupingTypes
from evidently.tests.base_test import Test
from evidently.tests.base_test import TestParameters
from evidently.tests.base_test import TestResult
from evidently.tests.base_test import TestStatus
from evidently.tests.base_test import TestValueCondition
from evidently.utils.data_drift_utils import resolve_stattest_threshold
from evidently.utils.data_preprocessing import DataDefinition
from evidently.utils.generators import BaseGenerator
from evidently.utils.types import Numeric
from evidently.utils.visualizations import plot_contour_single
from evidently.utils.visualizations import plot_distr_with_cond_perc_button

DATA_DRIFT_GROUP = GroupData("data_drift", "Data Drift", "")
GroupingTypes.TestGroup.add_value(DATA_DRIFT_GROUP)


class ColumnDriftParameter(ExcludeNoneMixin, TestParameters):  # type: ignore[misc] # pydantic Config
    stattest: str
    score: float
    threshold: float
    detected: bool
    column_name: Optional[str] = None

    @classmethod
    def from_metric(cls, data: ColumnDataDriftMetrics, column_name: str = None):
        return ColumnDriftParameter(
            stattest=data.stattest_name,
            score=np.round(data.drift_score, 3),
            threshold=data.stattest_threshold,
            detected=data.drift_detected,
            column_name=column_name,
        )


class ColumnsDriftParameters(ConditionTestParameters):
    # todo: rename to columns?
    features: Dict[str, ColumnDriftParameter]

    @classmethod
    def from_data_drift_table(cls, table: DataDriftTableResults, condition: TestValueCondition):
        return ColumnsDriftParameters(
            features={
                feature: ColumnDriftParameter.from_metric(data) for feature, data in table.drift_by_columns.items()
            },
            condition=condition,
        )

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "Feature name": feature,
                    "Stattest": data.stattest,
                    "Drift score": data.score,
                    "Threshold": data.threshold,
                    "Data Drift": "Detected" if data.detected else "Not detected",
                }
                for feature, data in self.features.items()
            ],
        )


class BaseDataDriftMetricsTest(BaseCheckValueTest, WithDriftOptionsFields, ABC):
    group: ClassVar = DATA_DRIFT_GROUP.id
    _metric: DataDriftTable
    columns: Optional[List[str]]
    feature_importance: Optional[bool]

    def __init__(
        self,
        columns: Optional[List[str]] = None,
        eq: Optional[Numeric] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
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
        is_critical: bool = True,
        feature_importance: Optional[bool] = False,
    ):
        super().__init__(
            eq=eq,
            gt=gt,
            gte=gte,
            is_in=is_in,
            lt=lt,
            lte=lte,
            not_eq=not_eq,
            not_in=not_in,
            is_critical=is_critical,
            columns=columns,
            stattest=stattest,
            cat_stattest=cat_stattest,
            num_stattest=num_stattest,
            text_stattest=text_stattest,
            per_column_stattest=per_column_stattest,
            stattest_threshold=stattest_threshold,
            cat_stattest_threshold=cat_stattest_threshold,
            num_stattest_threshold=num_stattest_threshold,
            text_stattest_threshold=text_stattest_threshold,
            per_column_stattest_threshold=per_column_stattest_threshold,
            feature_importance=feature_importance,
        )
        self._metric = DataDriftTable(
            columns=self.columns,
            stattest=self.stattest,
            cat_stattest=self.cat_stattest,
            num_stattest=self.num_stattest,
            text_stattest=self.text_stattest,
            per_column_stattest=self.per_column_stattest,
            stattest_threshold=self.stattest_threshold,
            cat_stattest_threshold=self.cat_stattest_threshold,
            num_stattest_threshold=self.num_stattest_threshold,
            text_stattest_threshold=self.text_stattest_threshold,
            per_column_stattest_threshold=self.per_column_stattest_threshold,
            feature_importance=self.feature_importance,
        )

    @property
    def metric(self):
        return self._metric

    def check(self):
        result = super().check()
        metrics = self.metric.get_result()

        return TestResult(
            name=result.name,
            description=result.description,
            status=TestStatus(result.status),
            group=self.group,
            parameters=ColumnsDriftParameters.from_data_drift_table(metrics, self.get_condition()),
        )


class TestNumberOfDriftedColumns(BaseDataDriftMetricsTest):
    name: ClassVar = "Number of Drifted Features"

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition
        else:
            return TestValueCondition(lt=max(0, self.metric.get_result().number_of_columns // 3))

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().number_of_drifted_columns

    def get_description(self, value: Numeric) -> str:
        n_features = self.metric.get_result().number_of_columns
        return (
            f"The drift is detected for {value} out of {n_features} features. "
            f"The test threshold is {self.get_condition()}."
        )


class TestShareOfDriftedColumns(BaseDataDriftMetricsTest):
    name: ClassVar = "Share of Drifted Columns"

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition
        else:
            return TestValueCondition(lt=0.3)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().share_of_drifted_columns

    def get_description(self, value: Numeric) -> str:
        n_drifted_features = self.metric.get_result().number_of_drifted_columns
        n_features = self.metric.get_result().number_of_columns
        return (
            f"The drift is detected for {value * 100:.3g}% features "
            f"({n_drifted_features} out of {n_features}). The test threshold is {self.get_condition()}"
        )


class TestColumnDrift(Test):
    name: ClassVar = "Drift per Column"
    group: ClassVar = DATA_DRIFT_GROUP.id
    _metric: ColumnDriftMetric
    column_name: ColumnName
    stattest: Optional[PossibleStatTestType] = None
    stattest_threshold: Optional[float] = None

    def __init__(
        self,
        column_name: Union[str, ColumnName],
        stattest: Optional[PossibleStatTestType] = None,
        stattest_threshold: Optional[float] = None,
        is_critical: bool = True,
    ):
        self.column_name = ColumnName.from_any(column_name)
        self.stattest = stattest
        self.stattest_threshold = stattest_threshold

        super().__init__(is_critical=is_critical)
        self._metric = ColumnDriftMetric(
            column_name=self.column_name,
            stattest=self.stattest,
            stattest_threshold=self.stattest_threshold,
        )

    @property
    def metric(self):
        return self._metric

    def check(self):
        drift_info = self.metric.get_result()

        p_value = np.round(drift_info.drift_score, 3)
        stattest_name = drift_info.stattest_name
        threshold = drift_info.stattest_threshold
        description = (
            f"The drift score for the feature **{self.column_name.display_name}** is {p_value:.3g}. "
            f"The drift detection method is {stattest_name}. "
            f"The drift detection threshold is {threshold}."
        )

        if not drift_info.drift_detected:
            result_status = TestStatus.SUCCESS

        else:
            result_status = TestStatus.FAIL

        return TestResult(
            name=self.name,
            description=description,
            status=result_status,
            group=self.group,
            parameters=ColumnDriftParameter.from_metric(drift_info, column_name=self.column_name.display_name),
        )

    def groups(self) -> Dict[str, str]:
        return {
            GroupingTypes.ByFeature.id: self.column_name.display_name,
        }


class TestAllFeaturesValueDrift(BaseGenerator):
    """Create value drift tests for numeric and category features"""

    columns: Optional[List[str]]
    stattest: Optional[PossibleStatTestType]
    cat_stattest: Optional[PossibleStatTestType]
    num_stattest: Optional[PossibleStatTestType]
    text_stattest: Optional[PossibleStatTestType]
    per_column_stattest: Optional[Dict[str, PossibleStatTestType]]
    stattest_threshold: Optional[float]
    cat_stattest_threshold: Optional[float]
    num_stattest_threshold: Optional[float]
    text_stattest_threshold: Optional[float]
    per_column_stattest_threshold: Optional[Dict[str, float]]

    def __init__(
        self,
        columns: Optional[List[str]] = None,
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
        is_critical: bool = True,
    ):
        self.is_critical = is_critical
        self.columns = columns
        self.stattest = stattest
        self.cat_stattest = cat_stattest
        self.num_stattest = num_stattest
        self.text_stattest = text_stattest
        self.per_column_stattest = per_column_stattest
        self.stattest_threshold = stattest_threshold
        self.cat_stattest_threshold = cat_stattest_threshold
        self.num_stattest_threshold = num_stattest_threshold
        self.text_stattest_threshold = text_stattest_threshold
        self.per_column_stattest_threshold = per_column_stattest_threshold

    def generate(self, data_definition: DataDefinition) -> List[TestColumnDrift]:
        results = []
        for column in data_definition.get_columns(ColumnType.Categorical, features_only=True):
            if self.columns and column.column_name not in self.columns:
                continue
            stattest, threshold = resolve_stattest_threshold(
                column.column_name,
                "cat",
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
            results.append(
                TestColumnDrift(
                    column_name=column.column_name,
                    stattest=stattest,
                    stattest_threshold=threshold,
                    is_critical=self.is_critical,
                )
            )
        for column in data_definition.get_columns(ColumnType.Numerical, features_only=True):
            if self.columns and column.column_name not in self.columns:
                continue
            stattest, threshold = resolve_stattest_threshold(
                column.column_name,
                "num",
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
            results.append(
                TestColumnDrift(
                    column_name=column.column_name,
                    stattest=stattest,
                    stattest_threshold=threshold,
                    is_critical=self.is_critical,
                )
            )
        for column in data_definition.get_columns(ColumnType.Text, features_only=True):
            if self.columns and column.column_name not in self.columns:
                continue
            stattest, threshold = resolve_stattest_threshold(
                column.column_name,
                "text",
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
            results.append(
                TestColumnDrift(
                    column_name=column.column_name,
                    stattest=stattest,
                    stattest_threshold=threshold,
                    is_critical=self.is_critical,
                )
            )
        return results


class TestCustomFeaturesValueDrift(BaseGenerator):
    """Create value drift tests for specified features"""

    features: List[str]
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
        features: List[str],
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
        is_critical: bool = True,
    ):
        self.is_critical = is_critical
        self.features = features
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

    def generate(self, data_definition: DataDefinition) -> List[TestColumnDrift]:
        result = []
        for name in self.features:
            column = data_definition.get_column(name)
            stattest, threshold = resolve_stattest_threshold(
                name,
                "cat"
                if column.column_type == ColumnType.Categorical
                else "num"
                if column.column_type == ColumnType.Numerical
                else "text"
                if column.column_type == ColumnType.Text
                else "datetime",
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
            result.append(
                TestColumnDrift(
                    column_name=name,
                    stattest=stattest,
                    stattest_threshold=threshold,
                    is_critical=self.is_critical,
                )
            )
        return result


@default_renderer(wrap_type=TestNumberOfDriftedColumns)
class TestNumberOfDriftedColumnsRenderer(TestRenderer):
    def render_html(self, obj: TestNumberOfDriftedColumns) -> TestHtmlInfo:
        info = super().render_html(obj)
        result = obj.get_result()
        if result.status == TestStatus.ERROR:
            return info
        parameters = result.parameters
        assert isinstance(parameters, ColumnsDriftParameters)
        df = parameters.to_dataframe()
        df = df.sort_values("Data Drift")
        columns = ["Feature name"]
        current_fi = obj.metric.get_result().current_fi
        reference_fi = obj.metric.get_result().reference_fi
        if current_fi is not None:
            df["current_feature_importance"] = df["Feature name"].apply(lambda x: current_fi.get(x, ""))
            columns.append("current_feature_importance")
        if reference_fi is not None:
            df["reference_feature_importance"] = df["Feature name"].apply(lambda x: reference_fi.get(x, ""))
            columns.append("reference_feature_importance")
        columns += ["Stattest", "Drift score", "Threshold", "Data Drift"]
        df = df[columns]
        info.with_details(
            title="Drift Table",
            info=table_data(column_names=df.columns.to_list(), data=df.values),
        )
        return info


@default_renderer(wrap_type=TestShareOfDriftedColumns)
class TestShareOfDriftedColumnsRenderer(TestRenderer):
    def render_html(self, obj: TestShareOfDriftedColumns) -> TestHtmlInfo:
        info = super().render_html(obj)
        result = obj.get_result()
        if result.status == TestStatus.ERROR:
            return info
        parameters = result.parameters
        current_fi = obj.metric.get_result().current_fi
        reference_fi = obj.metric.get_result().reference_fi
        assert isinstance(parameters, ColumnsDriftParameters)
        df = parameters.to_dataframe()
        df = df.sort_values("Data Drift")
        columns = ["Feature name"]
        if current_fi is not None:
            df["current_feature_importance"] = df["Feature name"].apply(lambda x: current_fi.get(x, ""))
            columns.append("current_feature_importance")
        if reference_fi is not None:
            df["reference_feature_importance"] = df["Feature name"].apply(lambda x: reference_fi.get(x, ""))
            columns.append("reference_feature_importance")
        columns += ["Stattest", "Drift score", "Threshold", "Data Drift"]
        df = df[columns]
        info.details = [
            DetailsInfo(
                id="drift_table",
                title="",
                info=BaseWidgetInfo(
                    title="",
                    type="table",
                    params={"header": df.columns.to_list(), "data": df.values},
                    size=2,
                ),
            ),
        ]
        return info


@default_renderer(wrap_type=TestColumnDrift)
class TestColumnDriftRenderer(TestRenderer):
    def render_html(self, obj: TestColumnDrift) -> TestHtmlInfo:
        info = super().render_html(obj)
        result = obj.metric.get_result()
        column_name = obj.column_name
        if result.column_type == "text":
            if result.current.characteristic_words is not None and result.reference.characteristic_words is not None:
                info.details = [
                    DetailsInfo(
                        id=f"{column_name} dritf curr",
                        title="current: characteristic words",
                        info=BaseWidgetInfo(
                            title="",
                            type="table",
                            params={
                                "header": ["", ""],
                                "data": [[el, ""] for el in result.current.characteristic_words],
                            },
                            size=2,
                        ),
                    ),
                    DetailsInfo(
                        id=f"{column_name} dritf ref",
                        title="reference: characteristic words",
                        info=BaseWidgetInfo(
                            title="",
                            type="table",
                            params={
                                "header": ["", ""],
                                "data": [[el, ""] for el in result.reference.characteristic_words],
                            },
                            size=2,
                        ),
                    ),
                ]
            else:
                return info
        else:
            if result.current.distribution is None:
                raise ValueError("Expected data is missing")
            fig = plot_distr_with_cond_perc_button(
                hist_curr=HistogramData.from_distribution(result.current.distribution),
                hist_ref=HistogramData.from_distribution(result.reference.distribution),
                xaxis_name="",
                yaxis_name="count",
                yaxis_name_perc="percent",
                color_options=self.color_options,
                to_json=False,
                condition=None,
            )
            info.with_details(f"{column_name}", plotly_figure(title="", figure=fig))
        return info


class TestEmbeddingsDrift(Test):
    name: ClassVar = "Drift for embeddings"
    group: ClassVar = DATA_DRIFT_GROUP.id
    embeddings_name: str
    drift_method: Optional[DriftMethod]
    _metric: EmbeddingsDriftMetric

    def __init__(self, embeddings_name: str, drift_method: Optional[DriftMethod] = None, is_critical: bool = True):
        self.embeddings_name = embeddings_name
        self.drift_method = drift_method
        super().__init__(is_critical=is_critical)
        self._metric = EmbeddingsDriftMetric(embeddings_name=self.embeddings_name, drift_method=self.drift_method)

    @property
    def metric(self):
        return self._metric

    def check(self):
        drift_info = self.metric.get_result()
        drift_score = drift_info.drift_score
        if drift_info.drift_detected:
            drift = "detected"

        else:
            drift = "not detected"

        description = (
            f"Data drift {drift}. "
            f"The drift score for the embedding set **{drift_info.embeddings_name}** is {drift_score:.3g}. "
            f"The drift detection method is **{drift_info.method_name}**. "
        )
        if not drift_info.drift_detected:
            result_status = TestStatus.SUCCESS

        else:
            result_status = TestStatus.FAIL
        return TestResult(
            name=self.name,
            description=description,
            status=result_status,
            group=self.group,
        )

    def groups(self) -> Dict[str, str]:
        return {}


@default_renderer(wrap_type=TestEmbeddingsDrift)
class TestEmbeddingsDriftRenderer(TestRenderer):
    def render_html(self, obj: TestEmbeddingsDrift) -> TestHtmlInfo:
        info = super().render_html(obj)
        result = obj.metric.get_result()
        fig = plot_contour_single(result.current, result.reference, "component 1", "component 2")
        info.with_details(f"Drift in embeddings '{result.embeddings_name}'", plotly_figure(title="", figure=fig))
        return info
