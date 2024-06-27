import numpy as np
from pyspark.sql import functions as sf

from evidently.core import ColumnType
from evidently.spark.base import SparkSeries
from evidently.spark.calculations.histogram import get_histogram
from evidently.spark.calculations.histogram import hist_bin_doane


def get_binned_data(
    reference_data: SparkSeries,
    current_data: SparkSeries,
    column_name: str,
    feature_type: ColumnType,
    fill_zeroes: bool = True,
):
    """Split variable into n buckets based on reference quantiles
    Args:
        reference_data: reference data
        current_data: current data
        feature_type: feature type
        n: number of quantiles
    Returns:
        reference_percents: % of records in each bucket for reference
        current_percents: % of records in each bucket for current
    """
    # n_vals = reference_data.distinct().count()

    if feature_type == ColumnType.Numerical:  # and n_vals > 20:
        bins, dmax, dmin = hist_bin_doane(
            current_data.dropna(subset=[column_name]).union(reference_data.dropna(subset=[column_name])), column_name
        )
        reference_percents = (
            get_histogram(reference_data, column_name=column_name, nbinsx=bins, density=False, dmax=dmax, dmin=dmin)[0]
            / reference_data.count()
        )
        current_percents = (
            get_histogram(current_data, column_name=column_name, nbinsx=bins, density=False, dmax=dmax, dmin=dmin)[0]
            / current_data.count()
        )

    else:
        ref_stats = reference_data.groupby(column_name).agg(sf.count(column_name).alias("ref"))
        cur_stats = current_data.groupby(column_name).agg(sf.count(column_name).alias("cur"))
        stats = ref_stats.join(cur_stats, on=column_name, how="fullouter").collect()

        reference_percents = np.array([r["ref"] or 0 for r in stats])
        reference_percents = reference_percents / reference_percents.sum()
        current_percents = np.array([r["cur"] or 0 for r in stats])
        current_percents = current_percents / current_percents.sum()

    if fill_zeroes:
        np.place(
            reference_percents,
            reference_percents == 0,
            min(reference_percents[reference_percents != 0]) / 10**6
            if min(reference_percents[reference_percents != 0]) <= 0.0001
            else 0.0001,
        )
        np.place(
            current_percents,
            current_percents == 0,
            min(current_percents[current_percents != 0]) / 10**6
            if min(current_percents[current_percents != 0]) <= 0.0001
            else 0.0001,
        )

    return reference_percents, current_percents
