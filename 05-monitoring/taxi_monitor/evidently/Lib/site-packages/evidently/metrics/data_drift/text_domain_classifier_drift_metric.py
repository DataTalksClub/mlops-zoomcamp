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

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.core import IncludeTags
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import CounterData
from evidently.renderers.html_widgets import TabData
from evidently.renderers.html_widgets import counter
from evidently.renderers.html_widgets import table_data
from evidently.renderers.html_widgets import widget_tabs


class TextDomainField(MetricResult):
    characteristic_examples: Optional[List[str]]
    characteristic_words: Optional[List[str]]


class TextDomainClassifierDriftResult(MetricResult):
    class Config:
        field_tags = {
            "current": {IncludeTags.Current, IncludeTags.Extra},
            "reference": {IncludeTags.Reference, IncludeTags.Extra},
            "text_column_name": {IncludeTags.Parameter},
        }

    text_column_name: str
    domain_classifier_roc_auc: float
    random_classifier_95_percentile: float
    content_drift: bool
    current: TextDomainField
    reference: TextDomainField


class TextDomainClassifierDriftMetric(Metric[TextDomainClassifierDriftResult]):
    text_column_name: str

    def __init__(self, text_column_name: str, options: AnyOptions = None) -> None:
        self.text_column_name = text_column_name
        super().__init__(options=options)

    @staticmethod
    def roc_auc_domain_classifier(X_train, X_test, y_train, y_test) -> Tuple:
        pipeline = Pipeline(
            [
                (
                    "vectorization",
                    TfidfVectorizer(sublinear_tf=True, max_df=0.5, stop_words="english"),
                ),
                (
                    "classification",
                    SGDClassifier(alpha=0.0001, max_iter=50, penalty="l1", loss="modified_huber"),
                ),
            ]
        )

        pipeline.fit(X_train, y_train)
        y_pred_proba = pipeline.predict_proba(X_test)[:, 1]
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        return roc_auc, y_pred_proba, pipeline

    @staticmethod
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

    @staticmethod
    def is_drift_detected(roc_auc_classifier_value: float, roc_auc_random_percentile: float) -> bool:
        if roc_auc_classifier_value > roc_auc_random_percentile:
            return True
        else:
            return False

    @staticmethod
    def get_typical_examples(X_test, y_test, y_pred_proba, examples_num=10) -> Tuple[List[str], List[str]]:
        typical_examples = pd.DataFrame({"text": X_test, "label": y_test, "predict_proba": y_pred_proba})

        typical_current = typical_examples[typical_examples["label"] == 1]
        typical_current.sort_values("predict_proba", ascending=False, inplace=True)
        typical_current = typical_current.head(examples_num)

        typical_reference = typical_examples[typical_examples["label"] == 0]
        typical_reference.sort_values("predict_proba", ascending=True, inplace=True)
        typical_reference = typical_reference.head(examples_num)
        return list(typical_current["text"]), list(typical_reference["text"])

    @staticmethod
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

    def calculate(self, data: InputData) -> TextDomainClassifierDriftResult:
        # create datasets for domain classifier training and testing
        ref_data = pd.Series() if data.reference_data is None else data.reference_data[self.text_column_name]
        domain_data = pd.concat(
            [
                pd.DataFrame({"text": ref_data, "target": 0}),
                pd.DataFrame({"text": data.current_data[self.text_column_name], "target": 1}),
            ]
        )

        X_train, X_test, y_train, y_test = train_test_split(
            domain_data["text"],
            domain_data["target"],
            test_size=0.5,
            random_state=42,
            shuffle=True,
        )
        # calculate domain classifier roc-auc score
        (
            domain_classifier_roc_auc,
            y_pred_proba,
            classifier_pipeline,
        ) = self.roc_auc_domain_classifier(
            X_train,
            X_test,
            y_train,
            y_test,
        )

        # calculate roc-auc scores 95 percentile if labels were assigned randomly
        random_classifier_95_percentile = self.roc_auc_random_classifier_percentile(y_test)

        # detect data drift if present
        is_content_drift = self.is_drift_detected(
            roc_auc_classifier_value=domain_classifier_roc_auc,
            roc_auc_random_percentile=random_classifier_95_percentile,
        )

        characteristic_examples_cur = None
        characteristic_examples_ref = None
        characteristic_words_cur = None
        characteristic_words_ref = None

        if is_content_drift:
            # get examples more characteristic of current or reference dataset
            characteristic_examples_cur, characteristic_examples_ref = self.get_typical_examples(
                X_test, y_test, y_pred_proba
            )

            # get words more characteristic of current or reference dataset
            characteristic_words_cur, characteristic_words_ref = self.get_typical_words(classifier_pipeline)

        return TextDomainClassifierDriftResult(
            text_column_name=self.text_column_name,
            domain_classifier_roc_auc=domain_classifier_roc_auc,
            random_classifier_95_percentile=random_classifier_95_percentile,
            content_drift=is_content_drift,
            current=TextDomainField(
                characteristic_examples=characteristic_examples_cur, characteristic_words=characteristic_words_cur
            ),
            reference=TextDomainField(
                characteristic_examples=characteristic_examples_ref, characteristic_words=characteristic_words_ref
            ),
        )


@default_renderer(wrap_type=TextDomainClassifierDriftMetric)
class TextDomainClassifierDriftMetricRenderer(MetricRenderer):
    @staticmethod
    def _get_table_stat(
        dataset_name: str, metric_result: TextDomainClassifierDriftResult, content_type="words"
    ) -> BaseWidgetInfo:
        if content_type == "words":
            if dataset_name == "current":
                data = metric_result.current.characteristic_words
            else:
                data = metric_result.reference.characteristic_words
        elif content_type == "examples":
            if dataset_name == "current":
                data = metric_result.current.characteristic_examples
            else:
                data = metric_result.reference.characteristic_examples
        else:
            raise Exception("Unknown content type {}. Supported types are ['words', 'examples']".format(content_type))
        if data is None:
            raise Exception(f"Stat '{content_type}' is not present")
        res = table_data(
            title="{} Dataset: characteristic {}".format(dataset_name.capitalize(), content_type.capitalize()),
            column_names=["", ""],
            data=[[el, ""] for el in data],
        )
        return res

    def render_html(self, obj: TextDomainClassifierDriftMetric) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        if metric_result.content_drift:
            drift_result_str = "DETECTED"
        else:
            drift_result_str = "NOT detected"

        result = [
            counter(
                counters=[
                    CounterData(
                        "Content drift is {}".format(drift_result_str),
                        "Content Drift for '{}'".format(metric_result.text_column_name),
                    )
                ],
                title="",
            )
        ]

        counters = [
            CounterData.float(
                "Domain classifier ROC-AUC score",
                metric_result.domain_classifier_roc_auc,
                3,
            ),
            CounterData.float(
                "95th percentile for random predictions",
                metric_result.random_classifier_95_percentile,
                3,
            ),
        ]

        result.append(counter(counters=counters, title=""))

        if metric_result.content_drift:
            current_table_words = self._get_table_stat("current", metric_result, content_type="words")
            reference_table_words = self._get_table_stat("reference", metric_result, content_type="words")

            current_table_examples = self._get_table_stat("current", metric_result, content_type="examples")
            reference_table_examples = self._get_table_stat("reference", metric_result, content_type="examples")

            tables_tabs = [
                TabData(title="Current dataset", widget=current_table_words),
                TabData(title="Reference dataset", widget=reference_table_words),
            ]
            tables = widget_tabs(tabs=tables_tabs)
            result.append(tables)

            tables_tabs = [
                TabData(title="Current dataset", widget=current_table_examples),
                TabData(title="Reference dataset", widget=reference_table_examples),
            ]
            tables = widget_tabs(tabs=tables_tabs)
            result.append(tables)
        return result
