"""Collection filter datastructures."""

from __future__ import annotations

from collections import abc  # noqa: TCH003
from dataclasses import dataclass
from datetime import datetime  # noqa: TCH003
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

T = TypeVar("T")

__all__ = (
    "BeforeAfter",
    "CollectionFilter",
    "FilterTypes",
    "LimitOffset",
    "OrderBy",
    "SearchFilter",
    "NotInCollectionFilter",
    "OnBeforeAfter",
    "NotInSearchFilter",
)


FilterTypes: TypeAlias = "BeforeAfter | OnBeforeAfter | CollectionFilter[Any] | LimitOffset | OrderBy | SearchFilter | NotInCollectionFilter[Any] | NotInSearchFilter"
"""Aggregate type alias of the types supported for collection filtering."""


@dataclass
class BeforeAfter:
    """Data required to filter a query on a ``datetime`` column."""

    field_name: str
    """Name of the model attribute to filter on."""
    before: datetime | None
    """Filter results where field earlier than this."""
    after: datetime | None
    """Filter results where field later than this."""


@dataclass
class OnBeforeAfter:
    """Data required to filter a query on a ``datetime`` column."""

    field_name: str
    """Name of the model attribute to filter on."""
    on_or_before: datetime | None
    """Filter results where field is on or earlier than this."""
    on_or_after: datetime | None
    """Filter results where field on or later than this."""


@dataclass
class CollectionFilter(Generic[T]):
    """Data required to construct a ``WHERE ... IN (...)`` clause."""

    field_name: str
    """Name of the model attribute to filter on."""
    values: abc.Collection[T]
    """Values for ``IN`` clause."""


@dataclass
class NotInCollectionFilter(Generic[T]):
    """Data required to construct a ``WHERE ... NOT IN (...)`` clause."""

    field_name: str
    """Name of the model attribute to filter on."""
    values: abc.Collection[T]
    """Values for ``NOT IN`` clause."""


@dataclass
class LimitOffset:
    """Data required to add limit/offset filtering to a query."""

    limit: int
    """Value for ``LIMIT`` clause of query."""
    offset: int
    """Value for ``OFFSET`` clause of query."""


@dataclass
class OrderBy:
    """Data required to construct a ``ORDER BY ...`` clause."""

    field_name: str
    """Name of the model attribute to sort on."""
    sort_order: Literal["asc", "desc"] = "asc"
    """Sort ascending or descending"""


@dataclass
class SearchFilter:
    """Data required to construct a ``WHERE field_name LIKE '%' || :value || '%'`` clause."""

    field_name: str
    """Name of the model attribute to sort on."""
    value: str
    """Values for ``LIKE`` clause."""
    ignore_case: bool | None = False
    """Should the search be case insensitive."""


@dataclass
class NotInSearchFilter:
    """Data required to construct a ``WHERE field_name NOT LIKE '%' || :value || '%'`` clause."""

    field_name: str
    """Name of the model attribute to search on."""
    value: str
    """Values for ``NOT LIKE`` clause."""
    ignore_case: bool | None = False
    """Should the search be case insensitive."""
