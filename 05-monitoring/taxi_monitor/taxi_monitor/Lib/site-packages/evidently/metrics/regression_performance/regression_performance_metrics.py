from typing import Dict
from typing import List
from typing import Optional

import numpy as np
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.calculations.regression_performance import calculate_regression_performance
from evidently.core import IncludeTags
from evidently.metric_results import DatasetColumns
from evidently.metric_results import Histogram
from evidently.metrics.regression_performance.objects import RegressionMetricScatter
from evidently.metrics.regression_performance.objects import RegressionMetricsScatter
from evidently.metrics.regression_performance.utils import apply_func_to_binned_data
from evidently.metrics.utils import make_target_bins_for_reg_plots
from evidently.model.widget import BaseWidgetInfo
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import CounterData
from evidently.renderers.html_widgets import counter
from evidently.renderers.html_widgets import header_text
from evidently.utils.data_operations import process_columns
from evidently.utils.visualizations import make_hist_for_cat_plot
from evidently.utils.visualizations import make_hist_for_num_plot


class RegressionMetrics(MetricResult):
    class Config:
        pd_exclude_fields = {"underperformance"}
        field_tags = {"underperformance": {IncludeTags.Extra}}

    r2_score: float
    rmse: float
    mean_error: float
    mean_abs_error: float
    mean_abs_perc_error: float
    abs_error_max: float
    underperformance: dict


class RegressionPerformanceMetricsResults(MetricResult):
    class Config:
        dict_exclude_fields = {"hist_for_plot", "vals_for_plots", "me_hist_for_plot"}
        pd_exclude_fields = {"hist_for_plot", "vals_for_plots", "me_hist_for_plot", "error_bias", "error_normality"}
        field_tags = {
            "current": {IncludeTags.Current},
            "reference": {IncludeTags.Reference},
            "rmse_default": {IncludeTags.Extra},
            "me_default_sigma": {IncludeTags.Extra},
            "mean_abs_error_default": {IncludeTags.Extra},
            "mean_abs_perc_error_default": {IncludeTags.Extra},
            "abs_error_max_default": {IncludeTags.Extra},
            "error_std": {IncludeTags.Extra},
            "abs_error_std": {IncludeTags.Extra},
            "abs_perc_error_std": {IncludeTags.Extra},
            "error_normality": {IncludeTags.Extra},
            "vals_for_plots": {IncludeTags.Render},
            "error_bias": {IncludeTags.Extra},
        }

    columns: DatasetColumns

    current: RegressionMetrics
    reference: Optional[RegressionMetrics]

    rmse_default: float

    me_default_sigma: float
    me_hist_for_plot: Histogram
    mean_abs_error_default: float
    mean_abs_perc_error_default: float
    abs_error_max_default: float
    error_std: float
    abs_error_std: float
    abs_perc_error_std: float
    error_normality: dict
    hist_for_plot: Histogram
    vals_for_plots: RegressionMetricsScatter
    error_bias: Optional[dict] = None


class RegressionPerformanceMetrics(Metric[RegressionPerformanceMetricsResults]):
    def get_parameters(self) -> tuple:
        return ()

    def calculate(self, data: InputData) -> RegressionPerformanceMetricsResults:
        columns = process_columns(data.current_data, data.column_mapping)

        current_metrics = calculate_regression_performance(
            dataset=data.current_data, columns=columns, error_bias_prefix="current_"
        )
        error_bias = current_metrics.error_bias
        reference_metrics = None

        if data.reference_data is not None:
            ref_columns = process_columns(data.reference_data, data.column_mapping)
            reference_metrics = calculate_regression_performance(
                dataset=data.reference_data,
                columns=ref_columns,
                error_bias_prefix="ref_",
            )

            if reference_metrics is not None and reference_metrics.error_bias:
                for feature_name, current_bias in reference_metrics.error_bias.items():
                    if feature_name in error_bias:
                        error_bias[feature_name].update(current_bias)

                    else:
                        error_bias[feature_name] = current_bias

        r2_score_value = r2_score(
            y_true=data.current_data[data.column_mapping.target],
            y_pred=data.current_data[data.column_mapping.prediction],
        )
        rmse_score_value = mean_squared_error(
            y_true=data.current_data[data.column_mapping.target],
            y_pred=data.current_data[data.column_mapping.prediction],
            squared=False,
        )

        # mae default values
        dummy_preds = data.current_data[data.column_mapping.target].median()
        mean_abs_error_default = mean_absolute_error(
            y_true=data.current_data[data.column_mapping.target],
            y_pred=[dummy_preds] * data.current_data.shape[0],
        )
        # rmse default values
        rmse_ref = None
        if data.reference_data is not None:
            rmse_ref = mean_squared_error(
                y_true=data.reference_data[data.column_mapping.target],
                y_pred=data.reference_data[data.column_mapping.prediction],
                squared=False,
            )
        dummy_preds = data.current_data[data.column_mapping.target].mean()
        rmse_default = mean_squared_error(
            y_true=data.current_data[data.column_mapping.target],
            y_pred=[dummy_preds] * data.current_data.shape[0],
            squared=False,
        )
        # mape default values
        # optimal constant for mape
        s = data.current_data[data.column_mapping.target]
        inv_y = 1 / s[s != 0].values
        w = inv_y / sum(inv_y)
        idxs = np.argsort(w)
        sorted_w = w[idxs]
        sorted_w_cumsum = np.cumsum(sorted_w)
        idx = np.where(sorted_w_cumsum > 0.5)[0][0]
        pos = idxs[idx]
        dummy_preds = s[s != 0].values[pos]

        mean_abs_perc_error_default = (
            mean_absolute_percentage_error(
                y_true=data.current_data[data.column_mapping.target],
                y_pred=[dummy_preds] * data.current_data.shape[0],
            )
            * 100
        )
        #  r2_score default values
        r2_score_ref = None
        if data.reference_data is not None:
            r2_score_ref = r2_score(
                y_true=data.reference_data[data.column_mapping.target],
                y_pred=data.reference_data[data.column_mapping.prediction],
            )
        # max error default values
        abs_error_max_ref = None
        mean_error_ref = None

        if reference_metrics is not None:
            abs_error_max_ref = reference_metrics.abs_error_max
            mean_error_ref = reference_metrics.mean_error

        y_true = data.current_data[data.column_mapping.target]
        y_pred = data.current_data[data.column_mapping.prediction]
        abs_error_max_default = np.abs(y_true - y_true.median()).max()

        #  me default values
        me_default_sigma = (y_pred - y_true).std()

        # visualisation

        df_target_binned = make_target_bins_for_reg_plots(
            data.current_data,
            data.column_mapping.target,
            data.column_mapping.prediction,
            data.reference_data,
        )
        curr_target_bins = df_target_binned.loc[df_target_binned.data == "curr", "target_binned"]
        ref_target_bins = None
        if data.reference_data is not None:
            ref_target_bins = df_target_binned.loc[df_target_binned.data == "ref", "target_binned"]
        hist_for_plot = make_hist_for_cat_plot(curr_target_bins, ref_target_bins)

        vals_for_plots: Dict[str, RegressionMetricScatter] = {}

        if data.reference_data is not None:
            is_ref_data = True

        else:
            is_ref_data = False

        for name, func in zip(
            ["r2_score", "rmse", "mean_abs_error", "mean_abs_perc_error"],
            [
                r2_score,
                lambda x, y: mean_squared_error(x, y, squared=False),
                mean_absolute_error,
                mean_absolute_percentage_error,
            ],
        ):
            vals_for_plots[name] = apply_func_to_binned_data(
                df_target_binned,
                func,
                data.column_mapping.target,
                data.column_mapping.prediction,
                is_ref_data,
            )

        # me plot
        err_curr = data.current_data[data.column_mapping.prediction] - data.current_data[data.column_mapping.target]
        err_ref = None

        if is_ref_data:
            err_ref = (
                data.reference_data[data.column_mapping.prediction] - data.reference_data[data.column_mapping.target]
            )
        me_hist_for_plot = make_hist_for_num_plot(err_curr, err_ref)

        if r2_score_ref is not None:
            r2_score_ref = float(r2_score_ref)

        if rmse_ref is not None:
            rmse_ref = float(rmse_ref)

        underperformance_ref = None

        if reference_metrics is not None:
            underperformance_ref = reference_metrics.underperformance

        if reference_metrics is not None:
            reference = RegressionMetrics(
                mean_error=mean_error_ref,
                underperformance=underperformance_ref,
                mean_abs_error=reference_metrics.mean_abs_error,
                mean_abs_perc_error=reference_metrics.mean_abs_perc_error,
                rmse=rmse_ref,
                r2_score=r2_score_ref,
                abs_error_max=abs_error_max_ref,
            )
        else:
            reference = None
        return RegressionPerformanceMetricsResults(
            columns=columns,
            current=RegressionMetrics(
                r2_score=r2_score_value,
                rmse=rmse_score_value,
                mean_error=current_metrics.mean_error,
                mean_abs_error=current_metrics.mean_abs_error,
                mean_abs_perc_error=current_metrics.mean_abs_perc_error,
                abs_error_max=current_metrics.abs_error_max,
                underperformance=current_metrics.underperformance,
            ),
            reference=reference,
            rmse_default=rmse_default,
            me_default_sigma=me_default_sigma,
            me_hist_for_plot=me_hist_for_plot,
            mean_abs_error_default=mean_abs_error_default,
            mean_abs_perc_error_default=mean_abs_perc_error_default,
            abs_error_max_default=abs_error_max_default,
            error_std=current_metrics.error_std,
            abs_error_std=current_metrics.abs_error_std,
            abs_perc_error_std=current_metrics.abs_perc_error_std,
            error_normality=current_metrics.error_normality,
            hist_for_plot=hist_for_plot,
            vals_for_plots=RegressionMetricsScatter(**vals_for_plots),
            error_bias=error_bias,
        )


@default_renderer(wrap_type=RegressionPerformanceMetrics)
class RegressionPerformanceMetricsRenderer(MetricRenderer):
    @staticmethod
    def _get_underperformance_tails(dataset_name: str, underperformance: dict) -> BaseWidgetInfo:
        return counter(
            title=f"{dataset_name.capitalize()}: Mean Error per Group (+/- std)",
            counters=[
                CounterData.float("Majority(90%)", underperformance["majority"]["mean_error"], 2),
                CounterData.float(
                    "Underestimation(5%)",
                    underperformance["underestimation"]["mean_error"],
                    2,
                ),
                CounterData.float(
                    "Overestimation(5%)",
                    underperformance["overestimation"]["mean_error"],
                    2,
                ),
            ],
        )

    def render_html(self, obj: RegressionPerformanceMetrics) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        target_name = metric_result.columns.utility_columns.target
        result = [
            header_text(label=f"Regression Model Performance. Target: '{target_name}’"),
            counter(
                title="Current: Regression Performance Metrics",
                counters=[
                    CounterData.float("Mean error", metric_result.current.mean_error, 3),
                    CounterData.float("MAE", metric_result.current.mean_abs_error, 3),
                    CounterData.float("MAPE", metric_result.current.mean_abs_perc_error, 3),
                    CounterData.float("RMSE", metric_result.current.rmse, 3),
                    CounterData.float("r2 score", metric_result.current.r2_score, 3),
                ],
            ),
        ]
        if metric_result.reference is not None:
            result.append(
                counter(
                    title="Reference: Regression Performance Metrics",
                    counters=[
                        CounterData.float("Mean error", metric_result.reference.mean_error, 3),
                        CounterData.float("MAE", metric_result.reference.mean_abs_error, 3),
                        CounterData.float("MAPE", metric_result.reference.mean_abs_perc_error, 3),
                        CounterData.float("RMSE", metric_result.reference.rmse, 3),
                        CounterData.float("r2 score", metric_result.reference.r2_score, 3),
                    ],
                ),
            )

        return result
