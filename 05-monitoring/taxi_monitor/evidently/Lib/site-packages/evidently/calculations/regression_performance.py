from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd
from scipy.stats import probplot

from evidently.metric_results import DatasetColumns


class ErrorWithQuantiles:
    def __init__(self, error, quantile_top, quantile_other):
        self.error = error
        self.quantile_top = quantile_top
        self.quantile_other = quantile_other


@dataclass
class FeatureBias:
    feature_type: str
    majority: float
    under: float
    over: float
    range: float

    def as_dict(self, prefix):
        return {
            prefix + "majority": self.majority,
            prefix + "under": self.under,
            prefix + "over": self.over,
            prefix + "range": self.range,
        }


def _calculate_error_normality(error: ErrorWithQuantiles):
    qq_lines = probplot(error.error, dist="norm", plot=None)
    qq_dots = [t.tolist() for t in qq_lines[0]]
    qq_line = list(qq_lines[1])
    return {
        "order_statistic_medians_x": [float(x) for x in qq_dots[0]],
        "order_statistic_medians_y": [float(x) for x in qq_dots[1]],
        "slope": float(qq_line[0]),
        "intercept": float(qq_line[1]),
        "r": float(qq_line[2]),
    }


def _calculate_quality_metrics(dataset, prediction_column, target_column, conf_interval_n_sigmas=1):
    me = np.mean(dataset[prediction_column] - dataset[target_column])
    sde = np.std(dataset[prediction_column] - dataset[target_column], ddof=1)

    abs_err = np.abs(dataset[prediction_column] - dataset[target_column])
    abs_error_max = abs_err.max()
    mae = np.mean(abs_err)
    sdae = np.std(abs_err, ddof=1)

    epsilon = np.finfo(np.float64).eps
    abs_perc_err = np.abs(dataset[prediction_column] - dataset[target_column]) / np.maximum(
        dataset[target_column], epsilon
    )
    mape = 100.0 * np.mean(abs_perc_err)
    sdape = np.std(abs_perc_err, ddof=1)

    return {
        "mean_error": float(me),
        "mean_abs_error": float(mae),
        "mean_abs_perc_error": float(mape),
        "abs_error_max": abs_error_max,
        "error_std": conf_interval_n_sigmas * float(sde),
        "abs_error_std": conf_interval_n_sigmas * float(sdae),
        "abs_perc_error_std": conf_interval_n_sigmas * float(sdape),
    }


def _prepare_dataset(dataset, target_column, prediction_column):
    dataset.replace([np.inf, -np.inf], np.nan, inplace=True)
    dataset.dropna(axis=0, how="any", inplace=True, subset=[target_column, prediction_column])


def _calculate_underperformance(err_quantiles: ErrorWithQuantiles, conf_interval_n_sigmas: int = 1):
    error = err_quantiles.error
    quantile_top = err_quantiles.quantile_top
    quantile_other = err_quantiles.quantile_other
    mae_under = np.mean(error[error <= quantile_top])
    mae_exp = np.mean(error[(error > quantile_top) & (error < quantile_other)])
    mae_over = np.mean(error[error >= quantile_other])
    sd_under = np.std(error[error <= quantile_top], ddof=1)
    sd_exp = np.std(error[(error > quantile_top) & (error < quantile_other)], ddof=1)
    sd_over = np.std(error[error >= quantile_other], ddof=1)

    return {
        "majority": {
            "mean_error": float(mae_exp),
            "std_error": conf_interval_n_sigmas * float(sd_exp),
        },
        "underestimation": {
            "mean_error": float(mae_under),
            "std_error": conf_interval_n_sigmas * float(sd_under),
        },
        "overestimation": {
            "mean_error": float(mae_over),
            "std_error": conf_interval_n_sigmas * float(sd_over),
        },
    }


def error_bias_table(dataset, err_quantiles, num_feature_names, cat_feature_names) -> Dict[str, FeatureBias]:
    num_bias = {
        feature_name: _error_num_feature_bias(dataset, feature_name, err_quantiles)
        for feature_name in num_feature_names
    }
    cat_bias = {
        feature_name: _error_cat_feature_bias(dataset, feature_name, err_quantiles)
        for feature_name in cat_feature_names
    }
    error_bias = num_bias.copy()
    error_bias.update(cat_bias)
    return error_bias


def _error_num_feature_bias(dataset, feature_name, err_quantiles: ErrorWithQuantiles) -> FeatureBias:
    error = err_quantiles.error
    quantile_top = err_quantiles.quantile_top
    quantile_other = err_quantiles.quantile_other
    ref_overal_value = np.mean(dataset[feature_name])
    ref_under_value = np.mean(dataset[error <= quantile_top][feature_name])

    ref_over_value = np.mean(dataset[error >= quantile_other][feature_name])
    if ref_over_value == ref_under_value:
        ref_range_value = 0

    else:
        ref_range_value = (
            100
            * abs(ref_over_value - ref_under_value)
            / (np.max(dataset[feature_name]) - np.min(dataset[feature_name]))
        )

    return FeatureBias(
        feature_type="num",
        majority=float(ref_overal_value),
        under=float(ref_under_value),
        over=float(ref_over_value),
        range=float(ref_range_value),
    )


def _stable_value_counts(series: pd.Series):
    return series.value_counts().reindex(pd.unique(series))


def _error_cat_feature_bias(dataset, feature_name, err_quantiles: ErrorWithQuantiles) -> FeatureBias:
    error = err_quantiles.error
    quantile_top = err_quantiles.quantile_top
    quantile_other = err_quantiles.quantile_other
    ref_overall_value = _stable_value_counts(dataset[feature_name]).idxmax()
    ref_under_value = _stable_value_counts(dataset[error <= quantile_top][feature_name]).idxmax()
    ref_over_value = _stable_value_counts(dataset[error >= quantile_other][feature_name]).idxmax()
    if (
        (ref_overall_value != ref_under_value)
        or (ref_over_value != ref_overall_value)
        or (ref_under_value != ref_overall_value)
    ):
        ref_range_value = 1
    else:
        ref_range_value = 0

    if pd.isnull(ref_overall_value):
        ref_overall_value = None

    if pd.isnull(ref_under_value):
        ref_under_value = None

    if pd.isnull(ref_over_value):
        ref_over_value = None

    return FeatureBias(
        feature_type="cat",
        majority=ref_overall_value,
        under=ref_under_value,
        over=ref_over_value,
        range=float(ref_range_value),
    )


def error_with_quantiles(dataset, prediction_column, target_column, quantile: float):
    error = dataset[prediction_column] - dataset[target_column]

    # underperformance metrics
    quantile_top = np.quantile(error, quantile)
    quantile_other = np.quantile(error, 1 - quantile)
    return ErrorWithQuantiles(error, quantile_top, quantile_other)


@dataclass
class RegressionPerformanceMetrics:
    mean_error: float
    mean_abs_error: float
    mean_abs_perc_error: float
    error_std: float
    abs_error_max: float
    abs_error_std: float
    abs_perc_error_std: float
    error_normality: dict
    underperformance: dict
    error_bias: dict


def calculate_regression_performance(
    dataset: pd.DataFrame, columns: DatasetColumns, error_bias_prefix: str
) -> RegressionPerformanceMetrics:
    target_column = columns.utility_columns.target
    prediction_column = columns.utility_columns.prediction

    num_feature_names = columns.num_feature_names
    cat_feature_names = columns.cat_feature_names

    if target_column is None or prediction_column is None:
        raise ValueError("Target and prediction should be present")

    _prepare_dataset(dataset, target_column, prediction_column)
    # calculate quality metrics
    quality_metrics = _calculate_quality_metrics(dataset, prediction_column, target_column)
    # error normality
    err_quantiles = error_with_quantiles(dataset, prediction_column, target_column, quantile=0.05)
    quality_metrics["error_normality"] = _calculate_error_normality(err_quantiles)
    # underperformance metrics
    quality_metrics["underperformance"] = _calculate_underperformance(err_quantiles)
    quality_metrics["error_bias"] = {}
    feature_bias = error_bias_table(dataset, err_quantiles, num_feature_names, cat_feature_names)
    # convert to old format
    quality_metrics["error_bias"] = {
        feature: dict(feature_type=bias.feature_type, **bias.as_dict(error_bias_prefix))
        for feature, bias in feature_bias.items()
    }
    return RegressionPerformanceMetrics(**quality_metrics)
