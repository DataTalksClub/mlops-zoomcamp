import uuid
from itertools import repeat
from typing import List
from typing import Optional
from typing import Union

import pandas as pd

from evidently.base_metric import ColumnName
from evidently.base_metric import additional_feature
from evidently.core import ColumnType
from evidently.features.generated_features import GeneratedFeature
from evidently.utils.data_preprocessing import DataDefinition

_legacy_models = ["gpt-3.5-turbo-instruct", "babbage-002", "davinci-002"]


class OpenAIFeature(GeneratedFeature):
    column_name: str
    feature_id: str
    prompt: str
    prompt_replace_string: str
    context: Optional[str]
    context_column: Optional[str]
    context_replace_string: str
    openai_params: dict
    model: str
    check_mode: str
    possible_values: Optional[List[str]]

    def __init__(
        self,
        column_name: str,
        model: str,
        prompt: str,
        feature_type: str,
        context: Optional[str] = None,
        context_column: Optional[str] = None,
        prompt_replace_string: str = "REPLACE",
        context_replace_string: str = "CONTEXT",
        check_mode: str = "any_line",
        possible_values: Optional[List[str]] = None,
        openai_params: Optional[dict] = None,
        display_name: Optional[str] = None,
    ):
        self.feature_id = str(uuid.uuid4())
        self.prompt = prompt
        self.prompt_replace_string = prompt_replace_string
        if context is not None and context_column is not None:
            raise ValueError("Context and context_column are mutually exclusive")
        self.context = context
        self.context_column = context_column
        self.context_replace_string = context_replace_string
        self.openai_params = openai_params or {}
        self.model = model
        self.feature_type = ColumnType.Categorical if feature_type == "cat" else ColumnType.Numerical
        self.column_name = column_name
        self.display_name = display_name
        self.check_mode = check_mode
        self.possible_values = [v.lower() for v in possible_values] if possible_values else None
        super().__init__()

    def generate_feature(self, data: pd.DataFrame, data_definition: DataDefinition) -> pd.DataFrame:
        from openai import OpenAI

        column_data = data[self.column_name].values.tolist()
        client = OpenAI()
        result: List[Union[str, float, None]] = []

        if self.model in _legacy_models:
            func = _completions_openai_call
        else:
            func = _chat_completions_openai_call

        if self.context_column is not None:
            context_column = data[self.context_column].values.tolist()
        else:
            context_column = repeat(self.context)

        for message, context in zip(column_data, context_column):
            context = "" if context is None else context
            prompt_answer = func(
                client,
                model=self.model,
                prompt=self.prompt,
                prompt_replace_string=self.prompt_replace_string,
                context_replace_string=self.context_replace_string,
                prompt_message=message,
                context=context,
                params=self.openai_params,
            )
            processed_response = _postprocess_response(
                prompt_answer,
                self.check_mode,
                self.possible_values,
            )
            if self.feature_type == ColumnType.Categorical:
                result.append(processed_response)
            else:
                try:
                    result.append(float(processed_response) if processed_response else None)
                except ValueError:
                    result.append(None)

        return pd.DataFrame(dict([(self._feature_column_name(), result)]), index=data.index)

    def feature_name(self) -> ColumnName:
        return additional_feature(
            self,
            self._feature_column_name(),
            self.display_name or f"OpenAI for {self.column_name}",
        )

    def _feature_column_name(self) -> str:
        if self.display_name:
            return self.display_name.replace(" ", "_").lower()
        return self.column_name + "_" + self.feature_id


def _completions_openai_call(
    client,
    model: str,
    prompt: str,
    prompt_replace_string: str,
    context_replace_string: str,
    prompt_message: str,
    context: str,
    params: dict,
):
    final_prompt = prompt.replace(context_replace_string, context).replace(prompt_replace_string, prompt_message)
    prompt_answer = client.completions.create(model=model, prompt=final_prompt, **params)
    return prompt_answer.choices[0].text


def _chat_completions_openai_call(
    client,
    model: str,
    prompt: str,
    prompt_replace_string: str,
    context_replace_string: str,
    prompt_message: str,
    context: str,
    params: dict,
):
    final_prompt = prompt.replace(prompt_replace_string, prompt_message)
    prompt_answer = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": final_prompt},
        ],
        **params,
    )
    return prompt_answer.choices[0].message.content


def _postprocess_response(response: str, check_mode: str, possible_values: Optional[List[str]]) -> Optional[str]:
    for line in response.split("\n"):
        line = line.strip().lower()
        if line:
            if possible_values:
                if check_mode.endswith("contains"):
                    for v in possible_values:
                        if v in line:
                            return v
                else:
                    if line in possible_values:
                        return line
                if check_mode.startswith("any_line"):
                    continue
                else:
                    return None
            return line
    return None
