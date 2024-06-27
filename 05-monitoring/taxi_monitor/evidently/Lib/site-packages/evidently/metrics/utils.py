import pandas as pd


def make_target_bins_for_reg_plots(
    curr: pd.DataFrame, target_column, preds_column, ref: pd.DataFrame = None
) -> pd.DataFrame:
    df_for_bins = pd.DataFrame(
        {
            "data": "curr",
            target_column: curr[target_column],
            preds_column: curr[preds_column],
        }
    )
    if ref is not None:
        df_for_bins = pd.concat(
            [
                df_for_bins,
                pd.DataFrame(
                    {
                        "data": "ref",
                        target_column: ref[target_column],
                        preds_column: ref[preds_column],
                    }
                ),
            ]
        )
    df_for_bins["target_binned"] = pd.cut(df_for_bins[target_column], min(df_for_bins[target_column].nunique(), 10))
    return df_for_bins
