from itertools import combinations

import pandas as pd


def get_number_of_all_pandas_missed_values(dataset: pd.DataFrame) -> int:
    """Calculate the number of missed - nulls by pandas - values in a dataset"""
    return dataset.isnull().sum().sum()


def get_number_of_empty_columns(dataset: pd.DataFrame) -> int:
    """Calculate the number of empty columns in a dataset"""
    return dataset.isnull().all().sum()


def get_number_of_duplicated_columns(dataset: pd.DataFrame) -> int:
    """Calculate the number of duplicated columns in a dataset"""
    return sum([1 for i, j in combinations(dataset, 2) if dataset[i].equals(dataset[j])])


def get_number_of_almost_duplicated_columns(dataset: pd.DataFrame, threshold: float) -> int:
    """Calculate the number of almost duplicated columns in a dataset"""
    result = 0
    all_rows = dataset.shape[0]
    checked_columns = set()

    for column_name_1 in dataset.columns:
        checked_columns.add(column_name_1)

        for column_name_2 in dataset.columns:
            if column_name_2 in checked_columns:
                continue

            # if dtypes of columns are different, then columns are not duplicated
            # check names because of problems with categorical columns
            if dataset[column_name_1].dtype.name != dataset[column_name_2].dtype.name:
                continue

            # if columns are categorical, then we need to check categories lists
            # if the lists are not the same, Series.eq method raises an exception
            if isinstance(dataset[column_name_1].dtype, pd.CategoricalDtype) and isinstance(
                dataset[column_name_2].dtype, pd.CategoricalDtype
            ):
                if dataset[column_name_1].cat.categories.tolist() != dataset[column_name_2].cat.categories.tolist():
                    continue

            score = dataset[column_name_1].eq(dataset[column_name_2]).sum() / all_rows

            if score >= threshold:
                result += 1

    return result


def get_number_of_constant_columns(dataset: pd.DataFrame) -> int:
    """Calculate the number of constant columns in a dataset"""
    return len(dataset.columns[dataset.nunique() <= 1])  # type: ignore


def get_number_of_almost_constant_columns(dataset: pd.DataFrame, threshold: float) -> int:
    """Calculate the number of almost constant columns in a dataset"""
    result = 0
    dataset_row = dataset.shape[0]

    if dataset_row <= 0:
        return 0

    for column_name in dataset.columns:
        score = dataset[column_name].value_counts().max() / dataset.shape[0]

        if score >= threshold:
            result += 1

    return result
