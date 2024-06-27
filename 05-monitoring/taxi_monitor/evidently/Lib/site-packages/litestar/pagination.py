# ruff: noqa: UP006,UP007
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

__all__ = (
    "AbstractAsyncClassicPaginator",
    "AbstractAsyncCursorPaginator",
    "AbstractAsyncOffsetPaginator",
    "AbstractSyncClassicPaginator",
    "AbstractSyncCursorPaginator",
    "AbstractSyncOffsetPaginator",
    "ClassicPagination",
    "CursorPagination",
    "OffsetPagination",
)


T = TypeVar("T")
C = TypeVar("C", int, str, UUID)


@dataclass
class ClassicPagination(Generic[T]):
    """Container for data returned using limit/offset pagination."""

    __slots__ = ("items", "page_size", "current_page", "total_pages")

    items: List[T]
    """List of data being sent as part of the response."""
    page_size: int
    """Number of items per page."""
    current_page: int
    """Current page number."""
    total_pages: int
    """Total number of pages."""


# AA requires it's own `OffsetPagination` class in versions greater that 0.9.0
# If we find it, use it.
try:
    from advanced_alchemy.service import (
        OffsetPagination,  # pyright: ignore[reportMissingImports,reportGeneralTypeIssues]
    )
except ImportError:

    @dataclass
    class OffsetPagination(Generic[T]):  # type: ignore[no-redef]
        """Container for data returned using limit/offset pagination."""

        __slots__ = ("items", "limit", "offset", "total")

        items: List[T]
        """List of data being sent as part of the response."""
        limit: int
        """Maximal number of items to send."""
        offset: int
        """Offset from the beginning of the query.

        Identical to an index.
        """
        total: int
        """Total number of items."""


@dataclass
class CursorPagination(Generic[C, T]):
    """Container for data returned using cursor pagination."""

    __slots__ = ("items", "results_per_page", "cursor", "next_cursor")

    items: List[T]
    """List of data being sent as part of the response."""
    results_per_page: int
    """Maximal number of items to send."""
    cursor: Optional[C]
    """Unique ID, designating the last identifier in the given data set.

    This value can be used to request the "next" batch of records.
    """


class AbstractSyncClassicPaginator(ABC, Generic[T]):
    """Base paginator class for sync classic pagination.

    Implement this class to return paginated result sets using the classic pagination scheme.
    """

    @abstractmethod
    def get_total(self, page_size: int) -> int:
        """Return the total number of records.

        Args:
            page_size: Maximal number of records to return.

        Returns:
            An integer.
        """
        raise NotImplementedError

    @abstractmethod
    def get_items(self, page_size: int, current_page: int) -> list[T]:
        """Return a list of items of the given size 'page_size' correlating with 'current_page'.

        Args:
            page_size: Maximal number of records to return.
            current_page: The current page of results to return.

        Returns:
            A list of items.
        """
        raise NotImplementedError

    def __call__(self, page_size: int, current_page: int) -> ClassicPagination[T]:
        """Return a paginated result set.

        Args:
            page_size: Maximal number of records to return.
            current_page: The current page of results to return.

        Returns:
            A paginated result set.
        """
        total_pages = self.get_total(page_size=page_size)

        items = self.get_items(page_size=page_size, current_page=current_page)

        return ClassicPagination[T](
            items=items, total_pages=total_pages, page_size=page_size, current_page=current_page
        )


class AbstractAsyncClassicPaginator(ABC, Generic[T]):
    """Base paginator class for async classic pagination.

    Implement this class to return paginated result sets using the classic pagination scheme.
    """

    @abstractmethod
    async def get_total(self, page_size: int) -> int:
        """Return the total number of records.

        Args:
            page_size: Maximal number of records to return.

        Returns:
            An integer.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_items(self, page_size: int, current_page: int) -> list[T]:
        """Return a list of items of the given size 'page_size' correlating with 'current_page'.

        Args:
            page_size: Maximal number of records to return.
            current_page: The current page of results to return.

        Returns:
            A list of items.
        """
        raise NotImplementedError

    async def __call__(self, page_size: int, current_page: int) -> ClassicPagination[T]:
        """Return a paginated result set.

        Args:
            page_size: Maximal number of records to return.
            current_page: The current page of results to return.

        Returns:
            A paginated result set.
        """
        total_pages = await self.get_total(page_size=page_size)

        items = await self.get_items(page_size=page_size, current_page=current_page)

        return ClassicPagination[T](
            items=items, total_pages=total_pages, page_size=page_size, current_page=current_page
        )


class AbstractSyncOffsetPaginator(ABC, Generic[T]):
    """Base paginator class for limit / offset pagination.

    Implement this class to return paginated result sets using the limit / offset pagination scheme.
    """

    @abstractmethod
    def get_total(self) -> int:
        """Return the total number of records.

        Returns:
            An integer.
        """
        raise NotImplementedError

    @abstractmethod
    def get_items(self, limit: int, offset: int) -> list[T]:
        """Return a list of items of the given size 'limit' starting from position 'offset'.

        Args:
            limit: Maximal number of records to return.
            offset: Starting position within the result set (assume index 0 as starting position).

        Returns:
            A list of items.
        """
        raise NotImplementedError

    def __call__(self, limit: int, offset: int) -> OffsetPagination[T]:
        """Return a paginated result set.

        Args:
            limit: Maximal number of records to return.
            offset: Starting position within the result set (assume index 0 as starting position).

        Returns:
            A paginated result set.
        """
        total = self.get_total()

        items = self.get_items(limit=limit, offset=offset)

        return OffsetPagination[T](items=items, total=total, offset=offset, limit=limit)


class AbstractAsyncOffsetPaginator(ABC, Generic[T]):
    """Base paginator class for limit / offset pagination.

    Implement this class to return paginated result sets using the limit / offset pagination scheme.
    """

    @abstractmethod
    async def get_total(self) -> int:
        """Return the total number of records.

        Returns:
            An integer.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_items(self, limit: int, offset: int) -> list[T]:
        """Return a list of items of the given size 'limit' starting from position 'offset'.

        Args:
            limit: Maximal number of records to return.
            offset: Starting position within the result set (assume index 0 as starting position).

        Returns:
            A list of items.
        """
        raise NotImplementedError

    async def __call__(self, limit: int, offset: int) -> OffsetPagination[T]:
        """Return a paginated result set.

        Args:
            limit: Maximal number of records to return.
            offset: Starting position within the result set (assume index 0 as starting position).

        Returns:
            A paginated result set.
        """
        total = await self.get_total()
        items = await self.get_items(limit=limit, offset=offset)

        return OffsetPagination[T](items=items, total=total, offset=offset, limit=limit)


class AbstractSyncCursorPaginator(ABC, Generic[C, T]):
    """Base paginator class for sync cursor pagination.

    Implement this class to return paginated result sets using the cursor pagination scheme.
    """

    @abstractmethod
    def get_items(self, cursor: C | None, results_per_page: int) -> tuple[list[T], C | None]:
        """Return a list of items of the size 'results_per_page' following the given cursor, if any,

        Args:
            cursor: A unique identifier that acts as the 'cursor' after which results should be given.
            results_per_page: A maximal number of results to return.

        Returns:
            A tuple containing the result set and a new cursor that marks the last record retrieved.
            The new cursor can be used to ask for the 'next_cursor' batch of results.
        """
        raise NotImplementedError

    def __call__(self, cursor: C | None, results_per_page: int) -> CursorPagination[C, T]:
        """Return a paginated result set given an optional cursor (unique ID) and a maximal number of results to return.

        Args:
            cursor: A unique identifier that acts as the 'cursor' after which results should be given.
            results_per_page: A maximal number of results to return.

        Returns:
            A paginated result set.
        """
        items, new_cursor = self.get_items(cursor=cursor, results_per_page=results_per_page)

        return CursorPagination[C, T](
            items=items,
            results_per_page=results_per_page,
            cursor=new_cursor,
        )


class AbstractAsyncCursorPaginator(ABC, Generic[C, T]):
    """Base paginator class for async cursor pagination.

    Implement this class to return paginated result sets using the cursor pagination scheme.
    """

    @abstractmethod
    async def get_items(self, cursor: C | None, results_per_page: int) -> tuple[list[T], C | None]:
        """Return a list of items of the size 'results_per_page' following the given cursor, if any,

        Args:
            cursor: A unique identifier that acts as the 'cursor' after which results should be given.
            results_per_page: A maximal number of results to return.

        Returns:
            A tuple containing the result set and a new cursor that marks the last record retrieved.
            The new cursor can be used to ask for the 'next_cursor' batch of results.
        """
        raise NotImplementedError

    async def __call__(self, cursor: C | None, results_per_page: int) -> CursorPagination[C, T]:
        """Return a paginated result set given an optional cursor (unique ID) and a maximal number of results to return.

        Args:
            cursor: A unique identifier that acts as the 'cursor' after which results should be given.
            results_per_page: A maximal number of results to return.

        Returns:
            A paginated result set.
        """
        items, new_cursor = await self.get_items(cursor=cursor, results_per_page=results_per_page)

        return CursorPagination[C, T](
            items=items,
            results_per_page=results_per_page,
            cursor=new_cursor,
        )
