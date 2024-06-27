import abc
from abc import ABC
from typing import Any
from typing import ClassVar
from typing import List
from typing import Optional
from typing import Union

from evidently.metric_results import DatasetClassificationQuality
from evidently.metric_results import Label
from evidently.metric_results import ROCCurve
from evidently.metrics.classification_performance.classification_dummy_metric import ClassificationDummyMetric
from evidently.metrics.classification_performance.classification_quality_metric import ClassificationConfusionMatrix
from evidently.metrics.classification_performance.classification_quality_metric import ClassificationQualityMetric
from evidently.metrics.classification_performance.classification_quality_metric import ClassificationQualityMetricResult
from evidently.metrics.classification_performance.confusion_matrix_metric import ClassificationConfusionMatrixParameters
from evidently.metrics.classification_performance.objects import ClassMetric
from evidently.metrics.classification_performance.quality_by_class_metric import ClassificationQualityByClass
from evidently.metrics.classification_performance.roc_curve_metric import ClassificationRocCurve
from evidently.renderers.base_renderer import TestHtmlInfo
from evidently.renderers.base_renderer import TestRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import TabData
from evidently.renderers.html_widgets import get_roc_auc_tab_data
from evidently.renderers.html_widgets import plotly_figure
from evidently.renderers.html_widgets import widget_tabs
from evidently.tests.base_test import BaseCheckValueTest
from evidently.tests.base_test import CheckValueParameters
from evidently.tests.base_test import GroupData
from evidently.tests.base_test import GroupingTypes
from evidently.tests.base_test import TestValueCondition
from evidently.tests.utils import approx
from evidently.tests.utils import plot_boxes
from evidently.tests.utils import plot_conf_mtrx
from evidently.tests.utils import plot_rates
from evidently.utils.types import Numeric

CLASSIFICATION_GROUP = GroupData("classification", "Classification", "")
GroupingTypes.TestGroup.add_value(CLASSIFICATION_GROUP)


class SimpleClassificationTest(BaseCheckValueTest):
    condition_arg: ClassVar[str] = "gt"

    group: ClassVar = CLASSIFICATION_GROUP.id
    name: ClassVar[str]
    _metric: ClassificationQualityMetric
    _dummy_metric: ClassificationDummyMetric

    def __init__(
        self,
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
            is_critical=is_critical,
        )
        self._metric = ClassificationQualityMetric()
        self._dummy_metric = ClassificationDummyMetric()

    @property
    def metric(self):
        return self._metric

    @property
    def dummy_metric(self):
        return self._dummy_metric

    def calculate_value_for_test(self) -> Optional[Any]:
        return self.get_value(self.metric.get_result().current)

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition

        ref_metrics = self.metric.get_result().reference

        if ref_metrics is not None:
            return TestValueCondition(eq=approx(self.get_value(ref_metrics), relative=0.2))

        if self.get_value(self.dummy_metric.get_result().dummy) is None:
            raise ValueError("Neither required test parameters nor reference data has been provided.")

        return TestValueCondition(**{self.condition_arg: self.get_value(self.dummy_metric.get_result().dummy)})

    @abc.abstractmethod
    def get_value(self, result: DatasetClassificationQuality):
        raise NotImplementedError()


class SimpleClassificationTestTopK(SimpleClassificationTest, ClassificationConfusionMatrixParameters, ABC):
    _conf_matrix: ClassificationConfusionMatrix

    def __init__(
        self,
        probas_threshold: Optional[float] = None,
        k: Optional[int] = None,
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
        if k is not None and probas_threshold is not None:
            raise ValueError("Only one of 'probas_threshold' or 'k' should be given")
        self.k = k
        self.probas_threshold = probas_threshold
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
        self._dummy_metric = ClassificationDummyMetric(probas_threshold=self.probas_threshold, k=self.k)
        self._metric = ClassificationQualityMetric(probas_threshold=self.probas_threshold, k=self.k)
        self._conf_matrix = self.confusion_matric_metric()

    def calculate_value_for_test(self) -> Optional[Any]:
        return self.get_value(self.metric.get_result().current)

    @property
    def conf_matrix(self):
        return self._conf_matrix


class TestAccuracyScore(SimpleClassificationTestTopK):
    name = "Accuracy Score"

    def get_value(self, result: DatasetClassificationQuality):
        return result.accuracy

    def get_description(self, value: Numeric) -> str:
        return f"The Accuracy Score is {value:.3g}. The test threshold is {self.get_condition()}"


@default_renderer(wrap_type=TestAccuracyScore)
class TestAccuracyScoreRenderer(TestRenderer):
    def render_html(self, obj: TestAccuracyScore) -> TestHtmlInfo:
        info = super().render_html(obj)
        curr_matrix = obj.conf_matrix.get_result().current_matrix
        ref_matrix = obj.conf_matrix.get_result().reference_matrix
        fig = plot_conf_mtrx(curr_matrix, ref_matrix)
        info.with_details("Accuracy Score", plotly_figure(figure=fig, title=""))
        return info


class TestPrecisionScore(SimpleClassificationTestTopK):
    name = "Precision Score"

    def get_value(self, result: DatasetClassificationQuality):
        return result.precision

    def get_description(self, value: Numeric) -> str:
        return f"The Precision Score is {value:.3g}. The test threshold is {self.get_condition()}"


@default_renderer(wrap_type=TestPrecisionScore)
class TestPrecisionScoreRenderer(TestRenderer):
    def render_html(self, obj: TestPrecisionScore) -> TestHtmlInfo:
        info = super().render_html(obj)
        curr_matrix = obj.conf_matrix.get_result().current_matrix
        ref_matrix = obj.conf_matrix.get_result().reference_matrix
        fig = plot_conf_mtrx(curr_matrix, ref_matrix)
        info.with_details("Precision Score", plotly_figure(figure=fig, title=""))
        return info


class TestF1Score(SimpleClassificationTestTopK):
    name: ClassVar = "F1 Score"

    def get_value(self, result: DatasetClassificationQuality):
        return result.f1

    def get_description(self, value: Numeric) -> str:
        return f"The F1 Score is {value:.3g}. The test threshold is {self.get_condition()}"


@default_renderer(wrap_type=TestF1Score)
class TestF1ScoreRenderer(TestRenderer):
    def render_html(self, obj: TestF1Score) -> TestHtmlInfo:
        info = super().render_html(obj)
        curr_matrix = obj.conf_matrix.get_result().current_matrix
        ref_matrix = obj.conf_matrix.get_result().reference_matrix
        fig = plot_conf_mtrx(curr_matrix, ref_matrix)
        info.with_details("F1 Score", plotly_figure(title="", figure=fig))
        return info


class TestRecallScore(SimpleClassificationTestTopK):
    name = "Recall Score"

    def get_value(self, result: DatasetClassificationQuality):
        return result.recall

    def get_description(self, value: Numeric) -> str:
        return f"The Recall Score is {value:.3g}. The test threshold is {self.get_condition()}"


@default_renderer(wrap_type=TestRecallScore)
class TestRecallScoreRenderer(TestRenderer):
    def render_html(self, obj: TestRecallScore) -> TestHtmlInfo:
        info = super().render_html(obj)
        curr_matrix = obj.conf_matrix.get_result().current_matrix
        ref_matrix = obj.conf_matrix.get_result().reference_matrix
        fig = plot_conf_mtrx(curr_matrix, ref_matrix)
        info.with_details("Recall Score", plotly_figure(title="", figure=fig))
        return info


class TestRocAuc(SimpleClassificationTest):
    name: ClassVar = "ROC AUC Score"
    _roc_curve: ClassificationRocCurve

    def __init__(
        self,
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
        self._roc_curve = ClassificationRocCurve()
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

    def get_value(self, result: DatasetClassificationQuality):
        return result.roc_auc

    def get_description(self, value: Numeric) -> str:
        if value is None:
            return "Not enough data to calculate ROC AUC. Consider providing probabilities instead of labels."

        else:
            return f"The ROC AUC Score is {value:.3g}. The test threshold is {self.get_condition()}"


@default_renderer(wrap_type=TestRocAuc)
class TestRocAucRenderer(TestRenderer):
    def render_html(self, obj: TestRocAuc) -> TestHtmlInfo:
        info = super().render_html(obj)
        curr_roc_curve: Optional[ROCCurve] = obj._roc_curve.get_result().current_roc_curve
        ref_roc_curve: Optional[ROCCurve] = obj._roc_curve.get_result().reference_roc_curve

        if curr_roc_curve is None:
            return info

        tab_data = get_roc_auc_tab_data(curr_roc_curve, ref_roc_curve, color_options=self.color_options)

        if len(tab_data) == 1:
            return info.with_details("ROC Curve", tab_data[0][1])

        tabs = [TabData(name, widget) for name, widget in tab_data]
        return info.with_details("", widget_tabs(title="", tabs=tabs))


class TestLogLoss(SimpleClassificationTest):
    condition_arg = "lt"
    name = "Logarithmic Loss"

    def get_value(self, result: DatasetClassificationQuality):
        return result.log_loss

    def get_description(self, value: Numeric) -> str:
        if value is None:
            return "Not enough data to calculate Logarithmic Loss. Consider providing probabilities instead of labels."

        else:
            return f"The Logarithmic Loss is {value:.3g}. The test threshold is {self.get_condition()}"


@default_renderer(wrap_type=TestLogLoss)
class TestLogLossRenderer(TestRenderer):
    def render_html(self, obj: TestLogLoss) -> TestHtmlInfo:
        info = super().render_html(obj)
        result: ClassificationQualityMetricResult = obj.metric.get_result()

        curr_metrics = result.current.plot_data
        ref_metrics = None if result.reference is None else result.reference.plot_data

        if curr_metrics is not None:
            fig = plot_boxes(
                curr_for_plots=curr_metrics,
                ref_for_plots=ref_metrics,
                color_options=self.color_options,
            )
            info.with_details("Logarithmic Loss", plotly_figure(title="", figure=fig))

        return info


class TestTPR(SimpleClassificationTestTopK):
    name = "True Positive Rate"

    def get_value(self, result: DatasetClassificationQuality):
        return result.tpr

    def get_description(self, value: Numeric) -> str:
        if value is None:
            return "This test is applicable only for binary classification"

        return f"The True Positive Rate is {value:.3g}. The test threshold is {self.get_condition()}"


@default_renderer(wrap_type=TestTPR)
class TestTPRRenderer(TestRenderer):
    def render_html(self, obj: TestF1Score) -> TestHtmlInfo:
        info = super().render_html(obj)
        curr_metrics = obj.metric.get_result().current
        ref_metrics = obj.metric.get_result().reference
        curr_rate_plots_data = curr_metrics.rate_plots_data
        ref_rate_plots_data = None

        if ref_metrics is not None:
            ref_rate_plots_data = ref_metrics.rate_plots_data

        if curr_rate_plots_data is not None:
            fig = plot_rates(
                curr_rate_plots_data=curr_rate_plots_data,
                ref_rate_plots_data=ref_rate_plots_data,
                color_options=self.color_options,
            )
            info.with_details("TPR", plotly_figure(title="", figure=fig))

        return info


class TestTNR(SimpleClassificationTestTopK):
    name = "True Negative Rate"

    def get_value(self, result: DatasetClassificationQuality):
        return result.tnr

    def get_description(self, value: Numeric) -> str:
        if value is None:
            return "This test is applicable only for binary classification"

        return f"The True Negative Rate is {value:.3g}. The test threshold is {self.get_condition()}"


@default_renderer(wrap_type=TestTNR)
class TestTNRRenderer(TestRenderer):
    def render_html(self, obj: TestF1Score) -> TestHtmlInfo:
        info = super().render_html(obj)
        curr_metrics = obj.metric.get_result().current
        ref_metrics = obj.metric.get_result().reference
        curr_rate_plots_data = curr_metrics.rate_plots_data
        ref_rate_plots_data = None

        if ref_metrics is not None:
            ref_rate_plots_data = ref_metrics.rate_plots_data

        if curr_rate_plots_data is not None:
            fig = plot_rates(
                curr_rate_plots_data=curr_rate_plots_data,
                ref_rate_plots_data=ref_rate_plots_data,
                color_options=self.color_options,
            )
            info.with_details("TNR", plotly_figure(title="", figure=fig))

        return info


class TestFPR(SimpleClassificationTestTopK):
    condition_arg: ClassVar = "lt"
    name = "False Positive Rate"

    def get_value(self, result: DatasetClassificationQuality):
        return result.fpr

    def get_description(self, value: Numeric) -> str:
        if value is None:
            return "This test is applicable only for binary classification"

        return f"The False Positive Rate is {value:.3g}. The test threshold is {self.get_condition()}"


@default_renderer(wrap_type=TestFPR)
class TestFPRRenderer(TestRenderer):
    def render_html(self, obj: TestF1Score) -> TestHtmlInfo:
        info = super().render_html(obj)
        curr_metrics = obj.metric.get_result().current
        ref_metrics = obj.metric.get_result().reference
        curr_rate_plots_data = curr_metrics.rate_plots_data
        ref_rate_plots_data = None

        if ref_metrics is not None:
            ref_rate_plots_data = ref_metrics.rate_plots_data

        if curr_rate_plots_data is not None:
            fig = plot_rates(
                curr_rate_plots_data=curr_rate_plots_data,
                ref_rate_plots_data=ref_rate_plots_data,
                color_options=self.color_options,
            )
            info.with_details("FPR", plotly_figure(title="", figure=fig))

        return info


class TestFNR(SimpleClassificationTestTopK):
    condition_arg: ClassVar = "lt"
    name = "False Negative Rate"

    def get_value(self, result: DatasetClassificationQuality):
        return result.fnr

    def get_description(self, value: Numeric) -> str:
        if value is None:
            return "This test is applicable only for binary classification"

        return f"The False Negative Rate is {value:.3g}. The test threshold is {self.get_condition()}"


@default_renderer(wrap_type=TestFNR)
class TestFNRRenderer(TestRenderer):
    def render_html(self, obj: TestF1Score) -> TestHtmlInfo:
        info = super().render_html(obj)
        curr_metrics = obj.metric.get_result().current
        ref_metrics = obj.metric.get_result().reference
        curr_rate_plots_data = curr_metrics.rate_plots_data
        ref_rate_plots_data = None

        if ref_metrics is not None:
            ref_rate_plots_data = ref_metrics.rate_plots_data

        if curr_rate_plots_data is not None:
            fig = plot_rates(
                curr_rate_plots_data=curr_rate_plots_data,
                ref_rate_plots_data=ref_rate_plots_data,
                color_options=self.color_options,
            )
            info.with_details("FNR", plotly_figure(title="", figure=fig))

        return info


class ByClassParameters(CheckValueParameters):
    label: Label


class ByClassClassificationTest(BaseCheckValueTest, ABC):
    group: ClassVar = CLASSIFICATION_GROUP.id
    _metric: ClassificationQualityMetric
    _by_class_metric: ClassificationQualityByClass
    _dummy_metric: ClassificationDummyMetric
    _conf_matrix: ClassificationConfusionMatrix
    label: Label
    probas_threshold: Optional[float] = None
    k: Optional[int] = None

    def __init__(
        self,
        label: Label,
        probas_threshold: Optional[float] = None,
        k: Optional[int] = None,
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
        if k is not None and probas_threshold is not None:
            raise ValueError("Only one of 'probas_threshold' or 'k' should be given")

        self.label = label
        self.probas_threshold = probas_threshold
        self.k = k
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

        self._metric = ClassificationQualityMetric(probas_threshold=self.probas_threshold, k=self.k)
        self._dummy_metric = ClassificationDummyMetric(probas_threshold=self.probas_threshold, k=self.k)
        self._by_class_metric = ClassificationQualityByClass(probas_threshold=self.probas_threshold, k=self.k)
        self._conf_matrix = ClassificationConfusionMatrix(probas_threshold=self.probas_threshold, k=self.k)

    @property
    def metric(self):
        return self._metric

    @property
    def dummy_metric(self):
        return self._dummy_metric

    @property
    def by_class_metric(self):
        return self._by_class_metric

    @property
    def conf_matrix(self):
        return self._conf_matrix

    def calculate_value_for_test(self) -> Optional[Any]:
        return self.get_value(self.by_class_metric.get_result().current.metrics[self.label])

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition

        result = self.by_class_metric.get_result()
        ref_metrics = result.reference.metrics if result.reference is not None else None

        if ref_metrics is not None:
            return TestValueCondition(eq=approx(self.get_value(ref_metrics[self.label]), relative=0.2))

        dummy_result = self.dummy_metric.get_result().metrics_matrix[self.label]

        if self.get_value(dummy_result) is None:
            raise ValueError("Neither required test parameters nor reference data has been provided.")

        return TestValueCondition(gt=self.get_value(dummy_result))

    @abc.abstractmethod
    def get_value(self, result: ClassMetric):
        raise NotImplementedError()

    def get_parameters(self) -> ByClassParameters:
        return ByClassParameters(condition=self.get_condition(), value=self._value, label=self.label)


class TestPrecisionByClass(ByClassClassificationTest):
    name: ClassVar[str] = "Precision Score by Class"

    def get_value(self, result: ClassMetric):
        return result.precision

    def get_description(self, value: Numeric) -> str:
        return (
            f"The precision score of the label **{self.label}** is {value:.3g}. "
            f"The test threshold is {self.get_condition()}"
        )


@default_renderer(wrap_type=TestPrecisionByClass)
class TestPrecisionByClassRenderer(TestRenderer):
    def render_html(self, obj: TestPrecisionByClass) -> TestHtmlInfo:
        info = super().render_html(obj)
        curr_matrix = obj.conf_matrix.get_result().current_matrix
        ref_matrix = obj.conf_matrix.get_result().reference_matrix
        fig = plot_conf_mtrx(curr_matrix, ref_matrix)
        info.with_details("Precision by Class", plotly_figure(title="", figure=fig))
        return info


class TestRecallByClass(ByClassClassificationTest):
    name: ClassVar[str] = "Recall Score by Class"

    def get_value(self, result: ClassMetric):
        return result.recall

    def get_description(self, value: Numeric) -> str:
        return (
            f"The recall score of the label **{self.label}** is {value:.3g}. "
            f"The test threshold is {self.get_condition()}"
        )


@default_renderer(wrap_type=TestRecallByClass)
class TestRecallByClassRenderer(TestRenderer):
    def render_html(self, obj: TestRecallByClass) -> TestHtmlInfo:
        info = super().render_html(obj)
        curr_matrix = obj.conf_matrix.get_result().current_matrix
        ref_matrix = obj.conf_matrix.get_result().reference_matrix
        fig = plot_conf_mtrx(curr_matrix, ref_matrix)
        info.with_details("Recall by Class", plotly_figure(title="", figure=fig))
        return info


class TestF1ByClass(ByClassClassificationTest):
    name: ClassVar[str] = "F1 Score by Class"

    def get_value(self, result: ClassMetric):
        return result.f1

    def get_description(self, value: Numeric) -> str:
        return (
            f"The F1 score of the label **{self.label}** is {value:.3g}. The test threshold is {self.get_condition()}"
        )


@default_renderer(wrap_type=TestF1ByClass)
class TestF1ByClassRenderer(TestRenderer):
    def render_html(self, obj: TestF1ByClass) -> TestHtmlInfo:
        info = super().render_html(obj)
        curr_matrix = obj.conf_matrix.get_result().current_matrix
        ref_matrix = obj.conf_matrix.get_result().reference_matrix
        fig = plot_conf_mtrx(curr_matrix, ref_matrix)
        info.with_details("F1 by Class", plotly_figure(title="", figure=fig))
        return info
