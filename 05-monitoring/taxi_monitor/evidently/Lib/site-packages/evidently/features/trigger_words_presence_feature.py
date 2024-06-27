import re
from typing import List
from typing import Optional

import numpy as np
import pandas as pd
from nltk.stem.wordnet import WordNetLemmatizer

from evidently.base_metric import additional_feature
from evidently.core import ColumnType
from evidently.features.generated_features import GeneratedFeature
from evidently.utils.data_preprocessing import DataDefinition


class TriggerWordsPresent(GeneratedFeature):
    column_name: str
    words_list: List[str]
    lemmatize: bool = True
    _lem: WordNetLemmatizer

    def __init__(
        self,
        column_name: str,
        words_list: List[str],
        lemmatize: bool = True,
        display_name: Optional[str] = None,
    ):
        self.feature_type = ColumnType.Categorical
        self.column_name = column_name
        self.words_list = words_list
        self.lemmatize = lemmatize
        self.display_name = display_name
        super().__init__()

    def generate_feature(self, data: pd.DataFrame, data_definition: DataDefinition) -> pd.DataFrame:
        if not hasattr(self, "_lem"):
            import nltk

            nltk.download("wordnet", quiet=True)
            self._lem = WordNetLemmatizer()

        def listed_words_present(s, words_list=(), lemmatize=True):
            if s is None or (isinstance(s, float) and np.isnan(s)):
                return 0
            words = re.sub("[^A-Za-z0-9 ]+", "", s).split()
            for word_ in words:
                word = word_.lower()
                if lemmatize:
                    word = self._lem.lemmatize(word)
                if word in words_list:
                    return 1
            return 0

        return pd.DataFrame(
            dict(
                [
                    (
                        self._feature_column_name(),
                        data[self.column_name].apply(
                            lambda x: listed_words_present(
                                x,
                                words_list=self.words_list,
                                lemmatize=self.lemmatize,
                            )
                        ),
                    )
                ]
            )
        )

    def get_parameters(self):
        return self.column_name, tuple(self.words_list), self.lemmatize

    def feature_name(self):
        return additional_feature(self, self._feature_column_name(), self.display_name or self._feature_display_name())

    def _feature_column_name(self):
        return self.column_name + "_" + "_".join(self.words_list) + "_" + str(self.lemmatize)

    def _feature_display_name(self):
        return f"TriggerWordsPresent [words: {self.words_list}, lemmatize: {self.lemmatize}] for {self.column_name}"
