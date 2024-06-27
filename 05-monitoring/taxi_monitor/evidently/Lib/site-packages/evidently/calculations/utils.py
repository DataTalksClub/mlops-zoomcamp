from typing import Dict
from typing import Optional
from typing import Tuple

import numpy as np
import pandas as pd

from evidently.utils.visualizations import choose_agg_period
from evidently.utils.visualizations import get_gaussian_kde
from evidently.utils.visualizations import is_possible_contour

MAX_CATEGORIES = 5


def make_hist_df(hist: Tuple[np.ndarray, np.ndarray]) -> pd.DataFrame:
    hist_df = pd.DataFrame(
        np.array(
            [
                hist[1][:-1],
                hist[0],
                [f"{x[0]}-{x[1]}" for x in zip(hist[1][:-1], hist[1][1:])],
            ]
        ).T,
        columns=["x", "count", "range"],
    )

    hist_df["x"] = hist_df["x"].astype(float)
    hist_df["count"] = hist_df["count"].astype(int)
    return hist_df


def make_hist_for_num_plot(curr: pd.Series, ref: pd.Series = None):
    result = {}
    if ref is not None:
        ref = ref.dropna()
    bins = np.histogram_bin_edges(pd.concat([curr.dropna(), ref]), bins="doane")
    curr_hist = np.histogram(curr, bins=bins)
    result["current"] = make_hist_df(curr_hist)
    if ref is not None:
        ref_hist = np.histogram(ref, bins=bins)
        result["reference"] = make_hist_df(ref_hist)
    return result


def make_hist_for_cat_plot(curr: pd.Series, ref: pd.Series = None, normalize: bool = False, dropna=False):
    result = {}
    hist_df = curr.astype(str).value_counts(normalize=normalize, dropna=dropna).reset_index()
    hist_df.columns = ["x", "count"]
    result["current"] = hist_df
    if ref is not None:
        hist_df = ref.astype(str).value_counts(normalize=normalize, dropna=dropna).reset_index()
        hist_df.columns = ["x", "count"]
        result["reference"] = hist_df
    return result


def get_count_values(col1: pd.Series, col2: pd.Series, col1_name: str, col2_name: str):
    df = pd.DataFrame({col2_name: col2, col1_name: col1})
    df = df.groupby([col2_name, col1_name], observed=False).size()
    df.name = "count_objects"
    df = df.reset_index()
    return df[df["count_objects"] > 0]


def get_data_for_cat_cat_plot(
    col1_name: str,
    col2_name: str,
    col1_curr: pd.Series,
    col2_curr: pd.Series,
    col1_ref: Optional[pd.Series],
    col2_ref: Optional[pd.Series],
):
    result = {}
    result["current"] = get_count_values(col2_curr, col1_curr, col2_name, col1_name)
    if col1_ref is not None and col2_ref is not None:
        result["reference"] = get_count_values(col2_ref, col1_ref, col2_name, col1_name)
    return result


def get_data_for_num_num_plot(
    agg_data: bool,
    col1_name: str,
    col2_name: str,
    col1_curr: pd.Series,
    col2_curr: pd.Series,
    col1_ref: Optional[pd.Series],
    col2_ref: Optional[pd.Series],
):
    if (
        not agg_data
        or not is_possible_contour(col2_curr, col1_curr)
        or (col1_ref is not None and col2_ref is not None and not is_possible_contour(col2_ref, col1_ref))
    ):
        result = {
            "current": {
                col1_name: col1_curr.tolist(),
                col2_name: col2_curr.tolist(),
            }
        }
        if col1_ref is not None and col2_ref is not None:
            result["reference"] = {
                col1_name: col1_ref.tolist(),
                col2_name: col2_ref.tolist(),
            }
        return result, None

    result = {"current": get_gaussian_kde(col2_curr, col1_curr)}
    if col1_ref is not None and col2_ref is not None:
        result["reference"] = get_gaussian_kde(col2_ref, col1_ref)
    return None, result


def prepare_box_data(
    curr: pd.DataFrame,
    ref: Optional[pd.DataFrame],
    cat_feature_name: str,
    num_feature_name: str,
) -> Dict[str, Dict[str, list]]:
    dfs = [curr]
    names = ["current"]
    if ref is not None:
        dfs.append(ref)
        names.append("reference")
    res = {}
    for df, name in zip(dfs, names):
        data = df.groupby(cat_feature_name, observed=False)[num_feature_name]
        df_for_plot = data.quantile([0, 0.25, 0.5, 0.75, 1]).reset_index()
        df_for_plot.columns = [cat_feature_name, "q", num_feature_name]
        res_df = {}
        values = df_for_plot[cat_feature_name].unique()

        def _quantiles(qdf, value):
            return qdf[df_for_plot.q == value].set_index(cat_feature_name).loc[values, num_feature_name].tolist()

        res_df["mins"] = _quantiles(df_for_plot, 0)
        res_df["lowers"] = _quantiles(df_for_plot, 0.25)
        res_df["means"] = _quantiles(df_for_plot, 0.5)
        res_df["uppers"] = _quantiles(df_for_plot, 0.75)
        res_df["maxs"] = _quantiles(df_for_plot, 1)
        res_df["values"] = values
        res[name] = res_df

    return res


def transform_df_to_time_mean_view(
    period_data: pd.Series,
    datetime_column_name: str,
    datetime_data: pd.Series,
    data_column_name: str,
    column_data: pd.Series,
):
    df = pd.DataFrame({"period": period_data, data_column_name: column_data, datetime_column_name: datetime_data})
    df = df.groupby("period")[data_column_name].mean().reset_index()
    df[datetime_column_name] = df["period"].dt.to_timestamp()
    return df


def prepare_data_for_date_num(date_curr, date_ref, datetime_name, num_name, num_curr, num_ref):
    prefix, freq = choose_agg_period(date_curr, date_ref)
    current_period_data = date_curr.dt.to_period(freq=freq)
    df_for_time_plot_ref = None
    reference_period_data = None
    if date_ref is not None:
        reference_period_data = date_ref.dt.to_period(freq=freq)
    df_for_time_plot_curr = transform_df_to_time_mean_view(
        current_period_data,
        datetime_name,
        date_curr,
        num_name,
        num_curr,
    )
    if reference_period_data is not None:
        df_for_time_plot_ref = transform_df_to_time_mean_view(
            reference_period_data,
            datetime_name,
            date_ref,
            num_name,
            num_ref,
        )
    return df_for_time_plot_curr, df_for_time_plot_ref, prefix


def relabel_data(
    current_data: pd.Series,
    reference_data: Optional[pd.Series],
    max_categories: Optional[int] = MAX_CATEGORIES,
) -> Tuple[pd.Series, Optional[pd.Series]]:
    if max_categories is None:
        return current_data.copy(), reference_data.copy() if reference_data is not None else None

    current_data_str = current_data.astype(str)
    reference_data_str = None
    if reference_data is not None:
        reference_data_str = reference_data.astype(str)
        unique_values = len(
            np.union1d(
                current_data_str.unique(),
                reference_data_str.unique(),
            )
        )
    else:
        unique_values = current_data_str.nunique()

    if unique_values > max_categories:
        curr_cats = current_data_str.value_counts(normalize=True)

        if reference_data_str is not None:
            ref_cats = reference_data_str.value_counts(normalize=True)
            categories = pd.concat([curr_cats, ref_cats])

        else:
            categories = curr_cats

        cats = categories.sort_values(ascending=False).index.drop_duplicates(keep="first")[:max_categories].values

        result_current = current_data.apply(lambda x: x if str(x) in cats else "other")
        result_reference = None
        if reference_data is not None:
            result_reference = reference_data.apply(lambda x: x if str(x) in cats else "other")
        return result_current, result_reference
    else:
        return current_data.copy(), reference_data.copy() if reference_data is not None else None


def transform_df_to_time_count_view(
    period_data: pd.Series,
    datetime_column_name: str,
    datetime_data: pd.Series,
    data_column_name: str,
    column_data: pd.Series,
):
    df = pd.DataFrame({"period": period_data, datetime_column_name: datetime_data, data_column_name: column_data})
    df = df.groupby(["period", data_column_name]).size()
    df.name = "num"
    df = df.reset_index()
    df[datetime_column_name] = df["period"].dt.to_timestamp()
    return df[df["num"] > 0]


def prepare_data_for_date_cat(date_curr, date_ref, datetime_name, cat_name, cat_curr, cat_ref):
    prefix, freq = choose_agg_period(date_curr, date_ref)
    current_period_data = date_curr.dt.to_period(freq=freq)
    df_for_time_plot_ref = None
    reference_period_data = None
    if date_ref is not None:
        reference_period_data = date_ref.dt.to_period(freq=freq)
    df_for_time_plot_curr = transform_df_to_time_count_view(
        current_period_data,
        datetime_name,
        date_curr,
        cat_name,
        cat_curr,
    )
    if reference_period_data is not None:
        df_for_time_plot_ref = transform_df_to_time_count_view(
            reference_period_data,
            datetime_name,
            date_ref,
            cat_name,
            cat_ref,
        )
    return df_for_time_plot_curr, df_for_time_plot_ref, prefix
