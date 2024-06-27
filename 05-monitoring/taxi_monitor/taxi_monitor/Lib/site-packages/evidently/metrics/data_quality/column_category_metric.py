from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pandas as pd

from evidently.base_metric import ColumnName
from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.core import IncludeTags
from evidently.metric_results import HistogramData
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import CounterData
from evidently.renderers.html_widgets import counter
from evidently.renderers.html_widgets import header_text


class CategoryStat(MetricResult):
    class Config:
        field_tags = {"all_num": {IncludeTags.Extra}}

    all_num: int
    category_num: int
    category_ratio: float


class CountOfValues(MetricResult):
    current: HistogramData
    reference: Optional[HistogramData] = None


class ColumnCategoryMetricResult(MetricResult):
    class Config:
        pd_exclude_fields = {"counts"}
        field_tags = {
            "current": {IncludeTags.Current},
            "reference": {IncludeTags.Reference},
            "column_name": {IncludeTags.Parameter},
            "counts": {IncludeTags.Extra},
        }

    def __init__(self, **data):
        """for backward compatibility"""
        if "counts_of_values" in data:
            counts_of_values: Dict[str, pd.DataFrame] = data.pop("counts_of_values")
            counts = CountOfValues(
                current=HistogramData(x=counts_of_values["current"]["x"], count=counts_of_values["current"]["count"])
            )
            if "reference" in counts_of_values:
                counts.reference = HistogramData(
                    x=counts_of_values["reference"]["x"], count=counts_of_values["reference"]["count"]
                )
            data["counts"] = counts
        super().__init__(**data)

    column_name: str
    category: Union[int, float, str]
    current: CategoryStat
    reference: Optional[CategoryStat] = None
    counts: CountOfValues

    @property
    def counts_of_values(self) -> Dict[str, pd.DataFrame]:
        """for backward compatibility"""
        result = {"current": pd.DataFrame({"x": self.counts.current.x, "count": self.counts.current.count})}
        if self.counts.reference is not None:
            result["reference"] = pd.DataFrame({"x": self.counts.reference.x, "count": self.counts.reference.count})
        return result


class ColumnCategoryMetric(Metric[ColumnCategoryMetricResult]):
    """Calculates count and shares of values in the predefined values list"""

    column_name: ColumnName
    category: Union[int, float, str]

    def __init__(
        self, column_name: Union[str, ColumnName], category: Union[int, float, str], options: AnyOptions = None
    ) -> None:
        self.column_name = ColumnName.from_any(column_name)
        self.category = category
        super().__init__(options=options)

    def calculate(self, data: InputData) -> ColumnCategoryMetricResult:
        if not data.has_column(self.column_name):
            raise ValueError(f"Column '{self.column_name.display_name}' was not found in data.")

        current_column = data.get_current_column(self.column_name)
        reference_column = data.get_reference_column(self.column_name)

        counts_of_values = {}
        current_counts = current_column.value_counts(dropna=False).reset_index()
        current_counts.columns = ["x", "count"]
        counts_of_values["current"] = current_counts.head(10)
        counts_of_values["current"].index = counts_of_values["current"].index.astype("str")
        if reference_column is not None:
            reference_counts = reference_column.value_counts(dropna=False).reset_index()
            reference_counts.columns = ["x", "count"]
            counts_of_values["reference"] = reference_counts.head(10)
            counts_of_values["reference"].index = counts_of_values["reference"].index.astype("str")

        reference: Optional[CategoryStat] = None
        if reference_column is not None:
            reference = CategoryStat(
                all_num=len(reference_column),
                category_num=(reference_column == self.category).sum(),
                category_ratio=(reference_column == self.category).mean(),
            )
        return ColumnCategoryMetricResult(
            column_name=self.column_name.display_name,
            category=self.category,
            current=CategoryStat(
                all_num=current_column.shape[0],
                category_num=(current_column == self.category).sum(),
                category_ratio=(current_column == self.category).mean(),
            ),
            reference=reference,
            counts_of_values=counts_of_values,
        )


@default_renderer(wrap_type=ColumnCategoryMetric)
class ColumnCategoryMetricRenderer(MetricRenderer):
    def _get_count_info(self, stat: CategoryStat):
        percents = round(stat.category_ratio * 100, 3)
        return f"{stat.category_num} out of {stat.all_num} ({percents}%)"

    def render_html(self, obj: ColumnCategoryMetric) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        result = [header_text(label=f"Column '{metric_result.column_name}'. Сategory '{metric_result.category}'.")]
        counters = [
            CounterData.string(
                label="current",
                value=self._get_count_info(metric_result.current),
            ),
        ]

        if metric_result.reference is not None:
            counters.append(
                CounterData.string(
                    label="reference",
                    value=self._get_count_info(metric_result.reference),
                ),
            )
        result.append(counter(counters=counters))
        return result
