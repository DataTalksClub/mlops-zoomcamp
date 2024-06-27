from typing import Any
from typing import Callable
from typing import Tuple
from typing import Type
from typing import Union
from typing import overload

from pyspark.sql import Column
from pyspark.sql import DataFrame
from pyspark.sql.types import ByteType
from pyspark.sql.types import DataType
from pyspark.sql.types import DateType
from pyspark.sql.types import DecimalType
from pyspark.sql.types import DoubleType
from pyspark.sql.types import FloatType
from pyspark.sql.types import IntegerType
from pyspark.sql.types import LongType
from pyspark.sql.types import ShortType
from pyspark.sql.types import StringType
from pyspark.sql.types import TimestampType

from evidently.base_metric import ColumnName

CharType: Type[DataType]
VarcharType: Type[DataType]
TimestampNTZType: Type[DataType]

try:
    from pyspark.sql.types import CharType  # type: ignore[no-redef]
except ImportError:
    CharType = StringType

try:
    from pyspark.sql.types import VarcharType  # type: ignore[no-redef]
except ImportError:
    VarcharType = StringType


try:
    from pyspark.sql.types import TimestampNTZType  # type: ignore[no-redef]
except ImportError:
    TimestampNTZType = TimestampType


def get_column_type(df: DataFrame, column: str):
    return df.schema.fields[df.schema.names.index(column)].dataType


def is_numeric_dtype(dtype: DataType):
    return isinstance(dtype, (LongType, FloatType, IntegerType, ShortType, ByteType, DoubleType, DecimalType))


def is_integer_dtype(dtype: DataType):
    return isinstance(dtype, (LongType, IntegerType, ShortType))


def is_string_dtype(dtype: DataType):
    return isinstance(dtype, (StringType, VarcharType, CharType))


def is_datetime64_dtype(dtype: DataType):
    return isinstance(dtype, (DateType, TimestampType, TimestampNTZType))


def is_numeric_column_dtype(df: DataFrame, column: ColumnName):
    dtype = get_column_type(df, column.name)

    return is_numeric_dtype(dtype)


@overload
def calculate_stats(df: DataFrame, column_name: str, funcs: Callable[[str], Column]) -> Any: ...


@overload
def calculate_stats(df: DataFrame, column_name: str, *funcs: Callable[[str], Column]) -> Tuple: ...


def calculate_stats(df: DataFrame, column_name: str, *funcs: Callable[[str], Column]) -> Union[Tuple, Any]:
    cols = [f(column_name).alias(str(i)) for i, f in enumerate(funcs)]
    result = df.select(cols).first()
    if result is None:
        raise ValueError("Empty DataFrame")
    if len(funcs) == 1:
        return result["0"]
    return tuple(result[str(i)] for i in range(len(funcs)))
