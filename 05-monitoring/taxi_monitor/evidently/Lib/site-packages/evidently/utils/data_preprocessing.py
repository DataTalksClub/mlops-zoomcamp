import dataclasses
import logging
import warnings
from enum import Enum
from typing import Collection
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

import numpy as np
import pandas as pd

from evidently._pydantic_compat import BaseModel
from evidently.core import ColumnType
from evidently.pipeline.column_mapping import ColumnMapping
from evidently.pipeline.column_mapping import RecomType
from evidently.pipeline.column_mapping import TargetNames
from evidently.pipeline.column_mapping import TaskType
from evidently.pydantic_utils import EnumValueMixin


@dataclasses.dataclass
class _InputData:
    reference: Optional[pd.DataFrame]
    current: pd.DataFrame


class ColumnDefinition(BaseModel):
    column_name: str
    column_type: ColumnType

    def __init__(self, column_name: str, column_type: ColumnType):
        super().__init__(column_name=column_name, column_type=column_type)


class PredictionColumns(BaseModel):
    predicted_values: Optional[ColumnDefinition] = None
    prediction_probas: Optional[List[ColumnDefinition]] = None

    def __init__(
        self,
        predicted_values: Optional[ColumnDefinition] = None,
        prediction_probas: Optional[List[ColumnDefinition]] = None,
    ):
        super().__init__(predicted_values=predicted_values, prediction_probas=prediction_probas)

    def get_columns_list(self) -> List[ColumnDefinition]:
        result = [self.predicted_values]
        if self.prediction_probas is not None:
            result.extend(self.prediction_probas)
        return [col for col in result if col is not None]


def _check_filter(
    column: ColumnDefinition, utility_columns: List[str], filter_def: ColumnType = None, features_only: bool = False
) -> bool:
    if filter_def is None:
        return column.column_name not in utility_columns if features_only else True
    if not features_only:
        return column.column_type == filter_def

    return column.column_type == filter_def and column.column_name not in utility_columns


class DataDefinition(EnumValueMixin):
    columns: Dict[str, ColumnDefinition]
    target: Optional[ColumnDefinition]
    prediction_columns: Optional[PredictionColumns]
    id_column: Optional[ColumnDefinition]
    datetime_column: Optional[ColumnDefinition]
    embeddings: Optional[Dict[str, List[str]]]
    user_id: Optional[ColumnDefinition]
    item_id: Optional[ColumnDefinition]

    task: Optional[str]
    classification_labels: Optional[TargetNames]
    reference_present: bool
    recommendations_type: Optional[RecomType]

    def get_column(self, column_name: str) -> ColumnDefinition:
        return self.columns[column_name]

    def get_columns(self, filter_def: ColumnType = None, features_only: bool = False) -> List[ColumnDefinition]:
        if self.prediction_columns is not None:
            prediction = self.prediction_columns.get_columns_list()
        else:
            prediction = []
        utility_columns = [
            col.column_name
            for col in [
                self.id_column,
                self.datetime_column,
                self.target,
                self.user_id,
                self.item_id,
                *prediction,
            ]
            if col is not None
        ]
        return [
            column
            for column in self.columns.values()
            if _check_filter(column, utility_columns, filter_def, features_only)
        ]

    def get_column_names(self, filter_def: ColumnType = None, features_only: bool = False) -> List[str]:
        return [x.column_name for x in self.get_columns(filter_def, features_only)]

    def get_target_column(self) -> Optional[ColumnDefinition]:
        return self.target

    def get_prediction_columns(self) -> Optional[PredictionColumns]:
        return self.prediction_columns

    def get_id_column(self) -> Optional[ColumnDefinition]:
        return self.id_column

    def get_user_id_column(self) -> Optional[ColumnDefinition]:
        return self.user_id

    def get_item_id_column(self) -> Optional[ColumnDefinition]:
        return self.item_id

    def get_datetime_column(self) -> Optional[ColumnDefinition]:
        return self.datetime_column


class DataDefinitionError(ValueError):
    pass


def _is_cardinality_exceeded(
    column_name: Optional[str],
    data: _InputData,
    limit: Optional[int],
) -> bool:
    cardinality = _get_column_cardinality(column_name, data)
    if limit and cardinality >= min(limit, data.current.shape[0]):
        return True
    return False


def _process_column(
    column_name: Optional[str],
    data: _InputData,
    if_partially_present: str = "raise",
    predefined_type: Optional[ColumnType] = None,
    mapping: Optional[ColumnMapping] = None,
    cardinality_limit: Optional[int] = None,
) -> Optional[ColumnDefinition]:
    if column_name is None:
        return None
    presence = _get_column_presence(column_name, data)
    if presence == ColumnPresenceState.Missing:
        return None
    if presence == ColumnPresenceState.Partially:
        if if_partially_present == "raise":
            raise ValueError(f"Column ({column_name}) is partially present in data")
        if if_partially_present == "skip":
            return None
        if if_partially_present == "keep":
            pass
    column_type = (
        predefined_type
        if predefined_type is not None
        else _get_column_type(column_name, data, mapping, cardinality_limit)
    )
    return ColumnDefinition(column_name, column_type)


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
        prediction_present = _get_column_presence(prediction, data)
        if prediction_present == ColumnPresenceState.Missing:
            return None
        if prediction_present == ColumnPresenceState.Partially:
            raise ValueError(f"Prediction column ({prediction}) is partially present in data")
        prediction_type = _get_column_type(prediction, data, mapping)
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
        if mapping is not None and mapping.recommendations_type == RecomType.RANK:
            return PredictionColumns(predicted_values=ColumnDefinition(prediction, prediction_type))
        if (
            task == TaskType.RECOMMENDER_SYSTEMS
            and mapping is not None
            and mapping.recommendations_type == RecomType.SCORE
        ):
            return PredictionColumns(prediction_probas=[ColumnDefinition(prediction, prediction_type)])
        if task is None:
            if prediction_type == ColumnType.Numerical and target_type == ColumnType.Categorical:
                # probably this is binary with single column of probabilities
                return PredictionColumns(prediction_probas=[ColumnDefinition(prediction, prediction_type)])
            return PredictionColumns(predicted_values=ColumnDefinition(prediction, prediction_type))
    if isinstance(prediction, list):
        presence = [_get_column_presence(column, data) for column in prediction]
        if all([item == ColumnPresenceState.Missing for item in presence]):
            return None
        if all([item == ColumnPresenceState.Present for item in presence]):
            prediction_defs = [ColumnDefinition(column, _get_column_type(column, data)) for column in prediction]
            if any([item.column_type != ColumnType.Numerical for item in prediction_defs]):
                raise ValueError(f"Some prediction columns have incorrect types {prediction_defs}")
            return PredictionColumns(prediction_probas=prediction_defs)
    raise ValueError("Unexpected type for prediction field in column_mapping")


def _filter_by_type(column: Optional[ColumnDefinition], column_type: ColumnType, exclude: List[str]) -> bool:
    return column is not None and column.column_type == column_type and column.column_name not in exclude


def _column_not_present_in_list(
    column: Optional[str],
    columns: Collection[str],
    handle_error: str,
    message: str,
) -> Optional[str]:
    if column is None:
        return None
    if column not in columns:
        return column
    if handle_error == "error":
        raise ValueError(message.format(column=column))
    if handle_error == "warning":
        logging.warning(message.format(column=column))
        return None
    if handle_error == "skip":
        return None
    raise ValueError(f"Unknown handle error type {handle_error}")


def create_data_definition(
    reference_data: Optional[pd.DataFrame],
    current_data: pd.DataFrame,
    mapping: ColumnMapping,
    categorical_features_cardinality_limit: Optional[int] = None,
) -> DataDefinition:
    data = _InputData(reference_data, current_data)
    embedding_columns = set()
    embeddings: Optional[Dict[str, List[str]]] = None
    if mapping.embeddings is not None:
        embeddings = dict()
        for embedding_name, columns in mapping.embeddings.items():
            embeddings[embedding_name] = []
            for column in columns:
                presence = _get_column_presence(column, data)
                if presence != ColumnPresenceState.Present:
                    logging.warning(f"Column {column} isn't present in data. Skipping it.")
                else:
                    embeddings[embedding_name].append(column)
                    embedding_columns.add(column)

    id_column = _process_column(
        _column_not_present_in_list(
            mapping.id,
            embedding_columns,
            "warning",
            "Column {column} is in embeddings list and as an ID field. Ignoring ID field.",
        ),
        data,
    )
    user_id = _process_column(
        _column_not_present_in_list(
            mapping.user_id,
            embedding_columns,
            "warning",
            "Column {column} is in embeddings list and as an user_id field. Ignoring user_id field.",
        ),
        data,
    )
    item_id = _process_column(
        _column_not_present_in_list(
            mapping.item_id,
            embedding_columns,
            "warning",
            "Column {column} is in embeddings list and as an item_id field. Ignoring item_id field.",
        ),
        data,
    )
    target_column = _process_column(
        _column_not_present_in_list(
            mapping.target,
            embedding_columns,
            "warning",
            "Column {column} is in embeddings list and as a target field. Ignoring target field.",
        ),
        data,
        mapping=mapping,
    )
    datetime_column = _process_column(
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
        user_id,
        item_id,
        datetime_column,
        target_column,
        *prediction_cols,
    ]
    utility_column_names = [column.column_name for column in all_columns if column is not None]
    data_columns = set(data.current.columns) | (set(data.reference.columns) if data.reference is not None else set())
    col_defs = [
        _process_column(
            column_name,
            data,
            if_partially_present="skip",
            mapping=mapping,
            cardinality_limit=categorical_features_cardinality_limit,
        )
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
                _process_column(
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
        categorical_features = [
            _process_column(
                column_name,
                data,
                predefined_type=ColumnType.Categorical,
                mapping=mapping,
                cardinality_limit=categorical_features_cardinality_limit,
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
        all_columns.extend(categorical_features)

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
                _process_column(
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
                _process_column(column_name, data, predefined_type=ColumnType.Text, mapping=mapping)
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
        labels = list(data.current[target_column.column_name].unique())
        if data.reference is not None:
            labels = list(set(labels) | set(data.reference[target_column.column_name].unique()))
        if None in labels:
            warnings.warn(
                f"Target column '{target_column.column_name}' contains 'None' values, which is not supported as label value"
            )
            labels = [v for v in labels if v is not None]
    recommendations_type = mapping.recommendations_type or RecomType.SCORE

    classification_labels = mapping.target_names or labels
    return DataDefinition(
        columns={col.column_name: col for col in all_columns if col is not None},
        id_column=id_column,
        user_id=user_id,
        item_id=item_id,
        datetime_column=datetime_column,
        target=target_column,
        prediction_columns=prediction_columns,
        task=task,
        classification_labels=classification_labels,
        embeddings=embeddings,
        reference_present=reference_data is not None,
        recommendations_type=recommendations_type,
    )


def get_column_name_or_none(column: Optional[ColumnDefinition]) -> Optional[str]:
    if column is None:
        return None
    return column.column_name


def create_column_mapping(data_definition: DataDefinition) -> ColumnMapping:
    prediction = None
    prediction_columns = data_definition.get_prediction_columns()
    if prediction_columns and prediction_columns.predicted_values:
        prediction = prediction_columns.predicted_values.column_name

    column_mapping = ColumnMapping(
        target=get_column_name_or_none(data_definition.get_target_column()),
        prediction=prediction,
        datetime=get_column_name_or_none(data_definition.get_datetime_column()),
        id=get_column_name_or_none(data_definition.get_id_column()),
        numerical_features=data_definition.get_column_names(ColumnType.Numerical, features_only=True),
        categorical_features=data_definition.get_column_names(ColumnType.Categorical, features_only=True),
        datetime_features=data_definition.get_column_names(ColumnType.Datetime, features_only=True),
        text_features=data_definition.get_column_names(ColumnType.Text, features_only=True),
        target_names=data_definition.classification_labels,
        task=data_definition.task,
        embeddings=data_definition.embeddings,
        user_id=get_column_name_or_none(data_definition.get_user_id_column()),
        item_id=get_column_name_or_none(data_definition.get_item_id_column()),
        recommendations_type=RecomType(data_definition.recommendations_type),
    )
    return column_mapping


class ColumnPresenceState(Enum):
    Present = 0
    Partially = 1
    Missing = 2


def _get_column_presence(column_name: str, data: _InputData) -> ColumnPresenceState:
    if column_name in data.current.columns:
        if data.reference is None or column_name in data.reference.columns:
            return ColumnPresenceState.Present
        return ColumnPresenceState.Partially
    if data.reference is None or column_name not in data.reference.columns:
        return ColumnPresenceState.Missing
    return ColumnPresenceState.Partially


def _get_column_cardinality(column_name: Optional[str], data: _InputData) -> float:
    if column_name in data.current.columns:
        return data.current[column_name].nunique()
    return 0


NUMBER_UNIQUE_AS_CATEGORICAL = 5


def _get_column_type(
    column_name: str, data: _InputData, mapping: Optional[ColumnMapping] = None, cardinality_limit: Optional[int] = None
) -> ColumnType:
    if mapping is not None:
        if mapping.categorical_features and column_name in mapping.categorical_features:
            if cardinality_limit and _is_cardinality_exceeded(column_name, data, cardinality_limit):
                raise DataDefinitionError(f"The cardinality of column ({column_name}) has been exceeded")
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
        ref_type = data.reference[column_name].dtype
        ref_unique = data.reference[column_name].nunique()
    cur_type = None
    cur_unique = None
    if column_name in data.current.columns:
        cur_type = data.current[column_name].dtype
        cur_unique = data.current[column_name].nunique()
    if ref_type is not None and cur_type is not None:
        if ref_type != cur_type:
            available_set = ["i", "u", "f", "c", "m", "M"]
            if ref_type.kind not in available_set or cur_type.kind not in available_set:
                logging.warning(
                    f"Column {column_name} have different types in reference {ref_type} and current {cur_type}."
                    f" Returning type from reference"
                )
                cur_type = ref_type
            if not np.can_cast(cur_type, ref_type) and not np.can_cast(ref_type, cur_type):
                logging.warning(
                    f"Column {column_name} have different types in reference {ref_type} and current {cur_type}."
                    f" Returning type from reference"
                )
                cur_type = ref_type
    nunique = ref_unique or cur_unique
    # special case: target
    column_dtype = cur_type if cur_type is not None else ref_type
    if mapping is not None and (column_name == mapping.target or (mapping.target is None and column_name == "target")):
        reg_condition = mapping.task == "regression" or (
            pd.api.types.is_numeric_dtype(column_dtype)
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
            pd.api.types.is_string_dtype(column_dtype)
            or (
                pd.api.types.is_integer_dtype(column_dtype)
                and mapping.task != "regression"
                and (nunique is not None and nunique <= NUMBER_UNIQUE_AS_CATEGORICAL)
            )
            or (
                pd.api.types.is_numeric_dtype(column_dtype)
                and mapping.task != "regression"
                and (nunique is not None and nunique <= NUMBER_UNIQUE_AS_CATEGORICAL)
                and (data.current[column_name].max() > 1 or data.current[column_name].min() < 0)
            )
            or (
                pd.api.types.is_numeric_dtype(column_dtype)
                and mapping.task == "classification"
                and (data.current[column_name].max() > 1 or data.current[column_name].min() < 0)
            )
        ):
            return ColumnType.Categorical
        else:
            return ColumnType.Numerical

    # all other features
    if pd.api.types.is_integer_dtype(column_dtype):
        nunique = ref_unique or cur_unique
        if nunique is not None and nunique <= NUMBER_UNIQUE_AS_CATEGORICAL:
            return ColumnType.Categorical
        return ColumnType.Numerical
    if pd.api.types.is_numeric_dtype(column_dtype):
        if column_dtype == bool:
            return ColumnType.Categorical
        return ColumnType.Numerical
    if pd.api.types.is_datetime64_dtype(column_dtype):
        return ColumnType.Datetime
    if _is_cardinality_exceeded(column_name, data, cardinality_limit):
        return ColumnType.Unknown
    return ColumnType.Categorical
