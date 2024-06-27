from abc import ABC
from typing import ClassVar
from typing import List
from typing import Optional
from typing import Union

from evidently.metrics import RegressionDummyMetric
from evidently.metrics import RegressionQualityMetric
from evidently.metrics.regression_performance.visualization import regression_perf_plot
from evidently.renderers.base_renderer import TestHtmlInfo
from evidently.renderers.base_renderer import TestRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import plotly_figure
from evidently.renderers.render_utils import plot_distr
from evidently.tests.base_test import BaseCheckValueTest
from evidently.tests.base_test import GroupData
from evidently.tests.base_test import GroupingTypes
from evidently.tests.base_test import TestValueCondition
from evidently.tests.utils import approx
from evidently.utils.types import Numeric
from evidently.utils.visualizations import plot_distr_with_cond_perc_button

REGRESSION_GROUP = GroupData("regression", "Regression", "")
GroupingTypes.TestGroup.add_value(REGRESSION_GROUP)


class BaseRegressionPerformanceMetricsTest(BaseCheckValueTest, ABC):
    group: ClassVar = REGRESSION_GROUP.id
    _metric: RegressionQualityMetric
    _dummy_metric: RegressionDummyMetric

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
        self._metric = RegressionQualityMetric()
        self._dummy_metric = RegressionDummyMetric()

    @property
    def metric(self):
        return self._metric

    @property
    def dummy_metric(self):
        return self._dummy_metric


class TestValueMAE(BaseRegressionPerformanceMetricsTest):
    name: ClassVar = "Mean Absolute Error (MAE)"

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition
        metric_result = self.metric.get_result()
        ref_mae = metric_result.reference.mean_abs_error if metric_result.reference is not None else None
        if ref_mae is not None:
            return TestValueCondition(eq=approx(ref_mae, relative=0.1))
        return TestValueCondition(lt=self.dummy_metric.get_result().mean_abs_error_default)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.mean_abs_error

    def get_description(self, value: Numeric) -> str:
        return f"The MAE is {value:.3}. The test threshold is {self.get_condition()}"


@default_renderer(wrap_type=TestValueMAE)
class TestValueMAERenderer(TestRenderer):
    def render_html(self, obj: TestValueMAE) -> TestHtmlInfo:
        info = super().render_html(obj)
        result = obj.metric.get_result()
        fig = regression_perf_plot(
            val_for_plot=result.vals_for_plots.mean_abs_error,
            hist_for_plot=result.hist_for_plot,
            name="MAE",
            curr_metric=result.current.mean_abs_error,
            ref_metric=result.reference.mean_abs_error if result.reference is not None else None,
            color_options=self.color_options,
        )
        info.with_details("MAE", plotly_figure(title="", figure=fig))
        return info


class TestValueMAPE(BaseRegressionPerformanceMetricsTest):
    name: ClassVar = "Mean Absolute Percentage Error (MAPE)"

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition
        metric_result = self.metric.get_result()
        ref_mae = metric_result.reference.mean_abs_perc_error if metric_result.reference is not None else None
        if ref_mae is not None:
            return TestValueCondition(eq=approx(ref_mae, relative=0.1))
        return TestValueCondition(lt=self.dummy_metric.get_result().mean_abs_perc_error_default)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.mean_abs_perc_error

    def get_description(self, value: Numeric) -> str:
        return f"The MAPE is {value:.3}. The test threshold is {self.get_condition()}."


@default_renderer(wrap_type=TestValueMAPE)
class TestValueMAPERenderer(TestRenderer):
    def render_html(self, obj: TestValueMAPE) -> TestHtmlInfo:
        info = super().render_html(obj)
        result = obj.metric.get_result()
        val_for_plot = result.vals_for_plots.mean_abs_perc_error
        val_for_plot = val_for_plot * 100
        fig = regression_perf_plot(
            val_for_plot=val_for_plot,
            hist_for_plot=result.hist_for_plot,
            name="MAPE",
            curr_metric=result.current.mean_abs_perc_error,
            ref_metric=result.reference.mean_abs_perc_error if result.reference is not None else None,
            color_options=self.color_options,
        )
        info.with_details("MAPE", plotly_figure(title="", figure=fig))
        return info


class TestValueRMSE(BaseRegressionPerformanceMetricsTest):
    name: ClassVar = "Root Mean Square Error (RMSE)"

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition
        metric_result = self.metric.get_result()
        rmse_ref = metric_result.reference.rmse if metric_result.reference is not None else None
        if rmse_ref is not None:
            return TestValueCondition(eq=approx(rmse_ref, relative=0.1))
        return TestValueCondition(lt=self.dummy_metric.get_result().rmse_default)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.rmse

    def get_description(self, value: Numeric) -> str:
        return f"The RMSE is {value:.3}. The test threshold is {self.get_condition()}."


@default_renderer(wrap_type=TestValueRMSE)
class TestValueRMSERenderer(TestRenderer):
    def render_html(self, obj: TestValueRMSE) -> TestHtmlInfo:
        info = super().render_html(obj)
        result = obj.metric.get_result()
        fig = regression_perf_plot(
            val_for_plot=result.vals_for_plots.rmse,
            hist_for_plot=result.hist_for_plot,
            name="RMSE",
            curr_metric=result.current.rmse,
            ref_metric=result.reference.rmse if result.reference is not None else None,
            color_options=self.color_options,
        )
        info.with_details("RMSE", plotly_figure(title="", figure=fig))
        return info


class TestValueMeanError(BaseRegressionPerformanceMetricsTest):
    name: ClassVar = "Mean Error (ME)"

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition
        return TestValueCondition(eq=approx(0, absolute=0.1 * self.metric.get_result().me_default_sigma))

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.mean_error

    def get_description(self, value: Numeric) -> str:
        return f"The ME is {value:.3}. The test threshold is {self.get_condition()}."


@default_renderer(wrap_type=TestValueMeanError)
class TestValueMeanErrorRenderer(TestRenderer):
    def render_html(self, obj: TestValueMeanError) -> TestHtmlInfo:
        info = super().render_html(obj)
        metric_result = obj.metric.get_result()
        me_hist_for_plot = metric_result.me_hist_for_plot
        hist_curr = me_hist_for_plot.current
        hist_ref = me_hist_for_plot.reference

        fig = plot_distr_with_cond_perc_button(
            hist_curr=hist_curr,
            hist_ref=hist_ref,
            xaxis_name="",
            yaxis_name="count",
            yaxis_name_perc="percent",
            color_options=self.color_options,
            to_json=False,
            condition=obj.get_condition(),
            value=metric_result.current.mean_error,
            value_name="current mean error",
        )
        # fig = plot_distr(hist_curr=hist_curr, hist_ref=hist_ref, color_options=self.color_options)
        # fig = plot_check(fig, obj.get_condition(), color_options=self.color_options)
        # fig = plot_metric_value(fig, metric_result.current.mean_error, "current mean error")
        info.with_details("", plotly_figure(title="", figure=fig))
        return info


class TestValueAbsMaxError(BaseRegressionPerformanceMetricsTest):
    name: ClassVar = "Max Absolute Error"

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition
        metric_result = self.metric.get_result()
        abs_error_max_ref = metric_result.reference.abs_error_max if metric_result.reference is not None else None
        if abs_error_max_ref is not None:
            return TestValueCondition(lte=approx(abs_error_max_ref, relative=0.1))
        return TestValueCondition(lte=self.dummy_metric.get_result().abs_error_max_default)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.abs_error_max

    def get_description(self, value: Numeric) -> str:
        return f"The Max Absolute Error is {value:.3}. The test threshold is {self.get_condition()}."


@default_renderer(wrap_type=TestValueAbsMaxError)
class TestValueAbsMaxErrorRenderer(TestRenderer):
    def render_html(self, obj: TestValueAbsMaxError) -> TestHtmlInfo:
        info = super().render_html(obj)
        me_hist_for_plot = obj.metric.get_result().me_hist_for_plot
        hist_curr = me_hist_for_plot.current
        hist_ref = me_hist_for_plot.reference

        fig = plot_distr(hist_curr=hist_curr, hist_ref=hist_ref, color_options=self.color_options)
        info.with_details("", plotly_figure(title="", figure=fig))
        return info


class TestValueR2Score(BaseRegressionPerformanceMetricsTest):
    name: ClassVar = "R2 Score"

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition
        result = self.metric.get_result()
        r2_score_ref = result.reference.r2_score if result.reference is not None else None
        if r2_score_ref is not None:
            return TestValueCondition(eq=approx(r2_score_ref, relative=0.1))
        return TestValueCondition(gt=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.r2_score

    def get_description(self, value: Numeric) -> str:
        return f"The R2 score is {value:.3}. The test threshold is {self.get_condition()}."


@default_renderer(wrap_type=TestValueR2Score)
class TestValueR2ScoreRenderer(TestRenderer):
    def render_html(self, obj: TestValueR2Score) -> TestHtmlInfo:
        info = super().render_html(obj)
        result = obj.metric.get_result()

        fig = regression_perf_plot(
            val_for_plot=result.vals_for_plots.r2_score,
            hist_for_plot=result.hist_for_plot,
            name="R2_score",
            curr_metric=result.current.r2_score,
            ref_metric=result.reference.r2_score if result.reference is not None else None,
            color_options=self.color_options,
        )
        info.with_details("R2 Score", plotly_figure(title="", figure=fig))
        return info
