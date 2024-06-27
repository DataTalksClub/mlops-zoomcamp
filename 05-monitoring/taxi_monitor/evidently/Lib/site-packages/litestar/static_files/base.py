# ruff: noqa: PTH118
from __future__ import annotations

import os.path
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Sequence

from litestar.enums import ScopeType
from litestar.exceptions import MethodNotAllowedException, NotFoundException
from litestar.file_system import FileSystemAdapter
from litestar.response.file import ASGIFileResponse
from litestar.status_codes import HTTP_404_NOT_FOUND

__all__ = ("StaticFiles",)

if TYPE_CHECKING:
    from litestar.types import Receive, Scope, Send
    from litestar.types.composite_types import PathType
    from litestar.types.file_types import FileInfo, FileSystemProtocol


class StaticFiles:
    """ASGI App that handles file sending."""

    __slots__ = ("is_html_mode", "directories", "adapter", "send_as_attachment", "headers")

    def __init__(
        self,
        is_html_mode: bool,
        directories: Sequence[PathType],
        file_system: FileSystemProtocol,
        send_as_attachment: bool = False,
        resolve_symlinks: bool = True,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Initialize the Application.

        Args:
            is_html_mode: Flag dictating whether serving html. If true, the default file will be ``index.html``.
            directories: A list of directories to serve files from.
            file_system: The file_system spec to use for serving files.
            send_as_attachment: Whether to send the file with a ``content-disposition`` header of
             ``attachment`` or ``inline``
            resolve_symlinks: Resolve symlinks to the directories
            headers: Headers that will be sent with every response.
        """
        self.adapter = FileSystemAdapter(file_system)
        self.directories = tuple(
            os.path.normpath(Path(p).resolve() if resolve_symlinks else Path(p)) for p in directories
        )
        self.is_html_mode = is_html_mode
        self.send_as_attachment = send_as_attachment
        self.headers = headers

    async def get_fs_info(
        self, directories: Sequence[PathType], file_path: PathType
    ) -> tuple[Path, FileInfo] | tuple[None, None]:
        """Return the resolved path and a :class:`stat_result <os.stat_result>`.

        .. versionchanged:: 2.8.3

            Prevent `CVE-2024-32982 <https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-32982>`_
            by ensuring that the resolved path is within the configured directory as part of `advisory
            GHSA-83pv-qr33-2vcf <https://github.com/advisories/GHSA-83pv-qr33-2vcf>`_.

        Args:
            directories: A list of directory paths.
            file_path: A file path to resolve

        Returns:
            A tuple with an optional resolved :class:`Path <anyio.Path>` instance and an optional
            :class:`stat_result <os.stat_result>`.
        """
        for directory in directories:
            try:
                joined_path = Path(directory, file_path)
                normalized_file_path = os.path.normpath(joined_path)
                if os.path.commonpath([directory, normalized_file_path]) == str(directory) and (
                    file_info := await self.adapter.info(joined_path)
                ):
                    return joined_path, file_info
            except FileNotFoundError:
                continue
        return None, None

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI callable.

        Args:
            scope: ASGI scope
            receive: ASGI ``receive`` callable
            send: ASGI ``send`` callable

        Returns:
            None
        """
        if scope["type"] != ScopeType.HTTP or scope["method"] not in {"GET", "HEAD"}:
            raise MethodNotAllowedException()

        res = await self.handle(path=scope["path"], is_head_response=scope["method"] == "HEAD")
        await res(scope=scope, receive=receive, send=send)

    async def handle(self, path: str, is_head_response: bool) -> ASGIFileResponse:
        split_path = path.split("/")
        filename = split_path[-1]
        joined_path = Path(*split_path)
        resolved_path, fs_info = await self.get_fs_info(directories=self.directories, file_path=joined_path)
        content_disposition_type: Literal["inline", "attachment"] = (
            "attachment" if self.send_as_attachment else "inline"
        )

        if self.is_html_mode and fs_info and fs_info["type"] == "directory":
            filename = "index.html"
            resolved_path, fs_info = await self.get_fs_info(
                directories=self.directories,
                file_path=Path(resolved_path or joined_path) / filename,
            )

        if fs_info and fs_info["type"] == "file":
            return ASGIFileResponse(
                file_path=resolved_path or joined_path,
                file_info=fs_info,
                file_system=self.adapter.file_system,
                filename=filename,
                content_disposition_type=content_disposition_type,
                is_head_response=is_head_response,
                headers=self.headers,
            )

        if self.is_html_mode:
            # for some reason coverage doesn't catch these two lines
            filename = "404.html"  # pragma: no cover
            resolved_path, fs_info = await self.get_fs_info(  # pragma: no cover
                directories=self.directories, file_path=filename
            )

            if fs_info and fs_info["type"] == "file":
                return ASGIFileResponse(
                    file_path=resolved_path or joined_path,
                    file_info=fs_info,
                    file_system=self.adapter.file_system,
                    filename=filename,
                    status_code=HTTP_404_NOT_FOUND,
                    content_disposition_type=content_disposition_type,
                    is_head_response=is_head_response,
                    headers=self.headers,
                )

        raise NotFoundException(
            f"no file or directory match the path {resolved_path or joined_path} was found"
        )  # pragma: no cover
