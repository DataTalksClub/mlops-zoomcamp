from abc import ABC
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pandas as pd

from evidently.base_metric import ColumnName
from evidently.calculations.data_quality import get_corr_method
from evidently.core import ColumnType
from evidently.metric_results import HistogramData
from evidently.metrics import ColumnCategoryMetric
from evidently.metrics import ColumnQuantileMetric
from evidently.metrics import ColumnSummaryMetric
from evidently.metrics import ColumnValueListMetric
from evidently.metrics import ColumnValueRangeMetric
from evidently.metrics import ConflictPredictionMetric
from evidently.metrics import ConflictTargetMetric
from evidently.metrics import DatasetCorrelationsMetric
from evidently.metrics.data_integrity.column_summary_metric import CategoricalCharacteristics
from evidently.metrics.data_integrity.column_summary_metric import ColumnCharacteristics
from evidently.metrics.data_integrity.column_summary_metric import ColumnSummaryResult
from evidently.metrics.data_integrity.column_summary_metric import DatetimeCharacteristics
from evidently.metrics.data_integrity.column_summary_metric import NumericCharacteristics
from evidently.metrics.data_integrity.column_summary_metric import TextCharacteristics
from evidently.metrics.data_quality.column_category_metric import CategoryStat
from evidently.metrics.data_quality.dataset_correlations_metric import DatasetCorrelation
from evidently.model.widget import BaseWidgetInfo
from evidently.renderers.base_renderer import DetailsInfo
from evidently.renderers.base_renderer import TestHtmlInfo
from evidently.renderers.base_renderer import TestRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import plotly_figure
from evidently.tests.base_test import BaseCheckValueTest
from evidently.tests.base_test import CheckValueParameters
from evidently.tests.base_test import ColumnCheckValueParameters
from evidently.tests.base_test import ConditionFromReferenceMixin
from evidently.tests.base_test import GroupData
from evidently.tests.base_test import GroupingTypes
from evidently.tests.base_test import Test
from evidently.tests.base_test import TestParameters
from evidently.tests.base_test import TestResult
from evidently.tests.base_test import TestStatus
from evidently.tests.base_test import TestValueCondition
from evidently.tests.utils import approx
from evidently.tests.utils import plot_correlations
from evidently.tests.utils import plot_value_counts_tables
from evidently.tests.utils import plot_value_counts_tables_ref_curr
from evidently.utils.data_preprocessing import DataDefinition
from evidently.utils.generators import BaseGenerator
from evidently.utils.types import Numeric
from evidently.utils.visualizations import plot_distr_with_cond_perc_button

DATA_QUALITY_GROUP = GroupData("data_quality", "Data Quality", "")
GroupingTypes.TestGroup.add_value(DATA_QUALITY_GROUP)


class BaseDataQualityMetricsValueTest(ConditionFromReferenceMixin[ColumnCharacteristics], ABC):
    reference_field: ClassVar = "reference_characteristics"
    group: ClassVar = DATA_QUALITY_GROUP.id
    _metric: ColumnSummaryMetric
    column_name: ColumnName

    def __init__(
        self,
        column_name: Union[str, ColumnName],
        eq: Optional[Numeric] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
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
            column_name=ColumnName.from_any(column_name),
            is_critical=is_critical,
        )
        self._metric = ColumnSummaryMetric(self.column_name)


class TestConflictTarget(Test):
    group: ClassVar = DATA_QUALITY_GROUP.id
    name: ClassVar = "Test number of conflicts in target"
    _metric: ConflictTargetMetric

    def __init__(self, is_critical: bool = True):
        self._metric = ConflictTargetMetric()
        super().__init__(is_critical=is_critical)

    @property
    def metric(self):
        return self._metric

    def check(self):
        metric_result = self.metric.get_result()

        if metric_result.number_not_stable_target is None:
            test_result = TestStatus.ERROR
            description = "No target in the dataset"

        elif metric_result.number_not_stable_target > 0:
            test_result = TestStatus.FAIL
            description = f"Not stable target rows count is {metric_result.number_not_stable_target}"

        else:
            test_result = TestStatus.SUCCESS
            description = "Target is stable"

        return TestResult(name=self.name, description=description, status=test_result, group=self.group)

    def groups(self) -> Dict[str, str]:
        return {}


class TestConflictPrediction(Test):
    group: ClassVar = DATA_QUALITY_GROUP.id
    name: ClassVar = "Test number of conflicts in prediction"
    _metric: ConflictPredictionMetric

    def __init__(self, is_critical: bool = True):
        self._metric = ConflictPredictionMetric()
        super().__init__(is_critical=is_critical)

    @property
    def metric(self):
        return self._metric

    def check(self):
        metric_result = self.metric.get_result()

        if metric_result.current.number_not_stable_prediction is None:
            test_result = TestStatus.ERROR
            description = "No prediction in the dataset"

        elif metric_result.current.number_not_stable_prediction > 0:
            test_result = TestStatus.FAIL
            description = f"Not stable prediction rows count is {metric_result.current.number_not_stable_prediction}"

        else:
            test_result = TestStatus.SUCCESS
            description = "Prediction is stable"

        return TestResult(name=self.name, description=description, status=test_result, group=self.group)

    def groups(self) -> Dict[str, str]:
        return {}


class BaseDataQualityCorrelationsMetricsValueTest(ConditionFromReferenceMixin[DatasetCorrelation], ABC):
    group: ClassVar = DATA_QUALITY_GROUP.id
    _metric: DatasetCorrelationsMetric
    method: Optional[str]

    def __init__(
        self,
        method: Optional[str] = None,
        eq: Optional[Numeric] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
    ):
        self.method = method
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
        )
        self._metric = DatasetCorrelationsMetric()


class TestTargetPredictionCorrelation(BaseDataQualityCorrelationsMetricsValueTest):
    name: ClassVar = "Correlation between Target and Prediction"

    def get_condition_from_reference(self, reference: Optional[DatasetCorrelation]) -> TestValueCondition:
        if reference is not None:
            method = get_corr_method(self.method, self.metric.get_result().target_correlation, False)
            value = reference.stats[method].target_prediction_correlation

            if value is not None:
                return TestValueCondition(eq=approx(value, absolute=0.25))

        return TestValueCondition(gt=0)

    def calculate_value_for_test(self) -> Optional[Numeric]:
        method = get_corr_method(self.method, self.metric.get_result().target_correlation, False)
        return self.metric.get_result().current.stats[method].target_prediction_correlation

    def get_description(self, value: Numeric) -> str:
        if value is None:
            return "No target or prediction in the dataset."
        return (
            f"The correlation between the target and prediction is {value:.3}. "
            f"The test threshold is {self.get_condition()}."
        )


class TestHighlyCorrelatedColumns(BaseDataQualityCorrelationsMetricsValueTest):
    name: ClassVar = "Highly Correlated Columns"

    def get_condition_from_reference(self, reference: Optional[DatasetCorrelation]) -> TestValueCondition:
        if reference is not None:
            value = reference.stats[get_corr_method(self.method)].abs_max_features_correlation

            if value is not None:
                return TestValueCondition(eq=approx(value, relative=0.1))

        return TestValueCondition(lt=0.9)

    def calculate_value_for_test(self) -> Optional[Numeric]:
        return self.metric.get_result().current.stats[get_corr_method(self.method)].abs_max_features_correlation

    def get_description(self, value: Numeric) -> str:
        return f"The maximum correlation is {value:.3g}. The test threshold is {self.get_condition()}."


@default_renderer(wrap_type=TestHighlyCorrelatedColumns)
class TestHighlyCorrelatedColumnsRenderer(TestRenderer):
    def render_html(self, obj: TestHighlyCorrelatedColumns) -> TestHtmlInfo:
        info = super().render_html(obj)
        metric_result = obj.metric.get_result()
        method = get_corr_method(obj.method)
        current_correlations = metric_result.current.correlation[method]

        if metric_result.reference is not None:
            reference_correlations: Optional[pd.DataFrame] = metric_result.reference.correlation[method]

        else:
            reference_correlations = None

        fig = plot_correlations(current_correlations, reference_correlations)
        info.with_details("Highly Correlated Features", plotly_figure(title="", figure=fig))
        return info


class TestTargetFeaturesCorrelations(BaseDataQualityCorrelationsMetricsValueTest):
    name: ClassVar = "Correlation between Target and Features"

    def get_condition_from_reference(self, reference: Optional[DatasetCorrelation]) -> TestValueCondition:
        if reference is not None:
            method = get_corr_method(self.method, self.metric.get_result().target_correlation, False)
            value = reference.stats[method].abs_max_target_features_correlation

            if value is not None:
                return TestValueCondition(eq=approx(value, relative=0.1))

        return TestValueCondition(lt=0.9)

    def calculate_value_for_test(self) -> Optional[Numeric]:
        method = get_corr_method(self.method, self.metric.get_result().target_correlation, False)
        return self.metric.get_result().current.stats[method].abs_max_target_features_correlation

    def get_description(self, value: Numeric) -> str:
        if value is None:
            return "No target in the current dataset"

        else:
            return f"The maximum correlation is {value:.3g}. The test threshold is {self.get_condition()}."


class TestPredictionFeaturesCorrelations(BaseDataQualityCorrelationsMetricsValueTest):
    name: ClassVar = "Correlation between Prediction and Features"

    def get_condition_from_reference(self, reference: Optional[DatasetCorrelation]) -> TestValueCondition:
        if reference is not None:
            method = get_corr_method(self.method, self.metric.get_result().target_correlation, False)
            value = reference.stats[method].abs_max_prediction_features_correlation

            if value is not None:
                return TestValueCondition(eq=approx(value, relative=0.1))

        return TestValueCondition(lt=0.9)

    def calculate_value_for_test(self) -> Optional[Numeric]:
        method = get_corr_method(self.method, self.metric.get_result().target_correlation, False)
        return self.metric.get_result().current.stats[method].abs_max_prediction_features_correlation

    def get_description(self, value: Numeric) -> str:
        if value is None:
            return "No prediction in the current dataset"

        else:
            return f"The maximum correlation is {value:.3g}. The test threshold is {self.get_condition()}."


@default_renderer(wrap_type=TestPredictionFeaturesCorrelations)
@default_renderer(wrap_type=TestTargetFeaturesCorrelations)
class TestPredictionFeaturesCorrelationsRenderer(TestRenderer):
    def render_html(self, obj: TestTargetFeaturesCorrelations) -> TestHtmlInfo:
        info = super().render_html(obj)
        metric_result = obj.metric.get_result()
        method = get_corr_method(obj.method, metric_result.target_correlation, False)
        current_correlations = metric_result.current.correlation[method]

        if metric_result.reference is not None:
            reference_correlations: Optional[pd.DataFrame] = metric_result.reference.correlation[method]

        else:
            reference_correlations = None

        fig = plot_correlations(current_correlations, reference_correlations)
        info.with_details("Target-Features Correlations", plotly_figure(title="", figure=fig))
        return info


class TestCorrelationChanges(BaseDataQualityCorrelationsMetricsValueTest):
    group: ClassVar = DATA_QUALITY_GROUP.id
    name: ClassVar = "Change in Correlation"
    _metric: DatasetCorrelationsMetric
    corr_diff: float
    column_name: Optional[ColumnName]

    def __init__(
        self,
        corr_diff: float = 0.25,
        method: str = "pearson",
        column_name: Optional[Union[str, ColumnName]] = None,
        eq: Optional[Numeric] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
    ):
        self.corr_diff = corr_diff
        if column_name is not None:
            self.column_name = ColumnName.from_any(column_name)
        super().__init__(
            method=method,
            eq=eq,
            gt=gt,
            gte=gte,
            is_in=is_in,
            lt=lt,
            lte=lte,
            not_eq=not_eq,
            not_in=not_in,
            is_critical=is_critical,
        )

    def get_condition_from_reference(self, reference: Optional[DatasetCorrelation]) -> TestValueCondition:
        pass

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition

        return TestValueCondition(eq=0)

    def calculate_value_for_test(self) -> Optional[Numeric]:
        metric_result = self.metric.get_result()

        if metric_result.reference is None:
            raise ValueError("Reference should be present")

        if self.method is None:
            raise ValueError("method should be set")
        current_correlations = metric_result.current.correlation[self.method]
        reference_correlations: Optional[pd.DataFrame] = metric_result.reference.correlation[self.method]
        if self.column_name is None:
            diff = reference_correlations - current_correlations
            return (diff.abs() > self.corr_diff).sum().sum() / 2

        current_correlations = current_correlations[self.column_name.display_name]
        if reference_correlations is not None:
            reference_correlations = reference_correlations[self.column_name.display_name]
        diff = reference_correlations - current_correlations
        return (diff.abs() > self.corr_diff).sum()

    def get_description(self, value: Numeric) -> str:
        return f"The number of correlation violations is {value:.3g}. The test threshold is {self.get_condition()}."


@default_renderer(wrap_type=TestCorrelationChanges)
class TestCorrelationChangesRenderer(TestRenderer):
    def render_html(self, obj: TestCorrelationChanges) -> TestHtmlInfo:
        info = super().render_html(obj)
        metric_result = obj.metric.get_result()

        if obj.method is None:
            raise ValueError("method should be set")
        current_correlations = metric_result.current.correlation[obj.method]

        if metric_result.reference is not None:
            reference_correlations: Optional[pd.DataFrame] = metric_result.reference.correlation[obj.method]

        else:
            reference_correlations = None

        fig = plot_correlations(current_correlations, reference_correlations)
        info.with_details("Target-Features Correlations", plotly_figure(title="", figure=fig))
        return info


class BaseFeatureDataQualityMetricsTest(BaseDataQualityMetricsValueTest, ABC):
    def __init__(
        self,
        column_name: Union[str, ColumnName],
        eq: Optional[Numeric] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
    ):
        super().__init__(
            column_name=column_name,
            eq=eq,
            gt=gt,
            gte=gte,
            is_in=is_in,
            lt=lt,
            lte=lte,
            not_eq=not_eq,
            not_in=not_in,
            is_critical=is_critical,
        )

    def groups(self) -> Dict[str, str]:
        return {
            GroupingTypes.ByFeature.id: self.column_name.display_name,
        }

    def check(self):
        result = super().check()

        if self._value is None:
            result.mark_as_error(f"No value for the feature '{self.column_name}'")
            return result

        return result

    def get_stat(self, current: NumericCharacteristics):
        raise NotImplementedError


class TestColumnValueMin(BaseFeatureDataQualityMetricsTest):
    name: ClassVar = "Min Value"

    def get_stat(self, current: NumericCharacteristics):
        return current.min

    def get_condition_from_reference(self, reference: Optional[ColumnCharacteristics]) -> TestValueCondition:
        if reference is not None:
            if not isinstance(reference, NumericCharacteristics):
                raise ValueError(f"{self.column_name} should be numerical or bool")
            min_value = reference.min
            return TestValueCondition(gte=min_value)
        raise ValueError("Neither required test parameters nor reference data has been provided.")

    def calculate_value_for_test(self) -> Optional[Union[Numeric, bool]]:
        features_stats = self.metric.get_result().current_characteristics
        if not isinstance(features_stats, NumericCharacteristics):
            raise ValueError(f"{self.column_name} should be numerical or bool")
        min_value = features_stats.min
        return min_value

    def get_description(self, value: Numeric) -> str:
        return f"The minimum value of the column **{self.column_name}** is {value} The test threshold is {self.get_condition()}."


class TestColumnValueMax(BaseFeatureDataQualityMetricsTest):
    name: ClassVar = "Max Value"

    def get_stat(self, current: NumericCharacteristics):
        return current.max

    def get_condition_from_reference(self, reference: Optional[ColumnCharacteristics]) -> TestValueCondition:
        if reference is not None:
            if not isinstance(reference, NumericCharacteristics):
                raise ValueError(f"{self.column_name} should be numerical or bool")
            max_value = reference.max
            return TestValueCondition(lte=max_value)
        raise ValueError("Neither required test parameters nor reference data has been provided.")

    def calculate_value_for_test(self) -> Optional[Union[Numeric, bool]]:
        features_stats = self.metric.get_result().current_characteristics
        if not isinstance(features_stats, NumericCharacteristics):
            raise ValueError(f"{self.column_name} should be numerical or bool")
        max_value = features_stats.max
        if isinstance(max_value, str):
            raise ValueError(f"{self.column_name} should be numerical or bool")
        return max_value

    def get_description(self, value: Numeric) -> str:
        return f"The maximum value of the column **{self.column_name}** is {value}. The test threshold is {self.get_condition()}."


class TestColumnValueMean(BaseFeatureDataQualityMetricsTest):
    name: ClassVar = "Mean Value"

    def get_stat(self, current: NumericCharacteristics):
        return current.mean

    def get_condition_from_reference(self, reference: Optional[ColumnCharacteristics]) -> TestValueCondition:
        if reference is not None:
            if not isinstance(reference, NumericCharacteristics):
                raise ValueError(f"{self.column_name} should be numerical or bool")
            return TestValueCondition(eq=approx(reference.mean, 0.1))
        raise ValueError("Neither required test parameters nor reference data has been provided.")

    def calculate_value_for_test(self) -> Optional[Numeric]:
        features_stats = self.metric.get_result().current_characteristics
        if not isinstance(features_stats, NumericCharacteristics):
            raise ValueError(f"{self.column_name} should be numerical or bool")
        return features_stats.mean

    def get_description(self, value: Numeric) -> str:
        return f"The mean value of the column **{self.column_name}** is {value:.3g}. The test threshold is {self.get_condition()}."


class TestColumnValueMedian(BaseFeatureDataQualityMetricsTest):
    name: ClassVar = "Median Value"

    def get_stat(self, current: NumericCharacteristics):
        return current.p50

    def get_condition_from_reference(self, reference: Optional[ColumnCharacteristics]) -> TestValueCondition:
        if reference is not None:
            if not isinstance(reference, NumericCharacteristics):
                raise ValueError(f"{self.column_name} should be numerical or bool")
            return TestValueCondition(eq=approx(reference.p50, 0.1))
        raise ValueError("Neither required test parameters nor reference data has been provided.")

    def calculate_value_for_test(self) -> Optional[Numeric]:
        features_stats = self.metric.get_result().current_characteristics
        if not isinstance(features_stats, NumericCharacteristics):
            raise ValueError(f"{self.column_name} should be numerical or bool")
        return features_stats.p50

    def get_description(self, value: Numeric) -> str:
        return f"The median value of the column **{self.column_name}** is {value:.3g}. The test threshold is {self.get_condition()}."


@default_renderer(wrap_type=TestColumnValueMin)
@default_renderer(wrap_type=TestColumnValueMax)
@default_renderer(wrap_type=TestColumnValueMean)
@default_renderer(wrap_type=TestColumnValueMedian)
class TestColumnValueFeatureRenderer(TestRenderer):
    def render_html(self, obj: BaseFeatureDataQualityMetricsTest) -> TestHtmlInfo:
        metric_result: ColumnSummaryResult = obj.metric.get_result()
        column_name, info, curr_distr, ref_distr = self._feature_render_html(obj)
        current_characteristics = metric_result.current_characteristics
        if not isinstance(current_characteristics, NumericCharacteristics):
            raise ValueError(f"{column_name} should be numerical or bool")
        value = obj.get_stat(current_characteristics)
        value_name: Optional[str] = None
        if value is not None:
            value = float(value)
            value_name = f"current {column_name} {obj.name.lower()}"

        fig = plot_distr_with_cond_perc_button(
            hist_curr=curr_distr,
            hist_ref=ref_distr,
            xaxis_name="",
            yaxis_name="count",
            yaxis_name_perc="percent",
            color_options=self.color_options,
            to_json=False,
            condition=obj.get_condition(),
            value=value,
            value_name=value_name,
        )

        info.with_details(f"{obj.name} {column_name}", plotly_figure(title="", figure=fig))
        return info

    def _feature_render_html(self, obj):
        column_name = obj.column_name
        info = super().render_html(obj)
        metric_result: ColumnSummaryResult = obj.metric.get_result()
        bins_for_hist = metric_result.plot_data.bins_for_hist
        if bins_for_hist is None:
            raise ValueError(f"{column_name} should be numerical or bool")
        curr_distr = bins_for_hist.current
        ref_distr = bins_for_hist.reference
        # fig = plot_distr(hist_curr=curr_distr, hist_ref=ref_distr, color_options=self.color_options)
        # return column_name, fig, info, metric_result
        return column_name, info, curr_distr, ref_distr


class TestColumnValueStd(BaseFeatureDataQualityMetricsTest):
    name: ClassVar = "Standard Deviation (SD)"

    def get_stat(self, current: NumericCharacteristics):
        return current.std

    def get_condition_from_reference(self, reference: Optional[ColumnCharacteristics]) -> TestValueCondition:
        if reference is not None:
            if not isinstance(reference, NumericCharacteristics):
                raise ValueError(f"{self.column_name} should be numerical or bool")
            return TestValueCondition(eq=approx(reference.std, 0.1))
        raise ValueError("Neither required test parameters nor reference data has been provided.")

    def calculate_value_for_test(self) -> Optional[Numeric]:
        features_stats = self.metric.get_result().current_characteristics
        if not isinstance(features_stats, NumericCharacteristics):
            raise ValueError(f"{self.column_name} should be numerical or bool")
        return features_stats.std

    def get_description(self, value: Numeric) -> str:
        return (
            f"The standard deviation of the column **{self.column_name}** is {value:.3g}. "
            f"The test threshold is {self.get_condition()}."
        )


@default_renderer(wrap_type=TestColumnValueStd)
class TestColumnValueStdRenderer(TestColumnValueFeatureRenderer):
    def render_html(self, obj: BaseFeatureDataQualityMetricsTest) -> TestHtmlInfo:
        column_name, info, curr_distr, ref_distr = self._feature_render_html(obj)
        fig = plot_distr_with_cond_perc_button(
            hist_curr=curr_distr,
            hist_ref=ref_distr,
            xaxis_name="",
            yaxis_name="count",
            yaxis_name_perc="percent",
            color_options=self.color_options,
            to_json=False,
            condition=None,
        )
        info.with_details(f"Std Value {column_name}", plotly_figure(title="", figure=fig))
        return info


class TestNumberOfUniqueValues(BaseFeatureDataQualityMetricsTest):
    name: ClassVar = "Number of Unique Values"

    def get_stat(self, current: NumericCharacteristics):
        return current.unique

    def get_condition_from_reference(self, reference: Optional[ColumnCharacteristics]) -> TestValueCondition:
        if reference is not None:
            if not isinstance(reference, (NumericCharacteristics, CategoricalCharacteristics, DatetimeCharacteristics)):
                raise ValueError(f"{self.column_name} should be numerical, categorical or datetime")
            unique_count = reference.unique
            return TestValueCondition(eq=approx(unique_count, relative=0.1))

        return TestValueCondition(gt=1)

    def calculate_value_for_test(self) -> Optional[Numeric]:
        features_stats = self.metric.get_result().current_characteristics
        if isinstance(features_stats, TextCharacteristics):
            raise ValueError(f"{self.column_name} should be numerical, categorical or datetime")
        return features_stats.unique

    def get_description(self, value: Numeric) -> str:
        return (
            f"The number of the unique values in the column **{self.column_name}** is {value}. "
            f"The test threshold is {self.get_condition()}."
        )


@default_renderer(wrap_type=TestNumberOfUniqueValues)
class TestNumberOfUniqueValuesRenderer(TestRenderer):
    def render_html(self, obj: TestNumberOfUniqueValues) -> TestHtmlInfo:
        info = super().render_html(obj)
        column_name = obj.column_name
        counts_data = obj.metric.get_result().plot_data.counts_of_values
        if counts_data is not None:
            curr_df = counts_data["current"]
            ref_df = None
            if "reference" in counts_data.keys():
                ref_df = counts_data["reference"]
            info.details = plot_value_counts_tables_ref_curr(column_name, curr_df, ref_df, "num_of_unique_vals")

        return info


class TestUniqueValuesShare(BaseFeatureDataQualityMetricsTest):
    name: ClassVar = "Share of Unique Values"

    def get_stat(self, current: NumericCharacteristics):
        return current.unique_percentage

    def get_condition_from_reference(self, reference: Optional[ColumnCharacteristics]) -> TestValueCondition:
        if reference is not None:
            if not isinstance(reference, (NumericCharacteristics, CategoricalCharacteristics, DatetimeCharacteristics)):
                raise ValueError(f"{self.column_name} should be numerical, categorical or datetime")
            unique_percentage = reference.unique_percentage

            if unique_percentage is not None:
                return TestValueCondition(eq=approx(unique_percentage / 100.0, relative=0.1))

        raise ValueError("Neither required test parameters nor reference data has been provided.")

    def calculate_value_for_test(self) -> Optional[Numeric]:
        features_stats = self.metric.get_result().current_characteristics
        if isinstance(features_stats, TextCharacteristics):
            raise ValueError(f"{self.column_name} should be numerical, categorical or datetime")
        unique_percentage = features_stats.unique_percentage

        if unique_percentage is None:
            return None

        return unique_percentage / 100.0

    def get_description(self, value: Numeric) -> str:
        return (
            f"The share of the unique values in the column **{self.column_name}** is {value:.3}. "
            f"The test threshold is {self.get_condition()}."
        )


@default_renderer(wrap_type=TestUniqueValuesShare)
class TestUniqueValuesShareRenderer(TestRenderer):
    def render_html(self, obj: TestUniqueValuesShare) -> TestHtmlInfo:
        info = super().render_html(obj)
        column_name = obj.column_name
        counts_data = obj.metric.get_result().plot_data.counts_of_values
        if counts_data is not None:
            curr_df = counts_data["current"]
            ref_df = None
            if "reference" in counts_data.keys():
                ref_df = counts_data["reference"]
            info.details = plot_value_counts_tables_ref_curr(column_name, curr_df, ref_df, "unique_vals_sare")

        return info


class TestMostCommonValueShare(BaseFeatureDataQualityMetricsTest):
    name: ClassVar = "Share of the Most Common Value"

    def get_stat(self, current: NumericCharacteristics):
        return current.most_common_percentage

    def get_condition_from_reference(self, reference: Optional[ColumnCharacteristics]) -> TestValueCondition:
        if reference is not None:
            if not isinstance(reference, (NumericCharacteristics, CategoricalCharacteristics, DatetimeCharacteristics)):
                raise ValueError(f"{self.column_name} should be numerical, categorical or datetime")
            most_common_percentage = reference.most_common_percentage

            if most_common_percentage is not None:
                return TestValueCondition(eq=approx(most_common_percentage / 100.0, relative=0.1))

        return TestValueCondition(lt=0.8)

    def calculate_value_for_test(self) -> Optional[Numeric]:
        features_stats = self.metric.get_result().current_characteristics
        if isinstance(features_stats, TextCharacteristics):
            raise ValueError(f"{self.column_name} should be numerical, categorical or datetime")
        most_common_percentage = features_stats.most_common_percentage

        if most_common_percentage is None:
            return None

        return most_common_percentage / 100.0

    def get_description(self, value: Numeric) -> str:
        counts_data = self.metric.get_result().plot_data.counts_of_values
        if counts_data is None:
            raise ValueError("counts_of_values should be provided")
        most_common_value = counts_data["current"].iloc[0, 0]
        return (
            f"The most common value in the column **{self.column_name}** is {most_common_value}. "
            f"Its share is {value:.3g}. "
            f"The test threshold is {self.get_condition()}."
        )

    def get_parameters(self) -> ColumnCheckValueParameters:
        return ColumnCheckValueParameters(
            column_name=self.column_name.display_name, condition=self.get_condition(), value=self._value
        )


@default_renderer(wrap_type=TestMostCommonValueShare)
class TestMostCommonValueShareRenderer(TestRenderer):
    def render_html(self, obj: TestMostCommonValueShare) -> TestHtmlInfo:
        info = super().render_html(obj)
        column_name = obj.column_name

        if column_name is None:
            raise ValueError("column_name should be present")

        counts_data = obj.metric.get_result().plot_data.counts_of_values
        if counts_data is not None:
            curr_df = counts_data["current"]
            ref_df = None
            if "reference" in counts_data.keys():
                ref_df = counts_data["reference"]
            additional_plots = plot_value_counts_tables_ref_curr(column_name, curr_df, ref_df, "most_common_value_sare")
            info.details = additional_plots
        return info


class TestAllColumnsMostCommonValueShare(BaseGenerator):
    """Creates most common value share tests for each column in the dataset"""

    columns: Optional[List[str]]

    def __init__(self, columns: Optional[List[str]] = None, is_critical: bool = True):
        self.is_critical = is_critical
        self.columns = columns

    def generate(self, data_definition: DataDefinition) -> List[TestMostCommonValueShare]:
        if self.columns is None:
            columns = [
                column.column_name for column in data_definition.get_columns() if column.column_type != ColumnType.Text
            ]

        else:
            columns = self.columns

        return [
            TestMostCommonValueShare(
                column_name=column,
                is_critical=self.is_critical,
            )
            for column in columns
        ]


class MeanInNSigmasParameter(TestParameters):
    column_name: str
    current_mean: float
    n_sigmas: int  # ? float
    reference_mean: float
    reference_std: float


class TestMeanInNSigmas(Test):
    group: ClassVar = DATA_QUALITY_GROUP.id
    name: ClassVar = "Mean Value Stability"
    _metric: ColumnSummaryMetric
    column_name: ColumnName
    n_sigmas: int

    def __init__(self, column_name: Union[str, ColumnName], n_sigmas: int = 2, is_critical: bool = True):
        self.column_name = ColumnName.from_any(column_name)
        self.n_sigmas = n_sigmas
        super().__init__(is_critical=is_critical)
        self._metric = ColumnSummaryMetric(self.column_name)

    @property
    def metric(self):
        return self._metric

    def check(self):
        reference_feature_stats = self.metric.get_result().reference_characteristics
        features_stats = self.metric.get_result().current_characteristics

        # todo: this was thrown in a render, do we just cut it?
        # if not isinstance(features_stats, NumericCharacteristics):
        #     raise ValueError(f"{self.column_name} should be numerical or bool")

        if reference_feature_stats is None:
            test_result = TestStatus.ERROR
            description = "Reference should be present"
            parameters = None
        else:
            # todo: look up
            # if not isinstance(reference_feature_stats, NumericCharacteristics):
            #     raise ValueError(f"{self.column_name} should be numerical or bool")
            current_mean = features_stats.mean
            reference_mean = reference_feature_stats.mean
            reference_std = reference_feature_stats.std
            sigmas_value = reference_std * self.n_sigmas
            left_condition = reference_mean - sigmas_value
            right_condition = reference_mean + sigmas_value

            if left_condition < current_mean < right_condition:
                description = (
                    f"The mean value of the column **{self.column_name}** is {current_mean:.3g}."
                    f" The expected range is from {left_condition:.3g} to {right_condition:.3g}"
                )
                test_result = TestStatus.SUCCESS

            else:
                description = (
                    f"The mean value of the column **{self.column_name}** is {current_mean:.3g}."
                    f" The expected range is from {left_condition:.3g} to {right_condition:.3g}"
                )
                test_result = TestStatus.FAIL

            parameters = MeanInNSigmasParameter(
                column_name=self.column_name.display_name,
                n_sigmas=self.n_sigmas,
                current_mean=current_mean,
                reference_mean=reference_mean,
                reference_std=reference_std,
            )

        return TestResult(
            name=self.name,
            description=description,
            status=test_result,
            parameters=parameters,
            group=self.group,
        )

    def groups(self) -> Dict[str, str]:
        return {GroupingTypes.ByFeature.id: self.column_name.display_name}


@default_renderer(wrap_type=TestMeanInNSigmas)
class TestMeanInNSigmasRenderer(TestRenderer):
    def render_html(self, obj: TestMeanInNSigmas) -> TestHtmlInfo:
        column_name = obj.column_name
        metric_result: ColumnSummaryResult = obj.metric.get_result()
        info = super().render_html(obj)

        if metric_result.reference_characteristics is None or metric_result.plot_data.bins_for_hist is None:
            return info

        if not isinstance(metric_result.reference_characteristics, NumericCharacteristics):
            raise ValueError(f"{column_name} should be numerical or bool")
        ref_mean = metric_result.reference_characteristics.mean
        ref_std = metric_result.reference_characteristics.std

        if ref_std is None or ref_mean is None:
            raise ValueError("No mean or std for reference")

        gt = ref_mean - obj.n_sigmas * ref_std
        lt = ref_mean + obj.n_sigmas * ref_std
        ref_condition = TestValueCondition(gt=gt, lt=lt)
        curr_distr = metric_result.plot_data.bins_for_hist.current
        ref_distr = metric_result.plot_data.bins_for_hist.reference

        if not isinstance(metric_result.current_characteristics, NumericCharacteristics):
            raise ValueError(f"{obj.column_name} should be numerical or bool")
        mean_value = metric_result.current_characteristics.mean

        fig = plot_distr_with_cond_perc_button(
            hist_curr=curr_distr,
            hist_ref=ref_distr,
            xaxis_name="",
            yaxis_name="count",
            yaxis_name_perc="percent",
            color_options=self.color_options,
            to_json=False,
            condition=ref_condition,
            value=mean_value,
            value_name=f"current {column_name} mean value",
        )

        info.with_details("", plotly_figure(title="", figure=fig))
        return info


class TestNumColumnsMeanInNSigmas(BaseGenerator):
    """Create tests of mean for all numeric columns"""

    columns: Optional[List[str]]

    def __init__(self, columns: Optional[List[str]] = None, is_critical: bool = True):
        self.is_critical = is_critical
        self.columns = columns

    def generate(self, data_definition: DataDefinition) -> List[TestMeanInNSigmas]:
        if self.columns is None:
            columns = [
                column.column_name for column in data_definition.get_columns(ColumnType.Numerical, features_only=True)
            ]

        else:
            columns = [
                column
                for column in self.columns
                if data_definition.get_column(column).column_type == ColumnType.Numerical
            ]

        return [
            TestMeanInNSigmas(
                column_name=column,
                n_sigmas=2,
                is_critical=self.is_critical,
            )
            for column in columns
        ]


class TestValueRange(Test):
    group: ClassVar = DATA_QUALITY_GROUP.id
    name: ClassVar = "Value Range"
    _metric: ColumnValueRangeMetric
    column_name: ColumnName
    left: Optional[float]
    right: Optional[float]

    def __init__(
        self,
        column_name: Union[str, ColumnName],
        left: Optional[float] = None,
        right: Optional[float] = None,
        is_critical: bool = True,
    ):
        self.column_name = ColumnName.from_any(column_name)
        self.left = left
        self.right = right
        super().__init__(is_critical=is_critical)
        self._metric = ColumnValueRangeMetric(column_name=self.column_name, left=self.left, right=self.right)

    @property
    def metric(self):
        return self._metric

    def check(self):
        number_not_in_range = self.metric.get_result().current.number_not_in_range

        if number_not_in_range > 0:
            description = f"The column **{self.column_name}** has values out of range."
            test_result = TestStatus.FAIL
        else:
            description = f"All values in the column **{self.column_name}** are within range"
            test_result = TestStatus.SUCCESS

        return TestResult(
            name=self.name,
            description=description,
            status=test_result,
            group=self.group,
        )

    def groups(self) -> Dict[str, str]:
        return {GroupingTypes.ByFeature.id: self.column_name.display_name}


@default_renderer(wrap_type=TestValueRange)
class TestValueRangeRenderer(TestRenderer):
    def render_html(self, obj: TestValueRange) -> TestHtmlInfo:
        column_name = obj.column_name
        metric_result = obj.metric.get_result()
        ref_data = metric_result.reference
        hist_ref = None
        if ref_data is not None:
            hist_ref = HistogramData.from_distribution(metric_result.reference.distribution)
        info = super().render_html(obj)
        fig = plot_distr_with_cond_perc_button(
            hist_curr=HistogramData.from_distribution(metric_result.current.distribution),
            hist_ref=hist_ref,
            xaxis_name="",
            yaxis_name="count",
            yaxis_name_perc="percent",
            color_options=self.color_options,
            to_json=False,
            condition=None,
            lt=metric_result.right,
            gt=metric_result.left,
            dict_rename={"gt": "left", "lt": "right"},
        )
        info.with_details(
            f"Value Range {column_name.display_name}",
            plotly_figure(title="", figure=fig),
        )
        return info


class BaseDataQualityValueRangeMetricsTest(BaseCheckValueTest, ABC):
    group: ClassVar = DATA_QUALITY_GROUP.id
    _metric: ColumnValueRangeMetric
    column_name: ColumnName
    left: Optional[float]
    right: Optional[float]

    def __init__(
        self,
        column_name: Union[str, ColumnName],
        left: Optional[float] = None,
        right: Optional[float] = None,
        eq: Optional[Numeric] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
    ):
        self.column_name = ColumnName.from_any(column_name)
        self.left = left
        self.right = right

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
        )
        self._metric = ColumnValueRangeMetric(column_name=self.column_name, left=self.left, right=self.right)

    def groups(self) -> Dict[str, str]:
        return {GroupingTypes.ByFeature.id: self.column_name.display_name}

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition
        return TestValueCondition(eq=approx(0))

    @property
    def metric(self):
        return self._metric


class TestNumberOfOutRangeValues(BaseDataQualityValueRangeMetricsTest):
    name: ClassVar = "Number of Out-of-Range Values "

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.number_not_in_range

    def get_description(self, value: Numeric) -> str:
        return (
            f"The number of values out of range in the column **{self.column_name}** is {value}. "
            f" The test threshold is {self.get_condition()}."
        )


class ShareOfOutRangeParameters(CheckValueParameters):
    left: Optional[float]
    right: Optional[float]


class TestShareOfOutRangeValues(BaseDataQualityValueRangeMetricsTest):
    name: ClassVar = "Share of Out-of-Range Values"

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.share_not_in_range

    def get_description(self, value: Numeric) -> str:
        current_result = self.metric.get_result().current
        return (
            f"The share of values out of range in the column **{self.column_name.display_name}** is {value:.3g} "
            f"({current_result.number_not_in_range} out of {current_result.number_of_values}). "
            f" The test threshold is {self.get_condition()}."
        )

    def get_parameters(self) -> ShareOfOutRangeParameters:
        return ShareOfOutRangeParameters(
            condition=self.get_condition(), value=self._value, left=self.left, right=self.right
        )


@default_renderer(wrap_type=TestShareOfOutRangeValues)
@default_renderer(wrap_type=TestNumberOfOutRangeValues)
class TestRangeValuesRenderer(TestRenderer):
    def render_html(self, obj: BaseDataQualityValueRangeMetricsTest) -> TestHtmlInfo:
        column_name = obj.column_name
        metric_result = obj.metric.get_result()
        info = super().render_html(obj)
        ref_data = metric_result.reference
        hist_ref = None
        if ref_data is not None:
            hist_ref = HistogramData.from_distribution(metric_result.reference.distribution)
        info = super().render_html(obj)
        fig = plot_distr_with_cond_perc_button(
            hist_curr=HistogramData.from_distribution(metric_result.current.distribution),
            hist_ref=hist_ref,
            xaxis_name="",
            yaxis_name="count",
            yaxis_name_perc="percent",
            color_options=self.color_options,
            to_json=False,
            condition=None,
            lt=metric_result.right,
            gt=metric_result.left,
            dict_rename={"gt": "left", "lt": "right"},
        )

        info.with_details(f"{obj.name} for {column_name.display_name}", plotly_figure(title="", figure=fig))
        return info


class TestNumColumnsOutOfRangeValues(BaseGenerator):
    """Creates share of out of range values tests for all numeric columns"""

    columns: Optional[List[str]]

    def __init__(self, columns: Optional[List[str]] = None, is_critical: bool = True):
        self.is_critical = is_critical
        self.columns = columns

    def generate(self, data_definition: DataDefinition) -> List[TestShareOfOutRangeValues]:
        if self.columns is None:
            columns = [
                column.column_name for column in data_definition.get_columns(ColumnType.Numerical, features_only=True)
            ]

        else:
            columns = [
                column
                for column in self.columns
                if data_definition.get_column(column).column_type == ColumnType.Numerical
            ]

        return [
            TestShareOfOutRangeValues(
                column_name=column,
                is_critical=self.is_critical,
            )
            for column in columns
        ]


class ColumnValueListParameters(TestParameters):
    value: Numeric
    column_name: str
    values: Optional[List[Any]] = None


class TestValueList(Test):
    group: ClassVar = DATA_QUALITY_GROUP.id
    name: ClassVar = "Out-of-List Values"
    alias: ClassVar = "value_list"
    _metric: ColumnValueListMetric
    column_name: str
    values: Optional[list]

    def __init__(self, column_name: str, values: Optional[list] = None, is_critical: bool = True):
        self.column_name = column_name
        self.values = values
        super().__init__(is_critical=is_critical)
        self._metric = ColumnValueListMetric(column_name=self.column_name, values=values)

    @property
    def metric(self):
        return self._metric

    def check(self):
        metric_result = self.metric.get_result()

        if metric_result.current.number_not_in_list > 0:
            test_result = TestStatus.FAIL
            description = f"The column **{self.column_name}** has values out of list."

        else:
            test_result = TestStatus.SUCCESS
            description = f"All values in the column **{self.column_name}** are in the list."

        return TestResult(
            name=self.name,
            description=description,
            status=test_result,
            group=self.group,
            parameters=ColumnValueListParameters(
                value=metric_result.current.number_not_in_list, values=self.values, column_name=self.column_name
            ),
        )

    def groups(self) -> Dict[str, str]:
        return {GroupingTypes.ByFeature.id: self.column_name}


class BaseDataQualityValueListMetricsTest(BaseCheckValueTest, ABC):
    alias: ClassVar[str]
    group: ClassVar = DATA_QUALITY_GROUP.id
    _metric: ColumnValueListMetric
    column_name: str
    values: Optional[list]

    def __init__(
        self,
        column_name: str,
        values: Optional[list] = None,
        eq: Optional[Numeric] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
    ):
        self.column_name = column_name
        self.values = values
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
        )
        self._metric = ColumnValueListMetric(column_name=self.column_name, values=self.values)

    @property
    def metric(self):
        return self._metric

    def groups(self) -> Dict[str, str]:
        return {GroupingTypes.ByFeature.id: self.column_name}

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition
        return TestValueCondition(eq=approx(0))


class TestNumberOfOutListValues(BaseDataQualityValueListMetricsTest):
    name: ClassVar = "Number Out-of-List Values"
    alias: ClassVar = "number_value_list"

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.number_not_in_list

    def get_description(self, value: Numeric) -> str:
        return (
            f"The number of values out of list in the column **{self.column_name}** is {value}. "
            f"The test threshold is {self.get_condition()}."
        )


class ValueListParameters(CheckValueParameters):
    # todo: typing
    values: Optional[List[Any]] = None


class TestShareOfOutListValues(BaseDataQualityValueListMetricsTest):
    name: ClassVar = "Share of Out-of-List Values"
    alias: ClassVar = "share_value_list"

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.share_not_in_list

    def get_description(self, value: Numeric) -> str:
        metric_result = self.metric.get_result()
        number_not_in_range = metric_result.current.number_not_in_list
        rows_count = metric_result.current.rows_count
        return (
            f"The share of values out of list in the column **{self.column_name}** is {value:.3g} "
            f"({number_not_in_range} out of {rows_count}). "
            f"The test threshold is {self.get_condition()}."
        )

    def get_parameters(self) -> CheckValueParameters:
        return ValueListParameters(condition=self.get_condition(), value=self._value, values=self.values)


class TestCatColumnsOutOfListValues(BaseGenerator):
    """Create share of out of list values tests for category columns"""

    columns: Optional[List[str]]

    def __init__(self, columns: Optional[List[str]] = None, is_critical: bool = True):
        self.is_critical = is_critical
        self.columns = columns

    def generate(self, data_definition: DataDefinition) -> List[TestShareOfOutListValues]:
        if self.columns is None:
            columns = data_definition.get_columns(ColumnType.Categorical, features_only=True)

        else:
            columns = [
                column
                for column in self.columns
                if data_definition.get_column(column).column_type == ColumnType.Categorical
            ]
        return [
            TestShareOfOutListValues(
                column_name=column.column_name,
                is_critical=self.is_critical,
            )
            for column in columns
        ]


class TestColumnQuantile(BaseCheckValueTest):
    group: ClassVar = DATA_QUALITY_GROUP.id
    name: ClassVar = "Quantile Value"
    _metric: ColumnQuantileMetric
    column_name: ColumnName
    quantile: float

    def __init__(
        self,
        column_name: Union[str, ColumnName],
        quantile: float,
        eq: Optional[Numeric] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
    ):
        self.column_name = ColumnName.from_any(column_name)
        self.quantile = quantile
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
        )
        self._metric = ColumnQuantileMetric(column_name=self.column_name, quantile=self.quantile)

    @property
    def metric(self):
        return self._metric

    def groups(self) -> Dict[str, str]:
        return {GroupingTypes.ByFeature.id: self.column_name.display_name}

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition

        reference = self.metric.get_result().reference

        if reference is not None:
            return TestValueCondition(eq=approx(reference.value, 0.1))

        raise ValueError("Neither required test parameters nor reference data has been provided.")

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.value

    def get_description(self, value: Numeric) -> str:
        return (
            f"The {self.quantile} quantile value of the column **{self.column_name}** is {value:.3g}. "
            f"The test threshold is {self.get_condition()}."
        )


@default_renderer(wrap_type=TestColumnQuantile)
class TestColumnQuantileRenderer(TestRenderer):
    def render_html(self, obj: TestColumnQuantile) -> TestHtmlInfo:
        info = super().render_html(obj)
        metric_result = obj.metric.get_result()
        ref_data = metric_result.reference
        hist_ref = None
        if ref_data is not None:
            hist_ref = HistogramData.from_distribution(metric_result.reference.distribution)
        fig = plot_distr_with_cond_perc_button(
            hist_curr=HistogramData.from_distribution(metric_result.current.distribution),
            hist_ref=hist_ref,
            xaxis_name="",
            yaxis_name="count",
            yaxis_name_perc="percent",
            color_options=self.color_options,
            to_json=False,
            condition=obj.get_condition(),
            value=obj.metric.get_result().current.value,
            value_name="current quantile",
        )
        info.with_details("", plotly_figure(title="", figure=fig))
        return info


@default_renderer(wrap_type=TestShareOfOutListValues)
@default_renderer(wrap_type=TestNumberOfOutListValues)
@default_renderer(wrap_type=TestValueList)
class TestListValuesRenderer(TestRenderer):
    def render_html(self, obj: Union[BaseDataQualityValueListMetricsTest, TestValueList]) -> TestHtmlInfo:
        info = super().render_html(obj)
        metric_result = obj.metric.get_result()
        column_name = metric_result.column_name
        values = metric_result.values
        curr_df = pd.concat(
            [
                pd.DataFrame(metric_result.current.values_in_list, columns=["x", "count"]),
                pd.DataFrame(metric_result.current.values_not_in_list, columns=["x", "count"]),
            ]
        )

        if metric_result.reference is not None:
            ref_df = pd.concat(
                [
                    pd.DataFrame(metric_result.reference.values_in_list, columns=["x", "count"]),
                    pd.DataFrame(metric_result.reference.values_in_list, columns=["x", "count"]),
                ]
            )

        else:
            ref_df = None

        additional_plots = plot_value_counts_tables(column_name, values, curr_df, ref_df, obj.alias)
        info.details = additional_plots
        return info


class BaseDataQualityCategoryMetricsTest(BaseCheckValueTest, ABC):
    alias: ClassVar[str]
    group: ClassVar = DATA_QUALITY_GROUP.id
    _metric: ColumnCategoryMetric
    column_name: ColumnName
    category: Union[str, int, float]

    def __init__(
        self,
        column_name: Union[str, ColumnName],
        category: Union[str, int, float],
        eq: Optional[Numeric] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
    ):
        self.column_name = ColumnName.from_any(column_name)
        self.category = category
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
        )
        self._metric = ColumnCategoryMetric(column_name=self.column_name, category=self.category)

    @property
    def metric(self):
        return self._metric

    def groups(self) -> Dict[str, str]:
        return {GroupingTypes.ByFeature.id: self.column_name.display_name}

    def get_condition_from_reference(self, reference: Optional[CategoryStat]) -> Union[int, float]:
        raise NotImplementedError()

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition

        reference = self.metric.get_result().reference
        reference_value = self.get_condition_from_reference(reference)
        if reference is not None:
            return TestValueCondition(eq=approx(reference_value, 0.1))

        return TestValueCondition(gt=0)


class TestCategoryShare(BaseDataQualityCategoryMetricsTest):
    name: ClassVar = "Share of category"
    alias: ClassVar = "share_category"

    def get_condition_from_reference(self, reference: Optional[CategoryStat]) -> float:
        if reference is not None:
            return reference.category_ratio
        raise ValueError("Neither required test parameters nor reference data has been provided.")

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.category_ratio

    def get_description(self, value: Numeric) -> str:
        metric_result = self.metric.get_result()
        return (
            f"The share of category '{str(metric_result.category)}' in the column **{self.column_name.display_name}** is {value:.3g} "
            f"({metric_result.current.category_num} out of {metric_result.current.all_num}). "
            f"The test threshold is {self.get_condition()}."
        )

    def get_parameters(self) -> CheckValueParameters:
        return ValueListParameters(condition=self.get_condition(), value=self._value, category=self.category)


class TestCategoryCount(BaseDataQualityCategoryMetricsTest):
    name: ClassVar = "Count of category"
    alias: ClassVar = "count_category"

    def get_condition_from_reference(self, reference: Optional[CategoryStat]) -> int:
        if reference is not None:
            return reference.category_num
        raise ValueError("Neither required test parameters nor reference data has been provided.")

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.category_num

    def get_description(self, value: Numeric) -> str:
        metric_result = self.metric.get_result()
        return (
            f"The number of category '{metric_result.category}' in the column **{self.column_name.display_name}** is {value:.3g} "
            f"({metric_result.current.category_num} out of {metric_result.current.all_num}). "
            f"The test threshold is {self.get_condition()}."
        )

    def get_parameters(self) -> CheckValueParameters:
        return ValueListParameters(condition=self.get_condition(), value=self._value, category=self.category)


@default_renderer(wrap_type=TestCategoryCount)
@default_renderer(wrap_type=TestCategoryShare)
class TestCategoryRenderer(TestRenderer):
    @staticmethod
    def _get_number_and_percents(s: pd.Series, num: int) -> pd.DataFrame:
        """Get a string with missing values numbers and percents from info for results table"""
        return s.astype(str) + " (" + (s / num * 100).round(2).astype(str) + "%)"

    def get_value_counts_table_with_percents(
        self,
        info: TestHtmlInfo,
        curr_df: pd.DataFrame,
        ref_df: Optional[pd.DataFrame],
        n_curr: int,
        n_ref: Optional[int],
        name: str,
    ) -> TestHtmlInfo:
        curr_df = curr_df.copy()
        replace = [("current value counts", n_curr)]
        if ref_df is not None and n_ref is not None:
            ref_df = ref_df.copy()
            replace.append(("reference value counts", n_ref))
            df = curr_df.merge(ref_df, on="x", how="outer")
            df.columns = ["value", "current value counts", "reference value counts"]
            df[["current value counts", "reference value counts"]] = df[
                ["current value counts", "reference value counts"]
            ].fillna(0.0)
            df.sort_values(["current value counts", "reference value counts"], ascending=False, inplace=True)

        else:
            df = curr_df
            df.columns = ["value", "current value counts"]
            df.sort_values("current value counts", ascending=False, inplace=True)
        for col, n in replace:
            df[col] = self._get_number_and_percents(df[col].fillna(0), n)
        df["value"] = df["value"].astype(str)
        info.details = [
            DetailsInfo(
                id=name,
                title="",
                info=BaseWidgetInfo(
                    title="",
                    type="table",
                    params={
                        "header": list(df.columns),
                        "data": df.values,
                    },
                    size=2,
                ),
            )
        ]
        return info

    def render_html(self, obj: Union[TestCategoryCount, TestCategoryShare]) -> TestHtmlInfo:
        info = super().render_html(obj)
        column_name = obj.column_name.display_name
        counts_data = obj.metric.get_result().counts_of_values
        curr_df = counts_data["current"]
        ref_df = None
        if "reference" in counts_data.keys():
            ref_df = counts_data["reference"]
        n_curr = obj.metric.get_result().current.all_num
        ref = obj.metric.get_result().reference
        n_ref = None
        if ref is not None:
            n_ref = ref.all_num
        return self.get_value_counts_table_with_percents(
            info, curr_df, ref_df, n_curr, n_ref, f"cat_counts_{column_name}"
        )
