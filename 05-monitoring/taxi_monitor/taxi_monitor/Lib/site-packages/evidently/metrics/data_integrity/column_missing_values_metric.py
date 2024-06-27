from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional

import numpy as np
import pandas as pd

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.core import IncludeTags
from evidently.metrics.data_integrity.dataset_missing_values_metric import MissingValue
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import CounterData
from evidently.renderers.html_widgets import TabData
from evidently.renderers.html_widgets import counter
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import table_data
from evidently.renderers.html_widgets import widget_tabs


class ColumnMissingValues(MetricResult):
    """Statistics about missing values in a column"""

    class Config:
        pd_exclude_fields = {"different_missing_values"}
        field_tags = {"number_of_rows": {IncludeTags.Extra}, "different_missing_values": {IncludeTags.Extra}}

    # count of rows in the column
    number_of_rows: int
    # set of different missed values in the column
    different_missing_values: Dict[MissingValue, int]
    # number of different missed values in the column
    number_of_different_missing_values: int
    # count of missed values in the column
    number_of_missing_values: int
    # share of missed values in the column
    share_of_missing_values: float


class ColumnMissingValuesMetricResult(MetricResult):
    class Config:
        field_tags = {
            "current": {IncludeTags.Current},
            "reference": {IncludeTags.Reference},
            "column_name": {IncludeTags.Parameter},
        }

    column_name: str
    current: ColumnMissingValues
    reference: Optional[ColumnMissingValues] = None


class ColumnMissingValuesMetric(Metric[ColumnMissingValuesMetricResult]):
    """Count missing values in a column.

    Missing value is a null or NaN value.

    Calculate an amount of missing values kinds and count for such values.
    NA-types like numpy.NaN, pandas.NaT are counted as one type.

    You can set you own missing values list with `missing_values` parameter.
    Value None in the list means that Pandas null values will be included in the calculation.

    If `replace` parameter is False - add defaults to user's list.
    If `replace` parameter is True - use values from `missing_values` list only.
    """

    # default missing values list
    DEFAULT_MISSING_VALUES: ClassVar = ["", np.inf, -np.inf, None]
    missing_values: frozenset
    column_name: str

    def __init__(
        self, column_name: str, missing_values: Optional[list] = None, replace: bool = True, options: AnyOptions = None
    ) -> None:
        self.column_name = column_name

        _missing_values: list
        if missing_values is None:
            # use default missing values list if we have no user-defined missed values
            _missing_values = self.DEFAULT_MISSING_VALUES

        elif not replace:
            # add default missing values to user-defined list
            _missing_values = self.DEFAULT_MISSING_VALUES + missing_values
        else:
            _missing_values = missing_values

        # use frozenset because metrics parameters should be immutable/hashable for deduplication
        self.missing_values = frozenset(sorted(_missing_values, key=str))
        super().__init__(options=options)

    def _calculate_missing_values_stats(self, column: pd.Series) -> ColumnMissingValues:
        different_missing_values = {value: 0 for value in self.missing_values}
        number_of_missing_values = 0

        number_of_rows = len(column)

        # iterate by each value in custom missing values list and check the value in a column
        for value in self.missing_values:
            if value is None:
                # check all pandas missing values like numpy.NAN, pandas.NA, pandas.NaT, etc
                missing_values = column.isnull().sum()

            else:
                missing_values = (column == value).sum()

            if missing_values > 0:
                # increase overall counter
                number_of_missing_values += missing_values
                # increase by-missing-value counter
                different_missing_values[value] += missing_values

        share_of_missing_values = number_of_missing_values / number_of_rows

        # sort by missing values count
        different_missing_values = {
            value: count
            for value, count in sorted(different_missing_values.items(), key=lambda item: item[1], reverse=True)
        }

        number_of_different_missing_values = sum(
            [1 for value in different_missing_values if different_missing_values[value] > 0]
        )

        return ColumnMissingValues(
            different_missing_values=different_missing_values,
            number_of_different_missing_values=number_of_different_missing_values,
            number_of_missing_values=number_of_missing_values,
            share_of_missing_values=share_of_missing_values,
            number_of_rows=number_of_rows,
        )

    def calculate(self, data: InputData) -> ColumnMissingValuesMetricResult:
        if not self.missing_values:
            raise ValueError("Missed values list should not be empty.")

        if self.column_name not in data.current_data:
            raise ValueError(f"Column {self.column_name} is not in current data.")

        current_missing_values = self._calculate_missing_values_stats(data.current_data[self.column_name])

        if data.reference_data is None:
            reference_missing_values: Optional[ColumnMissingValues] = None

        else:
            if self.column_name not in data.reference_data:
                raise ValueError(f"Column {self.column_name} is not in reference data.")

            reference_missing_values = self._calculate_missing_values_stats(data.reference_data[self.column_name])

        return ColumnMissingValuesMetricResult(
            column_name=self.column_name,
            current=current_missing_values,
            reference=reference_missing_values,
        )


@default_renderer(wrap_type=ColumnMissingValuesMetric)
class ColumnMissingValuesMetricRenderer(MetricRenderer):
    @staticmethod
    def _get_table_stat(stats: ColumnMissingValues) -> BaseWidgetInfo:
        data = []

        for missed_value, count_of_missed in stats.different_missing_values.items():
            percent_of_missed = round(count_of_missed / stats.number_of_rows * 100, 3)
            value = f"{count_of_missed} ({percent_of_missed}%)"

            if missed_value is None:
                missed_value_str = "Pandas and Numpy NA, NaN, etc."

            elif not missed_value:
                missed_value_str = "Empty string"

            else:
                missed_value_str = str(missed_value)

            data.append((missed_value_str, value))

        matched_stat_headers = ["Missing values type", "Count"]
        return table_data(
            title="",
            column_names=matched_stat_headers,
            data=data,
        )

    @staticmethod
    def _get_info_string(stats: ColumnMissingValues) -> str:
        percents = round(stats.share_of_missing_values * 100, 3)
        return f"{stats.number_of_missing_values} ({percents}%)"

    def _get_details_missing_values_info(self, metric_result: ColumnMissingValuesMetricResult) -> BaseWidgetInfo:
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

    def render_html(self, obj: ColumnMissingValuesMetric) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()

        result = [
            header_text(label=f"Missing values in column '{metric_result.column_name}'"),
            self._get_details_missing_values_info(metric_result=metric_result),
        ]

        current_table = self._get_table_stat(metric_result.current)

        if metric_result.reference is not None:
            tables = widget_tabs(
                tabs=[
                    TabData(title="Current dataset", widget=current_table),
                    TabData(
                        title="Reference dataset",
                        widget=self._get_table_stat(metric_result.reference),
                    ),
                ]
            )

        else:
            tables = current_table

        result.append(tables)
        return result
