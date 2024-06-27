from typing import List
from typing import Optional
from typing import Union

import numpy as np
import pandas as pd

from evidently.base_metric import ColumnMetric
from evidently.base_metric import ColumnName
from evidently.base_metric import ColumnNotFound
from evidently.base_metric import DataDefinition
from evidently.base_metric import InputData
from evidently.base_metric import UsesRawDataMixin
from evidently.calculations.data_drift import ColumnDataDriftMetrics
from evidently.calculations.data_drift import ColumnType
from evidently.calculations.data_drift import DistributionIncluded
from evidently.calculations.data_drift import DriftStatsField
from evidently.calculations.data_drift import ScatterField
from evidently.calculations.data_drift import get_distribution_for_column
from evidently.calculations.data_drift import get_stattest
from evidently.calculations.data_drift import get_text_data_for_plots
from evidently.calculations.stattests import PossibleStatTestType
from evidently.metric_results import HistogramData
from evidently.metric_results import ScatterAggField
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.options.data_drift import DataDriftOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import CounterData
from evidently.renderers.html_widgets import TabData
from evidently.renderers.html_widgets import counter
from evidently.renderers.html_widgets import plotly_figure
from evidently.renderers.html_widgets import table_data
from evidently.renderers.html_widgets import widget_tabs
from evidently.utils.visualizations import plot_agg_line_data
from evidently.utils.visualizations import plot_distr_with_perc_button
from evidently.utils.visualizations import plot_scatter_for_data_drift
from evidently.utils.visualizations import prepare_df_for_time_index_plot


def get_one_column_drift(
    *,
    current_feature_data: pd.Series,
    reference_feature_data: pd.Series,
    index_data: pd.Series,
    datetime_data: Optional[pd.Series],
    column: ColumnName,
    options: DataDriftOptions,
    data_definition: DataDefinition,
    column_type: ColumnType,
    agg_data: bool,
) -> ColumnDataDriftMetrics:
    if column_type not in (ColumnType.Numerical, ColumnType.Categorical, ColumnType.Text):
        raise ValueError(f"Cannot calculate drift metric for column '{column}' with type {column_type}")

    target = data_definition.get_target_column()
    stattest = None
    if column.is_main_dataset():
        if target and column.name == target.column_name and column_type == ColumnType.Numerical:
            stattest = options.num_target_stattest_func

        elif target and column.name == target.column_name and column_type == ColumnType.Categorical:
            stattest = options.cat_target_stattest_func

    if not stattest:
        stattest = options.get_feature_stattest_func(column.name, column_type.value)

    threshold = options.get_threshold(column.name, column_type.value)
    current_column = current_feature_data
    reference_column = reference_feature_data

    # clean and check the column in reference dataset
    reference_column = reference_column.replace([-np.inf, np.inf], np.nan).dropna()

    if reference_column.empty:
        raise ValueError(
            f"An empty column '{column.name}' was provided for drift calculation in the reference dataset."
        )

    # clean and check the column in current dataset
    current_column = current_column.replace([-np.inf, np.inf], np.nan).dropna()

    if current_column.empty:
        raise ValueError(f"An empty column '{column.name}' was provided for drift calculation in the current dataset.")

    current_distribution = None
    reference_distribution = None
    current_small_distribution = None
    reference_small_distribution = None
    current_correlations = None
    reference_correlations = None

    typical_examples_cur = None
    typical_examples_ref = None
    typical_words_cur = None
    typical_words_ref = None

    if column_type == ColumnType.Numerical:
        if not pd.api.types.is_numeric_dtype(reference_column):
            raise ValueError(f"Column '{column}' in reference dataset should contain numerical values only.")

        if not pd.api.types.is_numeric_dtype(current_column):
            raise ValueError(f"Column '{column}' in current dataset should contain numerical values only.")

    drift_test_function = get_stattest(reference_column, current_column, column_type, stattest)
    drift_result = drift_test_function(reference_column, current_column, column_type, threshold)

    scatter: Optional[Union[ScatterField, ScatterAggField]] = None
    if column_type == ColumnType.Numerical:
        current_nbinsx = options.get_nbinsx(column.name)
        current_small_distribution = [
            t.tolist()
            for t in np.histogram(
                current_column[np.isfinite(current_column)],
                bins=current_nbinsx,
                density=True,
            )
        ]
        reference_small_distribution = [
            t.tolist()
            for t in np.histogram(
                reference_column[np.isfinite(reference_column)],
                bins=current_nbinsx,
                density=True,
            )
        ]
        if not agg_data:
            current_scatter = {column.display_name: current_column}
            if datetime_data is not None:
                current_scatter["Timestamp"] = datetime_data
                x_name = "Timestamp"
            else:
                current_scatter["Index"] = index_data
                x_name = "Index"
        else:
            current_scatter = {}
            datetime_name = None
            if datetime_data is not None:
                datetime_name = "Timestamp"
            df, prefix = prepare_df_for_time_index_plot(
                pd.DataFrame(
                    {
                        column.name: current_feature_data.values,
                        "Timestamp": None if datetime_data is None else datetime_data.values,
                    },
                    index=index_data.values,
                ),
                column.name,
                datetime_name,
            )
            current_scatter["current (mean)"] = df
            if prefix is None:
                x_name = "Index binned"
            else:
                x_name = f"Timestamp ({prefix})"

        plot_shape = {}
        reference_mean = reference_column.mean()
        reference_std = reference_column.std()
        plot_shape["y0"] = reference_mean - reference_std
        plot_shape["y1"] = reference_mean + reference_std
        if agg_data:
            scatter = ScatterAggField(scatter=current_scatter, x_name=x_name, plot_shape=plot_shape)
        else:
            scatter = ScatterField(scatter=current_scatter, x_name=x_name, plot_shape=plot_shape)

    elif column_type == ColumnType.Categorical:
        reference_counts = reference_column.value_counts(sort=False)
        current_counts = current_column.value_counts(sort=False)
        keys = set(reference_counts.keys()).union(set(current_counts.keys()))

        for key in keys:
            if key not in reference_counts:
                reference_counts = pd.concat([reference_counts, pd.Series([0], [key])])
            if key not in current_counts:
                current_counts = pd.concat([current_counts, pd.Series([0], [key])])

        reference_small_distribution = list(
            reversed(
                list(
                    map(
                        list,
                        zip(*sorted(reference_counts.items(), key=lambda x: str(x[0]))),
                    )
                )
            )
        )
        current_small_distribution = list(
            reversed(
                list(
                    map(
                        list,
                        zip(*sorted(current_counts.items(), key=lambda x: str(x[0]))),
                    )
                )
            )
        )
    if column_type != ColumnType.Text:
        current_distribution, reference_distribution = get_distribution_for_column(
            column_type=column_type.value,
            current=current_column,
            reference=reference_column,
        )
        if reference_distribution is None:
            raise ValueError(f"Cannot calculate reference distribution for column '{column}'.")

    elif column_type == ColumnType.Text and drift_result.drifted:
        (
            typical_examples_cur,
            typical_examples_ref,
            typical_words_cur,
            typical_words_ref,
        ) = get_text_data_for_plots(reference_column, current_column)

    metrics = ColumnDataDriftMetrics(
        column_name=column.display_name,
        column_type=column_type.value,
        stattest_name=drift_test_function.display_name,
        drift_score=drift_result.drift_score,
        drift_detected=drift_result.drifted,
        stattest_threshold=drift_result.actual_threshold,
        current=DriftStatsField(
            distribution=current_distribution,
            small_distribution=DistributionIncluded(x=current_small_distribution[1], y=current_small_distribution[0])
            if current_small_distribution
            else None,
            correlations=current_correlations,
            characteristic_examples=typical_examples_cur,
            characteristic_words=typical_words_cur,
        ),
        reference=DriftStatsField(
            distribution=reference_distribution,
            small_distribution=DistributionIncluded(
                x=reference_small_distribution[1], y=reference_small_distribution[0]
            )
            if reference_small_distribution
            else None,
            characteristic_examples=typical_examples_ref,
            characteristic_words=typical_words_ref,
            correlations=reference_correlations,
        ),
        scatter=scatter,
    )

    return metrics


class ColumnDriftMetric(UsesRawDataMixin, ColumnMetric[ColumnDataDriftMetrics]):
    """Calculate drift metric for a column"""

    stattest: Optional[PossibleStatTestType]
    stattest_threshold: Optional[float]

    def __init__(
        self,
        column_name: Union[ColumnName, str],
        stattest: Optional[PossibleStatTestType] = None,
        stattest_threshold: Optional[float] = None,
        options: AnyOptions = None,
    ):
        self.stattest = stattest
        self.stattest_threshold = stattest_threshold
        super().__init__(column_name=column_name, options=options)

    def get_parameters(self) -> tuple:
        return self.column_name, self.stattest_threshold, self.stattest

    def calculate(self, data: InputData) -> ColumnDataDriftMetrics:
        if data.reference_data is None:
            raise ValueError("Reference dataset should be present")

        try:
            current_feature_data = data.get_current_column(self.column_name)
        except ColumnNotFound as ex:
            raise ValueError(f"Cannot find column '{ex.column_name}' in current dataset")
        try:
            reference_feature_data = data.get_reference_column(self.column_name)
        except ColumnNotFound as ex:
            raise ValueError(f"Cannot find column '{ex.column_name}' in reference dataset")

        column_type = ColumnType.Numerical
        if self.column_name.is_main_dataset():
            column_type = data.data_definition.get_column(self.column_name.name).column_type
        else:
            if self.column_name._feature_class is not None:
                column_type = self.column_name._feature_class.feature_type

        datetime_column = data.data_definition.get_datetime_column()
        options = DataDriftOptions(all_features_stattest=self.stattest, threshold=self.stattest_threshold)
        if self.get_options().render_options.raw_data:
            agg_data = False
        else:
            agg_data = True
        drift_result = get_one_column_drift(
            current_feature_data=current_feature_data,
            reference_feature_data=reference_feature_data,
            column=self.column_name,
            index_data=data.current_data.index,
            column_type=column_type,
            datetime_data=data.current_data[datetime_column.column_name] if datetime_column else None,
            data_definition=data.data_definition,
            options=options,
            agg_data=agg_data,
        )

        return ColumnDataDriftMetrics(
            column_name=drift_result.column_name,
            column_type=drift_result.column_type,
            stattest_name=drift_result.stattest_name,
            stattest_threshold=drift_result.stattest_threshold,
            drift_score=drift_result.drift_score,
            drift_detected=drift_result.drift_detected,
            current=drift_result.current,
            scatter=drift_result.scatter,
            reference=drift_result.reference,
        )


@default_renderer(wrap_type=ColumnDriftMetric)
class ColumnDriftMetricRenderer(MetricRenderer):
    def render_html(self, obj: ColumnDriftMetric) -> List[BaseWidgetInfo]:
        result: ColumnDataDriftMetrics = obj.get_result()

        if result.drift_detected:
            drift = "detected"

        else:
            drift = "not detected"

        drift_score = round(result.drift_score, 3)

        tabs = []

        # fig_json = fig.to_plotly_json()
        if result.scatter is not None:
            if obj.get_options().render_options.raw_data:
                scatter_fig = plot_scatter_for_data_drift(
                    curr_y=result.scatter.scatter[result.column_name],
                    curr_x=result.scatter.scatter[result.scatter.x_name],
                    y0=result.scatter.plot_shape["y0"],
                    y1=result.scatter.plot_shape["y1"],
                    y_name=result.column_name,
                    x_name=result.scatter.x_name,
                    color_options=self.color_options,
                )
            else:
                scatter_fig = plot_agg_line_data(
                    curr_data=result.scatter.scatter,
                    ref_data=None,
                    line=(result.scatter.plot_shape["y0"] + result.scatter.plot_shape["y1"]) / 2,
                    std=(result.scatter.plot_shape["y0"] - result.scatter.plot_shape["y1"]) / 2,
                    xaxis_name=result.scatter.x_name,
                    xaxis_name_ref=None,
                    yaxis_name=f"{result.column_name} (mean +/- std)",
                    color_options=self.color_options,
                    return_json=False,
                    line_name="reference (mean)",
                )
            tabs.append(TabData("DATA DRIFT", plotly_figure(title="", figure=scatter_fig)))

        if result.current.distribution is not None and result.reference.distribution is not None:
            distr_fig = plot_distr_with_perc_button(
                hist_curr=HistogramData.from_distribution(result.current.distribution),
                hist_ref=HistogramData.from_distribution(result.reference.distribution),
                xaxis_name="",
                yaxis_name="Count",
                yaxis_name_perc="Percent",
                same_color=False,
                color_options=self.color_options,
                subplots=False,
                to_json=False,
            )
            tabs.append(TabData("DATA DISTRIBUTION", plotly_figure(title="", figure=distr_fig)))

        if (
            result.current.characteristic_examples is not None
            and result.reference.characteristic_examples is not None
            and result.current.characteristic_words is not None
            and result.reference.characteristic_words is not None
        ):
            current_table_words = table_data(
                title="",
                column_names=["", ""],
                data=[[el, ""] for el in result.current.characteristic_words],
            )
            reference_table_words = table_data(
                title="",
                column_names=["", ""],
                data=[[el, ""] for el in result.reference.characteristic_words],
            )
            current_table_examples = table_data(
                title="",
                column_names=["", ""],
                data=[[el, ""] for el in result.current.characteristic_examples],
            )
            reference_table_examples = table_data(
                title="",
                column_names=["", ""],
                data=[[el, ""] for el in result.reference.characteristic_examples],
            )

            tabs = [
                TabData(title="current: characteristic words", widget=current_table_words),
                TabData(
                    title="reference: characteristic words",
                    widget=reference_table_words,
                ),
                TabData(
                    title="current: characteristic examples",
                    widget=current_table_examples,
                ),
                TabData(
                    title="reference: characteristic examples",
                    widget=reference_table_examples,
                ),
            ]
        render_result = [
            counter(
                counters=[
                    CounterData(
                        (
                            f"Data drift {drift}. "
                            f"Drift detection method: {result.stattest_name}. "
                            f"Drift score: {drift_score}"
                        ),
                        f"Drift in column '{result.column_name}'",
                    )
                ],
                title="",
            )
        ]
        if len(tabs) > 0:
            render_result.append(
                widget_tabs(
                    title="",
                    tabs=tabs,
                )
            )

        return render_result
