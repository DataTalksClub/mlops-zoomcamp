"""Methods for clean null or NaN values in a dataset"""

from typing import Optional

import numpy as np
import pandas as pd

from evidently.core import ColumnType
from evidently.metric_results import DatasetColumns
from evidently.metric_results import DatasetUtilityColumns
from evidently.pipeline.column_mapping import ColumnMapping


def replace_infinity_values_to_nan(dataframe: pd.DataFrame) -> pd.DataFrame:
    #   document somewhere, that all analyzers are mutators, i.e. they will change
    #   the dataframe, like here: replace inf and nan values.
    dataframe.replace([np.inf, -np.inf], np.nan, inplace=True)
    return dataframe


def process_columns(dataset: pd.DataFrame, column_mapping: ColumnMapping) -> DatasetColumns:
    if column_mapping is None:
        # data mapping should not be empty in this step
        raise ValueError("column_mapping should be present")
    date_column = column_mapping.datetime if column_mapping.datetime in dataset else None
    # index column name
    id_column = column_mapping.id

    task = column_mapping.task

    target_column = column_mapping.target if column_mapping.target in dataset else None
    if task is None and target_column is not None:
        task = recognize_task(target_name=target_column, dataset=dataset)
    target_type = _get_target_type(dataset, column_mapping, task)
    num_feature_names = column_mapping.numerical_features
    cat_feature_names = column_mapping.categorical_features
    datetime_feature_names = column_mapping.datetime_features
    target_names = column_mapping.target_names
    utility_columns = [date_column, id_column, target_column]
    text_feature_names = column_mapping.text_features

    prediction_column: Optional[str] = None
    if isinstance(column_mapping.prediction, str):
        if column_mapping.prediction in dataset:
            prediction_column = column_mapping.prediction
        else:
            prediction_column = None
        utility_columns.append(prediction_column)
    elif column_mapping.prediction is None:
        prediction_column = None
    else:
        prediction_column = dataset[column_mapping.prediction].columns.tolist()

        if prediction_column:
            utility_columns += prediction_column

    utility_columns_set = set(utility_columns)
    cat_feature_names_set = set(cat_feature_names or [])
    text_feature_names_set = set(text_feature_names or [])

    if num_feature_names is None:
        # try to guess about numeric features in the dataset
        # ignore prediction, target, index and explicitly specified category columns and columns with text
        num_feature_names = sorted(
            list(
                set(dataset.select_dtypes([np.number]).columns)
                - utility_columns_set
                - cat_feature_names_set
                - text_feature_names_set
            )
        )

    else:
        num_feature_names = [col for col in num_feature_names if col in dataset.columns]
        empty_cols = dataset[num_feature_names].isnull().mean()
        empty_cols = empty_cols[empty_cols == 1.0].index
        num_feature_names = sorted(
            list(set(dataset[num_feature_names].select_dtypes([np.number]).columns).union(set(empty_cols)))
        )

    if datetime_feature_names is None:
        datetime_feature_names = sorted(list(set(dataset.select_dtypes(["datetime"]).columns) - utility_columns_set))
    else:
        empty_cols = dataset[datetime_feature_names].isnull().mean()
        empty_cols = empty_cols[empty_cols == 1.0].index
        datetime_feature_names = sorted(
            list(set(dataset[datetime_feature_names].select_dtypes(["datetime"]).columns).union(set(empty_cols)))
        )

    cat_feature_names = column_mapping.categorical_features

    if cat_feature_names is None:
        cat_feature_names = sorted(
            list(
                set(dataset.select_dtypes(exclude=[np.number, "datetime"]).columns)
                - utility_columns_set
                - text_feature_names_set
            )
        )

    else:
        cat_feature_names = dataset[cat_feature_names].columns.tolist()

    return DatasetColumns(
        utility_columns=DatasetUtilityColumns(
            date=date_column, id=id_column, target=target_column, prediction=prediction_column
        ),
        target_type=target_type,
        num_feature_names=num_feature_names or [],
        cat_feature_names=cat_feature_names or [],
        datetime_feature_names=datetime_feature_names or [],
        target_names=target_names,
        task=task,
        text_feature_names=text_feature_names or [],
    )


def _get_target_type(dataset: pd.DataFrame, column_mapping: ColumnMapping, task: Optional[str]) -> Optional[str]:
    """
    Args:
        dataset: input dataset
        column_mapping: column definition from user
    Returns:
        type of target (or prediction, if there are only prediction) or None if both columns missing.
    """
    column = None
    if column_mapping.target is not None and column_mapping.target in dataset:
        column = dataset[column_mapping.target]
    if (
        column is None
        and column_mapping.prediction is not None
        and isinstance(column_mapping.prediction, str)
        and column_mapping.prediction in dataset
    ):
        column = dataset[column_mapping.prediction]

    if column is None:
        return None

    if column_mapping.target_names is not None or task == "classification":
        column_type = "cat"
    elif pd.api.types.is_numeric_dtype(column.dtype):
        column_type = "num"
    elif pd.api.types.is_datetime64_dtype(column.dtype):
        column_type = "datetime"
    else:
        column_type = "cat"
    return column_type


def recognize_task(target_name: str, dataset: pd.DataFrame) -> str:
    """Try to guess about the target type:
    if the target has a numeric type and number of unique values > 5: task == ‘regression’
    in all other cases task == ‘classification’.

    Args:
        target_name: name of target column.
        dataset: usually the data which you used in training.

    Returns:
        Task parameter.
    """
    if pd.api.types.is_numeric_dtype(dataset[target_name]) and dataset[target_name].nunique() >= 5:
        task = "regression"

    else:
        task = "classification"

    return task


def recognize_column_type_(dataset: pd.DataFrame, column_name: str, columns: DatasetColumns) -> ColumnType:
    """Try to get the column type."""
    column = dataset[column_name]
    reg_condition = columns.task == "regression" or (
        pd.api.types.is_numeric_dtype(column) and columns.task != "classification" and column.nunique() > 5
    )
    if column_name == columns.utility_columns.target:
        if reg_condition:
            return ColumnType.Numerical

        else:
            return ColumnType.Categorical

    if isinstance(columns.utility_columns.prediction, str) and column_name == columns.utility_columns.prediction:
        if reg_condition or (
            not pd.api.types.is_integer_dtype(column)
            and pd.api.types.is_numeric_dtype(column)
            and column.max() <= 1
            and column.min() >= 0
        ):
            return ColumnType.Numerical

        else:
            return ColumnType.Categorical

    if column_name in columns.num_feature_names:
        return ColumnType.Numerical

    if isinstance(columns.utility_columns.prediction, list) and column_name in columns.utility_columns.prediction:
        return ColumnType.Numerical

    if column_name in columns.cat_feature_names:
        return ColumnType.Categorical

    if column_name in columns.datetime_feature_names:
        return ColumnType.Datetime

    if column_name in columns.text_feature_names:
        return ColumnType.Text

    if column_name == columns.utility_columns.id:
        return ColumnType.Id

    if column_name == columns.utility_columns.date:
        return ColumnType.Date

    return ColumnType.Unknown


def recognize_column_type(dataset: pd.DataFrame, column_name: str, columns: DatasetColumns) -> str:
    return recognize_column_type_(dataset, column_name, columns).value
