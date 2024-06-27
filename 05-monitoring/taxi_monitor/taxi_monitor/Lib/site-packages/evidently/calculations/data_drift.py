"""Methods and types for data drift calculations."""

from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

import numpy as np
import pandas as pd

from evidently.base_metric import ColumnMetricResult
from evidently.base_metric import MetricResult
from evidently.calculations.stattests import get_stattest
from evidently.core import ColumnType
from evidently.core import IncludeTags
from evidently.metric_results import DatasetColumns
from evidently.metric_results import Distribution
from evidently.metric_results import DistributionIncluded
from evidently.metric_results import ScatterAggField
from evidently.metric_results import ScatterField
from evidently.metric_results import raw_agg_properties
from evidently.options.data_drift import DataDriftOptions
from evidently.utils.data_drift_utils import get_text_data_for_plots
from evidently.utils.data_operations import recognize_column_type_
from evidently.utils.types import Numeric
from evidently.utils.visualizations import get_distribution_for_column
from evidently.utils.visualizations import prepare_df_for_time_index_plot

Examples = List[str]
Words = List[str]


class DriftStatsField(MetricResult):
    class Config:
        dict_exclude_fields = {"characteristic_examples", "characteristic_words", "correlations"}
        # todo: after tests PR
        field_tags = {
            "characteristic_examples": {IncludeTags.Render},
            "characteristic_words": {IncludeTags.Render},
            "correlations": {IncludeTags.Render},
            "small_distribution": {IncludeTags.Extra},
        }
        pd_include = False

    distribution: Optional[Distribution]
    characteristic_examples: Optional[Examples]
    characteristic_words: Optional[Words]
    small_distribution: Optional[DistributionIncluded]
    correlations: Optional[Dict[str, float]]


class ColumnDataDriftMetrics(ColumnMetricResult):
    class Config:
        # todo: change to field_tags: render
        dict_exclude_fields = {"scatter"}
        pd_exclude_fields = {"scatter"}
        field_tags = {
            "stattest_name": {IncludeTags.Parameter},
            "current": {IncludeTags.Current},
            "reference": {IncludeTags.Reference},
        }

    stattest_name: str
    stattest_threshold: Optional[float]
    drift_score: Numeric
    drift_detected: bool

    current: DriftStatsField
    reference: DriftStatsField

    scatter: Optional[Union[ScatterField, ScatterAggField]]
    scatter_raw, scatter_agg = raw_agg_properties("scatter", ScatterField, ScatterAggField, True)


@dataclass
class DatasetDrift:
    """Dataset drift calculation results"""

    number_of_drifted_columns: int
    dataset_drift_score: float
    dataset_drift: bool


class DatasetDriftMetrics(MetricResult):
    number_of_columns: int
    number_of_drifted_columns: int
    share_of_drifted_columns: float
    dataset_drift: bool
    drift_by_columns: Dict[str, ColumnDataDriftMetrics]
    options: DataDriftOptions
    dataset_columns: DatasetColumns


def get_one_column_drift(
    *,
    current_data: pd.DataFrame,
    reference_data: pd.DataFrame,
    column_name: str,
    options: DataDriftOptions,
    dataset_columns: DatasetColumns,
    column_type: ColumnType,
    agg_data: bool,
    num_correlations: Optional[tuple] = None,
    is_contains_nans: Optional[Tuple[pd.Series, pd.Series]] = None,
) -> ColumnDataDriftMetrics:
    if column_name not in current_data:
        raise ValueError(f"Cannot find column '{column_name}' in current dataset")

    if column_name not in reference_data:
        raise ValueError(f"Cannot find column '{column_name}' in reference dataset")

    if column_type not in (ColumnType.Numerical, ColumnType.Categorical, ColumnType.Text):
        raise ValueError(f"Cannot calculate drift metric for column '{column_name}' with type {column_type}")

    stattest = None

    if column_name == dataset_columns.utility_columns.target and column_type == ColumnType.Numerical:
        stattest = options.num_target_stattest_func

    elif column_name == dataset_columns.utility_columns.target and column_type == ColumnType.Categorical:
        stattest = options.cat_target_stattest_func

    if not stattest:
        stattest = options.get_feature_stattest_func(column_name, column_type.value)

    threshold = options.get_threshold(column_name, column_type.value)
    current_column = current_data[column_name]
    reference_column = reference_data[column_name]

    # clean and check the column in reference dataset
    if is_contains_nans is None or is_contains_nans[1][column_name]:
        reference_column = reference_column.replace([-np.inf, np.inf], np.nan).dropna()

    if reference_column.empty:
        raise ValueError(
            f"An empty column '{column_name}' was provided for drift calculation in the reference dataset."
        )

    # clean and check the column in current dataset
    if is_contains_nans is None or is_contains_nans[0][column_name]:
        current_column = current_column.replace([-np.inf, np.inf], np.nan).dropna()

    if current_column.empty:
        raise ValueError(f"An empty column '{column_name}' was provided for drift calculation in the current dataset.")

    current_distribution = None
    reference_distribution = None
    current_small_distribution = None
    reference_small_distribution = None
    current_correlations = None
    reference_correlations = None

    typical_examples_cur = None
    typical_examples_ref = None
    typical_words_cur = None
    typical_words_ref = None

    if column_type == ColumnType.Numerical:
        if not pd.api.types.is_numeric_dtype(reference_column):
            raise ValueError(f"Column '{column_name}' in reference dataset should contain numerical values only.")

        if not pd.api.types.is_numeric_dtype(current_column):
            raise ValueError(f"Column '{column_name}' in current dataset should contain numerical values only.")

    drift_test_function = get_stattest(reference_column, current_column, column_type, stattest)
    drift_result = drift_test_function(reference_column, current_column, column_type, threshold)

    scatter: Optional[Union[ScatterField, ScatterAggField]] = None
    if column_type == ColumnType.Numerical:
        numeric_columns = dataset_columns.num_feature_names

        if column_name not in numeric_columns:
            # for target and prediction cases add the column_name in the numeric columns list
            numeric_columns = numeric_columns + [column_name]

        if num_correlations is None:
            num_correlations = (current_data[numeric_columns].corr(), reference_data[numeric_columns].corr())

        current_correlations = num_correlations[0][column_name].to_dict()
        reference_correlations = num_correlations[1][column_name].to_dict()
        current_nbinsx = options.get_nbinsx(column_name)
        current_small_distribution = [
            t.tolist()
            for t in np.histogram(
                current_data[column_name][np.isfinite(current_data[column_name])],
                bins=current_nbinsx,
                density=True,
            )
        ]
        reference_small_distribution = [
            t.tolist()
            for t in np.histogram(
                reference_data[column_name][np.isfinite(reference_data[column_name])],
                bins=current_nbinsx,
                density=True,
            )
        ]
        datetime_column_name = dataset_columns.utility_columns.date
        if not agg_data:
            current_scatter = {column_name: current_data[column_name]}
            if datetime_column_name is not None:
                current_scatter["Timestamp"] = current_data[datetime_column_name]
                x_name = "Timestamp"
            else:
                current_scatter["Index"] = current_data.index
                x_name = "Index"
        else:
            current_scatter = {}
            if is_contains_nans is None or is_contains_nans[0].any():
                curr_data = current_data.copy()
                curr_data.dropna(axis=0, how="any", inplace=True, subset=[column_name])
            else:
                curr_data = current_data

            df, prefix = prepare_df_for_time_index_plot(
                curr_data,
                column_name,
                datetime_column_name,
            )
            current_scatter["current (mean)"] = df
            if prefix is None:
                x_name = "Index binned"
            else:
                if datetime_column_name is not None:
                    name = datetime_column_name
                elif curr_data.index.name is not None:
                    name = curr_data.index.name
                else:
                    name = "Index"
                x_name = f"{name} ({prefix})"

        plot_shape = {}
        reference_mean = reference_data[column_name].mean()
        reference_std = reference_data[column_name].std()
        plot_shape["y0"] = reference_mean - reference_std
        plot_shape["y1"] = reference_mean + reference_std
        if agg_data:
            scatter = ScatterAggField(scatter=current_scatter, x_name=x_name, plot_shape=plot_shape)
        else:
            scatter = ScatterField(scatter=current_scatter, x_name=x_name, plot_shape=plot_shape)

    elif column_type == ColumnType.Categorical:
        reference_counts = reference_data[column_name].value_counts(sort=False)
        current_counts = current_data[column_name].value_counts(sort=False)
        keys = set(reference_counts.keys()).union(set(current_counts.keys()))

        for key in keys:
            if key not in reference_counts:
                reference_counts = pd.concat([reference_counts, pd.Series([0], index=[key])])
            if key not in current_counts:
                current_counts = pd.concat([current_counts, pd.Series([0], index=[key])])

        reference_small_distribution = list(
            reversed(
                list(
                    map(
                        list,
                        zip(*sorted(reference_counts.items(), key=lambda x: str(x[0]))),
                    )
                )
            )
        )
        current_small_distribution = list(
            reversed(
                list(
                    map(
                        list,
                        zip(*sorted(current_counts.items(), key=lambda x: str(x[0]))),
                    )
                )
            )
        )
    if column_type != ColumnType.Text:
        if (
            column_type == ColumnType.Categorical
            and dataset_columns.target_names is not None
            and (
                column_name == dataset_columns.utility_columns.target
                or (
                    isinstance(dataset_columns.utility_columns.prediction, str)
                    and column_name == dataset_columns.utility_columns.prediction
                )
            )
        ):
            column_values = np.union1d(current_column.unique(), reference_column.unique())
            new_values = np.setdiff1d(list(dataset_columns.target_names), column_values)
            if len(new_values) > 0:
                raise ValueError(f"Values {new_values} not presented in 'target_names'")
            else:
                current_column = current_column.map(dataset_columns.target_names)
                reference_column = reference_column.map(dataset_columns.target_names)
        current_distribution, reference_distribution = get_distribution_for_column(
            column_type=column_type.value,
            current=current_column,
            reference=reference_column,
        )
        if reference_distribution is None:
            raise ValueError(f"Cannot calculate reference distribution for column '{column_name}'.")

    elif column_type == ColumnType.Text and drift_result.drifted:
        (
            typical_examples_cur,
            typical_examples_ref,
            typical_words_cur,
            typical_words_ref,
        ) = get_text_data_for_plots(reference_column, current_column)

    metrics = ColumnDataDriftMetrics(
        column_name=column_name,
        column_type=column_type.value,
        stattest_name=drift_test_function.display_name,
        drift_score=drift_result.drift_score,
        drift_detected=drift_result.drifted,
        stattest_threshold=drift_result.actual_threshold,
        current=DriftStatsField(
            distribution=current_distribution,
            small_distribution=DistributionIncluded(x=current_small_distribution[1], y=current_small_distribution[0])
            if current_small_distribution
            else None,
            correlations=current_correlations,
            characteristic_examples=typical_examples_cur,
            characteristic_words=typical_words_cur,
        ),
        reference=DriftStatsField(
            distribution=reference_distribution,
            small_distribution=DistributionIncluded(
                x=reference_small_distribution[1], y=reference_small_distribution[0]
            )
            if reference_small_distribution
            else None,
            characteristic_examples=typical_examples_ref,
            characteristic_words=typical_words_ref,
            correlations=reference_correlations,
        ),
        scatter=scatter,
    )

    return metrics


def _get_pred_labels_from_prob(dataframe: pd.DataFrame, prediction_column: list) -> List[str]:
    """Get labels from probabilities from columns by prediction columns list"""
    array_prediction = dataframe[prediction_column].to_numpy()
    prediction_ids = np.argmax(array_prediction, axis=-1)
    prediction_labels = [prediction_column[x] for x in prediction_ids]
    return prediction_labels


def ensure_prediction_column_is_string(
    *,
    prediction_column: Optional[Union[str, Sequence]],
    current_data: pd.DataFrame,
    reference_data: pd.DataFrame,
    threshold: float = 0.5,
) -> Optional[str]:
    """Update dataset by predictions type:

    - if prediction column is None or a string, no dataset changes
    - (binary classification) if predictions is a list and its length equals 2
        set predicted_labels column by `threshold`
    - (multy label classification) if predictions is a list and its length is greater than 2
        set predicted_labels from probability values in columns by prediction column


    Returns:
         prediction column name.
    """
    result_prediction_column = None

    if prediction_column is None or isinstance(prediction_column, str):
        result_prediction_column = prediction_column

    elif isinstance(prediction_column, list):
        if len(prediction_column) > 2:
            reference_data["predicted_labels"] = _get_pred_labels_from_prob(reference_data, prediction_column)
            current_data["predicted_labels"] = _get_pred_labels_from_prob(current_data, prediction_column)
            result_prediction_column = "predicted_labels"

        elif len(prediction_column) == 2:
            reference_data["predicted_labels"] = (reference_data[prediction_column[0]] > threshold).astype(int)
            current_data["predicted_labels"] = (current_data[prediction_column[0]] > threshold).astype(int)
            result_prediction_column = "predicted_labels"

    return result_prediction_column


def get_dataset_drift(drift_metrics: Dict[str, ColumnDataDriftMetrics], drift_share=0.5) -> DatasetDrift:
    number_of_drifted_columns = sum([1 if drift.drift_detected else 0 for _, drift in drift_metrics.items()])
    share_drifted_columns = number_of_drifted_columns / len(drift_metrics)
    dataset_drift = bool(share_drifted_columns >= drift_share)
    return DatasetDrift(
        number_of_drifted_columns=number_of_drifted_columns,
        dataset_drift_score=share_drifted_columns,
        dataset_drift=dataset_drift,
    )


def _get_all_columns_for_drift(dataset_columns: DatasetColumns) -> List[str]:
    result = []
    target_column = dataset_columns.utility_columns.target

    if target_column:
        result.append(target_column)

    prediction_column = dataset_columns.utility_columns.prediction

    if isinstance(prediction_column, str):
        result.append(prediction_column)

    if dataset_columns.num_feature_names:
        result += dataset_columns.num_feature_names

    if dataset_columns.cat_feature_names:
        result += dataset_columns.cat_feature_names

    if dataset_columns.text_feature_names:
        result += dataset_columns.text_feature_names

    return result


def get_drift_for_columns(
    *,
    current_data: pd.DataFrame,
    reference_data: pd.DataFrame,
    dataset_columns: DatasetColumns,
    data_drift_options: DataDriftOptions,
    drift_share_threshold: Optional[float] = None,
    columns: Optional[List[str]] = None,
    agg_data: bool,
) -> DatasetDriftMetrics:
    if columns is None:
        # ensure prediction column is a string - add label values for classification tasks
        ensure_prediction_column_is_string(
            prediction_column=dataset_columns.utility_columns.prediction,
            current_data=current_data,
            reference_data=reference_data,
        )
        columns = _get_all_columns_for_drift(dataset_columns)

    drift_share_threshold = (
        drift_share_threshold if drift_share_threshold is not None else data_drift_options.drift_share
    )

    # calculate result
    drift_by_columns: Dict[str, ColumnDataDriftMetrics] = {}

    dataset = pd.concat([reference_data, current_data])
    columns_types = {
        column_name: recognize_column_type_(
            dataset=dataset,
            column_name=column_name,
            columns=dataset_columns,
        )
        for column_name in columns
    }

    num_columns = [k for k, v in columns_types.items() if v == ColumnType.Numerical]

    is_current_contains_nans = current_data.isna().any()
    if is_current_contains_nans[num_columns].any():
        current_correlations = current_data[num_columns].corr()
    else:
        current_correlations = pd.DataFrame(
            data=np.corrcoef(current_data[num_columns].values, rowvar=False),
            columns=num_columns,
            index=num_columns,
        )

    is_reference_contains_nans = reference_data.isna().any()
    if is_reference_contains_nans[num_columns].any():
        reference_correlations = reference_data[num_columns].corr()
    else:
        reference_correlations = pd.DataFrame(
            data=np.corrcoef(reference_data[num_columns].values, rowvar=False),
            columns=num_columns,
            index=num_columns,
        )
    num_correlations = (
        current_correlations,
        reference_correlations,
    )

    for column_name in columns:
        drift_by_columns[column_name] = get_one_column_drift(
            current_data=current_data,
            reference_data=reference_data,
            column_name=column_name,
            column_type=columns_types[column_name],
            options=data_drift_options,
            dataset_columns=dataset_columns,
            agg_data=agg_data,
            num_correlations=num_correlations,
            is_contains_nans=(is_current_contains_nans, is_reference_contains_nans),
        )

    dataset_drift = get_dataset_drift(drift_by_columns, drift_share_threshold)
    return DatasetDriftMetrics(
        number_of_columns=len(columns),
        number_of_drifted_columns=dataset_drift.number_of_drifted_columns,
        share_of_drifted_columns=dataset_drift.dataset_drift_score,
        dataset_drift=dataset_drift.dataset_drift,
        drift_by_columns=drift_by_columns,
        options=data_drift_options,
        dataset_columns=dataset_columns,
    )
