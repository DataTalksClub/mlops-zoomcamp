from typing import TYPE_CHECKING
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

import numpy as np
import pandas as pd
from numpy import dtype
from pandas.core.dtypes.common import is_float_dtype
from pandas.core.dtypes.common import is_integer_dtype
from pandas.core.dtypes.common import is_object_dtype
from pandas.core.dtypes.common import is_string_dtype
from sklearn import metrics

from evidently.metric_results import Boxes
from evidently.metric_results import ConfusionMatrix
from evidently.metric_results import DatasetClassificationQuality
from evidently.metric_results import DatasetColumns
from evidently.metric_results import PredictionData
from evidently.metric_results import RatesPlotData
from evidently.pipeline.column_mapping import ColumnMapping

if TYPE_CHECKING:
    pass


def calculate_confusion_by_classes(
    confusion_matrix: np.ndarray, class_names: Sequence[Union[str, int]]
) -> Dict[Union[str, int], Dict[str, int]]:
    """Calculate metrics:
    - TP (true positive)
    - TN (true negative)
    - FP (false positive)
    - FN (false negative)
    for each class from confusion matrix.

    Returns:
        a dict like::

            {
                "class_1_name": {
                    "tp": 1,
                    "tn": 5,
                    "fp": 0,
                    "fn": 3,
                },
                "class_1_name": {
                    "tp": 1,
                    "tn": 5,
                    "fp": 0,
                    "fn": 3,
                },
            }
    """
    true_positive = np.diag(confusion_matrix)
    false_positive = confusion_matrix.sum(axis=0) - np.diag(confusion_matrix)
    false_negative = confusion_matrix.sum(axis=1) - np.diag(confusion_matrix)
    true_negative = confusion_matrix.sum() - (false_positive + false_negative + true_positive)
    confusion_by_classes = {}

    for idx, class_name in enumerate(class_names):
        confusion_by_classes[class_name] = {
            "tp": true_positive[idx],
            "tn": true_negative[idx],
            "fp": false_positive[idx],
            "fn": false_negative[idx],
        }

    return confusion_by_classes


def k_probability_threshold(
    prediction_probas: pd.DataFrame, k: Optional[int] = None, prob_threshold: Optional[float] = None
) -> float:
    probas = prediction_probas.iloc[:, 0].sort_values(ascending=False)
    if prob_threshold is not None:
        if prob_threshold < 0.0 or prob_threshold > 1.0:
            raise ValueError(f"prob_threshold should be in range [0.0, 1.0] but was {k}")
        return probas.iloc[max(int(np.ceil(prob_threshold * prediction_probas.shape[0])) - 1, 0)]
    if k is None:
        raise ValueError("Either k or prob_threshold should be not None")
    if k <= 0:
        raise ValueError("K should be > 0")
    return probas.iloc[min(k, prediction_probas.shape[0] - 1)]


def get_prediction_data(
    data: pd.DataFrame, data_columns: DatasetColumns, pos_label: Optional[Union[str, int]], threshold: float = 0.5
) -> PredictionData:
    """Get predicted values and optional prediction probabilities from source data.
    Also take into account a threshold value - if a probability is less than the value, do not take it into account.

    Return and object with predicted values and an optional prediction probabilities.
    """
    # binary or multiclass classification
    # for binary prediction_probas has column order [pos_label, neg_label]
    # for multiclass classification return just values and probas
    prediction = data_columns.utility_columns.prediction
    target = data_columns.utility_columns.target

    if isinstance(prediction, list) and len(prediction) > 2:
        # list of columns with prediction probas, should be same as target labels
        return PredictionData(
            predictions=data[prediction].idxmax(axis=1),
            prediction_probas=data[prediction],
            labels=prediction,
        )

    if isinstance(prediction, str) and not is_float_dtype(data[prediction]) and target is not None:
        # if prediction is not probas, get unique values from it and target
        labels = np.union1d(data[target].unique(), data[prediction].unique()).tolist()
        return PredictionData(
            predictions=data[prediction],
            prediction_probas=None,
            labels=labels,
        )

    elif isinstance(prediction, str) and not is_float_dtype(data[prediction]) and target is None:
        # if prediction is not probas, get unique values from it
        labels = data[prediction].unique().tolist()

    elif isinstance(prediction, str) and is_float_dtype(data[prediction]) and target is not None:
        # if prediction is probas, get unique values from target only
        labels = data[target].unique().tolist()

    elif isinstance(prediction, list):
        labels = prediction

    # binary classification
    # prediction in mapping is a list of two columns:
    # one is positive value probabilities, second is negative value probabilities
    if isinstance(prediction, list) and len(prediction) == 2:
        pos_label = _check_pos_labels(pos_label, labels)
        labels = pd.Series(labels)

        # get negative label for binary classification
        neg_label = labels[labels != pos_label].iloc[0]

        predictions = threshold_probability_labels(data[prediction], pos_label, neg_label, threshold)
        return PredictionData(
            predictions=predictions,
            prediction_probas=data[[pos_label, neg_label]],
            labels=[pos_label, neg_label],
        )

    # binary classification
    # target is strings or other values, prediction is a string with positive label name, one column with probabilities
    if (
        isinstance(prediction, str)
        and target is not None
        and (is_string_dtype(data[target]) or is_object_dtype(data[target]))
        and is_float_dtype(data[prediction])
    ):
        pos_label = _check_pos_labels(pos_label, labels)
        if prediction not in labels:
            raise ValueError(
                "No prediction for the target labels were found. "
                "Consider to rename columns with the prediction to match target labels."
            )

        # get negative label for binary classification
        labels = pd.Series(labels)
        neg_label = labels[labels != pos_label].iloc[0]
        if pos_label == prediction:
            pos_preds = data[prediction]

        else:
            pos_preds = data[prediction].apply(lambda x: 1.0 - x)

        prediction_probas = pd.DataFrame.from_dict(
            {
                pos_label: pos_preds,
                neg_label: pos_preds.apply(lambda x: 1.0 - x),
            }
        )
        predictions = threshold_probability_labels(prediction_probas, pos_label, neg_label, threshold)
        return PredictionData(
            predictions=predictions,
            prediction_probas=prediction_probas,
            labels=[pos_label, neg_label],
        )

    # binary target and preds are numbers and prediction is a label
    if not isinstance(prediction, list) and prediction in [0, 1, "0", "1"] and pos_label == 0:
        if prediction in [0, "0"]:
            pos_preds = data[prediction]
        else:
            pos_preds = data[prediction].apply(lambda x: 1.0 - x)
        predictions = pos_preds.apply(lambda x: 0 if x >= threshold else 1)
        prediction_probas = pd.DataFrame.from_dict(
            {
                0: pos_preds,
                1: pos_preds.apply(lambda x: 1.0 - x),
            }
        )
        return PredictionData(
            predictions=predictions,
            prediction_probas=prediction_probas,
            labels=[0, 1],
        )

    # binary target and preds are numbers
    elif (
        isinstance(prediction, str)
        and target is not None
        and is_integer_dtype(data[target].dtype)
        and is_float_dtype(data[prediction])
    ):
        predictions = (data[prediction] >= threshold).astype(dtype("int64"))
        prediction_probas = pd.DataFrame.from_dict(
            {
                1: data[prediction],
                0: data[prediction].apply(lambda x: 1.0 - x),
            }
        )
        return PredictionData(
            predictions=predictions,
            prediction_probas=prediction_probas,
            labels=[1, 0],
        )

    # for other cases return just prediction values, probabilities are None by default
    return PredictionData(
        predictions=data[prediction],
        prediction_probas=None,
        labels=data[prediction].unique().tolist(),
    )


def _check_pos_labels(pos_label: Optional[Union[str, int]], labels: List[str]) -> Union[str, int]:
    if pos_label is None:
        raise ValueError("Undefined pos_label.")

    if pos_label not in labels:
        raise ValueError(f"Cannot find pos_label '{pos_label}' in labels {labels}")

    return pos_label


def threshold_probability_labels(
    prediction_probas: pd.DataFrame, pos_label: Union[str, int], neg_label: Union[str, int], threshold: float
) -> pd.Series:
    """Get prediction values by probabilities with the threshold apply"""
    return prediction_probas[pos_label].apply(lambda x: pos_label if x >= threshold else neg_label)


STEP_SIZE = 0.05


def calculate_pr_table(binded):
    result = []
    binded.sort(key=lambda item: item[1], reverse=True)
    data_size = len(binded)
    target_class_size = sum([x[0] for x in binded])
    offset = max(round(data_size * STEP_SIZE), 1)

    for step in np.arange(offset, data_size + offset, offset):
        count = min(step, data_size)
        prob = round(binded[min(step, data_size - 1)][1], 2)
        top = round(100.0 * min(step, data_size) / data_size, 1)
        tp = sum([x[0] for x in binded[: min(step, data_size)]])
        fp = count - tp
        precision = round(100.0 * tp / count, 1)
        recall = round(100.0 * tp / target_class_size, 1)
        result.append([top, int(count), prob, int(tp), int(fp), precision, recall])
    return result


def calculate_lift_table(binded):
    result = []
    binded.sort(key=lambda item: item[1], reverse=True)
    data_size = len(binded)
    target_class_size = sum([x[0] for x in binded])
    # we don't use declared STEP_SIZE due to specifics
    # of lift metric calculation and visualization
    offset = int(max(np.floor(data_size * 0.01), 1))

    for step in np.arange(offset, data_size + 1, offset):
        count = min(step, data_size)
        prob = round(binded[min(step, data_size - 1)][1], 2)
        top = round(100.0 * min(step, data_size) / data_size)
        tp = sum([x[0] for x in binded[: min(step, data_size)]])
        fp = count - tp
        precision = round(100.0 * tp / count, 1)
        recall = round(100.0 * tp / target_class_size, 1)
        f1_score = round(2 / (1 / precision + 1 / recall), 1)
        lift = round(recall / top, 2)
        if count <= target_class_size:
            max_lift = round(100.0 * count / target_class_size / top, 2)
        else:
            max_lift = round(100.0 / top, 2)
        relative_lift = round(lift / max_lift, 2)
        percent = round(100 * target_class_size / data_size, 2)
        result.append(
            [
                top,
                int(count),
                prob,
                int(tp),
                int(fp),
                precision,
                recall,
                f1_score,
                lift,
                max_lift,
                relative_lift,
                percent,
            ]
        )
    return result


def calculate_matrix(target: pd.Series, prediction: pd.Series, labels: List[Union[str, int]]) -> ConfusionMatrix:
    sorted_labels = sorted(labels)
    matrix = metrics.confusion_matrix(target, prediction, labels=sorted_labels)
    return ConfusionMatrix(labels=sorted_labels, values=[row.tolist() for row in matrix])


def collect_plot_data(prediction_probas: pd.DataFrame) -> Boxes:
    res = {}
    mins = []
    lowers = []
    means = []
    uppers = []
    maxs = []
    for col in prediction_probas.columns:
        mins.append(np.percentile(prediction_probas[col], 0))
        lowers.append(np.percentile(prediction_probas[col], 25))
        means.append(np.percentile(prediction_probas[col], 50))
        uppers.append(np.percentile(prediction_probas[col], 75))
        maxs.append(np.percentile(prediction_probas[col], 100))
    res["mins"] = mins
    res["lowers"] = lowers
    res["means"] = means
    res["uppers"] = uppers
    res["maxs"] = maxs
    return Boxes(mins=mins, lowers=lowers, means=means, uppers=uppers, maxs=maxs)


def calculate_metrics(
    column_mapping: ColumnMapping,
    confusion_matrix: ConfusionMatrix,
    target: pd.Series,
    prediction: PredictionData,
) -> "DatasetClassificationQuality":
    if column_mapping.pos_label is not None:
        pos_label = column_mapping.pos_label
    else:
        pos_label = 1
    tpr = None
    tnr = None
    fpr = None
    fnr = None
    roc_auc = None
    log_loss = None
    rate_plots_data: Optional[RatesPlotData] = None
    plot_data = None
    if len(prediction.labels) == 2:
        confusion_by_classes = calculate_confusion_by_classes(
            np.array(confusion_matrix.values),
            confusion_matrix.labels,
        )
        conf_by_pos_label = confusion_by_classes[pos_label]
        precision = metrics.precision_score(target, prediction.predictions, pos_label=pos_label)
        recall = metrics.recall_score(target, prediction.predictions, pos_label=pos_label)
        f1 = metrics.f1_score(target, prediction.predictions, pos_label=pos_label)
        tpr = conf_by_pos_label["tp"] / (conf_by_pos_label["tp"] + conf_by_pos_label["fn"])
        tnr = conf_by_pos_label["tn"] / (conf_by_pos_label["tn"] + conf_by_pos_label["fp"])
        fpr = conf_by_pos_label["fp"] / (conf_by_pos_label["fp"] + conf_by_pos_label["tn"])
        fnr = conf_by_pos_label["fn"] / (conf_by_pos_label["fn"] + conf_by_pos_label["tp"])
    else:
        precision = metrics.precision_score(target, prediction.predictions, average="macro")
        recall = metrics.recall_score(target, prediction.predictions, average="macro")
        f1 = metrics.f1_score(target, prediction.predictions, average="macro")
    if prediction.prediction_probas is not None:
        binaraized_target = (
            target.astype(str).values.reshape(-1, 1) == list(prediction.prediction_probas.columns.astype(str))
        ).astype(int)
        prediction_probas_array = prediction.prediction_probas.to_numpy()
        roc_auc = metrics.roc_auc_score(binaraized_target, prediction_probas_array, average="macro")
        log_loss = metrics.log_loss(binaraized_target, prediction_probas_array)
        plot_data = collect_plot_data(prediction.prediction_probas)
    if len(prediction.labels) == 2 and prediction.prediction_probas is not None:
        fprs, tprs, thrs = metrics.roc_curve(target == pos_label, prediction.prediction_probas[pos_label])
        tnrs = 1 - fprs
        fnrs = 1 - tprs
        rate_plots_data = RatesPlotData(
            thrs=thrs.tolist(), tpr=tprs.tolist(), fpr=fprs.tolist(), fnr=fnrs.tolist(), tnr=tnrs.tolist()
        )

    return DatasetClassificationQuality(
        accuracy=metrics.accuracy_score(target, prediction.predictions),
        precision=precision,
        recall=recall,
        f1=f1,
        tpr=tpr,
        tnr=tnr,
        fpr=fpr,
        fnr=fnr,
        roc_auc=roc_auc,
        log_loss=log_loss,
        rate_plots_data=rate_plots_data,
        plot_data=plot_data,
    )
