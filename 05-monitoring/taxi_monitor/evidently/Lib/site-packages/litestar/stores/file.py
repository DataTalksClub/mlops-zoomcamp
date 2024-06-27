from __future__ import annotations

import os
import shutil
import unicodedata
from tempfile import mkstemp
from typing import TYPE_CHECKING

from anyio import Path

from litestar.concurrency import sync_to_thread

from .base import NamespacedStore, StorageObject

__all__ = ("FileStore",)


if TYPE_CHECKING:
    from datetime import timedelta
    from os import PathLike


def _safe_file_name(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    return "".join(c if c.isalnum() else str(ord(c)) for c in name)


class FileStore(NamespacedStore):
    """File based, thread and process safe, asynchronous key/value store."""

    __slots__ = {"path": "file path"}

    def __init__(self, path: PathLike[str]) -> None:
        """Initialize ``FileStorage``.

        Args:
            path: Path to store data under
        """
        self.path = Path(path)

    def with_namespace(self, namespace: str) -> FileStore:
        """Return a new instance of :class:`FileStore`, using  a sub-path of the current store's path."""
        if not namespace.isalnum():
            raise ValueError(f"Invalid namespace: {namespace!r}")
        return FileStore(self.path / namespace)

    def _path_from_key(self, key: str) -> Path:
        return self.path / _safe_file_name(key)

    @staticmethod
    async def _load_from_path(path: Path) -> StorageObject | None:
        try:
            data = await path.read_bytes()
            return StorageObject.from_bytes(data)
        except FileNotFoundError:
            return None

    def _write_sync(self, target_file: Path, storage_obj: StorageObject) -> None:
        try:
            tmp_file_fd, tmp_file_name = mkstemp(dir=self.path, prefix=f"{target_file.name}.tmp")
            renamed = False
            try:
                try:
                    os.write(tmp_file_fd, storage_obj.to_bytes())
                finally:
                    os.close(tmp_file_fd)

                os.replace(tmp_file_name, target_file)  # noqa: PTH105
                renamed = True
            finally:
                if not renamed:
                    os.unlink(tmp_file_name)  # noqa: PTH108
        except OSError:
            pass

    async def _write(self, target_file: Path, storage_obj: StorageObject) -> None:
        await sync_to_thread(self._write_sync, target_file, storage_obj)

    async def set(self, key: str, value: str | bytes, expires_in: int | timedelta | None = None) -> None:
        """Set a value.

        Args:
            key: Key to associate the value with
            value: Value to store
            expires_in: Time in seconds before the key is considered expired

        Returns:
            ``None``
        """

        await self.path.mkdir(exist_ok=True)
        path = self._path_from_key(key)
        if isinstance(value, str):
            value = value.encode("utf-8")
        storage_obj = StorageObject.new(data=value, expires_in=expires_in)
        await self._write(path, storage_obj)

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
        path = self._path_from_key(key)
        storage_obj = await self._load_from_path(path)

        if not storage_obj:
            return None

        if storage_obj.expired:
            await path.unlink(missing_ok=True)
            return None

        if renew_for and storage_obj.expires_at:
            await self.set(key, value=storage_obj.data, expires_in=renew_for)

        return storage_obj.data

    async def delete(self, key: str) -> None:
        """Delete a value.

        If no such key exists, this is a no-op.

        Args:
            key: Key of the value to delete
        """
        path = self._path_from_key(key)
        await path.unlink(missing_ok=True)

    async def delete_all(self) -> None:
        """Delete all stored values.

        Note:
            This deletes and recreates :attr:`FileStore.path`
        """

        await sync_to_thread(shutil.rmtree, self.path)
        await self.path.mkdir(exist_ok=True)

    async def delete_expired(self) -> None:
        """Delete expired items.

        Since expired items are normally only cleared on access (i.e. when calling
        :meth:`.get`), this method should be called in regular intervals
        to free disk space.
        """
        async for file in self.path.iterdir():
            wrapper = await self._load_from_path(file)
            if wrapper and wrapper.expired:
                await file.unlink(missing_ok=True)

    async def exists(self, key: str) -> bool:
        """Check if a given ``key`` exists."""
        path = self._path_from_key(key)
        return await path.exists()

    async def expires_in(self, key: str) -> int | None:
        """Get the time in seconds ``key`` expires in. If no such ``key`` exists or no
        expiry time was set, return ``None``.
        """
        if storage_obj := await self._load_from_path(self._path_from_key(key)):
            return storage_obj.expires_in
        return None
