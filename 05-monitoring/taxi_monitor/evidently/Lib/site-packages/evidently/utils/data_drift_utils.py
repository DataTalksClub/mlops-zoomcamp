from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from evidently.calculations.stattests import PossibleStatTestType


def resolve_stattest_threshold(
    feature_name: str,
    feature_type: str,
    stattest: Optional[PossibleStatTestType],
    cat_stattest: Optional[PossibleStatTestType],
    num_stattest: Optional[PossibleStatTestType],
    text_stattest: Optional[PossibleStatTestType],
    per_column_stattest: Optional[Dict[str, PossibleStatTestType]],
    stattest_threshold: Optional[float],
    cat_stattest_threshold: Optional[float],
    num_stattest_threshold: Optional[float],
    text_stattest_threshold: Optional[float],
    per_column_stattest_threshold: Optional[Dict[str, float]],
) -> Tuple[Optional[PossibleStatTestType], Optional[float]]:
    return (
        _calculate_stattest(
            feature_name,
            feature_type,
            stattest,
            cat_stattest,
            num_stattest,
            text_stattest,
            per_column_stattest,
        ),
        _calculate_threshold(
            feature_name,
            feature_type,
            stattest_threshold,
            cat_stattest_threshold,
            num_stattest_threshold,
            text_stattest_threshold,
            per_column_stattest_threshold,
        ),
    )


def _calculate_stattest(
    feature_name: str,
    feature_type: str,
    stattest: Optional[PossibleStatTestType] = None,
    cat_stattest: Optional[PossibleStatTestType] = None,
    num_stattest: Optional[PossibleStatTestType] = None,
    text_stattest: Optional[PossibleStatTestType] = None,
    per_column_stattest: Optional[Dict[str, PossibleStatTestType]] = None,
) -> Optional[PossibleStatTestType]:
    func = None if stattest is None else stattest
    if feature_type == "cat":
        type_func = cat_stattest
    elif feature_type == "num":
        type_func = num_stattest
    elif feature_type == "text":
        type_func = text_stattest
    else:
        raise ValueError(f"Unexpected feature type {feature_type}.")
    func = func if type_func is None else type_func
    if per_column_stattest is None:
        return func
    return per_column_stattest.get(feature_name, func)


def _calculate_threshold(
    feature_name: str,
    feature_type: str,
    stattest_threshold: Optional[float] = None,
    cat_stattest_threshold: Optional[float] = None,
    num_stattest_threshold: Optional[float] = None,
    text_stattest_threshold: Optional[float] = None,
    per_column_stattest_threshold: Optional[Dict[str, float]] = None,
) -> Optional[float]:
    if per_column_stattest_threshold is not None and feature_name in per_column_stattest_threshold.keys():
        return per_column_stattest_threshold.get(feature_name)

    if cat_stattest_threshold is not None and feature_type == "cat":
        return cat_stattest_threshold

    if num_stattest_threshold is not None and feature_type == "num":
        return num_stattest_threshold

    if text_stattest_threshold is not None and feature_type == "text":
        return text_stattest_threshold

    if stattest_threshold is not None:
        return stattest_threshold
    return None


def roc_auc_domain_classifier(X_train, X_test, y_train, y_test) -> Tuple:
    pipeline = Pipeline(
        [
            ("vectorization", TfidfVectorizer(sublinear_tf=True, max_df=0.5, stop_words="english")),
            (
                "classification",
                SGDClassifier(alpha=0.0001, max_iter=50, penalty="l1", loss="modified_huber", random_state=42),
            ),
        ]
    )

    pipeline.fit(X_train, y_train)
    y_pred_proba = pipeline.predict_proba(X_test)[:, 1]
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    return roc_auc, y_pred_proba, pipeline


def roc_auc_random_classifier_percentile(y_test: np.ndarray, p_value=0.05, iter_num=1000, seed=42) -> float:
    def calc_roc_auc_random(y_test, seed=None):
        np.random.seed(seed)
        y_random_pred = np.random.rand(len(y_test))
        roc_auc_random = roc_auc_score(y_test, y_random_pred)
        return roc_auc_random

    np.random.seed(seed)
    seeds = np.random.randint(0, iter_num * 10, size=iter_num)
    roc_auc_values = [calc_roc_auc_random(y_test, seed=seed) for seed in seeds]
    return np.percentile(roc_auc_values, 100 * (1 - p_value))


def calculate_text_drift_score(
    reference_data: pd.Series,
    current_data: pd.Series,
    bootstrap: bool,
    p_value=0.05,
    threshold=0.55,
) -> Tuple[float, bool]:
    domain_data = pd.concat(
        [
            pd.DataFrame({"text": reference_data, "target": 0}),
            pd.DataFrame({"text": current_data, "target": 1}),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        domain_data["text"],
        domain_data["target"],
        test_size=0.5,
        random_state=42,
        shuffle=True,
    )

    domain_classifier_roc_auc, _, _ = roc_auc_domain_classifier(
        X_train,
        X_test,
        y_train,
        y_test,
    )
    if not bootstrap:
        return domain_classifier_roc_auc, domain_classifier_roc_auc > threshold
    random_classifier_percentile = roc_auc_random_classifier_percentile(y_test, p_value=p_value)
    return domain_classifier_roc_auc, domain_classifier_roc_auc > random_classifier_percentile


def get_typical_examples(X_test, y_test, y_pred_proba, examples_num=10) -> Tuple[List[str], List[str]]:
    typical_examples = pd.DataFrame({"text": X_test, "label": y_test, "predict_proba": y_pred_proba})

    typical_current = typical_examples[typical_examples["label"] == 1]
    typical_current.sort_values("predict_proba", ascending=False, inplace=True)
    typical_current = typical_current.head(examples_num)

    typical_reference = typical_examples[typical_examples["label"] == 0]
    typical_reference.sort_values("predict_proba", ascending=True, inplace=True)
    typical_reference = typical_reference.head(examples_num)
    return list(typical_current["text"]), list(typical_reference["text"])


def get_typical_words(pipeline, words_num=25) -> Tuple[List[str], List[str]]:
    weights_df = pd.DataFrame({"weight": pipeline["classification"].coef_[0]})
    weights_df.reset_index(inplace=True)
    weights_df.rename(columns={"index": "feature_ind"}, inplace=True)
    weights_df = weights_df[weights_df["weight"] != 0]

    # build inverted index for vocabulary
    inverted_vocabulary = {value: key for key, value in pipeline["vectorization"].vocabulary_.items()}
    words_typical_current = weights_df[weights_df["weight"] > 0]
    words_typical_current.sort_values("weight", ascending=False, inplace=True)
    words_typical_current = words_typical_current.head(words_num)
    words_typical_current["word"] = words_typical_current["feature_ind"].apply(lambda x: inverted_vocabulary[x])

    words_typical_reference = weights_df[weights_df["weight"] < 0]
    words_typical_reference.sort_values("weight", ascending=True, inplace=True)
    words_typical_reference = words_typical_reference.head(words_num)
    words_typical_reference["word"] = words_typical_reference["feature_ind"].apply(lambda x: inverted_vocabulary[x])

    return list(words_typical_current["word"]), list(words_typical_reference["word"])


def get_text_data_for_plots(reference_data: pd.Series, current_data: pd.Series):
    domain_data = pd.concat(
        [
            pd.DataFrame({"text": reference_data, "target": 0}),
            pd.DataFrame({"text": current_data, "target": 1}),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        domain_data["text"],
        domain_data["target"],
        test_size=0.5,
        random_state=42,
        shuffle=True,
    )

    _, y_pred_proba, classifier_pipeline = roc_auc_domain_classifier(
        X_train,
        X_test,
        y_train,
        y_test,
    )
    # get examples more characteristic of current or reference dataset
    typical_examples_cur, typical_examples_ref = get_typical_examples(X_test, y_test, y_pred_proba)

    # get words more characteristic of current or reference dataset
    typical_words_cur, typical_words_ref = get_typical_words(classifier_pipeline)

    return typical_examples_cur, typical_examples_ref, typical_words_cur, typical_words_ref


def add_emb_drift_to_reports(
    result,
    embeddings_data,
    embeddings,
    embeddings_drift_method,
    entity,
):
    sets = list(embeddings_data.keys())
    if embeddings is not None:
        sets = np.intersect1d(sets, embeddings)
    if len(sets) == 0:
        return result
    f: Optional[Callable]
    for emb_set in sets:
        if embeddings_drift_method is not None:
            f = embeddings_drift_method.get(emb_set)
        else:
            f = None
        result.append(entity(embeddings_name=emb_set, drift_method=f))
    return result
