from evidently.base_metric import ColumnNotFound
from evidently.calculation_engine.engine import metric_implementation
from evidently.calculations.data_drift import ColumnDataDriftMetrics
from evidently.core import ColumnType
from evidently.metrics import ColumnDriftMetric
from evidently.metrics import DataDriftTable
from evidently.metrics import DatasetDriftMetric
from evidently.metrics.data_drift.data_drift_table import DataDriftTableResults
from evidently.metrics.data_drift.dataset_drift_metric import DatasetDriftMetricResults
from evidently.options.data_drift import DataDriftOptions
from evidently.spark.calculations.data_drift import get_drift_for_columns
from evidently.spark.calculations.data_drift import get_one_column_drift
from evidently.spark.engine import SparkInputData
from evidently.spark.engine import SparkMetricImplementation


@metric_implementation(ColumnDriftMetric)
class SparkColumnDriftMetric(SparkMetricImplementation[ColumnDriftMetric]):
    def calculate(self, context, data: SparkInputData) -> ColumnDataDriftMetrics:
        if data.reference_data is None:
            raise ValueError("Reference dataset should be present")

        datetime_column = data.data_definition.get_datetime_column()
        datetime_column_name = datetime_column.column_name if datetime_column is not None else None
        try:
            current_feature_data = data.get_current_column(self.metric.column_name, datetime_column_name)
        except ColumnNotFound as ex:
            raise ValueError(f"Cannot find column '{ex.column_name}' in current dataset")
        try:
            reference_feature_data = data.get_reference_column(self.metric.column_name, datetime_column_name)
        except ColumnNotFound as ex:
            raise ValueError(f"Cannot find column '{ex.column_name}' in reference dataset")

        column_type = ColumnType.Numerical
        if self.metric.column_name.is_main_dataset():
            column_type = data.data_definition.get_column(self.metric.column_name.name).column_type

        options = DataDriftOptions(all_features_stattest=self.metric.stattest, threshold=self.metric.stattest_threshold)
        if self.metric.get_options().render_options.raw_data:
            raise NotImplementedError("Spark Metrics do not support raw data visualizations")
        if reference_feature_data is None:
            raise ValueError("Reference should be present for ColumnDriftMetric")
        drift_result = get_one_column_drift(
            current_feature_data=current_feature_data,
            reference_feature_data=reference_feature_data,
            column=self.metric.column_name,
            column_type=column_type,
            datetime_column=datetime_column_name,
            data_definition=data.data_definition,
            options=options,
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


@metric_implementation(DataDriftTable)
class SparkDataDriftTable(SparkMetricImplementation[DataDriftTable]):
    def calculate(self, context, data: SparkInputData) -> DataDriftTableResults:
        if data.reference_data is None:
            raise ValueError("Reference dataset should be present")

        if self.metric.get_options().render_options.raw_data:
            raise NotImplementedError("SparkEngine do not support raw_data=True")

        result = get_drift_for_columns(
            current_data=data.current_data,
            reference_data=data.reference_data,
            data_drift_options=self.metric.drift_options,
            data_definition=data.data_definition,
            column_mapping=data.column_mapping,
            columns=self.metric.columns,
        )
        return DataDriftTableResults(
            number_of_columns=result.number_of_columns,
            number_of_drifted_columns=result.number_of_drifted_columns,
            share_of_drifted_columns=result.share_of_drifted_columns,
            dataset_drift=result.dataset_drift,
            drift_by_columns=result.drift_by_columns,
            dataset_columns=result.dataset_columns,
        )


@metric_implementation(DatasetDriftMetric)
class SparkDatasetDriftMetric(SparkMetricImplementation[DatasetDriftMetric]):
    def calculate(self, context, data: SparkInputData) -> DatasetDriftMetricResults:
        if data.reference_data is None:
            raise ValueError("Reference dataset should be present")

        result = get_drift_for_columns(
            current_data=data.current_data,
            reference_data=data.reference_data,
            data_drift_options=self.metric.drift_options,
            data_definition=data.data_definition,
            column_mapping=data.column_mapping,
            columns=self.metric.columns,
        )
        return DatasetDriftMetricResults(
            drift_share=self.metric.drift_share,
            number_of_columns=result.number_of_columns,
            number_of_drifted_columns=result.number_of_drifted_columns,
            share_of_drifted_columns=result.share_of_drifted_columns,
            dataset_drift=result.dataset_drift,
        )
