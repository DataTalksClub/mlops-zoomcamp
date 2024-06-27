import json
from typing import Dict
from typing import List
from typing import Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.base_metric import UsesRawDataMixin
from evidently.calculations.classification_performance import get_prediction_data
from evidently.core import ColumnType
from evidently.core import IncludeTags
from evidently.features.generated_features import FeatureDescriptor
from evidently.features.generated_features import GeneratedFeature
from evidently.features.non_letter_character_percentage_feature import NonLetterCharacterPercentage
from evidently.features.OOV_words_percentage_feature import OOVWordsPercentage
from evidently.features.text_length_feature import TextLength
from evidently.metric_results import StatsByFeature
from evidently.model.widget import AdditionalGraphInfo
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import header_text
from evidently.utils.data_operations import process_columns
from evidently.utils.data_preprocessing import DataDefinition


class ClassificationQualityByFeatureTableResults(MetricResult):
    class Config:
        field_tags = {
            "current": {IncludeTags.Current},
            "reference": {IncludeTags.Reference},
            "target_name": {IncludeTags.Parameter},
            "columns": {IncludeTags.Parameter},
        }

    current: StatsByFeature
    reference: Optional[StatsByFeature]

    target_name: str
    columns: List[str]


class ClassificationQualityByFeatureTable(UsesRawDataMixin, Metric[ClassificationQualityByFeatureTableResults]):
    columns: Optional[List[str]]
    descriptors: Optional[Dict[str, Dict[str, FeatureDescriptor]]]
    _text_features_gen: Optional[Dict[str, Dict[str, GeneratedFeature]]]

    def __init__(
        self,
        columns: Optional[List[str]] = None,
        descriptors: Optional[Dict[str, Dict[str, FeatureDescriptor]]] = None,
        options: AnyOptions = None,
    ):
        self.columns = columns
        self._text_features_gen = None
        self.descriptors = descriptors
        super().__init__(options=options)

    def required_features(self, data_definition: DataDefinition):
        if len(data_definition.get_columns(ColumnType.Text, features_only=True)) > 0:
            text_cols = [col.column_name for col in data_definition.get_columns(ColumnType.Text, features_only=True)]
            text_features_gen: Dict[str, Dict[str, GeneratedFeature]] = {}
            text_features_gen_result = []
            for col in text_cols:
                if self.columns is not None and col not in self.columns:
                    continue
                if self.descriptors is None or col not in self.descriptors:
                    col_dict: Dict[str, GeneratedFeature] = {
                        f"{col}: Text Length": TextLength(col),
                        f"{col}: Non Letter Character %": NonLetterCharacterPercentage(col),
                        f"{col}: OOV %": OOVWordsPercentage(col),
                    }
                else:
                    column_descriptors = self.descriptors[col]
                    col_dict = {f"{col}: " + name: value.feature(col) for name, value in column_descriptors.items()}

                text_features_gen_result += list(col_dict.values())
                text_features_gen[col] = col_dict
            self._text_features_gen = text_features_gen

            return text_features_gen_result
        else:
            return []

    def get_parameters(self) -> tuple:
        return ()

    def calculate(self, data: InputData) -> ClassificationQualityByFeatureTableResults:
        if not self.get_options().render_options.raw_data:
            return ClassificationQualityByFeatureTableResults(
                current=StatsByFeature(plot_data=pd.DataFrame()),
                reference=None,
                target_name="",
                columns=[],
            )
        dataset_columns = process_columns(data.current_data, data.column_mapping)
        target_name = dataset_columns.utility_columns.target
        prediction_name = dataset_columns.utility_columns.prediction
        curr_df = data.current_data.copy()
        ref_df = None
        if data.reference_data is not None:
            ref_df = data.reference_data.copy()
        if target_name is None or prediction_name is None:
            raise ValueError("The columns 'target' and 'prediction' should be present")
        curr_predictions = get_prediction_data(data.current_data, dataset_columns, data.column_mapping.pos_label)
        ref_predictions = None
        if ref_df is not None:
            ref_predictions = get_prediction_data(data.reference_data, dataset_columns, data.column_mapping.pos_label)
        if self.columns is None:
            columns = (
                dataset_columns.num_feature_names
                + dataset_columns.cat_feature_names
                + dataset_columns.text_feature_names
            )
        else:
            columns = list(
                np.intersect1d(
                    self.columns,
                    (
                        dataset_columns.num_feature_names
                        + dataset_columns.cat_feature_names
                        + dataset_columns.text_feature_names
                    ),
                )
            )

        # process text columns

        if self._text_features_gen is not None:
            for column, features in self._text_features_gen.items():
                columns.remove(column)
                columns += list(features.keys())
                curr_text_df = pd.concat([data.get_current_column(x.feature_name()) for x in features.values()], axis=1)
                curr_text_df.columns = list(features.keys())
                curr_df = pd.concat([curr_df.reset_index(drop=True), curr_text_df.reset_index(drop=True)], axis=1)

                if ref_df is not None:
                    ref_text_df = pd.concat(
                        [data.get_reference_column(x.feature_name()) for x in features.values()],
                        axis=1,
                    )
                    ref_text_df.columns = list(features.keys())
                    ref_df = pd.concat([ref_df.reset_index(drop=True), ref_text_df.reset_index(drop=True)], axis=1)

        table_columns = set(columns + [target_name])
        if isinstance(prediction_name, str):
            table_columns.add(prediction_name)
        if isinstance(prediction_name, list):
            table_columns = table_columns.union(set(prediction_name))
        reference = None
        if ref_df is not None:
            reference = StatsByFeature(
                plot_data=ref_df[list(table_columns)],
                predictions=ref_predictions,
            )
        return ClassificationQualityByFeatureTableResults(
            current=StatsByFeature(
                plot_data=curr_df[list(table_columns)],
                predictions=curr_predictions,
            ),
            reference=reference,
            columns=columns,
            target_name=target_name,
        )


@default_renderer(wrap_type=ClassificationQualityByFeatureTable)
class ClassificationQualityByFeatureTableRenderer(MetricRenderer):
    def render_html(self, obj: ClassificationQualityByFeatureTable) -> List[BaseWidgetInfo]:
        if not obj.get_options().render_options.raw_data:
            return []
        result = obj.get_result()
        current_data = result.current.plot_data
        reference_data = result.reference.plot_data if result.reference is not None else None
        target_name = result.target_name
        curr_predictions = result.current.predictions
        # todo: better typing?
        assert curr_predictions is not None
        ref_predictions = result.reference.predictions if result.reference is not None else None
        columns = result.columns
        if ref_predictions is not None:
            labels = np.union1d(curr_predictions.labels, ref_predictions.labels).tolist()
        else:
            labels = curr_predictions.labels

        color_options = self.color_options

        current_data["prediction_labels"] = curr_predictions.predictions.values

        if reference_data is not None and ref_predictions is not None:
            reference_data["prediction_labels"] = ref_predictions.predictions.values

        additional_graphs_data = []
        params_data = []
        for feature_name in columns:
            # add data for table in params

            params_data.append(
                {
                    "details": {
                        "parts": [{"title": "All", "id": "All" + "_" + str(feature_name)}]
                        + [{"title": str(label), "id": feature_name + "_" + str(label)} for label in labels],
                        "insights": [],
                    },
                    "f1": feature_name,
                }
            )

            # create confusion based plots
            current_data["dataset"] = "Current"
            merged_data = current_data
            facet_col: Optional[str] = None
            category_orders: Optional[dict] = None
            if reference_data is not None:
                reference_data["dataset"] = "Reference"
                merged_data = pd.concat([reference_data, current_data])
                facet_col = "dataset"
                category_orders = {"dataset": ["Current", "Reference"]}

            fig = px.histogram(
                merged_data,
                x=feature_name,
                color=target_name,
                facet_col=facet_col,
                histnorm="",
                barmode="overlay",
                category_orders=category_orders,
            )

            fig_json = json.loads(fig.to_json())

            # write plot data in table as additional data
            additional_graphs_data.append(
                AdditionalGraphInfo(
                    "All" + "_" + str(feature_name),
                    {"data": fig_json["data"], "layout": fig_json["layout"]},
                )
            )

            # Probas plots
            if curr_predictions.prediction_probas is not None:
                ref_columns = list(set(columns + ["prediction_labels", target_name]))
                current_data = pd.concat(
                    [current_data[ref_columns], curr_predictions.prediction_probas],
                    axis=1,
                )
                if (
                    reference_data is not None
                    and ref_predictions is not None
                    and ref_predictions.prediction_probas is not None
                ):
                    reference_data = pd.concat(
                        [
                            reference_data[ref_columns],
                            ref_predictions.prediction_probas,
                        ],
                        axis=1,
                    )

                if reference_data is not None:
                    cols = 2
                    subplot_titles = ["current", "reference"]
                else:
                    cols = 1
                    subplot_titles = [""]
                for label in labels:
                    fig = make_subplots(
                        rows=1,
                        cols=cols,
                        subplot_titles=subplot_titles,
                        shared_yaxes=True,
                    )

                    # current Prediction
                    fig.add_trace(
                        go.Scatter(
                            x=current_data[current_data[target_name] == label][feature_name],
                            y=current_data[current_data[target_name] == label][label],
                            mode="markers",
                            name=str(label),
                            legendgroup=str(label),
                            marker=dict(
                                size=6,
                                # set color equal to a variable
                                color=color_options.get_current_data_color(),
                            ),
                        ),
                        row=1,
                        col=1,
                    )

                    fig.add_trace(
                        go.Scatter(
                            x=current_data[current_data[target_name] != label][feature_name],
                            y=current_data[current_data[target_name] != label][label],
                            mode="markers",
                            name="other",
                            legendgroup="other",
                            marker=dict(
                                size=6,
                                # set color equal to a variable
                                color=color_options.get_reference_data_color(),
                            ),
                        ),
                        row=1,
                        col=1,
                    )

                    fig.update_xaxes(title_text=feature_name, showgrid=True, row=1, col=1)

                    # REF
                    if reference_data is not None:
                        fig.add_trace(
                            go.Scatter(
                                x=reference_data[reference_data[target_name] == label][feature_name],
                                y=reference_data[reference_data[target_name] == label][label],
                                mode="markers",
                                name=str(label),
                                legendgroup=str(label),
                                showlegend=False,
                                marker=dict(size=6, color=color_options.get_current_data_color()),
                            ),
                            row=1,
                            col=2,
                        )

                        fig.add_trace(
                            go.Scatter(
                                x=reference_data[reference_data[target_name] != label][feature_name],
                                y=reference_data[reference_data[target_name] != label][label],
                                mode="markers",
                                name="other",
                                legendgroup="other",
                                showlegend=False,
                                marker=dict(
                                    size=6,
                                    color=color_options.get_reference_data_color(),
                                ),
                            ),
                            row=1,
                            col=2,
                        )
                        fig.update_xaxes(title_text=feature_name, row=1, col=2)

                    fig.update_layout(
                        yaxis_title="Probability",
                        yaxis=dict(range=(-0.1, 1.1), showticklabels=True),
                    )

                    fig_json = json.loads(fig.to_json())

                    # write plot data in table as additional data
                    additional_graphs_data.append(
                        AdditionalGraphInfo(
                            feature_name + "_" + str(label),
                            {"data": fig_json["data"], "layout": fig_json["layout"]},
                        )
                    )
            # labels plots
            else:
                for label in labels:

                    def confusion_func(row, label=label):
                        return self._confusion(row, target_name, "prediction_labels", label)

                    merged_data["Confusion"] = merged_data.apply(confusion_func, axis=1)

                    fig = px.histogram(
                        merged_data,
                        x=feature_name,
                        color="Confusion",
                        facet_col=facet_col,
                        histnorm="",
                        barmode="overlay",
                        category_orders=category_orders,
                    )
                    fig_json = json.loads(fig.to_json())

                    # write plot data in table as additional data
                    additional_graphs_data.append(
                        AdditionalGraphInfo(
                            feature_name + "_" + str(label),
                            {"data": fig_json["data"], "layout": fig_json["layout"]},
                        )
                    )
        return [
            header_text(label="Classification Quality By Feature"),
            BaseWidgetInfo(
                title="",
                type="big_table",
                size=2,
                params={
                    "rowsPerPage": min(len(columns), 10),
                    "columns": [{"title": "Feature", "field": "f1"}],
                    "data": params_data,
                },
                additionalGraphs=additional_graphs_data,
            ),
        ]

    def _confusion(self, row, target_column, prediction_column, label):
        if row[target_column] == label and row[prediction_column] == label:
            return "TP"
        if row[target_column] != label and row[prediction_column] == label:
            return "FP"
        if row[target_column] == label and row[prediction_column] != label:
            return "FN"
        return "TN"  # last option
