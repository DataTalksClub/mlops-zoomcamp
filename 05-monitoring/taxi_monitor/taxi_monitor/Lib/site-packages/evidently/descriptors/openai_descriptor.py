from typing import List
from typing import Optional

from evidently.features.generated_features import FeatureDescriptor
from evidently.features.generated_features import GeneratedFeature
from evidently.features.openai_feature import OpenAIFeature


class OpenAIPrompting(FeatureDescriptor):
    prompt: str
    prompt_replace_string: str
    context: Optional[str]
    context_column: Optional[str]
    context_replace_string: str
    openai_params: Optional[dict]
    model: str
    feature_type: str
    check_mode: str
    possible_values: Optional[List[str]]

    def __init__(
        self,
        prompt: str,
        model: str,
        feature_type: str,
        context: Optional[str] = None,
        context_column: Optional[str] = None,
        prompt_replace_string: str = "REPLACE",
        context_replace_string: str = "CONTEXT",
        display_name: Optional[str] = None,
        possible_values: Optional[List[str]] = None,
        openai_params: Optional[dict] = None,
        check_mode: str = "any_line",
    ):
        self.model = model
        self.feature_type = feature_type
        self.prompt_replace_string = prompt_replace_string
        self.prompt = prompt
        self.display_name = display_name
        self.possible_values = possible_values
        self.context = context
        self.context_column = context_column
        self.context_replace_string = context_replace_string
        self.openai_params = openai_params
        self.check_mode = check_mode
        super().__init__()

    def feature(self, column_name: str) -> GeneratedFeature:
        return OpenAIFeature(
            column_name,
            model=self.model,
            prompt=self.prompt,
            prompt_replace_string=self.prompt_replace_string,
            feature_type=self.feature_type,
            display_name=self.display_name,
            possible_values=self.possible_values,
            context=self.context,
            context_column=self.context_column,
            context_replace_string=self.context_replace_string,
            openai_params=self.openai_params,
            check_mode=self.check_mode,
        )
