import collections
import re
from typing import Dict
from typing import List
from typing import Optional
from typing import Pattern

import pandas as pd

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.calculations.data_quality import get_rows_count
from evidently.core import IncludeTags
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


class DataIntegrityValueByRegexpStat(MetricResult):
    """Statistics about matched by a regular expression values in a column for one dataset"""

    class Config:
        pd_exclude_fields = {"table_of_matched", "table_of_not_matched"}

        field_tags = {
            "number_of_rows": {IncludeTags.Extra},
            "table_of_matched": {IncludeTags.Extra},
            "table_of_not_matched": {IncludeTags.Extra},
        }

    # count of matched values in the column, without NaNs
    number_of_matched: int
    # count of not matched values in the column, without NaNs
    number_of_not_matched: int
    # count of rows in the column, including matched, not matched and NaNs
    number_of_rows: int
    # map with matched values (keys) and count of the values (value)
    table_of_matched: Dict[str, int]
    # map with not matched values (keys) and count of the values (values)
    table_of_not_matched: Dict[str, int]


class DataIntegrityValueByRegexpMetricResult(MetricResult):
    class Config:
        field_tags = {
            "current": {IncludeTags.Current},
            "reference": {IncludeTags.Reference},
            "column_name": {IncludeTags.Parameter},
            "reg_exp": {IncludeTags.Parameter},
            "top": {IncludeTags.Parameter},
        }

    # name of the column that we check by the regular expression
    column_name: str
    # the regular expression as a string
    reg_exp: str
    top: int
    # match statistic for current dataset
    current: DataIntegrityValueByRegexpStat
    # match statistic for reference dataset, equals None if the reference is not present
    reference: Optional[DataIntegrityValueByRegexpStat] = None


class ColumnRegExpMetric(Metric[DataIntegrityValueByRegexpMetricResult]):
    """Count number of values in a column matched or not by a regular expression (regexp)"""

    # name of the column that we check
    column_name: str
    # the regular expression
    reg_exp: str
    top: int
    # compiled regular expression for speed optimization
    _reg_exp_compiled: Pattern

    def __init__(self, column_name: str, reg_exp: str, top: int = 10, options: AnyOptions = None):
        self.top = top
        self.reg_exp = reg_exp
        self.column_name = column_name
        self._reg_exp_compiled = re.compile(reg_exp)
        super().__init__(options=options)

    def _calculate_stats_by_regexp(self, column: pd.Series) -> DataIntegrityValueByRegexpStat:
        number_of_matched = 0
        number_of_na = 0
        number_of_not_matched = 0
        table_of_matched: Dict[str, int] = collections.defaultdict(int)
        table_of_not_matched: Dict[str, int] = collections.defaultdict(int)

        for item in column:
            if pd.isna(item):
                number_of_na += 1
                continue

            item = str(item)

            if bool(self._reg_exp_compiled.match(str(item))):
                number_of_matched += 1
                table_of_matched[item] += 1

            else:
                number_of_not_matched += 1
                table_of_not_matched[item] += 1
        matched = sorted(table_of_matched.items(), key=lambda x: x[1], reverse=True)
        table_of_matched = {k: v for k, v in matched[: self.top]}

        not_matched = sorted(table_of_not_matched.items(), key=lambda x: x[1], reverse=True)
        table_of_not_matched = {k: v for k, v in not_matched[: self.top]}

        return DataIntegrityValueByRegexpStat(
            number_of_matched=number_of_matched,
            number_of_not_matched=number_of_not_matched,
            number_of_rows=get_rows_count(column),
            table_of_matched=table_of_matched,
            table_of_not_matched=table_of_not_matched,
        )

    def calculate(self, data: InputData) -> DataIntegrityValueByRegexpMetricResult:
        if self.top < 1:
            raise ValueError("Parameter top must be >= 1")

        if not self.reg_exp:
            raise ValueError("Parameter reg_exp must be not empty for ColumnRegExpMetric")

        if self.column_name not in data.current_data:
            raise ValueError(f"Column {self.column_name} not found in current dataset.")

        current = self._calculate_stats_by_regexp(data.current_data[self.column_name])
        reference = None

        if data.reference_data is not None:
            if self.column_name not in data.reference_data:
                raise ValueError(f"Column {self.column_name} was not found in reference dataset.")

            reference = self._calculate_stats_by_regexp(data.reference_data[self.column_name])

        return DataIntegrityValueByRegexpMetricResult(
            column_name=self.column_name,
            reg_exp=self.reg_exp,
            top=self.top,
            current=current,
            reference=reference,
        )


@default_renderer(wrap_type=ColumnRegExpMetric)
class ColumnRegExpMetricRenderer(MetricRenderer):
    @staticmethod
    def _get_counters(dataset_name: str, metrics: DataIntegrityValueByRegexpStat) -> BaseWidgetInfo:
        percents = round(metrics.number_of_not_matched * 100 / metrics.number_of_rows, 3)
        counters = [
            CounterData(label="Number of Values", value=f"{metrics.number_of_rows}"),
            CounterData(
                label="Mismatched",
                value=f"{metrics.number_of_not_matched} ({percents}%)",
            ),
        ]
        return counter(
            counters=counters,
            title=f"{dataset_name.capitalize()} dataset",
        )

    @staticmethod
    def _get_table_stat(dataset_name: str, top: int, metrics: DataIntegrityValueByRegexpStat) -> BaseWidgetInfo:
        return table_data(
            title=f"{dataset_name.capitalize()} Dataset: top {top} mismatched values",
            column_names=["Value", "Count"],
            data=metrics.table_of_not_matched.items(),
        )

    def render_html(self, obj: ColumnRegExpMetric) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        column_name = metric_result.column_name

        result = [
            header_text(label=f"RegExp Match for column '{column_name}'."),
            self._get_counters("current", metric_result.current),
        ]

        if metric_result.reference is not None:
            result.append(self._get_counters("reference", metric_result.reference))

        current_table = self._get_table_stat("current", metric_result.top, metric_result.current)

        if metric_result.reference is not None:
            tables_tabs = [
                TabData(title="Current dataset", widget=current_table),
                TabData(
                    title="Reference dataset",
                    widget=self._get_table_stat("reference", metric_result.top, metric_result.reference),
                ),
            ]
            tables = widget_tabs(tabs=tables_tabs)

        else:
            tables = current_table

        result.append(tables)
        return result
