"""Methods for overall dataset quality calculations - rows count, a specific values count, etc."""

import dataclasses
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

from evidently.calculations.utils import relabel_data
from evidently.core import ColumnType
from evidently.metric_results import ColumnCorrelations
from evidently.metric_results import DatasetColumns
from evidently.metric_results import Distribution
from evidently.metric_results import DistributionIncluded
from evidently.utils.data_preprocessing import DataDefinition
from evidently.utils.types import ColumnDistribution

MAX_CATEGORIES = 5


def get_rows_count(data: Union[pd.DataFrame, pd.Series]) -> int:
    """Count quantity of rows in  a dataset"""
    return data.shape[0]


@dataclasses.dataclass
class FeatureQualityStats:
    """Class for all features data quality metrics store.

    A type of the feature is stored in `feature_type` field.
    Concrete stat kit depends on the feature type. Is a metric is not applicable - leave `None` value for it.

    Metrics for all feature types:
        - feature type - cat for category, num for numeric, datetime for datetime features
        - count - quantity of a meaningful values (do not take into account NaN values)
        - missing_count - quantity of meaningless (NaN) values
        - missing_percentage - the percentage of the missed values
        - unique_count - quantity of unique values
        - unique_percentage - the percentage of the unique values
        - max - maximum value (not applicable for category features)
        - min - minimum value (not applicable for category features)
        - most_common_value - the most common value in the feature values
        - most_common_value_percentage - the percentage of the most common value
        - most_common_not_null_value - if `most_common_value` equals NaN - the next most common value. Otherwise - None
        - most_common_not_null_value_percentage - the percentage of `most_common_not_null_value` if it is defined.
            If `most_common_not_null_value` is not defined, equals None too.

    Metrics for numeric features only:
        - infinite_count - quantity infinite values (for numeric features only)
        - infinite_percentage - the percentage of infinite values (for numeric features only)
        - percentile_25 - 25% percentile for meaningful values
        - percentile_50 - 50% percentile for meaningful values
        - percentile_75 - 75% percentile for meaningful values
        - mean - the sum of the meaningful values divided by the number of the meaningful values
        - std - standard deviation of the values

    Metrics for category features only:
        - new_in_current_values_count - quantity of new values in the current dataset after the reference
            Defined for reference dataset only.
        - new_in_current_values_count - quantity of values in the reference dataset that not presented in the current
            Defined for reference dataset only.
    """

    # feature type - cat for category, num for numeric, datetime for datetime features
    feature_type: str
    # quantity on
    number_of_rows: int = 0
    count: int = 0
    infinite_count: Optional[int] = None
    infinite_percentage: Optional[float] = None
    missing_count: Optional[int] = None
    missing_percentage: Optional[float] = None
    unique_count: Optional[int] = None
    unique_percentage: Optional[float] = None
    percentile_25: Optional[float] = None
    percentile_50: Optional[float] = None
    percentile_75: Optional[float] = None
    max: Optional[Union[int, float, bool, str]] = None
    min: Optional[Union[int, float, bool, str]] = None
    mean: Optional[float] = None
    most_common_value: Optional[Union[int, float, bool, str]] = None
    most_common_value_percentage: Optional[float] = None
    std: Optional[float] = None
    most_common_not_null_value: Optional[Union[int, float, bool, str]] = None
    most_common_not_null_value_percentage: Optional[float] = None
    new_in_current_values_count: Optional[int] = None
    unused_in_current_values_count: Optional[int] = None

    def is_datetime(self):
        """Checks that the object store stats for a datetime feature"""
        return self.feature_type == "datetime"

    def is_numeric(self):
        """Checks that the object store stats for a numeric feature"""
        return self.feature_type == "num"

    def is_category(self):
        """Checks that the object store stats for a category feature"""
        return self.feature_type == "cat"

    def as_dict(self):
        return {field.name: getattr(self, field.name) for field in dataclasses.fields(FeatureQualityStats)}

    def __eq__(self, other):
        for field in dataclasses.fields(FeatureQualityStats):
            other_field_value = getattr(other, field.name)
            self_field_value = getattr(self, field.name)

            if pd.isnull(other_field_value) and pd.isnull(self_field_value):
                continue

            if not other_field_value == self_field_value:
                return False

        return True


@dataclasses.dataclass
class DataQualityStats:
    rows_count: int
    num_features_stats: Optional[Dict[str, FeatureQualityStats]] = None
    cat_features_stats: Optional[Dict[str, FeatureQualityStats]] = None
    datetime_features_stats: Optional[Dict[str, FeatureQualityStats]] = None
    target_stats: Optional[Dict[str, FeatureQualityStats]] = None
    prediction_stats: Optional[Dict[str, FeatureQualityStats]] = None

    def get_all_features(self) -> Dict[str, FeatureQualityStats]:
        result = {}

        for features in (
            self.target_stats,
            self.prediction_stats,
            self.datetime_features_stats,
            self.cat_features_stats,
            self.num_features_stats,
        ):
            if features is not None:
                result.update(features)

        return result

    def __getitem__(self, item) -> FeatureQualityStats:
        for features in (
            self.target_stats,
            self.prediction_stats,
            self.datetime_features_stats,
            self.cat_features_stats,
            self.num_features_stats,
        ):
            if features is not None and item in features:
                return features[item]

        raise KeyError(item)


def get_features_stats(feature: pd.Series, feature_type: ColumnType) -> FeatureQualityStats:
    def get_percentage_from_all_values(value: Union[int, float]) -> float:
        return np.round(100 * value / all_values_count, 2)

    result = FeatureQualityStats(feature_type=feature_type.value)
    all_values_count = feature.shape[0]

    if not all_values_count > 0:
        # we have no data, return default stats for en empty dataset
        return result
    result.number_of_rows = all_values_count
    result.missing_count = int(feature.isnull().sum())
    result.count = int(feature.count())
    all_values_count = feature.shape[0]
    value_counts = feature.value_counts(dropna=False)
    result.missing_percentage = np.round(100 * result.missing_count / all_values_count, 2)
    unique_count: int = feature.nunique()
    result.unique_count = unique_count
    result.unique_percentage = get_percentage_from_all_values(unique_count)
    result.most_common_value = value_counts.index[0]
    result.most_common_value_percentage = get_percentage_from_all_values(value_counts.iloc[0])

    if result.count > 0 and pd.isnull(result.most_common_value):
        result.most_common_not_null_value = value_counts.index[1]
        result.most_common_not_null_value_percentage = get_percentage_from_all_values(value_counts.iloc[1])

    if feature_type == ColumnType.Numerical:
        # round most common feature value for numeric features to 1e-5
        if not np.issubdtype(feature, np.number):
            feature = feature.astype(float)
        if isinstance(result.most_common_value, float):
            result.most_common_value = np.round(result.most_common_value, 5)
        result.infinite_count = int(np.sum(np.isinf(feature)))
        result.infinite_percentage = get_percentage_from_all_values(result.infinite_count)
        result.max = np.round(feature.max(), 2)
        result.min = np.round(feature.min(), 2)
        common_stats = dict(feature.describe())
        std = common_stats["std"]
        result.std = np.round(std, 2)
        result.mean = np.round(common_stats["mean"], 2)
        result.percentile_25 = np.round(common_stats["25%"], 2)
        result.percentile_50 = np.round(common_stats["50%"], 2)
        result.percentile_75 = np.round(common_stats["75%"], 2)

    if feature_type == ColumnType.Datetime:
        # cast datetime value to str for datetime features
        result.most_common_value = str(result.most_common_value)
        # cast datetime value to str for datetime features
        result.max = str(feature.max())
        result.min = str(feature.min())

    return result


def calculate_data_quality_stats(
    dataset: pd.DataFrame, columns: DatasetColumns, task: Optional[str]
) -> DataQualityStats:
    result = DataQualityStats(rows_count=get_rows_count(dataset))

    result.num_features_stats = {
        feature_name: get_features_stats(dataset[feature_name], feature_type=ColumnType.Numerical)
        for feature_name in columns.num_feature_names
    }

    result.cat_features_stats = {
        feature_name: get_features_stats(dataset[feature_name], feature_type=ColumnType.Categorical)
        for feature_name in columns.cat_feature_names
    }

    if columns.utility_columns.date:
        date_list = columns.datetime_feature_names + [columns.utility_columns.date]

    else:
        date_list = columns.datetime_feature_names

    result.datetime_features_stats = {
        feature_name: get_features_stats(dataset[feature_name], feature_type=ColumnType.Datetime)
        for feature_name in date_list
    }

    target_name = columns.utility_columns.target

    if target_name is not None and target_name in dataset:
        result.target_stats = {}

        if task == "classification":
            result.target_stats[target_name] = get_features_stats(
                dataset[target_name],
                feature_type=ColumnType.Categorical,
            )

        else:
            result.target_stats[target_name] = get_features_stats(
                dataset[target_name],
                feature_type=ColumnType.Numerical,
            )

    prediction_name = columns.utility_columns.prediction

    if isinstance(prediction_name, str) and prediction_name in dataset:
        result.prediction_stats = {}

        if task == "classification":
            result.prediction_stats[prediction_name] = get_features_stats(
                dataset[prediction_name],
                feature_type=ColumnType.Categorical,
            )

        else:
            result.prediction_stats[prediction_name] = get_features_stats(
                dataset[prediction_name],
                feature_type=ColumnType.Numerical,
            )

    return result


def prepare_data_for_plots(
    current_data: pd.Series,
    reference_data: Optional[pd.Series],
    column_type: ColumnType,
    max_categories: Optional[int] = MAX_CATEGORIES,
) -> Tuple[pd.Series, Optional[pd.Series]]:
    if column_type == ColumnType.Categorical:
        current_data, reference_data = relabel_data(current_data, reference_data, max_categories)
    else:
        current_data = current_data.copy()
        if reference_data is not None:
            reference_data = reference_data.copy()
    return current_data, reference_data


def _select_features_for_corr(dataset: pd.DataFrame, data_definition: DataDefinition) -> tuple:
    """Define which features should be used for calculating correlation matrices:
        - for pearson, spearman, and kendall correlation matrices we select numerical features which have > 1
            unique values;
        - for kramer_v correlation matrix, we select categorical features which have > 1 unique values.
    Args:
        dataset: data for processing
        data_definition: definition for all columns in data
    Returns:
        num_for_corr: list of feature names for pearson, spearman, and kendall correlation matrices.
        cat_for_corr: list of feature names for kramer_v correlation matrix.
    """

    num = data_definition.get_columns(ColumnType.Numerical)
    cat = data_definition.get_columns(ColumnType.Categorical)
    num_for_corr = []
    cat_for_corr = []

    for col in num:
        col_name = col.column_name
        unique_count = dataset[col_name].nunique()
        if unique_count and unique_count > 1:
            num_for_corr.append(col_name)

    for col in cat:
        col_name = col.column_name
        unique_count = dataset[col_name].nunique()
        if unique_count and unique_count > 1:
            cat_for_corr.append(col_name)
    return num_for_corr, cat_for_corr


def _cramer_v(x: pd.Series, y: pd.Series) -> float:
    """Calculate Cramér's V: a measure of association between two nominal variables.
    Args:
        x: The array of observed values.
        y: The array of observed values.
    Returns:
        Value of the Cramér's V
    """
    arr = pd.crosstab(x, y).values
    chi2_stat = chi2_contingency(arr, correction=False)
    phi2 = chi2_stat[0] / arr.sum()
    n_rows, n_cols = arr.shape
    if min(n_cols - 1, n_rows - 1) == 0:
        value = np.nan
    else:
        value = np.sqrt(phi2 / min(n_cols - 1, n_rows - 1))

    return value


def get_pairwise_correlation(df, func: Callable[[pd.Series, pd.Series], float]) -> pd.DataFrame:
    """Compute pairwise correlation of columns
    Args:
        df: initial data frame.
        func: function for computing pairwise correlation.
    Returns:
        Correlation matrix.
    """
    columns = df.columns
    k = df.shape[1]
    if k <= 1:
        return pd.DataFrame()
    else:
        corr_array = np.eye(k)

        for i in range(k):
            for j in range(k):
                if i <= j:
                    continue
                c = func(df[columns[i]], df[columns[j]])
                corr_array[i, j] = c
                corr_array[j, i] = c
        return pd.DataFrame(data=corr_array, columns=columns, index=columns)


def _calculate_correlations(df: pd.DataFrame, num_for_corr, cat_for_corr, kind):
    """Calculate correlation matrix depending on the kind parameter
    Args:
        df: initial data frame.
        num_for_corr: list of feature names for pearson, spearman, and kendall correlation matrices.
        cat_for_corr: list of feature names for kramer_v correlation matrix.
        kind: Method of correlation:
            - pearson - standard correlation coefficient
            - kendall - Kendall Tau correlation coefficient
            - spearman - Spearman rank correlation
            - cramer_v - Cramer’s V measure of association
    Returns:
        Correlation matrix.
    """
    if kind == "pearson":
        return df[num_for_corr].corr("pearson")
    elif kind == "spearman":
        return df[num_for_corr].corr("spearman")
    elif kind == "kendall":
        return df[num_for_corr].corr("kendall")
    elif kind == "cramer_v":
        return get_pairwise_correlation(df[cat_for_corr], _cramer_v)


def calculate_correlations(
    dataset: pd.DataFrame, data_definition: DataDefinition, add_text_columns: Optional[list] = None
) -> Dict:
    num_for_corr, cat_for_corr = _select_features_for_corr(dataset, data_definition)
    if add_text_columns is not None:
        num_for_corr += add_text_columns
    correlations = {}

    for kind in ["pearson", "spearman", "kendall", "cramer_v"]:
        correlations[kind] = _calculate_correlations(dataset, num_for_corr, cat_for_corr, kind)

    return correlations


def calculate_cramer_v_correlation(column_name: str, dataset: pd.DataFrame, columns: List[str]) -> ColumnCorrelations:
    result_x = []
    result_y = []

    if not dataset[column_name].empty:
        for correlation_columns_name in columns:
            result_x.append(correlation_columns_name)
            result_y.append(_cramer_v(dataset[column_name], dataset[correlation_columns_name]))

    return ColumnCorrelations(
        column_name=column_name,
        kind="cramer_v",
        values=Distribution(x=result_x, y=result_y),
    )


def calculate_category_correlation(
    column_display_name: str,
    column: pd.Series,
    features: pd.DataFrame,
) -> List[ColumnCorrelations]:
    """For category columns calculate cramer_v correlation"""
    if column.empty or features.empty:
        return []

    result_x = []
    result_y = []

    for feature_name in features.columns:
        result_x.append(feature_name)
        result_y.append(_cramer_v(column, features[feature_name]))

    return [
        ColumnCorrelations(
            column_name=column_display_name,
            kind="cramer_v",
            values=DistributionIncluded(x=result_x, y=result_y),
        ),
    ]


def calculate_numerical_correlation(
    column_display_name: str,
    column: pd.Series,
    features: pd.DataFrame,
) -> List[ColumnCorrelations]:
    if column.empty or features.empty:
        return []

    result = []

    for kind in ["pearson", "spearman", "kendall"]:
        correlations_columns = []
        correlations_values = []

        for other_column_name in features.columns:
            correlations_columns.append(other_column_name)
            correlations_values.append(
                column.replace([np.inf, -np.inf], np.nan).corr(
                    features[other_column_name].replace([np.inf, -np.inf], np.nan), method=kind
                )
            )

        result.append(
            ColumnCorrelations(
                column_name=column_display_name,
                kind=kind,
                values=Distribution(x=correlations_columns, y=correlations_values),
            )
        )

    return result


def calculate_column_distribution(column: pd.Series, column_type: str) -> ColumnDistribution:
    if column.empty:
        distribution: ColumnDistribution = {}

    elif column_type == "num":
        # TODO: implement distribution for num column
        value_counts = column.value_counts(dropna=True)
        distribution = dict(value_counts)

    elif column_type == "cat":
        value_counts = column.value_counts(dropna=True)
        distribution = dict(value_counts)

    else:
        raise ValueError(f"Cannot calculate distribution for column type {column_type}")

    return distribution


def get_corr_method(method: Optional[str], target_correlation: Optional[str] = None, pearson_default: bool = True):
    if method is not None:
        return method
    if method is None and pearson_default is False:
        return target_correlation
    else:
        return "pearson"
