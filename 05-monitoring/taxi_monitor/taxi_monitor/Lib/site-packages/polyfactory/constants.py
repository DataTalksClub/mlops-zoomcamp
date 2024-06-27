from __future__ import annotations

import sys
from collections import abc, defaultdict, deque
from random import Random
from typing import (
    DefaultDict,
    Deque,
    Dict,
    FrozenSet,
    Iterable,
    List,
    Mapping,
    Sequence,
    Set,
    Tuple,
    Union,
)

try:
    from types import UnionType
except ImportError:
    UnionType = Union  # type: ignore[misc,assignment]

PY_38 = sys.version_info.major == 3 and sys.version_info.minor == 8  # noqa: PLR2004

# Mapping of type annotations into concrete types. This is used to normalize python <= 3.9 annotations.
INSTANTIABLE_TYPE_MAPPING = {
    DefaultDict: defaultdict,
    Deque: deque,
    Dict: dict,
    FrozenSet: frozenset,
    Iterable: list,
    List: list,
    Mapping: dict,
    Sequence: list,
    Set: set,
    Tuple: tuple,
    abc.Iterable: list,
    abc.Mapping: dict,
    abc.Sequence: list,
    abc.Set: set,
    UnionType: Union,
}


if not PY_38:
    TYPE_MAPPING = INSTANTIABLE_TYPE_MAPPING
else:
    # For 3.8, we have to keep the types from typing since dict[str] syntax is not supported in 3.8.
    TYPE_MAPPING = {
        DefaultDict: DefaultDict,
        Deque: Deque,
        Dict: Dict,
        FrozenSet: FrozenSet,
        Iterable: List,
        List: List,
        Mapping: Dict,
        Sequence: List,
        Set: Set,
        Tuple: Tuple,
        abc.Iterable: List,
        abc.Mapping: Dict,
        abc.Sequence: List,
        abc.Set: Set,
    }


DEFAULT_RANDOM = Random()
RANDOMIZE_COLLECTION_LENGTH = False
MIN_COLLECTION_LENGTH = 0
MAX_COLLECTION_LENGTH = 5
