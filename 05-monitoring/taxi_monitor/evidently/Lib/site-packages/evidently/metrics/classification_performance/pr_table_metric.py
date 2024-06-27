from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import Union

import pandas as pd

from evidently._pydantic_compat import BaseModel
from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.calculations.classification_performance import calculate_pr_table
from evidently.calculations.classification_performance import get_prediction_data
from evidently.core import IncludeTags
from evidently.metric_results import Label
from evidently.metric_results import PredictionData
from evidently.model.widget import BaseWidgetInfo
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import TabData
from evidently.renderers.html_widgets import WidgetSize
from evidently.renderers.html_widgets import table_data
from evidently.renderers.html_widgets import widget_tabs
from evidently.utils.data_operations import process_columns

if TYPE_CHECKING:
    from evidently._pydantic_compat import Model


class LabelModel(BaseModel):
    __root__: Union[int, str]

    def validate(cls: Type["Model"], value: Any):  # type: ignore[override, misc]
        try:
            return int(value)
        except TypeError:
            return value


PRTable = Dict[Union[LabelModel, Label], List[List[Union[float, int]]]]


class ClassificationPRTableResults(MetricResult):
    class Config:
        pd_include = False
        field_tags = {"current": {IncludeTags.Current}, "reference": {IncludeTags.Reference}}

    current: Optional[PRTable] = None
    reference: Optional[PRTable] = None


class ClassificationPRTable(Metric[ClassificationPRTableResults]):
    def calculate(self, data: InputData) -> ClassificationPRTableResults:
        dataset_columns = process_columns(data.current_data, data.column_mapping)
        target_name = dataset_columns.utility_columns.target
        prediction_name = dataset_columns.utility_columns.prediction
        if target_name is None or prediction_name is None:
            raise ValueError("The columns 'target' and 'prediction' columns should be present")
        curr_prediction = get_prediction_data(data.current_data, dataset_columns, data.column_mapping.pos_label)
        curr_pr_table = self.calculate_metrics(data.current_data[target_name], curr_prediction)
        ref_pr_table = None
        if data.reference_data is not None:
            ref_prediction = get_prediction_data(data.reference_data, dataset_columns, data.column_mapping.pos_label)
            ref_pr_table = self.calculate_metrics(data.reference_data[target_name], ref_prediction)
        return ClassificationPRTableResults(
            current=curr_pr_table,
            reference=ref_pr_table,
        )

    def calculate_metrics(self, target_data: pd.Series, prediction: PredictionData):
        labels = prediction.labels
        if prediction.prediction_probas is None:
            raise ValueError("PR Table can be calculated only on binary probabilistic predictions")
        binaraized_target = (target_data.values.reshape(-1, 1) == labels).astype(int)
        pr_table = {}
        if len(labels) <= 2:
            binaraized_target = pd.DataFrame(binaraized_target[:, 0])
            binaraized_target.columns = ["target"]

            binded = list(
                zip(
                    binaraized_target["target"].tolist(),
                    prediction.prediction_probas.iloc[:, 0].tolist(),
                )
            )
            pr_table[prediction.prediction_probas.columns[0]] = calculate_pr_table(binded)
        else:
            binaraized_target = pd.DataFrame(binaraized_target)
            binaraized_target.columns = labels

            for label in labels:
                binded = list(
                    zip(
                        binaraized_target[label].tolist(),
                        prediction.prediction_probas[label],
                    )
                )
                pr_table[label] = calculate_pr_table(binded)
        return pr_table


@default_renderer(wrap_type=ClassificationPRTable)
class ClassificationPRTableRenderer(MetricRenderer):
    def render_html(self, obj: ClassificationPRTable) -> List[BaseWidgetInfo]:
        reference_pr_table = obj.get_result().reference
        current_pr_table = obj.get_result().current
        columns = ["Top(%)", "Count", "Prob", "TP", "FP", "Precision", "Recall"]
        result = []
        size = WidgetSize.FULL
        # if reference_pr_table is not None:
        #     size = WidgetSize.HALF
        if current_pr_table is not None:
            if len(current_pr_table.keys()) == 1:
                result.append(
                    table_data(
                        column_names=columns,
                        data=current_pr_table[list(current_pr_table.keys())[0]],
                        title="Current: Precision-Recall Table",
                        size=size,
                    )
                )
            else:
                tab_data = []
                for label in current_pr_table.keys():
                    table = table_data(
                        column_names=columns,
                        data=current_pr_table[label],
                        title="",
                        size=size,
                    )
                    tab_data.append(TabData(str(label), table))
                result.append(widget_tabs(title="Current: Precision-Recall Table", tabs=tab_data))
        if reference_pr_table is not None:
            if len(reference_pr_table.keys()) == 1:
                result.append(
                    table_data(
                        column_names=columns,
                        data=reference_pr_table[list(reference_pr_table.keys())[0]],
                        title="Reference: Precision-Recall Table",
                        size=size,
                    )
                )
            else:
                tab_data = []
                for label in reference_pr_table.keys():
                    table = table_data(
                        column_names=columns,
                        data=reference_pr_table[label],
                        title="",
                        size=size,
                    )
                    tab_data.append(TabData(str(label), table))
                result.append(widget_tabs(title="Reference: Precision-Recall Table", tabs=tab_data))
        return result
