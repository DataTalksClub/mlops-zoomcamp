from __future__ import annotations

from typing import TYPE_CHECKING

import anyio
from anyio import Lock

from .base import StorageObject, Store

__all__ = ("MemoryStore",)


if TYPE_CHECKING:
    from datetime import timedelta


class MemoryStore(Store):
    """In memory, atomic, asynchronous key/value store."""

    __slots__ = ("_store", "_lock")

    def __init__(self) -> None:
        """Initialize :class:`MemoryStore`"""
        self._store: dict[str, StorageObject] = {}
        self._lock = Lock()

    async def set(self, key: str, value: str | bytes, expires_in: int | timedelta | None = None) -> None:
        """Set a value.

        Args:
            key: Key to associate the value with
            value: Value to store
            expires_in: Time in seconds before the key is considered expired

        Returns:
            ``None``
        """
        if isinstance(value, str):
            value = value.encode("utf-8")
        async with self._lock:
            self._store[key] = StorageObject.new(data=value, expires_in=expires_in)

    async def get(self, key: str, renew_for: int | timedelta | None = None) -> bytes | None:
        """Get a value.

        Args:
            key: Key associated with the value
            renew_for: If given and the value had an initial expiry time set, renew the
                expiry time for ``renew_for`` seconds. If the value has not been set
                with an expiry time this is a no-op

        Returns:
            The value associated with ``key`` if it exists and is not expired, else
            ``None``
        """
        async with self._lock:
            storage_obj = self._store.get(key)

            if not storage_obj:
                return None

            if storage_obj.expired:
                self._store.pop(key)
                return None

            if renew_for and storage_obj.expires_at:
                # don't use .set() here, so we can hold onto the lock for the whole operation
                storage_obj = StorageObject.new(data=storage_obj.data, expires_in=renew_for)
                self._store[key] = storage_obj

            return storage_obj.data

    async def delete(self, key: str) -> None:
        """Delete a value.

        If no such key exists, this is a no-op.

        Args:
            key: Key of the value to delete
        """
        async with self._lock:
            self._store.pop(key, None)

    async def delete_all(self) -> None:
        """Delete all stored values."""
        async with self._lock:
            self._store.clear()

    async def delete_expired(self) -> None:
        """Delete expired items.

        Since expired items are normally only cleared on access (i.e. when calling
        :meth:`.get`), this method should be called in regular intervals
        to free memory.
        """
        async with self._lock:
            new_store = {}
            for i, (key, storage_obj) in enumerate(self._store.items()):
                if not storage_obj.expired:
                    new_store[key] = storage_obj
                if i % 1000 == 0:
                    await anyio.sleep(0)
            self._store = new_store

    async def exists(self, key: str) -> bool:
        """Check if a given ``key`` exists."""
        return key in self._store

    async def expires_in(self, key: str) -> int | None:
        """Get the time in seconds ``key`` expires in. If no such ``key`` exists or no
        expiry time was set, return ``None``.
        """
        if storage_obj := self._store.get(key):
            return storage_obj.expires_in
        return None
