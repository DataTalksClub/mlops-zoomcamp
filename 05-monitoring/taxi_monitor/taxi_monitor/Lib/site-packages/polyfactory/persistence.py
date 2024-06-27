from __future__ import annotations

from typing import Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class SyncPersistenceProtocol(Protocol[T]):
    """Protocol for sync persistence"""

    def save(self, data: T) -> T:
        """Persist a single instance synchronously.

        :param data: A single instance to persist.

        :returns: The persisted result.

        """
        ...

    def save_many(self, data: list[T]) -> list[T]:
        """Persist multiple instances synchronously.

        :param data: A list of instances to persist.

        :returns: The persisted result

        """
        ...


@runtime_checkable
class AsyncPersistenceProtocol(Protocol[T]):
    """Protocol for async persistence"""

    async def save(self, data: T) -> T:
        """Persist a single instance asynchronously.

        :param data: A single instance to persist.

        :returns: The persisted result.
        """
        ...

    async def save_many(self, data: list[T]) -> list[T]:
        """Persist multiple instances asynchronously.

        :param data: A list of instances to persist.

        :returns: The persisted result
        """
        ...
