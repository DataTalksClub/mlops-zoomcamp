import re
from typing import Optional
from typing import Set
from typing import Tuple

import numpy as np
import pandas as pd
from nltk.corpus import words
from nltk.stem.wordnet import WordNetLemmatizer

from evidently.base_metric import additional_feature
from evidently.features.generated_features import GeneratedFeature
from evidently.utils.data_preprocessing import DataDefinition


class OOVWordsPercentage(GeneratedFeature):
    column_name: str
    ignore_words: Tuple = ()
    _lem: WordNetLemmatizer
    _eng_words: Set

    def __init__(self, column_name: str, ignore_words=(), display_name: Optional[str] = None):
        self.column_name = column_name
        self.ignore_words = ignore_words
        self.display_name = display_name
        super().__init__()

    def generate_feature(self, data: pd.DataFrame, data_definition: DataDefinition) -> pd.DataFrame:
        if not hasattr(self, "_lem"):
            import nltk

            nltk.download("wordnet", quiet=True)
            nltk.download("words", quiet=True)
            self._lem = WordNetLemmatizer()
            self._eng_words = set(words.words())

        def oov_share(s, ignore_words=()):
            if s is None or (isinstance(s, float) and np.isnan(s)):
                return 0
            oov_num = 0
            words_ = re.sub("[^A-Za-z0-9 ]+", "", s).split()  # leave only letters, digits and spaces, split by spaces
            if len(words_) == 0:
                return 0
            for word in words_:
                if word.lower() not in ignore_words and self._lem.lemmatize(word.lower()) not in self._eng_words:
                    oov_num += 1
            return 100 * oov_num / len(words_)

        return pd.DataFrame(
            dict(
                [
                    (
                        self.column_name,
                        data[self.column_name].apply(lambda x: oov_share(x, ignore_words=self.ignore_words)),
                    )
                ]
            )
        )

    def feature_name(self):
        return additional_feature(self, self.column_name, self.display_name or f"OOV Words % for {self.column_name}")

    def get_parameters(self) -> Optional[tuple]:
        return self.column_name, self.ignore_words
