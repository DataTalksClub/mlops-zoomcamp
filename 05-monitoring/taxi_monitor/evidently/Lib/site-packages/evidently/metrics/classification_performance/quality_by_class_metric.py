from typing import List
from typing import Optional

import numpy as np
import pandas as pd
import plotly.figure_factory as ff
import sklearn
from plotly import graph_objs as go
from plotly.subplots import make_subplots

from evidently.base_metric import InputData
from evidently.base_metric import MetricResult
from evidently.core import AllDict
from evidently.core import IncludeTags
from evidently.metric_results import DatasetColumns
from evidently.metrics.classification_performance.base_classification_metric import ThresholdClassificationMetric
from evidently.metrics.classification_performance.objects import ClassesMetrics
from evidently.metrics.classification_performance.objects import ClassificationReport
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import WidgetSize
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import plotly_figure
from evidently.utils.data_operations import process_columns


class ClassificationQuality(MetricResult):
    metrics: ClassesMetrics
    roc_aucs: Optional[List[float]]

    @property
    def metrics_dict(self):
        return self.dict(include={"metrics"}, exclude={"metrics": AllDict({"type"})})["metrics"]


class ClassificationQualityByClassResult(MetricResult):
    class Config:
        field_tags = {
            "current": {IncludeTags.Current},
            "reference": {IncludeTags.Reference},
            "columns": {IncludeTags.Parameter},
        }

    columns: DatasetColumns
    current: ClassificationQuality
    reference: Optional[ClassificationQuality]

    def get_pandas(self) -> pd.DataFrame:
        dfs = []
        for field in ["current", "reference"]:
            value: Optional[ClassificationQuality] = getattr(self, field)
            if value is None:
                continue
            for class_value, class_metrics in value.metrics.items():
                df = class_metrics.get_pandas()
                df["class_value"] = class_value
                df["dataset"] = field
                dfs.append(df)
        return pd.concat(dfs)


class ClassificationQualityByClass(ThresholdClassificationMetric[ClassificationQualityByClassResult]):
    def __init__(
        self,
        probas_threshold: Optional[float] = None,
        k: Optional[int] = None,
        options: AnyOptions = None,
    ):
        super().__init__(probas_threshold, k, options=options)

    def calculate(self, data: InputData) -> ClassificationQualityByClassResult:
        columns = process_columns(data.current_data, data.column_mapping)
        target, prediction = self.get_target_prediction_data(
            data.current_data,
            column_mapping=data.column_mapping,
        )
        metrics_matrix = ClassificationReport.create(
            target,
            prediction.predictions,
        ).classes

        current_roc_aucs = None
        if prediction.prediction_probas is not None:
            binaraized_target = (target.values.reshape(-1, 1) == list(prediction.prediction_probas.columns)).astype(int)
            current_roc_aucs = sklearn.metrics.roc_auc_score(
                binaraized_target, prediction.prediction_probas, average=None
            ).tolist()
        reference_roc_aucs = None

        reference = None
        if data.reference_data is not None:
            ref_target, ref_prediction = self.get_target_prediction_data(
                data.reference_data,
                column_mapping=data.column_mapping,
            )
            ref_metrics = ClassificationReport.create(
                ref_target,
                ref_prediction.predictions,
            ).classes
            if ref_prediction.prediction_probas is not None:
                binaraized_target = (
                    ref_target.values.reshape(-1, 1) == list(ref_prediction.prediction_probas.columns)
                ).astype(int)
                reference_roc_aucs = sklearn.metrics.roc_auc_score(
                    binaraized_target, ref_prediction.prediction_probas, average=None
                ).tolist()
            reference = ClassificationQuality(metrics=ref_metrics, roc_aucs=reference_roc_aucs)
        return ClassificationQualityByClassResult(
            columns=columns,
            current=ClassificationQuality(metrics=metrics_matrix, roc_aucs=current_roc_aucs),
            reference=reference,
        )


@default_renderer(wrap_type=ClassificationQualityByClass)
class ClassificationQualityByClassRenderer(MetricRenderer):
    def render_html(self, obj: ClassificationQualityByClass) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        columns = metric_result.columns
        current_metrics = metric_result.current.metrics_dict
        current_roc_aucs = metric_result.current.roc_aucs
        reference_metrics = metric_result.reference.metrics_dict if metric_result.reference is not None else None
        reference_roc_aucs = metric_result.reference.roc_aucs if metric_result.reference is not None else None

        metrics_frame = pd.DataFrame(current_metrics)
        names = metrics_frame.columns.tolist()
        if columns.target_names is not None and isinstance(columns.target_names, dict):
            # todo: refactor columns data typing
            names = [columns.target_names[int(x)] for x in names]  # type: ignore
        z = metrics_frame.iloc[:-1].values
        x = list(map(str, names))
        y = ["precision", "recall", "f1-score"]
        if current_roc_aucs is not None and len(current_roc_aucs) > 2:
            z = np.append(z, [current_roc_aucs], axis=0)
            y.append("roc-auc")

        # change each element of z to type string for annotations
        z_text = [[str(round(y, 3)) for y in x] for x in z]

        if reference_metrics is not None:
            cols = 2
            subplot_titles = ["current", "reference"]
        else:
            cols = 1
            subplot_titles = [""]
        fig = make_subplots(rows=1, cols=cols, subplot_titles=subplot_titles, shared_yaxes=True)
        trace = go.Heatmap(
            z=z,
            x=x,
            y=y,
            text=z_text,
            texttemplate="%{text}",
            coloraxis="coloraxis",
        )
        fig.add_trace(trace, 1, 1)

        if reference_metrics is not None:
            ref_metrics_frame = pd.DataFrame(reference_metrics)
            z = ref_metrics_frame.iloc[:-1].values
            x = list(map(str, names))
            y = ["precision", "recall", "f1-score"]

            if current_roc_aucs is not None and len(current_roc_aucs) > 2:
                assert reference_roc_aucs is not None
                z = np.append(z, [reference_roc_aucs], axis=0)
                y.append("roc-auc")

            z_text = [[str(round(y, 3)) for y in x] for x in z]
            trace = go.Heatmap(
                z=z,
                x=x,
                y=y,
                text=z_text,
                texttemplate="%{text}",
                coloraxis="coloraxis",
            )
            fig.add_trace(trace, 1, 2)
        fig.update_layout(coloraxis={"colorscale": "RdBu_r"})

        return [
            header_text(label="Quality Metrics by Class"),
            plotly_figure(figure=fig, title=""),
        ]


def _plot_metrics(columns: DatasetColumns, metrics_matrix: dict, title: str, size: WidgetSize):
    metrics_frame = pd.DataFrame(metrics_matrix)

    z = metrics_frame.iloc[:-1, :-3].values

    x = columns.target_names if columns.target_names else metrics_frame.columns.tolist()[:-3]

    y = ["precision", "recall", "f1-score"]

    # change each element of z to type string for annotations
    z_text = [[str(round(y, 3)) for y in x] for x in z]

    # set up figure
    fig = ff.create_annotated_heatmap(z, x=x, y=y, annotation_text=z_text, colorscale="bluered", showscale=True)
    fig.update_layout(xaxis_title="Class", yaxis_title="Metric")

    return plotly_figure(
        title=title,
        figure=fig,
        size=size,
    )
