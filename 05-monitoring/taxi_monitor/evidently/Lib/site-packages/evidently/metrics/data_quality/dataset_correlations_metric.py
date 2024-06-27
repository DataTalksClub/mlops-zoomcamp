import copy
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import numpy as np
import pandas as pd

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.calculations.classification_performance import get_prediction_data
from evidently.calculations.data_quality import calculate_correlations
from evidently.core import ColumnType
from evidently.core import IncludeTags
from evidently.features.non_letter_character_percentage_feature import NonLetterCharacterPercentage
from evidently.features.OOV_words_percentage_feature import OOVWordsPercentage
from evidently.features.text_length_feature import TextLength
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import HeatmapData
from evidently.renderers.html_widgets import TabData
from evidently.renderers.html_widgets import get_heatmaps_widget
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import widget_tabs
from evidently.utils.data_operations import process_columns
from evidently.utils.data_preprocessing import ColumnDefinition
from evidently.utils.data_preprocessing import DataDefinition
from evidently.utils.data_preprocessing import PredictionColumns


class CorrelationStats(MetricResult):
    class Config:
        field_tags = {
            "abs_max_target_features_correlation": {IncludeTags.Extra},
            "abs_max_prediction_features_correlation": {IncludeTags.Extra},
            "abs_max_correlation": {IncludeTags.Extra},
            "abs_max_features_correlation": {IncludeTags.Extra},
        }

    target_prediction_correlation: Optional[float] = None
    abs_max_target_features_correlation: Optional[float] = None
    abs_max_prediction_features_correlation: Optional[float] = None
    abs_max_correlation: Optional[float] = None
    abs_max_features_correlation: Optional[float] = None


class DatasetCorrelation(MetricResult):
    class Config:
        dict_exclude_fields = {"correlation", "correlations_calculate"}
        pd_include = False
        pd_exclude_fields = {"correlation", "correlations_calculate"}

        field_tags = {"correlations_calculate": {IncludeTags.Extra}}

    correlation: Dict[str, pd.DataFrame]
    stats: Dict[str, CorrelationStats]
    correlations_calculate: Optional[Dict[str, pd.DataFrame]]


class DatasetCorrelationsMetricResult(MetricResult):
    class Config:
        dict_exclude_fields = {"target_correlation"}
        pd_exclude_fields = {"target_correlation"}
        field_tags = {
            "current": {IncludeTags.Current},
            "reference": {IncludeTags.Reference},
            "target_correlation": {IncludeTags.Parameter},
        }

    current: DatasetCorrelation
    reference: Optional[DatasetCorrelation]
    target_correlation: Optional[str]


class DatasetCorrelationsMetric(Metric[DatasetCorrelationsMetricResult]):
    """Calculate different correlations with target, predictions and features"""

    _text_features_gen: Optional[
        Dict[
            str,
            Dict[str, Union[TextLength, NonLetterCharacterPercentage, OOVWordsPercentage]],
        ]
    ]

    def __init__(self, options: AnyOptions = None):
        self._text_features_gen = None
        super().__init__(options=options)

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

    @staticmethod
    def _get_correlations_stats(correlation: pd.DataFrame, data_definition: DataDefinition) -> CorrelationStats:
        correlation_matrix = correlation.copy()
        target = data_definition.get_target_column()
        target_name = None
        if target is not None:
            target_name = target.column_name
        prediction = data_definition.get_prediction_columns()
        prediction_name = None
        if prediction is not None and prediction.predicted_values is not None:
            prediction_name = prediction.predicted_values.column_name
        columns_corr = [i for i in correlation_matrix.columns if i not in [target_name, prediction_name]]
        # fill diagonal with 1 values for getting abs max values
        np.fill_diagonal(correlation_matrix.values, 0)

        if prediction_name in correlation_matrix and target_name in correlation_matrix:
            target_prediction_correlation = correlation_matrix.loc[prediction_name, target_name]

            if pd.isnull(target_prediction_correlation):
                target_prediction_correlation = None

        else:
            target_prediction_correlation = None

        if target_name in correlation_matrix:
            abs_max_target_features_correlation = correlation_matrix.loc[target_name, columns_corr].abs().max()

            if pd.isnull(abs_max_target_features_correlation):
                abs_max_target_features_correlation = None

        else:
            abs_max_target_features_correlation = None

        if prediction_name in correlation_matrix:
            abs_max_prediction_features_correlation = correlation_matrix.loc[prediction_name, columns_corr].abs().max()

            if pd.isnull(abs_max_prediction_features_correlation):
                abs_max_prediction_features_correlation = None

        else:
            abs_max_prediction_features_correlation = None

        abs_max_correlation = correlation_matrix.abs().max().max()

        if pd.isnull(abs_max_correlation):
            abs_max_correlation = None

        abs_max_features_correlation = correlation_matrix.loc[columns_corr, columns_corr].abs().max().max()

        if pd.isnull(abs_max_features_correlation):
            abs_max_features_correlation = None

        return CorrelationStats(
            target_prediction_correlation=target_prediction_correlation,
            abs_max_target_features_correlation=abs_max_target_features_correlation,
            abs_max_prediction_features_correlation=abs_max_prediction_features_correlation,
            abs_max_correlation=abs_max_correlation,
            abs_max_features_correlation=abs_max_features_correlation,
        )

    def _get_correlations(
        self, dataset: pd.DataFrame, data_definition: DataDefinition, add_text_columns: Optional[list]
    ) -> DatasetCorrelation:
        # process predictions. If task == 'classification' add prediction labels

        if add_text_columns is not None:
            correlations_calculate = calculate_correlations(dataset, data_definition, sum(add_text_columns, []))
            correlations = copy.deepcopy(correlations_calculate)
            for name, correlation in correlations_calculate.items():
                if name != "cramer_v":
                    for col_idx in add_text_columns:
                        correlation.loc[col_idx, col_idx] = 0
                    correlations_calculate[name] = correlation
        else:
            correlations_calculate = calculate_correlations(dataset, data_definition)
            correlations = copy.deepcopy(correlations_calculate)

        prediction_columns = data_definition.get_prediction_columns()
        if prediction_columns is not None and prediction_columns.prediction_probas is not None:
            names = [col.column_name for col in prediction_columns.prediction_probas]
            for name, correlation in correlations_calculate.items():
                if name != "cramer_v" and len(names) > 1:
                    correlation.loc[names, names] = 0
                    correlations_calculate[name] = correlation

        stats = {
            name: self._get_correlations_stats(correlation, data_definition)
            for name, correlation in correlations_calculate.items()
        }

        return DatasetCorrelation(
            correlation=correlations,
            stats=stats,
            correlations_calculate=correlations_calculate,
        )

    def calculate(self, data: InputData) -> DatasetCorrelationsMetricResult:
        target_correlation: Optional[str] = None
        data_definition = copy.deepcopy(data.data_definition)
        columns = process_columns(data.current_data, data.column_mapping)
        curr_df = data.current_data.copy()
        ref_df: Optional[pd.DataFrame] = None
        if data.reference_data is not None:
            ref_df = data.reference_data.copy()

        target_correlation = None
        target = data_definition.get_target_column()
        if target is not None:
            target_type = target.column_type
            if target_type == ColumnType.Numerical:
                target_correlation = "pearson"
            elif target_type == ColumnType.Categorical:
                target_correlation = "cramer_v"

        prediction_data = data_definition.get_prediction_columns()
        if prediction_data is not None and prediction_data.predicted_values is None:
            prediction_labels_name = "prediction_labels"
            prediction_curr = get_prediction_data(curr_df, columns, data.column_mapping.pos_label)
            curr_df[prediction_labels_name] = prediction_curr.predictions
            if ref_df is not None:
                prediction_ref = get_prediction_data(ref_df, columns, data.column_mapping.pos_label)
                ref_df[prediction_labels_name] = prediction_ref.predictions
            data_definition.prediction_columns = PredictionColumns(
                prediction_probas=prediction_data.prediction_probas,
                predicted_values=ColumnDefinition(prediction_labels_name, target_type),
            )
            data_definition.columns[prediction_labels_name] = ColumnDefinition(prediction_labels_name, target_type)

        # process text columns
        text_columns = []
        if self._text_features_gen is not None:
            for col in list(self._text_features_gen.keys()):
                curr_text_df = pd.concat(
                    [data.get_current_column(x.feature_name()) for x in list(self._text_features_gen[col].values())],
                    axis=1,
                )
                curr_text_df.columns = list(self._text_features_gen[col].keys())
                text_columns.append(list(curr_text_df.columns))
                curr_df = pd.concat(
                    [
                        curr_df.copy().reset_index(drop=True),
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
                            ref_df.copy().reset_index(drop=True),
                            ref_text_df.reset_index(drop=True),
                        ],
                        axis=1,
                    )
        current_correlations = self._get_correlations(
            dataset=curr_df,
            data_definition=data_definition,
            add_text_columns=text_columns,
        )

        if ref_df is not None:
            reference_correlation: Optional[DatasetCorrelation] = self._get_correlations(
                dataset=ref_df,
                data_definition=data_definition,
                add_text_columns=text_columns,
            )

        else:
            reference_correlation = None

        return DatasetCorrelationsMetricResult(
            current=current_correlations,
            reference=reference_correlation,
            target_correlation=target_correlation,
        )


@default_renderer(wrap_type=DatasetCorrelationsMetric)
class DataQualityCorrelationMetricsRenderer(MetricRenderer):
    def _get_heatmaps(self, metric_result: DatasetCorrelationsMetricResult) -> BaseWidgetInfo:
        tabs = []
        curr_corr_result = metric_result.current.correlation
        for correlation_method in curr_corr_result:
            current_correlation = curr_corr_result[correlation_method]

            if metric_result.reference is not None:
                ref_corr_result = metric_result.reference.correlation
                reference_heatmap_data: Optional[HeatmapData] = HeatmapData(
                    name="Reference", matrix=ref_corr_result[correlation_method]
                )

            else:
                reference_heatmap_data = None

            tabs.append(
                TabData(
                    title=correlation_method,
                    widget=get_heatmaps_widget(
                        primary_data=HeatmapData(name="Current", matrix=current_correlation),
                        secondary_data=reference_heatmap_data,
                        color_options=self.color_options,
                    ),
                )
            )

        return widget_tabs(title="", tabs=tabs)

    def render_html(self, obj: DatasetCorrelationsMetric) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        result = [
            header_text(label="Dataset Correlations"),
            self._get_heatmaps(metric_result=metric_result),
        ]
        return result
