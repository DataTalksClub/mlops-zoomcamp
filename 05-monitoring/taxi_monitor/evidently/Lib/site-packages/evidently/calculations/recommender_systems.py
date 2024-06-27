from typing import Optional

import pandas as pd

from evidently.base_metric import InputData
from evidently.pipeline.column_mapping import RecomType


def collect_dataset(
    users: pd.Series,
    target: pd.Series,
    preds: pd.Series,
    recommendations_type: RecomType,
    min_rel_score: Optional[int],
    no_feedback_users: bool,
    bin_data: bool,
):
    df = pd.concat([users, target, preds], axis=1)
    df.columns = ["users", "target", "preds"]
    if min_rel_score:
        df["target"] = (df["target"] >= min_rel_score).astype(int)
    if recommendations_type == RecomType.SCORE:
        df["preds"] = df.groupby("users")["preds"].transform("rank", ascending=False).astype(int)
    if bin_data:
        df["target"] = (df["target"] > 0).astype(int)
    if not no_feedback_users:
        users_with_clicks = df[df.target > 0].users.unique()
        df = df[df.users.isin(users_with_clicks)]

    return df


def get_curr_and_ref_df(
    data: InputData, min_rel_score: Optional[int] = None, no_feedback_users: bool = False, bin_data: bool = True
):
    target_column = data.data_definition.get_target_column()
    prediction = data.data_definition.get_prediction_columns()
    if target_column is None or prediction is None:
        raise ValueError("Target and prediction were not found in data.")
    _, target_current, target_reference = data.get_data(target_column.column_name)
    recommendations_type = data.column_mapping.recom_type or RecomType.SCORE
    if prediction.prediction_probas is not None:
        pred_name = prediction.prediction_probas[0].column_name
    elif prediction.predicted_values is not None:
        pred_name = prediction.predicted_values.column_name
    _, prediction_current, prediction_reference = data.get_data(pred_name)
    user_column = data.column_mapping.user_id
    if user_column is None:
        raise ValueError("User_id was not found in data.")
    _, user_current, user_reference = data.get_data(user_column)
    curr = collect_dataset(
        user_current,
        target_current,
        prediction_current,
        recommendations_type,
        min_rel_score,
        no_feedback_users,
        bin_data,
    )

    ref: Optional[pd.DataFrame] = None
    if user_reference is not None and target_reference is not None and prediction_reference is not None:
        ref = collect_dataset(
            user_reference,
            target_reference,
            prediction_reference,
            recommendations_type,
            min_rel_score,
            no_feedback_users,
            bin_data,
        )

    return curr, ref


def get_prediciton_name(data: InputData):
    if isinstance(data.column_mapping.prediction, str):
        return data.column_mapping.prediction
    if "prediction" in data.current_data.columns and (
        (data.reference_data is not None and "prediction" in data.reference_data.columns)
        or (data.reference_data is None)
    ):
        return "prediction"
    raise ValueError("Prediction should be presented and must be one column")


def get_stats_novelty(train_data: pd.DataFrame, item_id: str, user_id: str):
    user_interacted = train_data.groupby(item_id)[user_id].nunique()
    interactions = user_interacted / user_interacted.shape[0]
    return interactions
