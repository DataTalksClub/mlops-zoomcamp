import dataclasses
import random
from typing import Callable
from typing import List
from typing import Optional
from typing import Union

import pandas as pd


@dataclasses.dataclass
class SamplingOptions:
    type: str = "none"
    random_seed: int = 1
    ratio: float = 1.0
    n: int = 1


@dataclasses.dataclass
class DataOptions:
    date_column: str
    separator: str
    # is csv file contains header row
    header: bool
    # should be list of names, or None if columns should be inferred from data
    column_names: Optional[List[str]]

    def __init__(self, date_column: str = "datetime", separator=",", header=True, column_names=None):
        self.date_column = date_column
        self.header = header
        self.separator = separator
        self.column_names = column_names


def _skiprows(sampling_options: SamplingOptions) -> Union[Callable[[int], bool], None]:
    if sampling_options.type == "none":
        return None
    if sampling_options.type == "nth":
        if sampling_options.n < 1:
            raise Exception("nth sampling should have 'n' parameter >= 1")
        return __simple(sampling_options)
    if sampling_options.type == "random":
        skip_rows = RandomizedSkipRows(sampling_options.ratio, sampling_options.random_seed)
        return skip_rows.skiprows
    raise ValueError(f"Unexpected sampling type {sampling_options.type}")


def __simple(sampling_options: SamplingOptions):
    def func(row_idx):
        if row_idx == 0:
            result = False
        else:
            rem = row_idx % sampling_options.n
            result = rem != 1
        return result

    return func


class DataLoader:
    def __init__(self):
        pass

    def load(self, filename: str, data_options: DataOptions, sampling_options: SamplingOptions = None):
        sampling_opts = SamplingOptions("none", 0, 0) if sampling_options is None else sampling_options
        parse_dates = [data_options.date_column] if data_options.date_column else False
        return pd.read_csv(
            filename,
            header=0 if data_options.header else None,
            sep=data_options.separator,
            skiprows=_skiprows(sampling_opts),
            parse_dates=parse_dates,
        )


CHUNK_SIZE = 1000


class RandomizedSkipRows:
    def __init__(self, ratio: float, random_seed: int):
        self.random = random.Random(random_seed)
        self.ratio = ratio
        self.selected_rows = self._select()

    def skiprows(self, row_index: int):
        if row_index == 0:
            return False
        if row_index % CHUNK_SIZE == 0:
            self.selected_rows = self._select()
        idx = row_index - int(row_index / CHUNK_SIZE) * CHUNK_SIZE
        return self.selected_rows[idx]

    def _select(self):
        return [bool(self.random.random() < self.ratio) for _ in range(1000)]
