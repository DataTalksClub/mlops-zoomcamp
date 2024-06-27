import json
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from pandas.api.types import is_integer_dtype
from pandas.api.types import is_string_dtype
from plotly.subplots import make_subplots

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.base_metric import UsesRawDataMixin
from evidently.calculations.classification_performance import get_prediction_data
from evidently.core import ColumnType
from evidently.core import IncludeTags
from evidently.features.non_letter_character_percentage_feature import NonLetterCharacterPercentage
from evidently.features.OOV_words_percentage_feature import OOVWordsPercentage
from evidently.features.text_length_feature import TextLength
from evidently.metric_results import StatsByFeature
from evidently.model.widget import AdditionalGraphInfo
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.utils.data_operations import process_columns
from evidently.utils.data_preprocessing import DataDefinition


class TargetByFeaturesTableResults(MetricResult):
    class Config:
        dict_include = False
        field_tags = {
            "current": {IncludeTags.Current},
            "reference": {IncludeTags.Reference},
            "target_name": {IncludeTags.Parameter},
            "columns": {IncludeTags.Parameter},
            "task": {IncludeTags.Parameter},
        }

    current: StatsByFeature
    reference: Optional[StatsByFeature]
    target_name: Optional[str]
    columns: List[str]
    task: str


class TargetByFeaturesTable(UsesRawDataMixin, Metric[TargetByFeaturesTableResults]):
    columns: Optional[List[str]]
    _text_features_gen: Optional[
        Dict[
            str,
            Dict[str, Union[TextLength, NonLetterCharacterPercentage, OOVWordsPercentage]],
        ]
    ]

    def __init__(self, columns: Optional[List[str]] = None, options: AnyOptions = None):
        self.columns = columns
        super().__init__(options=options)
        self._text_features_gen = None

    def required_features(self, data_definition: DataDefinition):
        if len(data_definition.get_columns(ColumnType.Text, features_only=True)) > 0:
            text_cols = [col.column_name for col in data_definition.get_columns(ColumnType.Text, features_only=True)]
            text_features_gen = {}
            text_features_gen_result = []
            for col in text_cols:
                col_dict: Dict[
                    str,
                    Union[TextLength, NonLetterCharacterPercentage, OOVWordsPercentage],
                ] = {}
                col_dict[f"{col}: Text Length"] = TextLength(col)
                col_dict[f"{col}: Non Letter Character %"] = NonLetterCharacterPercentage(col)
                col_dict[f"{col}: OOV %"] = OOVWordsPercentage(col)

                text_features_gen_result += [
                    col_dict[f"{col}: Text Length"],
                    col_dict[f"{col}: Non Letter Character %"],
                    col_dict[f"{col}: OOV %"],
                ]
                text_features_gen[col] = col_dict
            self._text_features_gen = text_features_gen

            return text_features_gen_result
        else:
            return []

    def get_parameters(self) -> tuple:
        return ()

    def calculate(self, data: InputData) -> TargetByFeaturesTableResults:
        if not self.get_options().render_options.raw_data:
            return TargetByFeaturesTableResults(
                current=StatsByFeature(plot_data=pd.DataFrame()),
                reference=None,
                target_name=None,
                columns=[],
                task="",
            )
        dataset_columns = process_columns(data.current_data, data.column_mapping)
        target_name = dataset_columns.utility_columns.target
        prediction_name = dataset_columns.utility_columns.prediction
        if target_name is None and prediction_name is None:
            raise ValueError("The columns 'target' or 'prediction' should be present")
        if data.reference_data is None:
            raise ValueError("Reference data should be present")
        curr_df = data.current_data.copy()
        ref_df = data.reference_data.copy()
        curr_predictions = None
        ref_predictions = None
        if prediction_name is not None:
            curr_predictions = get_prediction_data(data.current_data, dataset_columns, data.column_mapping.pos_label)
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
        if data.column_mapping.task is not None:
            task = data.column_mapping.task
        else:
            if target_name is not None:
                if curr_df[target_name].nunique() < 5 or is_string_dtype(curr_df[target_name]):
                    task = "classification"
                else:
                    task = "regression"
            elif curr_predictions is not None:
                if is_string_dtype(curr_predictions.predictions) or (
                    is_integer_dtype(curr_predictions.predictions) and curr_predictions.predictions.nunique() < 5
                ):
                    task = "classification"
                else:
                    task = "regression"
            else:
                raise ValueError("Task parameter of column_mapping should be specified")
        # process text columns
        if (
            self._text_features_gen is not None
            and len(np.intersect1d(list(self._text_features_gen.keys()), columns)) >= 1
        ):
            for col in np.intersect1d(list(self._text_features_gen.keys()), columns):
                columns += list(self._text_features_gen[col].keys())
                columns.remove(col)
                curr_text_df = pd.concat(
                    [data.get_current_column(x.feature_name()) for x in list(self._text_features_gen[col].values())],
                    axis=1,
                )
                curr_text_df.columns = list(self._text_features_gen[col].keys())
                curr_df = pd.concat(
                    [
                        curr_df.reset_index(drop=True),
                        curr_text_df.reset_index(drop=True),
                    ],
                    axis=1,
                )

                if ref_df is not None:
                    ref_text_df = pd.concat(
                        [
                            data.get_reference_column(x.feature_name())
                            for x in list(self._text_features_gen[col].values())
                        ],
                        axis=1,
                    )
                    ref_text_df.columns = list(self._text_features_gen[col].keys())
                    ref_df = pd.concat(
                        [
                            ref_df.reset_index(drop=True),
                            ref_text_df.reset_index(drop=True),
                        ],
                        axis=1,
                    )
        table_columns = columns.copy()
        if target_name is not None:
            table_columns += [target_name]
        if prediction_name is not None and isinstance(prediction_name, str):
            table_columns += [prediction_name]
        if prediction_name is not None and isinstance(prediction_name, list):
            table_columns += prediction_name

        return TargetByFeaturesTableResults(
            current=StatsByFeature(
                plot_data=curr_df[table_columns],
                predictions=curr_predictions,
            ),
            reference=StatsByFeature(
                plot_data=ref_df[table_columns],
                predictions=ref_predictions,
            ),
            columns=columns,
            target_name=target_name,
            task=task,
        )


@default_renderer(wrap_type=TargetByFeaturesTable)
class TargetByFeaturesTableRenderer(MetricRenderer):
    def render_html(self, obj: TargetByFeaturesTable) -> List[BaseWidgetInfo]:
        if not obj.get_options().render_options.raw_data:
            return []
        result = obj.get_result()
        current_data = result.current.plot_data
        # todo: better typing
        assert current_data is not None
        reference_data = result.reference.plot_data if result.reference is not None else None
        target_name = result.target_name
        curr_predictions = result.current.predictions
        ref_predictions = result.reference.predictions if result.reference is not None else None
        columns = result.columns
        task = result.task
        if curr_predictions is not None and ref_predictions is not None:
            current_data["prediction_labels"] = curr_predictions.predictions.values
            reference_data["prediction_labels"] = ref_predictions.predictions.values

        additional_graphs_data = []
        params_data = []

        for feature_name in columns:
            # add data for table in params
            parts = []

            if target_name is not None:
                parts.append({"title": "Target", "id": feature_name + "_target_values"})
                if task == "regression":
                    target_fig = self._get_regression_fig(feature_name, target_name, current_data, reference_data)
                else:
                    target_fig = self._get_classification_fig(feature_name, target_name, current_data, reference_data)

                target_fig_json = json.loads(target_fig.to_json())

                additional_graphs_data.append(
                    AdditionalGraphInfo(
                        feature_name + "_target_values",
                        {
                            "data": target_fig_json["data"],
                            "layout": target_fig_json["layout"],
                        },
                    )
                )

            if curr_predictions is not None:
                parts.append({"title": "Prediction", "id": feature_name + "_prediction_values"})
                if task == "regression":
                    preds_fig = self._get_regression_fig(
                        feature_name, "prediction_labels", current_data, reference_data
                    )
                else:
                    preds_fig = self._get_classification_fig(
                        feature_name, "prediction_labels", current_data, reference_data
                    )
                preds_fig_json = json.loads(preds_fig.to_json())

                additional_graphs_data.append(
                    AdditionalGraphInfo(
                        feature_name + "_prediction_values",
                        {
                            "data": preds_fig_json["data"],
                            "layout": preds_fig_json["layout"],
                        },
                    )
                )

            params_data.append(
                {
                    "details": {
                        "parts": parts,
                        "insights": [],
                    },
                    "f1": feature_name,
                }
            )
        return [
            BaseWidgetInfo(
                title="Target (Prediction) Behavior By Feature",
                type="big_table",
                size=2,
                params={
                    "rowsPerPage": min(len(columns), 10),
                    "columns": [{"title": "Feature", "field": "f1"}],
                    "data": params_data,
                },
                additionalGraphs=additional_graphs_data,
            )
        ]

    def _get_regression_fig(self, feature_name: str, main_column: str, curr_data: pd.DataFrame, ref_data: pd.DataFrame):
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Current", "Reference"), shared_yaxes=True)
        fig.add_trace(
            go.Scattergl(
                x=curr_data[feature_name],
                y=curr_data[main_column],
                mode="markers",
                name="current",
                marker=dict(size=6, color=self.color_options.primary_color),
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=ref_data[feature_name],
                y=ref_data[main_column],
                mode="markers",
                name="reference",
                marker=dict(size=6, color=self.color_options.secondary_color),
            ),
            row=1,
            col=2,
        )
        fig.update_xaxes(title_text=feature_name, showgrid=True, row=1, col=1)
        fig.update_xaxes(title_text=feature_name, showgrid=True, row=1, col=2)
        fig.update_yaxes(title_text=main_column, showgrid=True, row=1, col=1)

        return fig

    def _get_classification_fig(
        self, feature_name: str, main_column: str, curr_data: pd.DataFrame, ref_data: pd.DataFrame
    ):
        curr = curr_data.copy()
        ref = ref_data.copy()
        ref["dataset"] = "Reference"
        curr["dataset"] = "Current"
        merged_data = pd.concat([ref, curr])
        fig = px.histogram(
            merged_data,
            x=feature_name,
            color=main_column,
            facet_col="dataset",
            barmode="overlay",
            category_orders={"dataset": ["Current", "Reference"]},
        )

        return fig
