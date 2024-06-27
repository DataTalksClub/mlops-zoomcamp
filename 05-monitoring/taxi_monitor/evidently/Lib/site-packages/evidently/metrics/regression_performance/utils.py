from evidently.metrics.regression_performance.objects import IntervalSeries
from evidently.metrics.regression_performance.objects import RegressionMetricScatter


def apply_func_to_binned_data(
    df_for_bins, func, target_column, preds_column, is_ref_data=False
) -> RegressionMetricScatter:
    def _apply(x):
        if x.shape[0] == 0:
            return None
        return func(x[target_column], x[preds_column])

    reference = None
    if is_ref_data:
        reference = IntervalSeries.from_data(
            df_for_bins[df_for_bins.data == "ref"].groupby("target_binned", observed=False).apply(_apply)
        )

    result = RegressionMetricScatter(
        current=IntervalSeries.from_data(
            df_for_bins[df_for_bins.data == "curr"].groupby("target_binned", observed=False).apply(_apply)
        ),
        reference=reference,
    )

    return result
