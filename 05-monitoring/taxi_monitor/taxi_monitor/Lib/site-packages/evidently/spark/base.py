import dataclasses
import logging
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Union

from pyspark.sql import DataFrame
from pyspark.sql import functions as sf

from evidently import ColumnMapping
from evidently import TaskType
from evidently.core import ColumnType
from evidently.spark.utils import calculate_stats
from evidently.spark.utils import get_column_type
from evidently.spark.utils import is_datetime64_dtype
from evidently.spark.utils import is_integer_dtype
from evidently.spark.utils import is_numeric_dtype
from evidently.spark.utils import is_string_dtype
from evidently.utils.data_preprocessing import NUMBER_UNIQUE_AS_CATEGORICAL
from evidently.utils.data_preprocessing import ColumnDefinition
from evidently.utils.data_preprocessing import ColumnPresenceState
from evidently.utils.data_preprocessing import DataDefinition
from evidently.utils.data_preprocessing import PredictionColumns
from evidently.utils.data_preprocessing import _column_not_present_in_list
from evidently.utils.data_preprocessing import _filter_by_type

SparkSeries = DataFrame
SparkDataFrame = DataFrame


@dataclasses.dataclass
class _InputData:
    reference: Optional[DataFrame]
    current: DataFrame


def _get_column_presence_spark(column_name: str, data: _InputData) -> ColumnPresenceState:
    if column_name in data.current.columns:
        if data.reference is None or column_name in data.reference.columns:
            return ColumnPresenceState.Present
        return ColumnPresenceState.Partially
    if data.reference is None or column_name not in data.reference.columns:
        return ColumnPresenceState.Missing
    return ColumnPresenceState.Partially


def _process_column_spark(
    column_name: Optional[str],
    data: _InputData,
    if_partially_present: str = "raise",
    predefined_type: Optional[ColumnType] = None,
    mapping: Optional[ColumnMapping] = None,
) -> Optional[ColumnDefinition]:
    if column_name is None:
        return None

    presence = _get_column_presence_spark(column_name, data)
    if presence == ColumnPresenceState.Missing:
        return None
    if presence == ColumnPresenceState.Partially:
        if if_partially_present == "raise":
            raise ValueError(f"Column ({column_name}) is partially present in data")
        if if_partially_present == "skip":
            return None
        if if_partially_present == "keep":
            pass
    column_type = predefined_type if predefined_type is not None else _get_column_type_spark(column_name, data, mapping)
    return ColumnDefinition(column_name, column_type)


def create_data_definition_spark(
    reference_data: Optional[DataFrame], current_data: DataFrame, mapping: ColumnMapping
) -> DataDefinition:
    data = _InputData(reference_data, current_data)
    embedding_columns = set()
    embeddings: Optional[Dict[str, List[str]]] = None
    if mapping.embeddings is not None:
        embeddings = dict()
        for embedding_name, columns in mapping.embeddings.items():
            embeddings[embedding_name] = []
            for column in columns:
                presence = _get_column_presence_spark(column, data)
                if presence != ColumnPresenceState.Present:
                    logging.warning(f"Column {column} isn't present in data. Skipping it.")
                else:
                    embeddings[embedding_name].append(column)
                    embedding_columns.add(column)

    id_column = _process_column_spark(
        _column_not_present_in_list(
            mapping.id,
            embedding_columns,
            "warning",
            "Column {column} is in embeddings list and as an ID field. Ignoring ID field.",
        ),
        data,
    )
    target_column = _process_column_spark(
        _column_not_present_in_list(
            mapping.target,
            embedding_columns,
            "warning",
            "Column {column} is in embeddings list and as a target field. Ignoring target field.",
        ),
        data,
        mapping=mapping,
    )
    datetime_column = _process_column_spark(
        _column_not_present_in_list(
            mapping.datetime,
            embedding_columns,
            "warning",
            "Column {column} is in embeddings list and as a datetime field. Ignoring datetime field.",
        ),
        data,
    )

    prediction_columns = _prediction_column(
        mapping.prediction,
        target_column.column_type if target_column is not None else None,
        mapping.task,
        data,
        mapping,
    )

    prediction_cols = prediction_columns.get_columns_list() if prediction_columns is not None else []

    all_columns = [
        id_column,
        datetime_column,
        target_column,
        *prediction_cols,
    ]
    utility_column_names = [column.column_name for column in all_columns if column is not None]
    data_columns: Set[str] = set(data.current.columns) | (
        set(data.reference.columns) if data.reference is not None else set()
    )
    col_defs = [
        _process_column_spark(column_name, data, if_partially_present="skip", mapping=mapping)
        for column_name in data_columns
    ]

    if mapping.numerical_features is None:
        num = [
            column
            for column in col_defs
            if column is not None
            and _filter_by_type(column, ColumnType.Numerical, utility_column_names)
            and _column_not_present_in_list(column.column_name, embedding_columns, "skip", "")
        ]
        all_columns.extend(num)
    else:
        all_columns.extend(
            [
                _process_column_spark(
                    column_name,
                    data,
                    predefined_type=ColumnType.Numerical,
                    mapping=mapping,
                )
                for column_name in mapping.numerical_features
                if column_name not in utility_column_names
                and _column_not_present_in_list(
                    column_name,
                    embedding_columns,
                    "warning",
                    "Column {column} is in embedding list and in numerical features list."
                    " Ignoring it in a features list.",
                )
            ]
        )

    if mapping.categorical_features is None:
        cat = [
            column
            for column in col_defs
            if column is not None
            and _filter_by_type(column, ColumnType.Categorical, utility_column_names)
            and _column_not_present_in_list(column.column_name, embedding_columns, "skip", "")
        ]
        all_columns.extend(cat)
    else:
        all_columns.extend(
            [
                _process_column_spark(
                    column_name,
                    data,
                    predefined_type=ColumnType.Categorical,
                    mapping=mapping,
                )
                for column_name in mapping.categorical_features
                if column_name not in utility_column_names
                and _column_not_present_in_list(
                    column_name,
                    embedding_columns,
                    "warning",
                    "Column {column} is in embedding list and in categorical features list."
                    " Ignoring it in a features list.",
                )
            ]
        )

    if mapping.datetime_features is None:
        dt = [
            column
            for column in col_defs
            if column is not None
            and _filter_by_type(column, ColumnType.Datetime, utility_column_names)
            and _column_not_present_in_list(column.column_name, embedding_columns, "skip", "")
        ]
        all_columns.extend(dt)
    else:
        all_columns.extend(
            [
                _process_column_spark(
                    column_name,
                    data,
                    predefined_type=ColumnType.Datetime,
                    mapping=mapping,
                )
                for column_name in mapping.datetime_features
                if column_name not in utility_column_names
                and _column_not_present_in_list(
                    column_name,
                    embedding_columns,
                    "warning",
                    "Column {column} is in embedding list and in datetime features list."
                    " Ignoring it in a features list.",
                )
            ]
        )

    if mapping.text_features is not None:
        all_columns.extend(
            [
                _process_column_spark(column_name, data, predefined_type=ColumnType.Text, mapping=mapping)
                for column_name in mapping.text_features
                if column_name not in utility_column_names
                and _column_not_present_in_list(
                    column_name,
                    embedding_columns,
                    "warning",
                    "Column {column} is in embedding list and in text features list."
                    " Ignoring it in a features list.",
                )
            ]
        )
    task = mapping.task
    if task is None:
        if target_column is None:
            task = None
        elif target_column.column_type == ColumnType.Categorical:
            task = TaskType.CLASSIFICATION_TASK
        elif target_column.column_type == ColumnType.Numerical:
            task = TaskType.REGRESSION_TASK
        else:
            task = None

    labels = None
    if target_column is not None:
        labels = [
            r[target_column.column_name] for r in data.current.select(target_column.column_name).distinct().collect()
        ]
        if data.reference is not None:
            ref_labels = [
                r[target_column.column_name]
                for r in data.reference.select(target_column.column_name).distinct().collect()
            ]
            labels = list(set(labels) | set(ref_labels))

    return DataDefinition(
        user_id=ColumnDefinition(mapping.user_id, ColumnType.Id) if mapping.user_id is not None else None,
        item_id=ColumnDefinition(mapping.item_id, ColumnType.Id) if mapping.item_id is not None else None,
        columns={col.column_name: col for col in all_columns if col is not None},
        id_column=id_column,
        datetime_column=datetime_column,
        target=target_column,
        prediction_columns=prediction_columns,
        task=task,
        classification_labels=mapping.target_names or labels,
        embeddings=embeddings,
        reference_present=reference_data is not None,
        recommendations_type=mapping.recommendations_type,
    )


def _get_column_type_spark(column_name: str, data: _InputData, mapping: Optional[ColumnMapping] = None) -> ColumnType:
    if mapping is not None:
        if mapping.categorical_features and column_name in mapping.categorical_features:
            return ColumnType.Categorical
        if mapping.numerical_features and column_name in mapping.numerical_features:
            return ColumnType.Numerical
        if mapping.datetime_features and column_name in mapping.datetime_features:
            return ColumnType.Datetime
        if mapping.text_features and column_name in mapping.text_features:
            return ColumnType.Text
    ref_type = None
    ref_unique = None
    if data.reference is not None and column_name in data.reference.columns:
        ref_type = get_column_type(data.reference, column_name)
        # todo: slow
        ref_unique = data.reference.select(column_name).distinct().count()
    cur_type = None
    cur_unique = None
    if column_name in data.current.columns:
        cur_type = get_column_type(data.current, column_name)
        cur_unique = data.current.select(column_name).distinct().count()
    if ref_type is not None and cur_type is not None:
        if ref_type != cur_type:
            # available_set = ["i", "u", "f", "c", "m", "M"]
            # if ref_type.kind not in available_set or cur_type.kind not in available_set:
            logging.warning(
                f"Column {column_name} have different types in reference {ref_type} and current {cur_type}."
                f" Returning type from reference"
            )
            cur_type = ref_type
        # if not np.can_cast(cur_type, ref_type) and not np.can_cast(ref_type, cur_type):
        #     logging.warning(
        #         f"Column {column_name} have different types in reference {ref_type} and current {cur_type}."
        #         f" Returning type from reference"
        #     )
        #     cur_type = ref_type
    nunique = ref_unique or cur_unique
    # special case: target
    if mapping is not None and (column_name == mapping.target or (mapping.target is None and column_name == "target")):
        reg_condition = mapping.task == "regression" or (
            is_numeric_dtype(cur_type if cur_type is not None else ref_type)
            and mapping.task != "classification"
            and (nunique is not None and nunique > NUMBER_UNIQUE_AS_CATEGORICAL)
        )
        if reg_condition:
            return ColumnType.Numerical
        else:
            return ColumnType.Categorical

    if mapping is not None and (
        (isinstance(mapping.prediction, str) and column_name == mapping.prediction)
        or (mapping.prediction is None and column_name == "prediction")
    ):
        if (
            is_string_dtype(cur_type if cur_type is not None else ref_type)
            or (
                is_integer_dtype(cur_type if cur_type is not None else ref_type)
                and mapping.task != "regression"
                and (nunique is not None and nunique <= NUMBER_UNIQUE_AS_CATEGORICAL)
            )
            or (
                is_numeric_dtype(cur_type if cur_type is not None else ref_type)
                and mapping.task != "regression"
                and (nunique is not None and nunique <= NUMBER_UNIQUE_AS_CATEGORICAL)
                and (
                    calculate_stats(data.current, column_name, sf.max) > 1
                    or calculate_stats(data.current, column_name, sf.min) < 0
                )
            )
            or (
                is_numeric_dtype(cur_type if cur_type is not None else ref_type)
                and mapping.task == "classification"
                and (
                    calculate_stats(data.current, column_name, sf.max) > 1
                    or calculate_stats(data.current, column_name, sf.min) < 0
                )
            )
        ):
            return ColumnType.Categorical
        else:
            return ColumnType.Numerical

    # all other features
    if is_integer_dtype(cur_type if cur_type is not None else ref_type):
        # spark only
        if (
            data.reference is None or ref_unique == 1 and data.reference.select(column_name).dropna().count() == 0
        ) and (data.current is None or cur_unique == 1 and data.current.select(column_name).dropna().count() == 0):
            return ColumnType.Numerical
        # spark only
        nunique = ref_unique or cur_unique
        if nunique is not None and nunique <= NUMBER_UNIQUE_AS_CATEGORICAL:
            return ColumnType.Categorical
        return ColumnType.Numerical
    if is_numeric_dtype(cur_type if cur_type is not None else ref_type):
        return ColumnType.Numerical
    if is_datetime64_dtype(cur_type if cur_type is not None else ref_type):
        return ColumnType.Datetime
    return ColumnType.Categorical


def _prediction_column(
    prediction: Optional[Union[str, int, Sequence[int], Sequence[str]]],
    target_type: Optional[ColumnType],
    task: Optional[str],
    data: _InputData,
    mapping: Optional[ColumnMapping] = None,
) -> Optional[PredictionColumns]:
    if prediction is None:
        return None
    if isinstance(prediction, str):
        prediction_present = _get_column_presence_spark(prediction, data)
        if prediction_present == ColumnPresenceState.Missing:
            return None
        if prediction_present == ColumnPresenceState.Partially:
            raise ValueError(f"Prediction column ({prediction}) is partially present in data")
        prediction_type = _get_column_type_spark(prediction, data, mapping)
        if task == TaskType.CLASSIFICATION_TASK:
            if prediction_type == ColumnType.Categorical:
                return PredictionColumns(predicted_values=ColumnDefinition(prediction, prediction_type))
            if prediction_type == ColumnType.Numerical:
                return PredictionColumns(prediction_probas=[ColumnDefinition(prediction, prediction_type)])
            raise ValueError(f"Unexpected type for prediction column ({prediction}) (it is {prediction_type})")
        if task == TaskType.REGRESSION_TASK:
            if prediction_type == ColumnType.Categorical:
                raise ValueError("Prediction type is categorical but task is regression")
            if prediction_type == ColumnType.Numerical:
                return PredictionColumns(predicted_values=ColumnDefinition(prediction, prediction_type))
        if task is None:
            if prediction_type == ColumnType.Numerical and target_type == ColumnType.Categorical:
                # probably this is binary with single column of probabilities
                return PredictionColumns(prediction_probas=[ColumnDefinition(prediction, prediction_type)])
            return PredictionColumns(predicted_values=ColumnDefinition(prediction, prediction_type))
    if isinstance(prediction, list):
        presence = [_get_column_presence_spark(column, data) for column in prediction]
        if all([item == ColumnPresenceState.Missing for item in presence]):
            return None
        if all([item == ColumnPresenceState.Present for item in presence]):
            prediction_defs = [ColumnDefinition(column, _get_column_type_spark(column, data)) for column in prediction]
            if any([item.column_type != ColumnType.Numerical for item in prediction_defs]):
                raise ValueError(f"Some prediction columns have incorrect types {prediction_defs}")
            return PredictionColumns(prediction_probas=prediction_defs)
    raise ValueError("Unexpected type for prediction field in column_mapping")
