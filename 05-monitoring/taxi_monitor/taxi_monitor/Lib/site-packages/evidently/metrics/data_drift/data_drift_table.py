from typing import Dict
from typing import List
from typing import Optional

import pandas as pd

from evidently.base_metric import InputData
from evidently.base_metric import MetricResult
from evidently.base_metric import UsesRawDataMixin
from evidently.calculations.data_drift import ColumnDataDriftMetrics
from evidently.calculations.data_drift import get_drift_for_columns
from evidently.calculations.stattests import PossibleStatTestType
from evidently.core import IncludeTags
from evidently.metric_results import DatasetColumns
from evidently.metric_results import HistogramData
from evidently.metrics.data_drift.base import WithDriftOptions
from evidently.metrics.data_drift.feature_importance import FeatureImportanceMetric
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.options.data_drift import DataDriftOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import ColumnDefinition
from evidently.renderers.html_widgets import ColumnType
from evidently.renderers.html_widgets import RichTableDataRow
from evidently.renderers.html_widgets import RowDetails
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import plotly_figure
from evidently.renderers.html_widgets import rich_table_data
from evidently.renderers.html_widgets import table_data
from evidently.utils.data_operations import process_columns
from evidently.utils.visualizations import plot_agg_line_data
from evidently.utils.visualizations import plot_distr_with_perc_button
from evidently.utils.visualizations import plot_scatter_for_data_drift


class DataDriftTableResults(MetricResult):
    class Config:
        dict_exclude_fields = {"dataset_columns"}
        field_tags = {
            "current_fi": {IncludeTags.Extra, IncludeTags.Current},
            "reference_fi": {IncludeTags.Extra, IncludeTags.Reference},
        }

    number_of_columns: int
    number_of_drifted_columns: int
    share_of_drifted_columns: float
    dataset_drift: bool
    drift_by_columns: Dict[str, ColumnDataDriftMetrics]
    dataset_columns: DatasetColumns
    current_fi: Optional[Dict[str, float]] = None
    reference_fi: Optional[Dict[str, float]] = None


class DataDriftTable(UsesRawDataMixin, WithDriftOptions[DataDriftTableResults]):
    columns: Optional[List[str]]
    feature_importance: Optional[bool]
    _feature_importance_metric: Optional[FeatureImportanceMetric]

    def __init__(
        self,
        columns: Optional[List[str]] = None,
        stattest: Optional[PossibleStatTestType] = None,
        cat_stattest: Optional[PossibleStatTestType] = None,
        num_stattest: Optional[PossibleStatTestType] = None,
        text_stattest: Optional[PossibleStatTestType] = None,
        per_column_stattest: Optional[Dict[str, PossibleStatTestType]] = None,
        stattest_threshold: Optional[float] = None,
        cat_stattest_threshold: Optional[float] = None,
        num_stattest_threshold: Optional[float] = None,
        text_stattest_threshold: Optional[float] = None,
        per_column_stattest_threshold: Optional[Dict[str, float]] = None,
        options: AnyOptions = None,
        feature_importance: Optional[bool] = False,
    ):
        self.columns = columns
        super().__init__(
            stattest=stattest,
            cat_stattest=cat_stattest,
            num_stattest=num_stattest,
            text_stattest=text_stattest,
            per_column_stattest=per_column_stattest,
            stattest_threshold=stattest_threshold,
            cat_stattest_threshold=cat_stattest_threshold,
            num_stattest_threshold=num_stattest_threshold,
            text_stattest_threshold=text_stattest_threshold,
            per_column_stattest_threshold=per_column_stattest_threshold,
            options=options,
            feature_importance=feature_importance,
        )
        self._drift_options = DataDriftOptions(
            all_features_stattest=stattest,
            cat_features_stattest=cat_stattest,
            num_features_stattest=num_stattest,
            text_features_stattest=text_stattest,
            per_feature_stattest=per_column_stattest,
            all_features_threshold=stattest_threshold,
            cat_features_threshold=cat_stattest_threshold,
            num_features_threshold=num_stattest_threshold,
            text_features_threshold=text_stattest_threshold,
            per_feature_threshold=per_column_stattest_threshold,
        )
        if feature_importance:
            self._feature_importance_metric = FeatureImportanceMetric()
        else:
            self._feature_importance_metric = None

    def get_parameters(self) -> tuple:
        return (None if self.columns is None else tuple(self.columns), self.feature_importance, self.drift_options)

    def calculate(self, data: InputData) -> DataDriftTableResults:
        if data.reference_data is None:
            raise ValueError("Reference dataset should be present")

        if self.get_options().render_options.raw_data:
            agg_data = False
        else:
            agg_data = True

        dataset_columns = process_columns(data.reference_data, data.column_mapping)
        result = get_drift_for_columns(
            current_data=data.current_data,
            reference_data=data.reference_data,
            data_drift_options=self.drift_options,
            dataset_columns=dataset_columns,
            columns=self.columns,
            agg_data=agg_data,
        )
        current_fi: Optional[Dict[str, float]] = None
        reference_fi: Optional[Dict[str, float]] = None

        if self._feature_importance_metric is not None:
            res = self._feature_importance_metric.get_result()
            current_fi = res.current
            reference_fi = res.reference

        return DataDriftTableResults(
            number_of_columns=result.number_of_columns,
            number_of_drifted_columns=result.number_of_drifted_columns,
            share_of_drifted_columns=result.share_of_drifted_columns,
            dataset_drift=result.dataset_drift,
            drift_by_columns=result.drift_by_columns,
            dataset_columns=result.dataset_columns,
            current_fi=current_fi,
            reference_fi=reference_fi,
        )


@default_renderer(wrap_type=DataDriftTable)
class DataDriftTableRenderer(MetricRenderer):
    def render_pandas(self, obj: DataDriftTable) -> pd.DataFrame:
        result: DataDriftTableResults = obj.get_result()
        return pd.concat([v.get_pandas() for v in result.drift_by_columns.values()])

    def _generate_column_params(
        self,
        column_name: str,
        data: ColumnDataDriftMetrics,
        agg_data: bool,
        current_fi: Optional[Dict[str, float]] = None,
        reference_fi: Optional[Dict[str, float]] = None,
    ) -> Optional[RichTableDataRow]:
        details = RowDetails()
        if data.column_type == "text":
            if (
                data.current.characteristic_examples is not None
                and data.reference.characteristic_examples is not None
                and data.current.characteristic_words is not None
                and data.reference.characteristic_words is not None
            ):
                current_table_words = table_data(
                    title="",
                    column_names=["", ""],
                    data=[[el, ""] for el in data.current.characteristic_words],
                )
                details.with_part("current: characteristic words", info=current_table_words)
                reference_table_words = table_data(
                    title="",
                    column_names=["", ""],
                    data=[[el, ""] for el in data.reference.characteristic_words],
                )
                details.with_part("reference: characteristic words", info=reference_table_words)
                current_table_examples = table_data(
                    title="",
                    column_names=["", ""],
                    data=[[el, ""] for el in data.current.characteristic_examples],
                )
                details.with_part("current: characteristic examples", info=current_table_examples)
                reference_table_examples = table_data(
                    title="",
                    column_names=["", ""],
                    data=[[el, ""] for el in data.reference.characteristic_examples],
                )
                details.with_part("reference: characteristic examples", info=reference_table_examples)

            data_drift = "Detected" if data.drift_detected else "Not Detected"

            fields = {
                "column_name": column_name,
                "column_type": data.column_type,
                "stattest_name": data.stattest_name,
                "data_drift": data_drift,
                "drift_score": round(data.drift_score, 6),
            }

        else:
            if (
                data.current.small_distribution is None
                or data.reference.small_distribution is None
                or data.current.distribution is None
                or data.reference.distribution is None
            ):
                return None

            current_small_hist = data.current.small_distribution
            ref_small_hist = data.reference.small_distribution
            data_drift = "Detected" if data.drift_detected else "Not Detected"
            if data.column_type == "num" and data.scatter is not None:
                if not agg_data:
                    scatter_fig = plot_scatter_for_data_drift(
                        curr_y=data.scatter.scatter[data.column_name],
                        curr_x=data.scatter.scatter[data.scatter.x_name],
                        y0=data.scatter.plot_shape["y0"],
                        y1=data.scatter.plot_shape["y1"],
                        y_name=data.column_name,
                        x_name=data.scatter.x_name,
                        color_options=self.color_options,
                    )
                else:
                    scatter_fig = plot_agg_line_data(
                        curr_data=data.scatter.scatter,
                        ref_data=None,
                        line=(data.scatter.plot_shape["y0"] + data.scatter.plot_shape["y1"]) / 2,
                        std=(data.scatter.plot_shape["y0"] - data.scatter.plot_shape["y1"]) / 2,
                        xaxis_name=data.scatter.x_name,
                        xaxis_name_ref=None,
                        yaxis_name=f"{data.column_name} (mean +/- std)",
                        color_options=self.color_options,
                        return_json=False,
                        line_name="reference (mean)",
                    )
                scatter = plotly_figure(title="", figure=scatter_fig)
                details.with_part("DATA DRIFT", info=scatter)
            fig = plot_distr_with_perc_button(
                hist_curr=HistogramData.from_distribution(data.current.distribution),
                hist_ref=HistogramData.from_distribution(data.reference.distribution),
                xaxis_name="",
                yaxis_name="Count",
                yaxis_name_perc="Percent",
                same_color=False,
                color_options=self.color_options,
                subplots=False,
                to_json=False,
            )
            distribution = plotly_figure(title="", figure=fig)
            details.with_part("DATA DISTRIBUTION", info=distribution)
            fields = {
                "column_name": column_name,
                "column_type": data.column_type,
                "stattest_name": data.stattest_name,
                "reference_distribution": {
                    "x": list(ref_small_hist.x),
                    "y": list(ref_small_hist.y),
                },
                "current_distribution": {
                    "x": list(current_small_hist.x),
                    "y": list(current_small_hist.y),
                },
                "data_drift": data_drift,
                "drift_score": round(data.drift_score, 6),
            }
        if current_fi is not None:
            fields["current_feature_importance"] = current_fi.get(column_name, "")
        if reference_fi is not None:
            fields["reference_feature_importance"] = reference_fi.get(column_name, "")
        return RichTableDataRow(details=details, fields=fields)

    def render_html(self, obj: DataDriftTable) -> List[BaseWidgetInfo]:
        results = obj.get_result()
        color_options = self.color_options
        target_column = results.dataset_columns.utility_columns.target
        prediction_column = results.dataset_columns.utility_columns.prediction
        agg_data = not obj.get_options().render_options.raw_data

        # set params data
        params_data = []

        # sort columns by drift score
        all_columns = sorted(
            results.drift_by_columns.keys(),
            key=lambda x: results.drift_by_columns[x].drift_score,
            reverse=True,
        )
        # move target and prediction to the top of the table
        columns = []
        if target_column in all_columns:
            columns.append(target_column)
            all_columns.remove(target_column)
        if isinstance(prediction_column, str) and prediction_column in all_columns:
            columns.append(prediction_column)
            all_columns.remove(prediction_column)

        columns = columns + all_columns

        for column_name in columns:
            column_params = self._generate_column_params(
                column_name,
                results.drift_by_columns[column_name],
                agg_data,
                results.current_fi,
                results.reference_fi,
            )

            if column_params is not None:
                params_data.append(column_params)

        drift_percents = round(results.share_of_drifted_columns * 100, 3)
        table_columns = [
            ColumnDefinition("Column", "column_name"),
            ColumnDefinition("Type", "column_type"),
        ]
        if results.current_fi is not None:
            table_columns.append(ColumnDefinition("Current feature importance", "current_feature_importance"))
        if results.reference_fi is not None:
            table_columns.append(ColumnDefinition("Reference feature importance", "reference_feature_importance"))
        table_columns = table_columns + [
            ColumnDefinition(
                "Reference Distribution",
                "reference_distribution",
                ColumnType.HISTOGRAM,
                options={
                    "xField": "x",
                    "yField": "y",
                    "color": color_options.primary_color,
                },
            ),
            ColumnDefinition(
                "Current Distribution",
                "current_distribution",
                ColumnType.HISTOGRAM,
                options={
                    "xField": "x",
                    "yField": "y",
                    "color": color_options.primary_color,
                },
            ),
            ColumnDefinition("Data Drift", "data_drift"),
            ColumnDefinition("Stat Test", "stattest_name"),
            ColumnDefinition("Drift Score", "drift_score"),
        ]

        return [
            header_text(label="Data Drift Summary"),
            rich_table_data(
                title=f"Drift is detected for {drift_percents}% of columns "
                f"({results.number_of_drifted_columns} out of {results.number_of_columns}).",
                columns=table_columns,
                data=params_data,
            ),
        ]
