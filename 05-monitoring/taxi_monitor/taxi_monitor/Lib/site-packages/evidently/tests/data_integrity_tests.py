from abc import ABC
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import numpy as np
import pandas as pd
from pandas.core.dtypes.common import infer_dtype_from_object

from evidently.base_metric import ColumnName
from evidently.metrics import ColumnRegExpMetric
from evidently.metrics import ColumnSummaryMetric
from evidently.metrics import DatasetMissingValuesMetric
from evidently.metrics import DatasetSummaryMetric
from evidently.metrics.data_integrity.dataset_missing_values_metric import DatasetMissingValues
from evidently.metrics.data_integrity.dataset_missing_values_metric import DatasetMissingValuesMetricResult
from evidently.metrics.data_integrity.dataset_summary_metric import DatasetSummary
from evidently.model.widget import BaseWidgetInfo
from evidently.renderers.base_renderer import DetailsInfo
from evidently.renderers.base_renderer import TestHtmlInfo
from evidently.renderers.base_renderer import TestRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.tests.base_test import BaseCheckValueTest
from evidently.tests.base_test import ColumnCheckValueParameters
from evidently.tests.base_test import ConditionFromReferenceMixin
from evidently.tests.base_test import GroupData
from evidently.tests.base_test import GroupingTypes
from evidently.tests.base_test import Test
from evidently.tests.base_test import TestParameters
from evidently.tests.base_test import TestResult
from evidently.tests.base_test import TestStatus
from evidently.tests.base_test import TestValueCondition
from evidently.tests.utils import approx
from evidently.tests.utils import dataframes_to_table
from evidently.tests.utils import plot_dicts_to_table
from evidently.tests.utils import plot_value_counts_tables_ref_curr
from evidently.utils.data_preprocessing import DataDefinition
from evidently.utils.generators import BaseGenerator
from evidently.utils.types import Numeric
from evidently.utils.types import NumericApprox

DATA_INTEGRITY_GROUP = GroupData("data_integrity", "Data Integrity", "")
GroupingTypes.TestGroup.add_value(DATA_INTEGRITY_GROUP)


class BaseIntegrityValueTest(ConditionFromReferenceMixin[DatasetSummary], ABC):
    group: ClassVar = DATA_INTEGRITY_GROUP.id
    _metric: DatasetSummaryMetric

    def __init__(
        self,
        eq: Optional[NumericApprox] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
    ):
        super().__init__(
            eq=eq,
            gt=gt,
            gte=gte,
            is_in=is_in,
            lt=lt,
            lte=lte,
            not_eq=not_eq,
            not_in=not_in,
            is_critical=is_critical,
        )
        self._metric = DatasetSummaryMetric()


class TestNumberOfColumns(BaseIntegrityValueTest):
    """Number of all columns in the data, including utility columns (id/index, datetime, target, predictions)"""

    name: ClassVar = "Number of Columns"

    def get_condition_from_reference(self, reference: Optional[DatasetSummary]):
        if reference is not None:
            return TestValueCondition(eq=reference.number_of_columns)
        return TestValueCondition(gt=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.number_of_columns

    def get_description(self, value: Numeric) -> str:
        return f"The number of columns is {value}. The test threshold is {self.get_condition()}."


@default_renderer(wrap_type=TestNumberOfColumns)
class TestNumberOfColumnsRenderer(TestRenderer):
    def render_html(self, obj: TestNumberOfColumns) -> TestHtmlInfo:
        info = super().render_html(obj)
        columns = ["column name", "current dtype"]
        dict_curr = obj.metric.get_result().current.columns_type
        dict_ref = None
        reference_stats = obj.metric.get_result().reference

        if reference_stats is not None:
            dict_ref = reference_stats.columns_type
            columns = columns + ["reference dtype"]

        additional_plots = plot_dicts_to_table(dict_curr, dict_ref, columns, "number_of_column", "diff")
        info.details = additional_plots
        return info


class TestNumberOfRows(BaseIntegrityValueTest):
    """Number of rows in the data"""

    name: ClassVar = "Number of Rows"

    def get_condition_from_reference(self, reference: Optional[DatasetSummary]):
        if reference is not None:
            return TestValueCondition(eq=approx(reference.number_of_rows, relative=0.1))

        return TestValueCondition(gt=30)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.number_of_rows

    def get_description(self, value: Numeric) -> str:
        return f"The number of rows is {value}. The test threshold is {self.get_condition()}."


class BaseIntegrityMissingValuesValuesTest(ConditionFromReferenceMixin[DatasetMissingValues], ABC):
    group: ClassVar = DATA_INTEGRITY_GROUP.id
    _metric: DatasetMissingValuesMetric
    missing_values: Optional[list] = None
    replace: bool = True

    def __init__(
        self,
        missing_values: Optional[list] = None,
        replace: bool = True,
        eq: Optional[Numeric] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
    ):
        self.missing_values = missing_values
        self.replace = replace
        super().__init__(
            eq=eq,
            gt=gt,
            gte=gte,
            is_in=is_in,
            lt=lt,
            lte=lte,
            not_eq=not_eq,
            not_in=not_in,
            is_critical=is_critical,
        )
        self._metric = DatasetMissingValuesMetric(missing_values=self.missing_values, replace=self.replace)


class BaseTestMissingValuesRenderer(TestRenderer):
    """Common class for tests of missing values.
    Some tests have the same details visualizations.
    """

    MISSING_VALUES_NAMING_MAPPING = {
        None: "Pandas nulls (None, NAN, etc.)",
        "": '"" (empty string)',
        np.inf: 'Numpy "inf" value',
        -np.inf: 'Numpy "-inf" value',
    }

    @staticmethod
    def _get_number_and_percents_of_missing_values(missing_values_info: DatasetMissingValues) -> pd.DataFrame:
        """Get a string with missing values numbers and percents from info for results table"""
        result = {}

        for columns_name in missing_values_info.number_of_missing_values_by_column:
            missing_values_count = missing_values_info.number_of_missing_values_by_column[columns_name]
            percent_count = missing_values_info.share_of_missing_values_by_column[columns_name] * 100
            result[columns_name] = f"{missing_values_count} ({percent_count:.2f}%)"

        return pd.DataFrame.from_dict(
            {
                name: dict(
                    value=missing_values_info.number_of_missing_values_by_column[name],
                    display=f"{missing_values_info.number_of_missing_values_by_column[name]}"
                    f" ({missing_values_info.share_of_missing_values_by_column[name] * 100:.2f}%)",
                )
                for name in missing_values_info.number_of_missing_values_by_column.keys()
            },
            orient="index",
            columns=["value", "display"],
        )

    def get_table_with_missing_values_and_percents_by_column(
        self, info: TestHtmlInfo, metric_result: DatasetMissingValuesMetricResult, name: str
    ) -> TestHtmlInfo:
        """Get a table with missing values number and percents"""
        columns = ["column name", "current number of missing values"]
        dict_curr = self._get_number_and_percents_of_missing_values(metric_result.current)
        dict_ref = None
        reference_stats = metric_result.reference

        if reference_stats is not None:
            # add one more column and values for reference data
            columns.append("reference number of missing values")
            dict_ref = self._get_number_and_percents_of_missing_values(reference_stats)

        additional_plots = dataframes_to_table(dict_curr, dict_ref, columns, name)
        info.details = additional_plots
        return info

    def _replace_missing_values_to_description(self, values: dict) -> dict:
        """Replace missing values in the dict keys to human-readable string"""
        return {self.MISSING_VALUES_NAMING_MAPPING.get(k, k): v for k, v in values.items()}

    def get_table_with_number_of_missing_values_by_one_missing_value(
        self, info: TestHtmlInfo, current_missing_values: dict, reference_missing_values: Optional[dict], name: str
    ) -> TestHtmlInfo:
        columns = ["missing value", "current number of missing values"]
        dict_curr = self._replace_missing_values_to_description(current_missing_values)
        dict_ref: Optional[dict] = None

        if reference_missing_values is not None:
            # add one more column and values for reference data
            columns.append("reference number of missing values")
            # cast keys to str because None could be in keys, and it is not processed correctly in visual tables
            dict_ref = self._replace_missing_values_to_description(reference_missing_values)

        additional_plots = plot_dicts_to_table(dict_curr, dict_ref, columns, name)
        info.details = additional_plots
        return info


class TestNumberOfDifferentMissingValues(BaseIntegrityMissingValuesValuesTest):
    """Check a number of different encoded missing values."""

    name: ClassVar = "Different Types of Missing Values"

    def get_condition_from_reference(self, reference: Optional[DatasetMissingValues]):
        if reference is not None:
            return TestValueCondition(eq=reference.number_of_different_missing_values)

        return TestValueCondition(eq=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.number_of_different_missing_values

    def get_description(self, value: Numeric) -> str:
        return (
            f"The number of differently encoded types of missing values is {value}. "
            f"The test threshold is {self.get_condition()}."
        )


@default_renderer(wrap_type=TestNumberOfDifferentMissingValues)
class TestNumberOfDifferentMissingValuesRenderer(BaseTestMissingValuesRenderer):
    def render_html(self, obj: TestNumberOfDifferentMissingValues) -> TestHtmlInfo:
        """Get a table with a missing value and number of the value in the dataset"""
        info = super().render_html(obj)
        metric_result = obj.metric.get_result()
        current_missing_values = metric_result.current.different_missing_values

        if metric_result.reference is None:
            reference_missing_values = None

        else:
            reference_missing_values = metric_result.reference.different_missing_values

        return self.get_table_with_number_of_missing_values_by_one_missing_value(
            info,
            current_missing_values,
            reference_missing_values,
            "number_of_different_missing_values",
        )


class TestNumberOfMissingValues(BaseIntegrityMissingValuesValuesTest):
    """Check a number of missing values."""

    name: ClassVar = "The Number of Missing Values"

    def get_condition_from_reference(self, reference: Optional[DatasetMissingValues]):
        if reference is not None:
            curr_number_of_rows = self.metric.get_result().current.number_of_rows
            ref_number_of_rows = reference.number_of_rows
            mult = curr_number_of_rows / ref_number_of_rows
            return TestValueCondition(
                lte=approx(
                    reference.number_of_missing_values * mult,
                    relative=0.1,
                ),
            )

        return TestValueCondition(eq=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.number_of_missing_values

    def get_description(self, value: Numeric) -> str:
        return f"The number of missing values is {value}. The test threshold is {self.get_condition()}."


@default_renderer(wrap_type=TestNumberOfMissingValues)
class TestNumberOfMissingValuesRenderer(BaseTestMissingValuesRenderer):
    def render_html(self, obj: TestNumberOfMissingValues) -> TestHtmlInfo:
        info = super().render_html(obj)
        metric_result = obj.metric.get_result()
        return self.get_table_with_missing_values_and_percents_by_column(
            info, metric_result, "number_of_missing_values"
        )


class TestShareOfMissingValues(BaseIntegrityMissingValuesValuesTest):
    """Check a share of missing values."""

    name: ClassVar = "Share of Missing Values"

    def get_condition_from_reference(self, reference: Optional[DatasetMissingValues]):
        if reference is not None:
            return TestValueCondition(lte=approx(reference.share_of_missing_values, relative=0.1))

        return TestValueCondition(eq=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.share_of_missing_values

    def get_description(self, value: Numeric) -> str:
        return f"The share of missing values is {value:.3g}. The test threshold is {self.get_condition()}."


@default_renderer(wrap_type=TestShareOfMissingValues)
class TestShareOfMissingValuesRenderer(BaseTestMissingValuesRenderer):
    def render_html(self, obj: TestNumberOfMissingValues) -> TestHtmlInfo:
        info = super().render_html(obj)
        metric_result = obj.metric.get_result()
        return self.get_table_with_missing_values_and_percents_by_column(info, metric_result, "share_of_missing_values")


class TestNumberOfColumnsWithMissingValues(BaseIntegrityMissingValuesValuesTest):
    """Check a number of columns with a missing value."""

    name: ClassVar = "The Number of Columns With Missing Values"

    def get_condition_from_reference(self, reference: Optional[DatasetMissingValues]):
        if reference is not None:
            return TestValueCondition(lte=reference.number_of_columns_with_missing_values)

        return TestValueCondition(eq=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.number_of_columns_with_missing_values

    def get_description(self, value: Numeric) -> str:
        return (
            f"The number of columns with missing values is {value}. " f"The test threshold is {self.get_condition()}."
        )


@default_renderer(wrap_type=TestNumberOfColumnsWithMissingValues)
class TestNumberOfColumnsWithMissingValuesRenderer(BaseTestMissingValuesRenderer):
    def render_html(self, obj: TestNumberOfMissingValues) -> TestHtmlInfo:
        info = super().render_html(obj)
        metric_result = obj.metric.get_result()
        return self.get_table_with_missing_values_and_percents_by_column(
            info, metric_result, "number_of_columns_with_missing_values"
        )


class TestShareOfColumnsWithMissingValues(BaseIntegrityMissingValuesValuesTest):
    """Check a share of columns with a missing value."""

    name: ClassVar = "The Share of Columns With Missing Values"

    def get_condition_from_reference(self, reference: Optional[DatasetMissingValues]):
        if reference is not None:
            return TestValueCondition(lte=reference.share_of_columns_with_missing_values)

        return TestValueCondition(eq=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.share_of_columns_with_missing_values

    def get_description(self, value: Numeric) -> str:
        return (
            f"The share of columns with missing values is {value:.3g}. "
            f"The test threshold is {self.get_condition()}."
        )


@default_renderer(wrap_type=TestShareOfColumnsWithMissingValues)
class TestShareOfColumnsWithMissingValuesRenderer(BaseTestMissingValuesRenderer):
    def render_html(self, obj: TestNumberOfMissingValues) -> TestHtmlInfo:
        info = super().render_html(obj)
        metric_result = obj.metric.get_result()
        return self.get_table_with_missing_values_and_percents_by_column(
            info, metric_result, "share_of_columns_with_missing_values"
        )


class TestNumberOfRowsWithMissingValues(BaseIntegrityMissingValuesValuesTest):
    """Check a number of rows with a missing value."""

    name: ClassVar = "The Number Of Rows With Missing Values"

    def get_condition_from_reference(self, reference: Optional[DatasetMissingValues]):
        if reference is not None:
            curr_number_of_rows = self.metric.get_result().current.number_of_rows
            ref_number_of_rows = reference.number_of_rows
            mult = curr_number_of_rows / ref_number_of_rows
            return TestValueCondition(
                lte=approx(reference.number_of_rows_with_missing_values * mult, relative=0.1),
            )

        return TestValueCondition(eq=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.number_of_rows_with_missing_values

    def get_description(self, value: Numeric) -> str:
        return f"The number of rows with missing values is {value}. " f"The test threshold is {self.get_condition()}."


class TestShareOfRowsWithMissingValues(BaseIntegrityMissingValuesValuesTest):
    """Check a share of rows with a missing value."""

    name: ClassVar = "The Share of Rows With Missing Values"

    def get_condition_from_reference(self, reference: Optional[DatasetMissingValues]):
        if reference is not None:
            return TestValueCondition(lte=approx(reference.share_of_rows_with_missing_values, relative=0.1))

        return TestValueCondition(eq=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.share_of_rows_with_missing_values

    def get_description(self, value: Numeric) -> str:
        return (
            f"The share of rows with missing values is {value:.3g}. " f"The test threshold is {self.get_condition()}."
        )


class BaseIntegrityColumnMissingValuesTest(ConditionFromReferenceMixin[DatasetMissingValues], ABC):
    group: ClassVar = DATA_INTEGRITY_GROUP.id
    _metric: DatasetMissingValuesMetric
    column_name: str
    missing_values: Optional[List] = None
    replace: bool = True

    def __init__(
        self,
        column_name: str,
        missing_values: Optional[list] = None,
        replace: bool = True,
        eq: Optional[Numeric] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
    ):
        self.column_name = column_name
        self.missing_values = missing_values
        self.replace = replace
        super().__init__(
            eq=eq,
            gt=gt,
            gte=gte,
            is_in=is_in,
            lt=lt,
            lte=lte,
            not_eq=not_eq,
            not_in=not_in,
            is_critical=is_critical,
        )
        self._metric = DatasetMissingValuesMetric(missing_values=self.missing_values, replace=self.replace)


class TestColumnNumberOfDifferentMissingValues(BaseIntegrityColumnMissingValuesTest):
    """Check a number of differently encoded missing values in one column."""

    name: ClassVar = "Different Types of Missing Values in a Column"

    def get_condition_from_reference(self, reference: Optional[DatasetMissingValues]):
        if reference is not None:
            if self.column_name not in reference.number_of_different_missing_values_by_column:
                raise ValueError(
                    f"Cannot define test default conditions: no column '{self.column_name}' in reference dataset."
                )

            ref_value = reference.number_of_different_missing_values_by_column[self.column_name]
            return TestValueCondition(lte=ref_value)

        return TestValueCondition(eq=0)

    def calculate_value_for_test(self) -> Numeric:
        metric_data = self.metric.get_result().current
        return metric_data.number_of_different_missing_values_by_column[self.column_name]

    def get_description(self, value: Numeric) -> str:
        return (
            f"The number of differently encoded types of missing values in the column **{self.column_name}** "
            f"is {value}. The test threshold is {self.get_condition()}."
        )


@default_renderer(wrap_type=TestColumnNumberOfDifferentMissingValues)
class TestColumnNumberOfDifferentMissingValuesRenderer(BaseTestMissingValuesRenderer):
    def render_html(self, obj: TestColumnNumberOfDifferentMissingValues) -> TestHtmlInfo:
        """Get a table with a missing value and number of the value in the dataset"""
        info = super().render_html(obj)
        metric_result = obj.metric.get_result()
        current_missing_values = metric_result.current.different_missing_values_by_column[obj.column_name]

        if metric_result.reference is None:
            reference_missing_values = None

        else:
            reference_missing_values = metric_result.reference.different_missing_values_by_column[obj.column_name]

        return self.get_table_with_number_of_missing_values_by_one_missing_value(
            info,
            current_missing_values,
            reference_missing_values,
            "number_of_different_missing_values",
        )


class TestColumnNumberOfMissingValues(BaseIntegrityColumnMissingValuesTest):
    """Check a number of missing values in one column."""

    name: ClassVar = "The Number of Missing Values in a Column"

    def get_condition_from_reference(self, reference: Optional[DatasetMissingValues]):
        if reference is not None:
            curr_number_of_rows = self.metric.get_result().current.number_of_rows
            ref_number_of_rows = reference.number_of_rows
            mult = curr_number_of_rows / ref_number_of_rows
            ref_value = reference.number_of_missing_values_by_column[self.column_name]
            return TestValueCondition(lte=approx(ref_value * mult, relative=0.1))

        return TestValueCondition(eq=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.number_of_missing_values_by_column[self.column_name]

    def get_description(self, value: Numeric) -> str:
        return (
            f"The number of missing values in the column **{self.column_name}** is {value}. "
            f"The test threshold is {self.get_condition()}."
        )


class TestColumnShareOfMissingValues(BaseIntegrityColumnMissingValuesTest):
    """Check a share of missing values in one column."""

    name: ClassVar = "The Share of Missing Values in a Column"

    def get_condition_from_reference(self, reference: Optional[DatasetMissingValues]):
        if reference is not None:
            ref_value = reference.share_of_missing_values_by_column[self.column_name]
            return TestValueCondition(lte=approx(ref_value, relative=0.1))

        return TestValueCondition(eq=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.share_of_missing_values_by_column[self.column_name]

    def get_description(self, value: Numeric) -> str:
        return (
            f"The share of missing values in the column **{self.column_name}** is {value:.3g}. "
            f"The test threshold is {self.get_condition()}."
        )

    def get_parameters(self):
        return ColumnCheckValueParameters(
            condition=self.get_condition(), value=self._value, column_name=self.column_name
        )


class TestAllColumnsShareOfMissingValues(BaseGenerator):
    columns: Optional[List[str]]

    def __init__(self, columns: Optional[List[str]] = None, is_critical: bool = True):
        self.is_critical = is_critical
        self.columns = columns

    def generate(self, data_definition: DataDefinition) -> List[TestColumnShareOfMissingValues]:
        if self.columns is None:
            columns = [column.column_name for column in data_definition.get_columns()]

        else:
            columns = self.columns

        return [
            TestColumnShareOfMissingValues(
                column_name=column,
                is_critical=self.is_critical,
            )
            for column in columns
        ]


class TestNumberOfConstantColumns(BaseIntegrityValueTest):
    """Number of columns contained only one unique value"""

    name: ClassVar = "Number of Constant Columns"

    def get_condition_from_reference(self, reference: Optional[DatasetSummary]):
        if reference is not None:
            value = reference.number_of_constant_columns
            return TestValueCondition(lte=value)

        return TestValueCondition(eq=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.number_of_constant_columns

    def get_description(self, value: Numeric) -> str:
        return f"The number of constant columns is {value}. The test threshold is {self.get_condition()}."


@default_renderer(wrap_type=TestNumberOfConstantColumns)
class TestNumberOfConstantColumnsRenderer(TestRenderer):
    def render_html(self, obj: TestNumberOfConstantColumns) -> TestHtmlInfo:
        info = super().render_html(obj)
        columns = ["column name", "current nunique"]
        dict_curr = obj.metric.get_result().current.number_uniques_by_columns
        dict_ref = {}
        reference_stats = obj.metric.get_result().reference

        if reference_stats is not None:
            dict_ref = reference_stats.number_uniques_by_columns
            columns = columns + ["reference nunique"]

        additional_plots = plot_dicts_to_table(dict_curr, dict_ref, columns, "number_of_constant_cols", "curr", True)
        info.details = additional_plots
        return info


class TestNumberOfEmptyRows(BaseIntegrityValueTest):
    """Number of rows contained all NAN values"""

    name: ClassVar = "Number of Empty Rows"

    def get_condition_from_reference(self, reference: Optional[DatasetSummary]):
        if reference is not None:
            ref_number_of_empty_rows = reference.number_of_empty_rows
            curr_number_of_rows = self.metric.get_result().current.number_of_rows
            ref_number_of_rows = reference.number_of_rows
            mult = curr_number_of_rows / ref_number_of_rows
            return TestValueCondition(eq=approx(ref_number_of_empty_rows * mult, 0.1))

        return TestValueCondition(eq=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.number_of_empty_rows

    def get_description(self, value: Numeric) -> str:
        return f"Number of Empty Rows is {value}. The test threshold is {self.get_condition()}."


class TestNumberOfEmptyColumns(BaseIntegrityValueTest):
    """Number of columns contained all NAN values"""

    name: ClassVar = "Number of Empty Columns"

    def get_condition_from_reference(self, reference: Optional[DatasetSummary]):
        if reference is not None:
            return TestValueCondition(lte=reference.number_of_empty_columns)

        return TestValueCondition(eq=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.number_of_empty_columns

    def get_description(self, value: Numeric) -> str:
        return f"Number of Empty Columns is {value}. The test threshold is {self.get_condition()}."


@default_renderer(wrap_type=TestNumberOfEmptyColumns)
class TestNumberOfEmptyColumnsRenderer(TestRenderer):
    def render_html(self, obj: TestNumberOfEmptyColumns) -> TestHtmlInfo:
        info = super().render_html(obj)
        columns = ["column name", "current number of NaNs"]
        dict_curr = obj.metric.get_result().current.nans_by_columns
        dict_ref = {}
        reference_stats = obj.metric.get_result().reference

        if reference_stats is not None:
            dict_ref = reference_stats.nans_by_columns
            columns = columns + ["reference number of NaNs"]

        additional_plots = plot_dicts_to_table(dict_curr, dict_ref, columns, "number_of_empty_columns")
        info.details = additional_plots
        return info


class TestNumberOfDuplicatedRows(BaseIntegrityValueTest):
    """How many rows have duplicates in the dataset"""

    name: ClassVar = "Number of Duplicate Rows"

    def get_condition_from_reference(self, reference: Optional[DatasetSummary]):
        if reference is not None:
            ref_num_of_duplicates = reference.number_of_duplicated_rows
            curr_number_of_rows = self.metric.get_result().current.number_of_rows
            ref_number_of_rows = reference.number_of_rows
            mult = curr_number_of_rows / ref_number_of_rows
            return TestValueCondition(eq=approx(ref_num_of_duplicates * mult, 0.1))

        return TestValueCondition(eq=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.number_of_duplicated_rows

    def get_description(self, value: Numeric) -> str:
        return f"The number of duplicate rows is {value}. The test threshold is {self.get_condition()}."


class TestNumberOfDuplicatedColumns(BaseIntegrityValueTest):
    """How many columns have duplicates in the dataset"""

    name: ClassVar = "Number of Duplicate Columns"

    def get_condition_from_reference(self, reference: Optional[DatasetSummary]):
        if reference is not None:
            value = reference.number_of_duplicated_columns
            return TestValueCondition(lte=value)

        return TestValueCondition(eq=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current.number_of_duplicated_columns

    def get_description(self, value: Numeric) -> str:
        return f"The number of duplicate columns is {value}. The test threshold is {self.get_condition()}."


class BaseIntegrityByColumnsConditionTest(BaseCheckValueTest, ABC):
    group: ClassVar = DATA_INTEGRITY_GROUP.id
    _data_integrity_metric: ColumnSummaryMetric
    column_name: ColumnName

    def __init__(
        self,
        column_name: Union[str, ColumnName],
        eq: Optional[Numeric] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
    ):
        super().__init__(
            eq=eq,
            gt=gt,
            gte=gte,
            is_in=is_in,
            lt=lt,
            lte=lte,
            not_eq=not_eq,
            not_in=not_in,
            is_critical=is_critical,
        )
        self.column_name = ColumnName.from_any(column_name)
        self._data_integrity_metric = ColumnSummaryMetric(column_name=column_name)

    def groups(self) -> Dict[str, str]:
        if self.column_name is not None:
            return {GroupingTypes.ByFeature.id: self.column_name.display_name}
        return {}


class BaseIntegrityOneColumnTest(Test, ABC):
    group: ClassVar = DATA_INTEGRITY_GROUP.id
    _metric: ColumnSummaryMetric
    column_name: ColumnName

    def __init__(self, column_name: Union[str, ColumnName], is_critical: bool = True):
        self.column_name = ColumnName.from_any(column_name)
        super().__init__(is_critical=is_critical)
        self._metric = ColumnSummaryMetric(self.column_name)

    @property
    def metric(self):
        return self._metric

    def groups(self) -> Dict[str, str]:
        return {GroupingTypes.ByFeature.id: self.column_name.display_name}


class TestColumnAllConstantValues(BaseIntegrityOneColumnTest):
    """Test that there is only one unique value in a column"""

    name: ClassVar = "All Constant Values in a Column"
    _metric: ColumnSummaryMetric

    def check(self):
        uniques_in_column = self.metric.get_result().current_characteristics.unique
        number_of_rows = self.metric.get_result().current_characteristics.number_of_rows
        column_name = self.column_name

        description = (
            f"The number of the unique values in the column **{column_name}** "
            f"is {uniques_in_column} out of {number_of_rows}"
        )

        if uniques_in_column <= 1:
            status = TestStatus.FAIL

        else:
            status = TestStatus.SUCCESS

        return TestResult(
            name=self.name, description=description, status=status, groups=self.groups(), group=self.group
        )


@default_renderer(wrap_type=TestColumnAllConstantValues)
class TestColumnAllConstantValuesRenderer(TestRenderer):
    def render_html(self, obj: TestColumnAllConstantValues) -> TestHtmlInfo:
        info = super().render_html(obj)
        column_name = obj.column_name
        counts_data = obj.metric.get_result().plot_data.counts_of_values
        if counts_data is not None:
            curr_df = counts_data["current"]
            ref_df = None
            if "reference" in counts_data.keys():
                ref_df = counts_data["reference"]
            additional_plots = plot_value_counts_tables_ref_curr(column_name, curr_df, ref_df, "AllConstantValues")
            info.details = additional_plots
        return info


class TestColumnAllUniqueValues(BaseIntegrityOneColumnTest):
    """Test that there is only uniques values in a column"""

    name: ClassVar = "All Unique Values in a Column"

    def check(self):
        uniques_in_column = self.metric.get_result().current_characteristics.unique
        number_of_rows = self.metric.get_result().current_characteristics.number_of_rows
        nans_in_column = self.metric.get_result().current_characteristics.missing
        column_name = self.column_name

        description = (
            f"The number of the unique values in the column **{column_name}** "
            f"is {uniques_in_column}  out of {number_of_rows}"
        )

        if uniques_in_column != number_of_rows - nans_in_column:
            status = TestStatus.FAIL

        else:
            status = TestStatus.SUCCESS

        return TestResult(
            name=self.name, description=description, status=status, groups=self.groups(), group=self.group
        )


@default_renderer(wrap_type=TestColumnAllUniqueValues)
class TestColumnAllUniqueValuesRenderer(TestRenderer):
    def render_html(self, obj: TestColumnAllUniqueValues) -> TestHtmlInfo:
        info = super().render_html(obj)
        column_name = obj.column_name
        counts_data = obj.metric.get_result().plot_data.counts_of_values
        if counts_data is not None:
            curr_df = counts_data["current"]
            ref_df = None
            if "reference" in counts_data.keys():
                ref_df = counts_data["reference"]
            additional_plots = plot_value_counts_tables_ref_curr(column_name, curr_df, ref_df, "AllUniqueValues")
            info.details = additional_plots
        return info


class ColumnTypeParameter(TestParameters):
    actual_type: str
    column_name: str
    expected_type: str


class ColumnTypesParameter(TestParameters):
    columns: List[ColumnTypeParameter]


class TestColumnsType(Test):
    """This test compares columns type against the specified ones or a reference dataframe"""

    group: ClassVar = DATA_INTEGRITY_GROUP.id
    name: ClassVar = "Column Types"
    columns_type: Optional[dict]
    _metric: DatasetSummaryMetric

    def __init__(self, columns_type: Optional[dict] = None, is_critical: bool = True):
        self.columns_type = columns_type
        self._metric = DatasetSummaryMetric()
        super().__init__(is_critical=is_critical)

    @property
    def metric(self):
        return self._metric

    def check(self):
        status = TestStatus.SUCCESS
        data_columns_type = self.metric.get_result().current.columns_type

        if self.columns_type is None:
            if self.metric.get_result().reference is None:
                status = TestStatus.ERROR
                description = "Cannot compare column types without conditions or a reference"
                return TestResult(name=self.name, description=description, status=status, group=self.group)

            # get types from reference
            columns_type = self.metric.get_result().reference.columns_type

        else:
            columns_type = self.columns_type

            if not columns_type:
                status = TestStatus.ERROR
                description = "Columns type condition is empty"
                return TestResult(name=self.name, description=description, status=status, group=self.group)

        invalid_types_count = 0
        columns = []

        for column_name, expected_type_object in columns_type.items():
            real_column_type_object = data_columns_type.get(column_name)

            if real_column_type_object is None:
                status = TestStatus.ERROR
                description = f"No column '{column_name}' in the metrics data"
                return TestResult(name=self.name, description=description, status=status, group=self.group)

            expected_type = infer_dtype_from_object(expected_type_object)
            real_column_type = infer_dtype_from_object(real_column_type_object)
            columns.append(
                ColumnTypeParameter(
                    actual_type=real_column_type.__name__, expected_type=expected_type.__name__, column_name=column_name
                )
            )

            if expected_type == real_column_type or issubclass(real_column_type, expected_type):
                # types are matched or expected type is a parent
                continue

            status = TestStatus.FAIL
            invalid_types_count += 1

        return TestResult(
            name=self.name,
            description=f"The number of columns with a type "
            f"mismatch is {invalid_types_count} out of {len(columns_type)}.",
            status=status,
            parameters=ColumnTypesParameter(columns=columns),
            group=self.group,
        )

    def groups(self) -> Dict[str, str]:
        return {}


@default_renderer(wrap_type=TestColumnsType)
class TestColumnsTypeRenderer(TestRenderer):
    def render_html(self, obj: TestColumnsType) -> TestHtmlInfo:
        info = super().render_html(obj)

        parameters = obj.get_result().parameters
        assert isinstance(parameters, ColumnTypesParameter)
        info.details = [
            DetailsInfo(
                title="",
                info=BaseWidgetInfo(
                    title="",
                    type="table",
                    params={
                        "header": ["Column Name", "Actual Type", "Expected Type"],
                        "data": [[c.column_name, c.actual_type, c.expected_type] for c in parameters.columns],
                    },
                    size=2,
                ),
            ),
        ]
        return info


class TestColumnRegExp(BaseCheckValueTest, ABC):
    group: ClassVar = DATA_INTEGRITY_GROUP.id
    name: ClassVar = "RegExp Match"
    _metric: ColumnRegExpMetric
    column_name: str
    reg_exp: str

    def __init__(
        self,
        column_name: str,
        reg_exp: str,
        eq: Optional[Numeric] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
    ):
        self.column_name = column_name
        self.reg_exp = reg_exp
        super().__init__(
            eq=eq,
            gt=gt,
            gte=gte,
            is_in=is_in,
            lt=lt,
            lte=lte,
            not_eq=not_eq,
            not_in=not_in,
            is_critical=is_critical,
        )
        self._metric = ColumnRegExpMetric(column_name=self.column_name, reg_exp=self.reg_exp)

    @property
    def metric(self):
        return self._metric

    def groups(self) -> Dict[str, str]:
        if self.column_name is not None:
            return {GroupingTypes.ByFeature.id: self.column_name}
        return {}

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition

        metric_result = self.metric.get_result()

        if metric_result.reference:
            ref_value = metric_result.reference.number_of_not_matched
            mult = metric_result.current.number_of_rows / metric_result.reference.number_of_rows

            if mult is not None:
                return TestValueCondition(eq=approx(ref_value * mult, relative=0.1))

        return TestValueCondition(eq=0)

    def calculate_value_for_test(self) -> Optional[Numeric]:
        return self.metric.get_result().current.number_of_not_matched

    def get_description(self, value: Numeric) -> str:
        return (
            f"The number of the mismatched values in the column **{self.column_name}** is {value}. "
            f"The test threshold is {self.get_condition()}."
        )


@default_renderer(wrap_type=TestColumnRegExp)
class TestColumnRegExpRenderer(TestRenderer):
    def render_html(self, obj: TestColumnRegExp) -> TestHtmlInfo:
        info = super().render_html(obj)
        column_name = obj.column_name
        metric_result = obj.metric.get_result()

        if metric_result.current.table_of_not_matched:
            curr_df = pd.DataFrame(metric_result.current.table_of_not_matched.items())
            curr_df.columns = ["x", "count"]

        else:
            curr_df = pd.DataFrame(columns=["x", "count"])

        ref_df = None

        if metric_result.reference is not None and metric_result.reference.table_of_not_matched:
            ref_df = pd.DataFrame(metric_result.reference.table_of_not_matched.items())
            ref_df.columns = ["x", "count"]

        additional_plots = plot_value_counts_tables_ref_curr(
            column_name, curr_df, ref_df, f"{column_name}_ColumnValueRegExp"
        )
        info.details = additional_plots
        return info
