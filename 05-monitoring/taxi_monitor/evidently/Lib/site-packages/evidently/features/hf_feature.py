from functools import partial
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import pandas as pd

from evidently.core import ColumnType
from evidently.features.generated_features import DataFeature
from evidently.utils.data_preprocessing import DataDefinition


class HuggingFaceFeature(DataFeature):
    column_name: str
    model: str
    params: dict

    def __init__(self, *, column_name: str, model: str, params: dict, display_name: str):
        self.column_name = column_name
        self.model = model
        self.params = params
        self.display_name = display_name
        self.feature_type = _model_type(model)
        super().__init__()

    def generate_data(self, data: pd.DataFrame, data_definition: DataDefinition) -> pd.Series:
        val = _models.get(self.model)
        if val is None:
            raise ValueError(f"Model {self.model} not found. Available models: {', '.join(_models.keys())}")
        _, available_params, func = val
        result = func(data[self.column_name], **{param: self.params.get(param, None) for param in available_params})
        return result


class HuggingFaceToxicityFeature(DataFeature):
    column_name: str
    model: Optional[str]
    toxic_label: Optional[str]

    def __init__(
        self,
        *,
        column_name: str,
        display_name: str,
        model: Optional[str] = None,
        toxic_label: Optional[str] = None,
    ):
        self.column_name = column_name
        self.display_name = display_name
        self.model = model
        self.toxic_label = toxic_label
        super().__init__()

    def generate_data(self, data: pd.DataFrame, data_definition: DataDefinition) -> pd.Series:
        return _toxicity(self.model, self.toxic_label, data[self.column_name])


def _samlowe_roberta_base_go_emotions(data: pd.Series, label: str) -> pd.Series:
    from transformers import pipeline

    def _convert_labels(row):
        return {x["label"]: x["score"] for x in row}

    classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)
    model_outputs = classifier(data.fillna("").tolist())
    return pd.Series([_convert_labels(out).get(label, None) for out in model_outputs], index=data.index)


def _openai_detector(data: pd.Series, score_threshold: float) -> pd.Series:
    from transformers import pipeline

    def _get_label(row):
        return row["label"] if row["score"] > score_threshold else "Unknown"

    pipe = pipeline("text-classification", model="roberta-base-openai-detector")
    return pd.Series([_get_label(x) for x in pipe(data.fillna("").tolist())], index=data.index)


def _map_labels(labels: List[str], scores: List[float], threshold: float) -> Optional[str]:
    if len(labels) == 0:
        return None
    if len(labels) == 1:
        if scores[0] > threshold:
            return labels[0]
        else:
            return "not " + labels[0]
    label = max(zip(labels, scores), key=lambda x: x[1])
    return label[0] if label[1] > threshold else "unknown"


def _lmnli_fever(data: pd.Series, labels: List[str], threshold: Optional[float]) -> pd.Series:
    from transformers import pipeline

    threshold = threshold if threshold is not None else 0.5

    classifier = pipeline(
        "zero-shot-classification",
        model="MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli",
    )
    output = classifier(data.fillna("").tolist(), labels, multi_label=False)

    return pd.Series([_map_labels(o["labels"], o["scores"], threshold) for o in output], index=data.index)


def _toxicity(model_name: Optional[str], toxic_label: Optional[str], data: pd.Series) -> pd.Series:
    import evaluate

    column_data = data.values.tolist()
    model = evaluate.load("toxicity", model_name, module_type="measurement")
    if toxic_label is None:
        scores = model.compute(predictions=column_data)
    else:
        scores = model.compute(predictions=column_data, toxic_label=toxic_label)
    return pd.Series(scores["toxicity"], index=data.index)


def _dfp(data: pd.Series, threshold: Optional[float]) -> pd.Series:
    from transformers import pipeline

    if threshold is None:
        threshold = 0.5

    model = pipeline("token-classification", "lakshyakh93/deberta_finetuned_pii")
    output = model(data.tolist())
    converted_output = [
        _map_labels(
            [x["entity"] for x in entities],
            [x["score"] for x in entities],
            threshold,
        )
        for entities in output
    ]
    return pd.Series(converted_output, index=data.index)


def _model_type(model: str) -> ColumnType:
    return _models.get(model, (ColumnType.Unknown, None, None))[0]


_models: Dict[str, Tuple[ColumnType, List[str], Callable[..., pd.Series]]] = {
    "SamLowe/roberta-base-go_emotions": (ColumnType.Numerical, ["label"], _samlowe_roberta_base_go_emotions),
    "openai-community/roberta-base-openai-detector": (ColumnType.Categorical, ["score_threshold"], _openai_detector),
    "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli": (
        ColumnType.Categorical,
        ["labels", "threshold"],
        _lmnli_fever,
    ),
    "DaNLP/da-electra-hatespeech-detection": (
        ColumnType.Numerical,
        [],
        partial(_toxicity, "DaNLP/da-electra-hatespeech-detection", "offensive"),
    ),
    "facebook/roberta-hate-speech-dynabench-r4-target": (
        ColumnType.Numerical,
        [],
        partial(_toxicity, "facebook/roberta-hate-speech-dynabench-r4-target", "hate"),
    ),
    "lakshyakh93/deberta_finetuned_pii": (
        ColumnType.Categorical,
        ["threshold"],
        _dfp,
    ),
}
