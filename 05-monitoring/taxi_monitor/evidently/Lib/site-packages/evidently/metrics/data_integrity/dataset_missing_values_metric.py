from typing import Any
from typing import ClassVar
from typing import Dict
from typing import FrozenSet
from typing import List
from typing import Optional
from typing import Union

import numpy as np
import pandas as pd

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.calculations.data_quality import get_rows_count
from evidently.core import IncludeTags
from evidently.core import pydantic_type_validator
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import CounterData
from evidently.renderers.html_widgets import HistogramData
from evidently.renderers.html_widgets import TabData
from evidently.renderers.html_widgets import counter
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import histogram
from evidently.renderers.html_widgets import table_data
from evidently.renderers.html_widgets import widget_tabs

NoneKey = type("NoneKey", tuple(), {})


@pydantic_type_validator(NoneKey)
def null_valudator(value):
    if value is None or value == "null":
        return None
    raise ValueError("not a None")


MissingValue = Union[np.double, NoneKey, Any]  # type: ignore[valid-type]


class DatasetMissingValues(MetricResult):
    """Statistics about missed values in a dataset"""

    class Config:
        pd_exclude_fields = {
            "different_missing_values_by_column",
            "different_missing_values",
            "number_of_different_missing_values_by_column",
            "number_of_missing_values_by_column",
            "share_of_missing_values_by_column",
            "columns_with_missing_values",
        }

        field_tags = {
            "different_missing_values": {IncludeTags.Extra},
            "different_missing_values_by_column": {IncludeTags.Extra},
            "number_of_different_missing_values_by_column": {IncludeTags.Extra},
            "number_of_missing_values_by_column": {IncludeTags.Extra},
            "share_of_missing_values_by_column": {IncludeTags.Extra},
            "number_of_rows": {IncludeTags.Extra},
            "number_of_columns": {IncludeTags.Extra},
            "columns_with_missing_values": {IncludeTags.Extra},
        }

    # set of different missing values in the dataset
    different_missing_values: Dict[MissingValue, int]
    # number of different missing values in the dataset
    number_of_different_missing_values: int
    # set of different missing values for each column
    different_missing_values_by_column: Dict[str, Dict[MissingValue, int]]
    # count of different missing values for each column
    number_of_different_missing_values_by_column: Dict[str, int]
    # count of missing values in all dataset
    number_of_missing_values: int
    # share of missing values in all dataset
    share_of_missing_values: float
    # count of missing values for each column
    number_of_missing_values_by_column: Dict[str, int]
    # share of missing values for each column
    share_of_missing_values_by_column: Dict[str, float]
    # count of rows in the dataset
    number_of_rows: int
    # count of rows with a missing value
    number_of_rows_with_missing_values: int
    # share of rows with a missing value
    share_of_rows_with_missing_values: float
    # count of columns in the dataset
    number_of_columns: int
    # list of columns with a missing value
    columns_with_missing_values: List[str]
    # count of columns with a missing value
    number_of_columns_with_missing_values: int
    # share of columns with a missing value
    share_of_columns_with_missing_values: float


class DatasetMissingValuesMetricResult(MetricResult):
    class Config:
        field_tags = {"current": {IncludeTags.Current}, "reference": {IncludeTags.Reference}}

    current: DatasetMissingValues
    reference: Optional[DatasetMissingValues] = None


class DatasetMissingValuesMetric(Metric[DatasetMissingValuesMetricResult]):
    """Count missing values in a dataset.

    Missing value is a null or NaN value.

    Calculate an amount of missing values kinds and count for such values.
    NA-types like numpy.NaN, pandas.NaT are counted as one type.

    You can set you own missing values list with `missing_values` parameter.
    Value `None` in the list means that Pandas null values will be included in the calculation.

    If `replace` parameter is False - add defaults to user's list.
    If `replace` parameter is True - use values from `missing_values` list only.
    """

    # default missing values list
    DEFAULT_MISSING_VALUES: ClassVar = ["", np.inf, -np.inf, None]
    missing_values: FrozenSet[MissingValue]

    def __init__(self, missing_values: Optional[list] = None, replace: bool = True, options: AnyOptions = None) -> None:
        _missing_values: list
        if missing_values is None:
            # use default missing values list if we have no user-defined values
            _missing_values = self.DEFAULT_MISSING_VALUES

        elif not replace:
            # add default values to the user-defined list
            _missing_values = self.DEFAULT_MISSING_VALUES + missing_values
        else:
            _missing_values = missing_values

        # use frozenset because metrics parameters should be immutable/hashable for deduplication
        self.missing_values = frozenset(_missing_values)
        super().__init__(options=options)

    def _calculate_missing_values_stats(self, dataset: pd.DataFrame) -> DatasetMissingValues:
        different_missing_values = {value: 0 for value in self.missing_values}
        columns_with_missing_values = set()
        number_of_missing_values = 0
        number_of_missing_values_by_column: Dict[str, int] = {}
        different_missing_values_by_column: Dict[str, Dict[Any, int]] = {}

        for column_name in dataset.columns:
            number_of_missing_values_by_column[column_name] = 0
            different_missing_values_by_column[column_name] = {}

            for value in self.missing_values:
                different_missing_values_by_column[column_name][value] = 0

        number_of_rows_with_missing_values = 0
        number_of_columns = len(dataset.columns)
        number_of_rows = get_rows_count(dataset)

        for column_name in dataset.columns:
            # iterate by each value in custom missing values list and check the value in a column
            for missing_value in self.missing_values:
                if missing_value is None:
                    # check all pandas null-types like numpy.NAN, pandas.NA, pandas.NaT, etc
                    column_missing_value = dataset[column_name].isnull().sum()

                else:
                    column_missing_value = (dataset[column_name] == missing_value).sum()

                if column_missing_value > 0:
                    # increase overall counter
                    number_of_missing_values += column_missing_value
                    # increase by-column counter
                    number_of_missing_values_by_column[column_name] += column_missing_value
                    # increase by-missing-value counter for each column
                    different_missing_values_by_column[column_name][missing_value] += column_missing_value
                    # increase by-missing-value counter
                    different_missing_values[missing_value] += column_missing_value
                    # add the column to set of columns with a missing value
                    columns_with_missing_values.add(column_name)

        dsf = dataset.isin(self.missing_values)
        if None in self.missing_values:
            dsf = dsf | dataset.isnull()
        number_of_rows_with_missing_values = dsf.any(axis="columns").sum()

        if number_of_rows == 0:
            share_of_missing_values_by_column = {}
            share_of_rows_with_missing_values = 0.0
            share_of_missing_values = 0.0

        else:
            share_of_missing_values_by_column = {
                column_name: value / number_of_rows for column_name, value in number_of_missing_values_by_column.items()
            }
            share_of_missing_values = number_of_missing_values / (number_of_columns * number_of_rows)
            share_of_rows_with_missing_values = number_of_rows_with_missing_values / number_of_rows

        number_of_different_missing_values_by_column = {}

        for column_name, missing_values in different_missing_values_by_column.items():
            # count a number of missing values that have a value in the column
            number_of_different_missing_values_by_column[column_name] = len(
                {keys for keys, values in missing_values.items() if values > 0}
            )

        number_of_columns_with_missing_values = len(columns_with_missing_values)
        number_of_different_missing_values = len(
            {k for k in different_missing_values if different_missing_values[k] > 0}
        )

        if number_of_columns == 0:
            share_of_columns_with_missing_values = 0.0

        else:
            share_of_columns_with_missing_values = number_of_columns_with_missing_values / number_of_columns

        return DatasetMissingValues(
            different_missing_values=different_missing_values,
            number_of_different_missing_values=number_of_different_missing_values,
            different_missing_values_by_column=different_missing_values_by_column,
            number_of_different_missing_values_by_column=number_of_different_missing_values_by_column,
            number_of_missing_values=number_of_missing_values,
            share_of_missing_values=share_of_missing_values,
            number_of_missing_values_by_column=number_of_missing_values_by_column,
            share_of_missing_values_by_column=share_of_missing_values_by_column,
            number_of_rows=number_of_rows,
            number_of_rows_with_missing_values=number_of_rows_with_missing_values,
            share_of_rows_with_missing_values=share_of_rows_with_missing_values,
            number_of_columns=number_of_columns,
            columns_with_missing_values=sorted(columns_with_missing_values),
            number_of_columns_with_missing_values=len(columns_with_missing_values),
            share_of_columns_with_missing_values=share_of_columns_with_missing_values,
        )

    def calculate(self, data: InputData) -> DatasetMissingValuesMetricResult:
        if not self.missing_values:
            raise ValueError("Missing values list should not be empty.")

        current_missing_values = self._calculate_missing_values_stats(data.current_data)

        if data.reference_data is not None:
            reference_missing_values: Optional[DatasetMissingValues] = self._calculate_missing_values_stats(
                data.reference_data
            )

        else:
            reference_missing_values = None

        return DatasetMissingValuesMetricResult(
            current=current_missing_values,
            reference=reference_missing_values,
        )


@default_renderer(wrap_type=DatasetMissingValuesMetric)
class DatasetMissingValuesMetricRenderer(MetricRenderer):
    def _get_table_stat(self, dataset_name: str, stats: DatasetMissingValues) -> BaseWidgetInfo:
        matched_stat = [(k, v) for k, v in stats.number_of_missing_values_by_column.items()]
        matched_stat = sorted(matched_stat, key=lambda x: x[1], reverse=True)
        matched_stat_headers = ["Value", "Count"]
        table_tab = table_data(
            title="",
            column_names=matched_stat_headers,
            data=matched_stat,
        )
        histogram_tab = histogram(
            title="",
            primary_hist=HistogramData(
                name="",
                x=pd.Series(stats.number_of_missing_values_by_column.keys()),
                count=pd.Series(stats.number_of_missing_values_by_column.values()),
            ),
            color_options=self.color_options,
        )
        return widget_tabs(
            title=f"{dataset_name.capitalize()} dataset",
            tabs=[
                TabData(title="Table", widget=table_tab),
                TabData(
                    title="Histogram",
                    widget=histogram_tab,
                ),
            ],
        )

    @staticmethod
    def _get_info_string(stats: DatasetMissingValues) -> str:
        percents = round(stats.share_of_missing_values * 100, 3)
        return f"{stats.number_of_missing_values} ({percents}%)"

    def _get_overall_missing_values_info(self, metric_result: DatasetMissingValuesMetricResult) -> BaseWidgetInfo:
        counters = [
            CounterData.string(
                "Missing values (Current data)",
                self._get_info_string(metric_result.current),
            ),
        ]
        if metric_result.reference is not None:
            counters.append(
                CounterData.string(
                    "Missing values (Reference data)",
                    self._get_info_string(metric_result.reference),
                ),
            )

        return counter(
            title="",
            counters=counters,
        )

    def render_html(self, obj: DatasetMissingValuesMetric) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        result = [
            header_text(label="Dataset Missing Values"),
            self._get_overall_missing_values_info(metric_result),
            self._get_table_stat(dataset_name="current", stats=metric_result.current),
        ]

        if metric_result.reference is not None:
            result.append(self._get_table_stat(dataset_name="reference", stats=metric_result.reference))

        return result
