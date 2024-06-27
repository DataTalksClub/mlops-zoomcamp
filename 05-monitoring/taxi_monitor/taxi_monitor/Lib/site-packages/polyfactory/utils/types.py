from typing import Union

try:
    from types import NoneType, UnionType

    UNION_TYPES = {UnionType, Union}
except ImportError:
    UNION_TYPES = {Union}

    NoneType = type(None)  # type: ignore[misc]

__all__ = ("NoneType", "UNION_TYPES")
