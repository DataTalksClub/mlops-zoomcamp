from typing import List
from typing import Optional

import pandas as pd
from sklearn import metrics

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.calculations.classification_performance import get_prediction_data
from evidently.core import IncludeTags
from evidently.metric_results import PredictionData
from evidently.metric_results import ROCCurve
from evidently.metric_results import ROCCurveData
from evidently.model.widget import BaseWidgetInfo
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import TabData
from evidently.renderers.html_widgets import get_roc_auc_tab_data
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import widget_tabs
from evidently.utils.data_operations import process_columns


class ClassificationRocCurveResults(MetricResult):
    class Config:
        pd_include = False

        field_tags = {"current_roc_curve": {IncludeTags.Current}, "reference_roc_curve": {IncludeTags.Reference}}

    current_roc_curve: Optional[ROCCurve] = None
    reference_roc_curve: Optional[ROCCurve] = None


class ClassificationRocCurve(Metric[ClassificationRocCurveResults]):
    def calculate(self, data: InputData) -> ClassificationRocCurveResults:
        dataset_columns = process_columns(data.current_data, data.column_mapping)
        target_name = dataset_columns.utility_columns.target
        prediction_name = dataset_columns.utility_columns.prediction
        if target_name is None or prediction_name is None:
            raise ValueError("The columns 'target' and 'prediction' columns should be present")
        curr_predictions = get_prediction_data(data.current_data, dataset_columns, data.column_mapping.pos_label)
        if curr_predictions.prediction_probas is None:
            raise ValueError("Roc Curve can be calculated only on binary probabilistic predictions")
        curr_roc_curve = self.calculate_metrics(data.current_data[target_name], curr_predictions)
        ref_roc_curve = None
        if data.reference_data is not None:
            ref_predictions = get_prediction_data(data.reference_data, dataset_columns, data.column_mapping.pos_label)
            ref_roc_curve = self.calculate_metrics(data.reference_data[target_name], ref_predictions)
        return ClassificationRocCurveResults(
            current_roc_curve=curr_roc_curve,
            reference_roc_curve=ref_roc_curve,
        )

    def calculate_metrics(self, target_data: pd.Series, prediction: PredictionData) -> ROCCurve:
        labels = prediction.labels
        if prediction.prediction_probas is None:
            raise ValueError("Roc Curve can be calculated only on binary probabilistic predictions")
        binaraized_target = (target_data.values.reshape(-1, 1) == labels).astype(int)
        roc_curve = {}
        if len(labels) <= 2:
            binaraized_target = pd.DataFrame(binaraized_target[:, 0])
            binaraized_target.columns = ["target"]

            fpr, tpr, thrs = metrics.roc_curve(binaraized_target, prediction.prediction_probas.iloc[:, 0])
            roc_curve[prediction.prediction_probas.columns[0]] = ROCCurveData(
                fpr=fpr.tolist(), tpr=tpr.tolist(), thrs=thrs.tolist()
            )
        else:
            binaraized_target = pd.DataFrame(binaraized_target)
            binaraized_target.columns = labels

            for label in labels:
                fpr, tpr, thrs = metrics.roc_curve(binaraized_target[label], prediction.prediction_probas[label])
                roc_curve[label] = ROCCurveData(fpr=fpr.tolist(), tpr=tpr.tolist(), thrs=thrs.tolist())
        return roc_curve


@default_renderer(wrap_type=ClassificationRocCurve)
class ClassificationRocCurveRenderer(MetricRenderer):
    def render_html(self, obj: ClassificationRocCurve) -> List[BaseWidgetInfo]:
        current_roc_curve: Optional[ROCCurve] = obj.get_result().current_roc_curve
        reference_roc_curve: Optional[ROCCurve] = obj.get_result().reference_roc_curve
        if current_roc_curve is None:
            return []

        tab_data = get_roc_auc_tab_data(current_roc_curve, reference_roc_curve, color_options=self.color_options)
        if len(tab_data) == 1:
            return [header_text(label="ROC Curve"), tab_data[0][1]]
        tabs = [TabData(name, widget) for name, widget in tab_data]
        return [header_text(label="ROC Curve"), widget_tabs(title="", tabs=tabs)]
