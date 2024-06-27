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


def _listed_words_present(
    in_str: str,
    mode: str,
    lem: WordNetLemmatizer,
    words_list: List[str],
    lemmatize: bool,
) -> int:
    wl = set(words_list)
    result = False
    if in_str is None or (isinstance(in_str, float) and np.isnan(in_str)):
        return False
    words = re.sub("[^A-Za-z0-9 ]+", "", in_str).split()
    for word_ in words:
        word = word_.lower()
        if lemmatize:
            word = lem.lemmatize(word)
        if word in wl:
            if mode in ("includes_all", "excludes_any"):
                wl.remove(word)
            else:
                result = True
    if mode in ("includes_all", "excludes_any"):
        result = len(wl) == 0
    if mode.startswith("excludes"):
        return not result
    return result


class WordsPresence(GeneratedFeature):
    column_name: str
    words_list: List[str]
    mode: str
    lemmatize: bool = True
    _lem: Optional[WordNetLemmatizer] = None

    def __init__(
        self,
        column_name: str,
        words_list: List[str],
        mode: str = "any",
        lemmatize: bool = True,
        display_name: Optional[str] = None,
    ):
        self.feature_type = ColumnType.Categorical
        self.column_name = column_name
        self.words_list = words_list
        if mode not in ["includes_any", "includes_all", "excludes_any", "excludes_all"]:
            raise ValueError("mode must be either 'includes_any', 'includes_all', 'excludes_any' or 'excludes_all'")
        self.mode = mode
        self.lemmatize = lemmatize
        self.display_name = display_name
        super().__init__()

    def generate_feature(self, data: pd.DataFrame, data_definition: DataDefinition) -> pd.DataFrame:
        if self._lem is None:
            import nltk

            nltk.download("wordnet", quiet=True)
            self._lem = WordNetLemmatizer()

        return pd.DataFrame(
            dict(
                [
                    (
                        self._feature_column_name(),
                        data[self.column_name].apply(
                            lambda x: _listed_words_present(x, self.mode, self._lem, self.words_list, self.lemmatize)
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
        raise NotImplementedError()

    def _feature_display_name(self):
        raise NotImplementedError()


class IncludesWords(WordsPresence):
    def __init__(
        self,
        column_name: str,
        words_list: List[str],
        mode: str = "any",
        lemmatize: bool = True,
        display_name: Optional[str] = None,
    ):
        super().__init__(column_name, words_list, "includes_" + mode, lemmatize, display_name)

    def _feature_column_name(self):
        return self.column_name + "_" + "_".join(self.words_list) + "_" + str(self.lemmatize) + "_" + str(self.mode)

    def _feature_display_name(self):
        return (
            f"Text Includes {self.mode} words [{self.words_list}],"
            f" lemmatize: {self.lemmatize}] for {self.column_name}"
        )


class ExcludesWords(WordsPresence):
    def __init__(
        self,
        column_name: str,
        words_list: List[str],
        mode: str = "any",
        lemmatize: bool = True,
        display_name: Optional[str] = None,
    ):
        super().__init__(column_name, words_list, "excludes_" + mode, lemmatize, display_name)

    def _feature_column_name(self):
        return self.column_name + "_" + "_".join(self.words_list) + "_" + str(self.lemmatize) + "_" + str(self.mode)

    def _feature_display_name(self):
        return (
            f"Text Excludes {self.mode} words [{self.words_list}],"
            f" lemmatize: {self.lemmatize}] for {self.column_name}"
        )
