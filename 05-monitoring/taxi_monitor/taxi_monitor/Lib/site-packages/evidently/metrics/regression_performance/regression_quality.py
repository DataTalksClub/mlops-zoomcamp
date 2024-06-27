from typing import Dict
from typing import List
from typing import Optional
from typing import Set

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
from evidently.metrics.regression_performance.regression_performance_metrics import RegressionMetrics
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


class MoreRegressionMetrics(RegressionMetrics):
    class Config:
        field_tags: Dict[str, Set[IncludeTags]] = {"underperformance": set()}

    error_std: float
    abs_error_std: float
    abs_perc_error_std: float


class RegressionQualityMetricResults(MetricResult):
    class Config:
        dict_exclude_fields = {"hist_for_plot", "vals_for_plots", "me_hist_for_plot"}
        pd_exclude_fields = {"hist_for_plot", "vals_for_plots", "me_hist_for_plot", "error_normality", "error_bias"}
        field_tags = {
            "current": {IncludeTags.Current},
            "reference": {IncludeTags.Reference},
            "rmse_default": {IncludeTags.Extra},
            "me_default_sigma": {IncludeTags.Extra},
            "mean_abs_error_default": {IncludeTags.Extra},
            "mean_abs_perc_error_default": {IncludeTags.Extra},
            "abs_error_max_default": {IncludeTags.Extra},
            "error_normality": {IncludeTags.Extra},
            "vals_for_plots": {IncludeTags.Render},
            "error_bias": {IncludeTags.Extra},
        }

    columns: DatasetColumns
    current: MoreRegressionMetrics
    reference: Optional[MoreRegressionMetrics]
    rmse_default: float
    me_default_sigma: float
    me_hist_for_plot: Histogram
    mean_abs_error_default: float
    mean_abs_perc_error_default: float
    abs_error_max_default: float
    error_normality: dict
    hist_for_plot: Histogram
    vals_for_plots: RegressionMetricsScatter
    error_bias: Optional[dict] = None


class RegressionQualityMetric(Metric[RegressionQualityMetricResults]):
    def calculate(self, data: InputData) -> RegressionQualityMetricResults:
        dataset_columns = process_columns(data.current_data, data.column_mapping)
        target_name = dataset_columns.utility_columns.target
        prediction_name = dataset_columns.utility_columns.prediction

        if target_name is None or prediction_name is None:
            raise ValueError("The columns 'target' and 'prediction' columns should be present")
        if not isinstance(prediction_name, str):
            raise ValueError("Expect one column for prediction. List of columns was provided.")
        current_metrics = calculate_regression_performance(
            dataset=data.current_data,
            columns=dataset_columns,
            error_bias_prefix="current_",
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
            y_true=data.current_data[target_name],
            y_pred=data.current_data[prediction_name],
        )
        rmse_score_value = mean_squared_error(
            y_true=data.current_data[target_name],
            y_pred=data.current_data[prediction_name],
            squared=False,
        )

        # mae default values
        dummy_preds = data.current_data[target_name].median()
        mean_abs_error_default = mean_absolute_error(
            y_true=data.current_data[target_name],
            y_pred=[dummy_preds] * data.current_data.shape[0],
        )
        # rmse default values
        rmse_ref = None
        if data.reference_data is not None:
            rmse_ref = mean_squared_error(
                y_true=data.reference_data[target_name],
                y_pred=data.reference_data[prediction_name],
                squared=False,
            )
        dummy_preds = data.current_data[target_name].mean()
        rmse_default = mean_squared_error(
            y_true=data.current_data[target_name],
            y_pred=[dummy_preds] * data.current_data.shape[0],
            squared=False,
        )
        # mape default values
        # optimal constant for mape
        s = data.current_data[target_name]
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
                y_true=data.current_data[target_name],
                y_pred=[dummy_preds] * data.current_data.shape[0],
            )
            * 100
        )
        #  r2_score default values
        r2_score_ref = None
        if data.reference_data is not None:
            r2_score_ref = r2_score(
                y_true=data.reference_data[target_name],
                y_pred=data.reference_data[prediction_name],
            )
        # max error default values
        abs_error_max_ref = None
        mean_error_ref = None

        if reference_metrics is not None:
            abs_error_max_ref = reference_metrics.abs_error_max
            mean_error_ref = reference_metrics.mean_error

        y_true = data.current_data[target_name]
        y_pred = data.current_data[prediction_name]
        abs_error_max_default = np.abs(y_true - y_true.median()).max()

        #  me default values
        me_default_sigma = (y_pred - y_true).std()

        # visualisation

        df_target_binned = make_target_bins_for_reg_plots(
            data.current_data, target_name, prediction_name, data.reference_data
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
                df_target_binned, func, target_name, prediction_name, is_ref_data
            )

        # me plot
        err_curr = data.current_data[prediction_name] - data.current_data[target_name]
        err_ref = None

        if is_ref_data:
            err_ref = data.reference_data[prediction_name] - data.reference_data[target_name]
        me_hist_for_plot = make_hist_for_num_plot(err_curr, err_ref)

        if r2_score_ref is not None:
            r2_score_ref = float(r2_score_ref)

        if rmse_ref is not None:
            rmse_ref = float(rmse_ref)

        underperformance_ref = None

        if reference_metrics is not None:
            underperformance_ref = reference_metrics.underperformance

        reference = None
        if reference_metrics is not None:
            reference = MoreRegressionMetrics(
                mean_error=mean_error_ref,
                underperformance=underperformance_ref,
                mean_abs_error=reference_metrics.mean_abs_error,
                mean_abs_perc_error=reference_metrics.mean_abs_perc_error,
                error_std=reference_metrics.error_std,
                abs_error_std=reference_metrics.abs_error_std,
                abs_perc_error_std=reference_metrics.abs_perc_error_std,
                rmse=rmse_ref,
                r2_score=r2_score_ref,
                abs_error_max=abs_error_max_ref,
            )

        return RegressionQualityMetricResults(
            columns=dataset_columns,
            current=MoreRegressionMetrics(
                r2_score=r2_score_value,
                rmse=rmse_score_value,
                mean_error=current_metrics.mean_error,
                mean_abs_error=current_metrics.mean_abs_error,
                mean_abs_perc_error=current_metrics.mean_abs_perc_error,
                abs_error_max=current_metrics.abs_error_max,
                error_std=current_metrics.error_std,
                abs_error_std=current_metrics.abs_error_std,
                abs_perc_error_std=current_metrics.abs_perc_error_std,
                underperformance=current_metrics.underperformance,
            ),
            reference=reference,
            rmse_default=rmse_default,
            me_default_sigma=me_default_sigma,
            me_hist_for_plot=me_hist_for_plot,
            mean_abs_error_default=mean_abs_error_default,
            mean_abs_perc_error_default=mean_abs_perc_error_default,
            abs_error_max_default=abs_error_max_default,
            error_normality=current_metrics.error_normality,
            hist_for_plot=hist_for_plot,
            vals_for_plots=RegressionMetricsScatter(**vals_for_plots),
            error_bias=error_bias,
        )


@default_renderer(wrap_type=RegressionQualityMetric)
class RegressionQualityMetricRenderer(MetricRenderer):
    def render_html(self, obj: RegressionQualityMetric) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        target_name = metric_result.columns.utility_columns.target
        result = [
            header_text(label=f"Regression Model Performance. Target: '{target_name}’"),
            counter(
                title="Current: Model Quality (+/- std)",
                counters=[
                    CounterData(
                        "ME",
                        f"{round(metric_result.current.mean_error, 2)} ({round(metric_result.current.error_std, 2)})",
                    ),
                    CounterData(
                        "MAE",
                        f"{round(metric_result.current.mean_abs_error, 2)} ({round(metric_result.current.abs_error_std, 2)})",
                    ),
                    CounterData(
                        "MAPE",
                        (
                            f"{round(metric_result.current.mean_abs_perc_error, 2)}"
                            f" ({round(metric_result.current.abs_perc_error_std, 2)})"
                        ),
                    ),
                ],
            ),
        ]
        if metric_result.reference is not None:
            result.append(
                counter(
                    title="Reference: Model Quality (+/- std)",
                    counters=[
                        CounterData(
                            "ME",
                            f"{round(metric_result.reference.mean_error, 2)} ({round(metric_result.reference.error_std, 2)})",
                        ),
                        CounterData(
                            "MAE",
                            (
                                f"{round(metric_result.reference.mean_abs_error, 2)}"
                                f" ({round(metric_result.reference.abs_error_std, 2)})"
                            ),
                        ),
                        CounterData(
                            "MAPE",
                            (
                                f"{round(metric_result.reference.mean_abs_perc_error, 2)}"
                                f" ({round(metric_result.reference.abs_perc_error_std, 2)})"
                            ),
                        ),
                    ],
                ),
            )
        return result
