import datetime
import json
import typing
import uuid
from typing import Callable
from typing import Tuple
from typing import Type

import numpy as np
import pandas as pd

from evidently.core import ColumnType
from evidently.utils.types import ApproxValue

_TYPES_MAPPING = (
    (
        (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64),
        int,
    ),
    ((np.double, np.float16, np.float32, np.float64), lambda obj: None if obj is np.nan else float(obj)),
    ((np.ndarray,), lambda obj: obj.tolist()),
    ((np.bool_), bool),
    ((pd.Timedelta,), str),
    ((np.void, type(pd.NaT)), lambda obj: None),  # should be before datetime as NaT is subclass of datetime.
    ((pd.Timestamp, datetime.datetime, datetime.date), lambda obj: obj.isoformat()),
    # map ApproxValue to json value
    ((ApproxValue,), lambda obj: obj.dict()),
    ((pd.Series, pd.Index, pd.Categorical), lambda obj: obj.tolist()),
    ((pd.DataFrame,), lambda obj: obj.to_dict()),
    ((frozenset,), lambda obj: list(obj)),
    ((uuid.UUID,), lambda obj: str(obj)),
    ((ColumnType,), lambda obj: obj.value),
    ((pd.Period,), lambda obj: str(obj)),
)


def add_type_mapping(types: Tuple[Type], encoder: Callable):
    global _TYPES_MAPPING  # noqa: PLW0603
    _TYPES_MAPPING += ((types, encoder),)  # type: ignore[assignment]


class NumpyEncoder(json.JSONEncoder):
    """Numpy and Pandas data types to JSON types encoder"""

    def default(self, o):
        """JSON converter calls the method when it cannot convert an object to a Python type
        Convert the object to a Python type

        If we cannot convert the object, leave the default `JSONEncoder` behaviour - raise a TypeError exception.
        """

        # check mapping rules
        for types_list, python_type in _TYPES_MAPPING:
            if isinstance(o, types_list):
                return python_type(o)

        # explicit check pandas null
        if not isinstance(o, typing.Sequence) and pd.isnull(o):
            return None

        return json.JSONEncoder.default(self, o)
