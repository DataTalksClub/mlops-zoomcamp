import abc
from typing import Generic
from typing import List
from typing import Optional
from typing import Tuple
from typing import TypeVar
from typing import Union

from evidently import ColumnMapping
from evidently.base_metric import ColumnName
from evidently.base_metric import ColumnNotFound
from evidently.base_metric import DatasetType
from evidently.base_metric import GenericInputData
from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.calculation_engine.engine import Engine
from evidently.calculation_engine.metric_implementation import MetricImplementation
from evidently.core import ColumnType
from evidently.spark.base import SparkDataFrame
from evidently.spark.base import SparkSeries
from evidently.spark.base import create_data_definition_spark
from evidently.utils.data_preprocessing import DataDefinition


class SparkInputData(InputData):
    reference_data: Optional[SparkDataFrame]
    current_data: SparkDataFrame
    reference_additional_features: Optional[SparkDataFrame]
    current_additional_features: Optional[SparkDataFrame]
    column_mapping: ColumnMapping
    data_definition: DataDefinition

    @staticmethod
    def _get_by_column_name(
        dataset: SparkDataFrame,
        additional: Optional[SparkDataFrame],
        column: ColumnName,
        add_columns: Optional[List[str]] = None,
    ) -> SparkSeries:
        if column.dataset == DatasetType.MAIN:
            if column.name not in dataset.columns:
                raise ColumnNotFound(column.name)
            return dataset.select([column.name] + (add_columns or []))
        if column.dataset == DatasetType.ADDITIONAL and additional is not None:
            return additional.select([column.name] + (add_columns or []))
        raise ValueError("unknown column data")

    def get_current_column(self, column: Union[str, ColumnName], datetime_column: Optional[str] = None) -> SparkSeries:
        _column = self._str_to_column_name(column)
        return self._get_by_column_name(
            self.current_data,
            self.current_additional_features,
            _column,
            [datetime_column] if datetime_column is not None else [],
        )

    def get_reference_column(
        self, column: Union[str, ColumnName], datetime_column: Optional[str] = None
    ) -> Optional[SparkSeries]:
        if self.reference_data is None:
            return None
        _column = self._str_to_column_name(column)
        if self.reference_additional_features is None and _column.dataset == DatasetType.ADDITIONAL:
            return None
        return self._get_by_column_name(
            self.reference_data,
            self.reference_additional_features,
            _column,
            [datetime_column] if datetime_column is not None else [],
        )

    def get_data(self, column: Union[str, ColumnName]) -> Tuple[ColumnType, SparkSeries, Optional[SparkSeries]]:
        ref_data = None
        if self.reference_data is not None:
            ref_data = self.get_reference_column(column)
        return self._determine_type(column), self.get_current_column(column), ref_data

    def _determine_type(self, column: Union[str, ColumnName]) -> ColumnType:
        if isinstance(column, ColumnName) and column.feature_class is not None:
            column_type = ColumnType.Numerical
        else:
            if isinstance(column, ColumnName):
                column_name = column.name
            else:
                column_name = column
            column_type = self.data_definition.get_column(column_name).column_type
        return column_type

    def has_column(self, column_name: Union[str, ColumnName]):
        column = self._str_to_column_name(column_name)
        if column.dataset == DatasetType.MAIN:
            return column.name in [definition.column_name for definition in self.data_definition.get_columns()]
        if self.current_additional_features is not None:
            return column.name in self.current_additional_features.columns
        return False

    def _str_to_column_name(self, column: Union[str, ColumnName]) -> ColumnName:
        if isinstance(column, str):
            _column = ColumnName(column, column, DatasetType.MAIN, None)
        else:
            _column = column
        return _column


class SparkEngine(Engine["SparkMetricImplementation", SparkInputData]):
    def convert_input_data(self, data: GenericInputData) -> SparkInputData:
        if not isinstance(data.current_data, SparkDataFrame) or (
            data.reference_data is not None and not isinstance(data.reference_data, SparkDataFrame)
        ):
            raise ValueError("SparkEngine works only with pyspark.sql.DataFrame input data")
        return SparkInputData(
            data.reference_data,
            data.current_data,
            reference_additional_features=None,
            current_additional_features=None,
            column_mapping=data.column_mapping,
            data_definition=data.data_definition,
            additional_data=data.additional_data,
        )

    def get_data_definition(
        self,
        current_data,
        reference_data,
        column_mapping: ColumnMapping,
        categorical_features_cardinality: Optional[int] = None,
    ):
        return create_data_definition_spark(current_data, reference_data, column_mapping)

    def generate_additional_features(self, data: SparkInputData):
        pass


TMetric = TypeVar("TMetric", bound=Metric)


class SparkMetricImplementation(Generic[TMetric], MetricImplementation):
    def __init__(self, engine: SparkEngine, metric: TMetric):
        self.engine = engine
        self.metric = metric

    @abc.abstractmethod
    def calculate(self, context, data: SparkInputData):
        raise NotImplementedError

    @classmethod
    def supported_engines(cls):
        return (SparkEngine,)
