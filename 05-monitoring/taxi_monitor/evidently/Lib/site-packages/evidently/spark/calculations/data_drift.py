from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

import numpy as np
from pyspark.sql import DataFrame
from pyspark.sql import functions as sf

from evidently import ColumnMapping
from evidently.base_metric import ColumnName
from evidently.base_metric import DataDefinition
from evidently.calculations.data_drift import ColumnDataDriftMetrics
from evidently.calculations.data_drift import ColumnType
from evidently.calculations.data_drift import DatasetDriftMetrics
from evidently.calculations.data_drift import DistributionIncluded
from evidently.calculations.data_drift import DriftStatsField
from evidently.calculations.data_drift import ScatterField
from evidently.calculations.data_drift import get_dataset_drift
from evidently.metric_results import DatasetColumns
from evidently.metric_results import DatasetUtilityColumns
from evidently.metric_results import ScatterAggField
from evidently.options.data_drift import DataDriftOptions
from evidently.spark import SparkEngine
from evidently.spark.base import SparkSeries
from evidently.spark.calculations.histogram import get_histogram
from evidently.spark.calculations.histogram import value_counts
from evidently.spark.calculations.stattests.base import get_stattest
from evidently.spark.utils import calculate_stats
from evidently.spark.utils import is_numeric_column_dtype
from evidently.spark.visualizations import get_distribution_for_column
from evidently.spark.visualizations import get_text_data_for_plots
from evidently.spark.visualizations import prepare_df_for_time_index_plot


def get_one_column_drift(
    *,
    current_feature_data: SparkSeries,
    reference_feature_data: SparkSeries,
    datetime_column: Optional[str],
    column: ColumnName,
    options: DataDriftOptions,
    data_definition: DataDefinition,
    column_type: ColumnType,
) -> ColumnDataDriftMetrics:
    if column_type not in (ColumnType.Numerical, ColumnType.Categorical, ColumnType.Text):
        raise ValueError(f"Cannot calculate drift metric for column '{column}' with type {column_type}")

    target = data_definition.get_target_column()
    stattest = None
    threshold = None
    if column.is_main_dataset():
        if target and column.name == target.column_name and column_type == ColumnType.Numerical:
            stattest = options.num_target_stattest_func

        elif target and column.name == target.column_name and column_type == ColumnType.Categorical:
            stattest = options.cat_target_stattest_func

        if not stattest:
            stattest = options.get_feature_stattest_func(column.name, column_type.value)

        threshold = options.get_threshold(column.name, column_type.value)
    current_column = current_feature_data
    reference_column = reference_feature_data

    # clean and check the column in reference dataset
    reference_column = reference_column.replace([-np.inf, np.inf], np.nan).dropna(subset=[column.name])

    if reference_column.rdd.isEmpty():
        raise ValueError(
            f"An empty column '{column.name}' was provided for drift calculation in the reference dataset."
        )

    # clean and check the column in current dataset
    current_column = current_column.replace([-np.inf, np.inf], np.nan).dropna(subset=[column.name])

    if current_column.rdd.isEmpty():
        raise ValueError(f"An empty column '{column.name}' was provided for drift calculation in the current dataset.")

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
        if not is_numeric_column_dtype(reference_column, column):
            raise ValueError(f"Column '{column}' in reference dataset should contain numerical values only.")

        if not is_numeric_column_dtype(current_column, column):
            raise ValueError(f"Column '{column}' in current dataset should contain numerical values only.")

    drift_test_function = get_stattest(reference_column, current_column, column_type.value, stattest)
    drift_result = drift_test_function(
        reference_column,
        current_column,
        column_type,
        threshold,
        engine=SparkEngine,
        column_name=column.name,
    )

    scatter: Optional[Union[ScatterField, ScatterAggField]] = None
    if column_type == ColumnType.Numerical:
        current_nbinsx = options.get_nbinsx(column.name)
        current_small_distribution = get_histogram(current_column, column.name, current_nbinsx, density=True)
        reference_small_distribution = get_histogram(reference_column, column.name, current_nbinsx, density=True)
        current_scatter = {}

        df, prefix = prepare_df_for_time_index_plot(
            current_column,
            column.name,
            datetime_column,
        )
        current_scatter["current (mean)"] = df
        if prefix is None:
            x_name = "Index binned"
        else:
            x_name = f"Timestamp ({prefix})"

        plot_shape = {}
        reference_mean, reference_std = calculate_stats(reference_column, column.name, sf.mean, sf.stddev)
        plot_shape["y0"] = reference_mean - reference_std
        plot_shape["y1"] = reference_mean + reference_std
        scatter = ScatterAggField(scatter=current_scatter, x_name=x_name, plot_shape=plot_shape)

    elif column_type == ColumnType.Categorical:
        current_vc = value_counts(current_column, column.name)
        reference_vc = value_counts(reference_column, column.name)
        keys = np.array(list(set(current_vc.keys()).union(reference_vc.keys())))
        current_small_distribution = [current_vc.get(k, 0) for k in keys], keys  # type: ignore[assignment]
        reference_small_distribution = [reference_vc.get(k, 0) for k in keys], keys  # type: ignore[assignment]
    if column_type != ColumnType.Text:
        current_distribution, reference_distribution = get_distribution_for_column(
            column_type=column_type,
            column_name=column.name,
            current=current_column,
            reference=reference_column,
        )
        if reference_distribution is None:
            raise ValueError(f"Cannot calculate reference distribution for column '{column}'.")

    elif column_type == ColumnType.Text and drift_result.drifted:
        (
            typical_examples_cur,
            typical_examples_ref,
            typical_words_cur,
            typical_words_ref,
        ) = get_text_data_for_plots(reference_column, current_column, column.name)

    metrics = ColumnDataDriftMetrics(
        column_name=column.display_name,
        column_type=column_type.value,
        stattest_name=drift_test_function.display_name,
        drift_score=drift_result.drift_score,
        drift_detected=drift_result.drifted,
        stattest_threshold=drift_result.actual_threshold,
        current=DriftStatsField(
            distribution=current_distribution,
            small_distribution=DistributionIncluded(
                x=current_small_distribution[1].tolist(), y=current_small_distribution[0]
            )
            if current_small_distribution
            else None,
            correlations=current_correlations,
            characteristic_examples=typical_examples_cur,
            characteristic_words=typical_words_cur,
        ),
        reference=DriftStatsField(
            distribution=reference_distribution,
            small_distribution=DistributionIncluded(
                x=reference_small_distribution[1].tolist(), y=reference_small_distribution[0]
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


def get_drift_for_columns(
    *,
    current_data: DataFrame,
    reference_data: DataFrame,
    data_definition: DataDefinition,
    column_mapping: ColumnMapping,
    data_drift_options: DataDriftOptions,
    drift_share_threshold: Optional[float] = None,
    columns: Optional[List[str]] = None,
) -> DatasetDriftMetrics:
    if columns is None:
        # ensure prediction column is a string - add label values for classification tasks
        prediction_columns = data_definition.get_prediction_columns()
        ensure_prediction_column_is_string(
            prediction_column=prediction_columns.get_columns_list() if prediction_columns is not None else None,
            current_data=current_data,
            reference_data=reference_data,
        )
        columns = _get_all_columns_for_drift(data_definition, column_mapping)

    drift_share_threshold = (
        drift_share_threshold if drift_share_threshold is not None else data_drift_options.drift_share
    )

    datetime_column = data_definition.get_datetime_column()
    datetime_column_name = datetime_column.column_name if datetime_column is not None else None

    # calculate result
    drift_by_columns: Dict[str, ColumnDataDriftMetrics] = {}

    for column_name in columns:
        drift_by_columns[column_name] = get_one_column_drift(
            current_feature_data=current_data,
            reference_feature_data=reference_data,
            datetime_column=datetime_column_name,
            column=ColumnName.from_any(column_name),
            options=data_drift_options,
            data_definition=data_definition,
            column_type=data_definition.get_column(column_name).column_type,
        )

    dataset_drift = get_dataset_drift(drift_by_columns, drift_share_threshold)
    return DatasetDriftMetrics(
        number_of_columns=len(columns),
        number_of_drifted_columns=dataset_drift.number_of_drifted_columns,
        share_of_drifted_columns=dataset_drift.dataset_drift_score,
        dataset_drift=dataset_drift.dataset_drift,
        drift_by_columns=drift_by_columns,
        options=data_drift_options,
        dataset_columns=DatasetColumns(
            utility_columns=DatasetUtilityColumns(),
            target_type=None,
            num_feature_names=[],
            cat_feature_names=[],
            text_feature_names=[],
            datetime_feature_names=[],
            target_names=[],
            task=None,
        ),
    )


def _get_all_columns_for_drift(data_definition: DataDefinition, column_mapping: ColumnMapping) -> List[str]:
    result: List[str] = []
    target_column = data_definition.get_target_column()

    if target_column:
        result.append(target_column.column_name)

    prediction_column = data_definition.get_prediction_columns()

    if prediction_column is not None:
        result.extend(c.column_name for c in prediction_column.get_columns_list())

    num_features = column_mapping.numerical_features or [
        c.column_name for c in data_definition.get_columns(ColumnType.Numerical, features_only=True)
    ]
    result += [c for c in num_features if data_definition.get_column(c).column_type == ColumnType.Numerical]
    cat_features = column_mapping.categorical_features or [
        c.column_name for c in data_definition.get_columns(ColumnType.Categorical, features_only=True)
    ]
    result += [c for c in cat_features if data_definition.get_column(c).column_type == ColumnType.Categorical]
    # todo: text
    # result += [c for c in column_mapping.numerical_features if data_definition.get_column(c).column_type == ColumnType.Numerical]

    return result


def ensure_prediction_column_is_string(
    *,
    prediction_column: Optional[Union[str, Sequence]],
    current_data: DataFrame,
    reference_data: DataFrame,
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
        raise NotImplementedError("SparkEngine do not support multiple prediction columns yet")
        # if len(prediction_column) > 2:
        #     reference_data["predicted_labels"] = _get_pred_labels_from_prob(reference_data, prediction_column)
        #     current_data["predicted_labels"] = _get_pred_labels_from_prob(current_data, prediction_column)
        #     result_prediction_column = "predicted_labels"
        #
        # elif len(prediction_column) == 2:
        #     reference_data["predicted_labels"] = (reference_data[prediction_column[0]] > threshold).astype(int)
        #     current_data["predicted_labels"] = (current_data[prediction_column[0]] > threshold).astype(int)
        #     result_prediction_column = "predicted_labels"

    return result_prediction_column
