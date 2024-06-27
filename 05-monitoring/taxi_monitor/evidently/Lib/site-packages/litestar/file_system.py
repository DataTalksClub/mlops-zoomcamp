from __future__ import annotations

from stat import S_ISDIR
from typing import TYPE_CHECKING, Any, AnyStr, cast

from anyio import AsyncFile, Path, open_file

from litestar.concurrency import sync_to_thread
from litestar.exceptions import InternalServerException, NotAuthorizedException
from litestar.types.file_types import FileSystemProtocol
from litestar.utils.predicates import is_async_callable

__all__ = ("BaseLocalFileSystem", "FileSystemAdapter")


if TYPE_CHECKING:
    from os import stat_result

    from _typeshed import OpenBinaryMode

    from litestar.types import PathType
    from litestar.types.file_types import FileInfo


class BaseLocalFileSystem(FileSystemProtocol):
    """Base class for a local file system."""

    async def info(self, path: PathType, **kwargs: Any) -> FileInfo:
        """Retrieve information about a given file path.

        Args:
            path: A file path.
            **kwargs: Any additional kwargs.

        Returns:
            A dictionary of file info.
        """
        result = await Path(path).stat()
        return await FileSystemAdapter.parse_stat_result(path=path, result=result)

    async def open(self, file: PathType, mode: str, buffering: int = -1) -> AsyncFile[AnyStr]:  # pyright: ignore
        """Return a file-like object from the filesystem.

        Notes:
            - The return value must be a context-manager

        Args:
            file: Path to the target file.
            mode: Mode, similar to the built ``open``.
            buffering: Buffer size.
        """
        return await open_file(file=file, mode=mode, buffering=buffering)  # type: ignore[call-overload, no-any-return]


class FileSystemAdapter:
    """Wrapper around a ``FileSystemProtocol``, normalising its interface."""

    def __init__(self, file_system: FileSystemProtocol) -> None:
        """Initialize an adapter from a given ``file_system``

        Args:
            file_system: A filesystem class adhering to the :class:`FileSystemProtocol <litestar.types.FileSystemProtocol>`
        """
        self.file_system = file_system

    async def info(self, path: PathType) -> FileInfo:
        """Proxies the call to the underlying FS Spec's ``info`` method, ensuring it's done in an async fashion and with
        strong typing.

        Args:
            path: A file path to load the info for.

        Returns:
            A dictionary of file info.
        """
        try:
            awaitable = (
                self.file_system.info(str(path))
                if is_async_callable(self.file_system.info)
                else sync_to_thread(self.file_system.info, str(path))
            )
            return cast("FileInfo", await awaitable)
        except FileNotFoundError as e:
            raise e
        except PermissionError as e:
            raise NotAuthorizedException(f"failed to read {path} due to missing permissions") from e
        except OSError as e:  # pragma: no cover
            raise InternalServerException from e

    async def open(
        self,
        file: PathType,
        mode: OpenBinaryMode = "rb",
        buffering: int = -1,
    ) -> AsyncFile[bytes]:
        """Return a file-like object from the filesystem.

        Notes:
            - The return value must function correctly in a context ``with`` block.

        Args:
            file: Path to the target file.
            mode: Mode, similar to the built ``open``.
            buffering: Buffer size.
        """
        try:
            if is_async_callable(self.file_system.open):  # pyright: ignore
                return cast(
                    "AsyncFile[bytes]",
                    await self.file_system.open(
                        file=file,
                        mode=mode,
                        buffering=buffering,
                    ),
                )
            return AsyncFile(await sync_to_thread(self.file_system.open, file, mode, buffering))  # type: ignore[arg-type]
        except PermissionError as e:
            raise NotAuthorizedException(f"failed to open {file} due to missing permissions") from e
        except OSError as e:
            raise InternalServerException from e

    @staticmethod
    async def parse_stat_result(path: PathType, result: stat_result) -> FileInfo:
        """Convert a ``stat_result`` instance into a ``FileInfo``.

        Args:
            path: The file path for which the :func:`stat_result <os.stat_result>` is provided.
            result: The :func:`stat_result <os.stat_result>` instance.

        Returns:
            A dictionary of file info.
        """
        file_info: FileInfo = {
            "created": result.st_ctime,
            "gid": result.st_gid,
            "ino": result.st_ino,
            "islink": await Path(path).is_symlink(),
            "mode": result.st_mode,
            "mtime": result.st_mtime,
            "name": str(path),
            "nlink": result.st_nlink,
            "size": result.st_size,
            "type": "directory" if S_ISDIR(result.st_mode) else "file",
            "uid": result.st_uid,
        }

        if file_info["islink"]:
            file_info["destination"] = str(await Path(path).readlink()).encode("utf-8")
            try:
                file_info["size"] = (await Path(path).stat()).st_size
            except OSError:  # pragma: no cover
                file_info["size"] = result.st_size

        return file_info
