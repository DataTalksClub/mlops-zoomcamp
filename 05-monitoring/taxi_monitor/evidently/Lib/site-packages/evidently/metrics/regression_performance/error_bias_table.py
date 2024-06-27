import copy
import json
from typing import ClassVar
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
from evidently.calculations.regression_performance import error_bias_table
from evidently.calculations.regression_performance import error_with_quantiles
from evidently.core import ColumnType
from evidently.core import IncludeTags
from evidently.features.generated_features import FeatureDescriptor
from evidently.features.generated_features import GeneratedFeature
from evidently.features.non_letter_character_percentage_feature import NonLetterCharacterPercentage
from evidently.features.OOV_words_percentage_feature import OOVWordsPercentage
from evidently.features.text_length_feature import TextLength
from evidently.model.widget import AdditionalGraphInfo
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import header_text
from evidently.utils.data_operations import process_columns
from evidently.utils.data_preprocessing import DataDefinition


class RegressionErrorBiasTableResults(MetricResult):
    class Config:
        dict_exclude_fields = {"current_plot_data", "reference_plot_data"}
        pd_exclude_fields = {
            "current_plot_data",
            "reference_plot_data",
            "num_feature_names",
            "cat_feature_names",
            "error_bias",
            "columns",
        }

        field_tags = {
            "current_plot_data": {IncludeTags.Current, IncludeTags.Render},
            "reference_plot_data": {IncludeTags.Reference, IncludeTags.Render},
            "target_name": {IncludeTags.Parameter},
            "prediction_name": {IncludeTags.Parameter},
            "num_feature_names": {IncludeTags.Parameter},
            "cat_feature_names": {IncludeTags.Parameter},
            "columns": {IncludeTags.Parameter},
            "error_bias": {IncludeTags.Extra},
        }

    top_error: float
    current_plot_data: pd.DataFrame
    reference_plot_data: Optional[pd.DataFrame]
    target_name: str
    prediction_name: str
    num_feature_names: List[str]
    cat_feature_names: List[str]
    error_bias: Optional[dict] = None
    columns: Optional[List[str]] = None


class RegressionErrorBiasTable(UsesRawDataMixin, Metric[RegressionErrorBiasTableResults]):
    # by default, we get 5% values for the error bias calculations
    TOP_ERROR_DEFAULT: ClassVar[float] = 0.05
    TOP_ERROR_MIN: ClassVar[float] = 0
    TOP_ERROR_MAX: ClassVar[float] = 0.5
    top_error: float
    columns: Optional[List[str]]
    descriptors: Optional[Dict[str, Dict[str, FeatureDescriptor]]]
    _text_features_gen: Optional[Dict[str, Dict[str, GeneratedFeature]]]

    def __init__(
        self,
        columns: Optional[List[str]] = None,
        top_error: Optional[float] = None,
        descriptors: Optional[Dict[str, Dict[str, FeatureDescriptor]]] = None,
        options: AnyOptions = None,
    ):
        if top_error is None:
            self.top_error = self.TOP_ERROR_DEFAULT

        else:
            self.top_error = top_error

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

    def calculate(self, data: InputData) -> RegressionErrorBiasTableResults:
        if not self.get_options().render_options.raw_data:
            return RegressionErrorBiasTableResults(
                top_error=-1,
                current_plot_data=pd.DataFrame(),
                reference_plot_data=None,
                target_name="",
                prediction_name="",
                num_feature_names=[],
                cat_feature_names=[],
                error_bias=None,
                columns=None,
            )
        if self.top_error <= self.TOP_ERROR_MIN or self.top_error >= self.TOP_ERROR_MAX:
            raise ValueError(
                f"Cannot calculate error bias - "
                f"top error should be in range ({self.TOP_ERROR_MIN}, {self.TOP_ERROR_MAX})."
            )

        dataset_columns = process_columns(data.current_data, data.column_mapping)
        target_name = dataset_columns.utility_columns.target
        prediction_name = dataset_columns.utility_columns.prediction
        curr_df = data.current_data
        ref_df = data.reference_data

        if target_name is None:
            raise ValueError("Target column should be present.")

        if prediction_name is None:
            raise ValueError("Prediction column should be present.")

        if not isinstance(prediction_name, str):
            raise ValueError("Expect one column for prediction. List of columns was provided.")

        if self.columns is None:
            columns = (
                dataset_columns.num_feature_names
                + dataset_columns.cat_feature_names
                + dataset_columns.text_feature_names
            )

        else:
            columns = self.columns

        num_feature_names = list(np.intersect1d(dataset_columns.num_feature_names, columns))
        cat_feature_names = list(np.intersect1d(dataset_columns.cat_feature_names, columns))
        # process text columns
        if self._text_features_gen is not None:
            for column, features in self._text_features_gen.items():
                columns.remove(column)
                num_feature_names += list(features.keys())
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

        columns_ext = np.union1d(columns, [target_name, prediction_name])
        curr_df = self._make_df_for_plot(curr_df[columns_ext], target_name, prediction_name, None)

        if ref_df is not None:
            ref_df = self._make_df_for_plot(ref_df[columns_ext], target_name, prediction_name, None)

        err_quantiles = error_with_quantiles(curr_df, prediction_name, target_name, quantile=self.top_error)

        feature_bias = error_bias_table(curr_df, err_quantiles, num_feature_names, cat_feature_names)
        error_bias = {
            feature: dict(feature_type=bias.feature_type, **bias.as_dict("current_"))
            for feature, bias in feature_bias.items()
        }

        if error_bias is not None:
            error_bias = copy.deepcopy(error_bias)

        else:
            error_bias = None

        if ref_df is not None:
            ref_err_quantiles = error_with_quantiles(ref_df, prediction_name, target_name, quantile=self.top_error)
            ref_feature_bias = error_bias_table(ref_df, ref_err_quantiles, num_feature_names, cat_feature_names)
            ref_error_bias = {
                feature: dict(feature_type=bias.feature_type, **bias.as_dict("ref_"))
                for feature, bias in ref_feature_bias.items()
            }
            if ref_error_bias is not None:
                if error_bias is not None:
                    for feature_name, reference_bias in ref_error_bias.items():
                        error_bias[feature_name].update(reference_bias)

                else:
                    error_bias = copy.deepcopy(ref_error_bias)

        if error_bias:
            error_bias_res = error_bias
        else:
            error_bias_res = {}

        columns = list(np.intersect1d(curr_df.columns, columns))
        table_columns = columns + [target_name, prediction_name]

        return RegressionErrorBiasTableResults(
            top_error=self.top_error,
            current_plot_data=curr_df[table_columns],
            reference_plot_data=None if ref_df is None else ref_df[table_columns],
            target_name=target_name,
            prediction_name=prediction_name,
            num_feature_names=[str(v) for v in num_feature_names],
            cat_feature_names=[str(v) for v in cat_feature_names],
            error_bias=error_bias_res,
            columns=[str(v) for v in columns],
        )

    @staticmethod
    def _make_df_for_plot(
        df: pd.DataFrame, target_name: str, prediction_name: str, datetime_column_name: Optional[str]
    ):
        result = df.replace([np.inf, -np.inf], np.nan)
        if datetime_column_name is not None:
            result.dropna(
                axis=0,
                how="any",
                inplace=True,
                subset=[target_name, prediction_name, datetime_column_name],
            )
            return result.sort_values(datetime_column_name)
        result.dropna(axis=0, how="any", inplace=True, subset=[target_name, prediction_name])
        return result.sort_index()


@default_renderer(wrap_type=RegressionErrorBiasTable)
class RegressionErrorBiasTableRenderer(MetricRenderer):
    def render_html(self, obj: RegressionErrorBiasTable) -> List[BaseWidgetInfo]:
        if not obj.get_options().render_options.raw_data:
            return []
        result = obj.get_result()
        current_data = result.current_plot_data
        reference_data = result.reference_plot_data
        target_name = result.target_name
        prediction_name = result.prediction_name

        if reference_data is not None:
            ref_error = reference_data[prediction_name] - reference_data[target_name]
            current_error = current_data[prediction_name] - current_data[target_name]

            ref_quantile_top = np.quantile(ref_error, obj.top_error)
            ref_quantile_other = np.quantile(ref_error, 1 - obj.top_error)

            current_quantile_top = np.quantile(current_error, obj.top_error)
            current_quantile_other = np.quantile(current_error, 1 - obj.top_error)

            # create subplots
            reference_data["dataset"] = "Reference"
            reference_data["Error bias"] = list(
                map(
                    self._error_bias_string(ref_quantile_top, ref_quantile_other),
                    ref_error,
                )
            )

            current_data["dataset"] = "Current"
            current_data["Error bias"] = list(
                map(
                    self._error_bias_string(current_quantile_top, current_quantile_other),
                    current_error,
                )
            )
            merged_data = pd.concat([reference_data, current_data])

            reference_data.drop(["dataset", "Error bias"], axis=1, inplace=True)
            current_data.drop(["dataset", "Error bias"], axis=1, inplace=True)

            params_data = []
            additional_graphs_data = []

            for feature_name in result.num_feature_names:
                feature_type = "num"

                feature_hist = px.histogram(
                    merged_data,
                    x=feature_name,
                    color="Error bias",
                    facet_col="dataset",
                    histnorm="percent",
                    barmode="overlay",
                    category_orders={
                        "dataset": ["Reference", "Current"],
                        "Error bias": ["Underestimation", "Overestimation", "Majority"],
                    },
                )

                feature_hist_json = json.loads(feature_hist.to_json())

                segment_fig = make_subplots(rows=1, cols=2, subplot_titles=("Reference", "Current"))

                segment_fig.add_trace(
                    go.Scatter(
                        x=reference_data[target_name],
                        y=reference_data[prediction_name],
                        mode="markers",
                        marker=dict(
                            size=6,
                            cmax=max(
                                max(reference_data[feature_name]),
                                max(current_data[feature_name]),
                            ),
                            cmin=min(
                                min(reference_data[feature_name]),
                                min(current_data[feature_name]),
                            ),
                            color=reference_data[feature_name],
                        ),
                        showlegend=False,
                    ),
                    row=1,
                    col=1,
                )

                segment_fig.add_trace(
                    go.Scatter(
                        x=current_data[target_name],
                        y=current_data[prediction_name],
                        mode="markers",
                        marker=dict(
                            size=6,
                            cmax=max(
                                max(reference_data[feature_name]),
                                max(current_data[feature_name]),
                            ),
                            cmin=min(
                                min(reference_data[feature_name]),
                                min(current_data[feature_name]),
                            ),
                            color=current_data[feature_name],
                            colorbar=dict(title=feature_name),
                        ),
                        showlegend=False,
                    ),
                    row=1,
                    col=2,
                )

                # Update xaxis properties
                segment_fig.update_xaxes(title_text="Actual Value", showgrid=True, row=1, col=1)
                segment_fig.update_xaxes(title_text="Actual Value", showgrid=True, row=1, col=2)

                # Update yaxis properties
                segment_fig.update_yaxes(title_text="Predicted Value", showgrid=True, row=1, col=1)
                segment_fig.update_yaxes(title_text="Predicted Value", showgrid=True, row=1, col=2)

                segment_json = json.loads(segment_fig.to_json())

                if result.error_bias is None:
                    raise ValueError("RegressionErrorBiasTableRenderer got no error_bias value")

                params_data.append(
                    {
                        "details": {
                            "parts": [
                                {"title": "Error bias", "id": feature_name + "_hist"},
                                {
                                    "title": "Predicted vs Actual",
                                    "id": feature_name + "_segm",
                                },
                            ],
                            "insights": [],
                        },
                        "f1": feature_name,
                        "f2": feature_type,
                        "f3": round(result.error_bias[feature_name]["ref_majority"], 2),
                        "f4": round(result.error_bias[feature_name]["ref_under"], 2),
                        "f5": round(result.error_bias[feature_name]["ref_over"], 2),
                        "f6": round(result.error_bias[feature_name]["ref_range"], 2),
                        "f7": round(result.error_bias[feature_name]["current_majority"], 2),
                        "f8": round(result.error_bias[feature_name]["current_under"], 2),
                        "f9": round(result.error_bias[feature_name]["current_over"], 2),
                        "f10": round(result.error_bias[feature_name]["current_range"], 2),
                    }
                )

                additional_graphs_data.append(
                    AdditionalGraphInfo(
                        feature_name + "_hist",
                        {
                            "data": feature_hist_json["data"],
                            "layout": feature_hist_json["layout"],
                        },
                    )
                )

                additional_graphs_data.append(
                    AdditionalGraphInfo(
                        feature_name + "_segm",
                        {
                            "data": segment_json["data"],
                            "layout": segment_json["layout"],
                        },
                    )
                )

            for feature_name in result.cat_feature_names:
                feature_type = "cat"

                feature_hist = px.histogram(
                    merged_data,
                    x=feature_name,
                    color="Error bias",
                    facet_col="dataset",
                    histnorm="percent",
                    barmode="overlay",
                    category_orders={
                        "dataset": ["Reference", "Current"],
                        "Error bias": ["Underestimation", "Overestimation", "Majority"],
                    },
                )

                feature_hist_json = json.loads(feature_hist.to_json())
                segment_fig = px.scatter(
                    merged_data[~merged_data[feature_name].isna()],
                    x=target_name,
                    y=prediction_name,
                    color=feature_name,
                    facet_col="dataset",
                )

                segment_json = json.loads(segment_fig.to_json())

                if result.error_bias is None:
                    raise ValueError("RegressionErrorBiasTableRenderer got no error_bias value")

                params_data.append(
                    {
                        "details": {
                            "parts": [
                                {"title": "Error bias", "id": feature_name + "_hist"},
                                {
                                    "title": "Predicted vs Actual",
                                    "id": feature_name + "_segm",
                                },
                            ],
                            "insights": [],
                        },
                        "f1": feature_name,
                        "f2": feature_type,
                        "f3": str(result.error_bias[feature_name]["ref_majority"]),
                        "f4": str(result.error_bias[feature_name]["ref_under"]),
                        "f5": str(result.error_bias[feature_name]["ref_over"]),
                        "f6": str(result.error_bias[feature_name]["ref_range"]),
                        "f7": str(result.error_bias[feature_name]["current_majority"]),
                        "f8": str(result.error_bias[feature_name]["current_under"]),
                        "f9": str(result.error_bias[feature_name]["current_over"]),
                        "f10": int(result.error_bias[feature_name]["current_range"]),
                    }
                )

                additional_graphs_data.append(
                    AdditionalGraphInfo(
                        feature_name + "_hist",
                        {
                            "data": feature_hist_json["data"],
                            "layout": feature_hist_json["layout"],
                        },
                    )
                )

                additional_graphs_data.append(
                    AdditionalGraphInfo(
                        feature_name + "_segm",
                        {
                            "data": segment_json["data"],
                            "layout": segment_json["layout"],
                        },
                    )
                )
            if result.columns is None:
                size = 0
            else:
                size = len(result.columns)
            widget_info = BaseWidgetInfo(
                title="",
                type="big_table",
                size=2,
                params={
                    "rowsPerPage": min(size, 10),
                    "columns": [
                        {"title": "Feature", "field": "f1"},
                        {"title": "Type", "field": "f2"},
                        {"title": "REF: Majority", "field": "f3"},
                        {"title": "REF: Under", "field": "f4"},
                        {"title": "REF: Over", "field": "f5"},
                        {"title": "REF: Range(%)", "field": "f6"},
                        {"title": "CURR: Majority", "field": "f7"},
                        {"title": "CURR: Under", "field": "f8"},
                        {"title": "CURR: Over", "field": "f9"},
                        {"title": "CURR: Range(%)", "field": "f10", "sort": "desc"},
                    ],
                    "data": params_data,
                },
                additionalGraphs=additional_graphs_data,
            )

        else:
            error = current_data[prediction_name] - current_data[target_name]

            quantile_top = np.quantile(error, obj.top_error)
            quantile_other = np.quantile(error, 1 - obj.top_error)

            current_data["Error bias"] = list(
                map(
                    lambda x: "Underestimation"
                    if x <= quantile_top
                    else "Majority"
                    if x < quantile_other
                    else "Overestimation",
                    error,
                )
            )

            params_data = []
            additional_graphs_data = []

            for feature_name in result.num_feature_names:  # + cat_feature_names: #feature_names:
                feature_type = "num"

                hist = px.histogram(
                    current_data,
                    x=feature_name,
                    color="Error bias",
                    histnorm="percent",
                    barmode="overlay",
                    category_orders={"Error bias": ["Underestimation", "Overestimation", "Majority"]},
                )

                hist_figure = json.loads(hist.to_json())

                segm = px.scatter(current_data, x=target_name, y=prediction_name, color=feature_name)
                segm_figure = json.loads(segm.to_json())

                if result.error_bias is None:
                    raise ValueError("Widget RegressionErrorBiasTableRenderer got no error_bias value")

                params_data.append(
                    {
                        "details": {
                            "parts": [
                                {"title": "Error bias", "id": feature_name + "_hist"},
                                {
                                    "title": "Predicted vs Actual",
                                    "id": feature_name + "_segm",
                                },
                            ],
                            "insights": [],
                        },
                        "f1": feature_name,
                        "f2": feature_type,
                        "f3": round(result.error_bias[feature_name]["current_majority"], 2),
                        "f4": round(result.error_bias[feature_name]["current_under"], 2),
                        "f5": round(result.error_bias[feature_name]["current_over"], 2),
                        "f6": round(result.error_bias[feature_name]["current_range"], 2),
                    }
                )

                additional_graphs_data.append(
                    AdditionalGraphInfo(
                        feature_name + "_hist",
                        {"data": hist_figure["data"], "layout": hist_figure["layout"]},
                    )
                )

                additional_graphs_data.append(
                    AdditionalGraphInfo(
                        feature_name + "_segm",
                        {"data": segm_figure["data"], "layout": segm_figure["layout"]},
                    )
                )

            for feature_name in result.cat_feature_names:  # feature_names:
                feature_type = "cat"

                hist = px.histogram(
                    current_data,
                    x=feature_name,
                    color="Error bias",
                    histnorm="percent",
                    barmode="overlay",
                    category_orders={"Error bias": ["Underestimation", "Overestimation", "Majority"]},
                )

                hist_figure = json.loads(hist.to_json())

                initial_type = current_data[feature_name].dtype
                current_data[feature_name] = current_data[feature_name].astype(str)
                segm = px.scatter(current_data, x=target_name, y=prediction_name, color=feature_name)
                current_data[feature_name] = current_data[feature_name].astype(initial_type)

                segm_figure = json.loads(segm.to_json())

                if result.error_bias is None:
                    raise ValueError("RegressionErrorBiasTableRenderer got no error_bias value")

                params_data.append(
                    {
                        "details": {
                            "parts": [
                                {"title": "Error bias", "id": feature_name + "_hist"},
                                {
                                    "title": "Predicted vs Actual",
                                    "id": feature_name + "_segm",
                                },
                            ],
                            "insights": [],
                        },
                        "f1": feature_name,
                        "f2": feature_type,
                        "f3": str(result.error_bias[feature_name]["current_majority"]),
                        "f4": str(result.error_bias[feature_name]["current_under"]),
                        "f5": str(result.error_bias[feature_name]["current_over"]),
                        "f6": str(result.error_bias[feature_name]["current_range"]),
                    }
                )

                additional_graphs_data.append(
                    AdditionalGraphInfo(
                        feature_name + "_hist",
                        {"data": hist_figure["data"], "layout": hist_figure["layout"]},
                    )
                )

                additional_graphs_data.append(
                    AdditionalGraphInfo(
                        feature_name + "_segm",
                        {"data": segm_figure["data"], "layout": segm_figure["layout"]},
                    )
                )

            current_data.drop("Error bias", axis=1, inplace=True)

            if result.columns is None:
                size = 0
            else:
                size = len(result.columns)

            widget_info = BaseWidgetInfo(
                title="",
                type="big_table",
                size=2,
                params={
                    "rowsPerPage": min(size, 10),
                    "columns": [
                        {"title": "Feature", "field": "f1"},
                        {"title": "Type", "field": "f2"},
                        {"title": "Majority", "field": "f3"},
                        {"title": "Underestimation", "field": "f4"},
                        {"title": "Overestimation", "field": "f5"},
                        {"title": "Range(%)", "field": "f6", "sort": "desc"},
                    ],
                    "data": params_data,
                },
                additionalGraphs=additional_graphs_data,
            )
        top_error_percents = int(result.top_error * 100)

        return [
            header_text(
                label=f"Error Bias: Mean/Most Common Feature Value per Group (Top - {top_error_percents}% Errors)"
            ),
            widget_info,
        ]

    @staticmethod
    def _error_bias_string(quantile_top, quantile_other):
        def __error_bias_string(error):
            if error <= quantile_top:
                return "Underestimation"

            if error < quantile_other:
                return "Majority"

            return "Overestimation"

        return __error_bias_string
