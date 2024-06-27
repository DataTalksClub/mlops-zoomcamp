from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePath  # noqa: TCH003
from typing import TYPE_CHECKING, Any, Sequence

from litestar.exceptions import ImproperlyConfiguredException
from litestar.file_system import BaseLocalFileSystem
from litestar.handlers import asgi, get, head
from litestar.response.file import ASGIFileResponse  # noqa: TCH001
from litestar.router import Router
from litestar.static_files.base import StaticFiles
from litestar.utils import normalize_path, warn_deprecation

__all__ = ("StaticFilesConfig",)

if TYPE_CHECKING:
    from litestar.datastructures import CacheControlHeader
    from litestar.handlers.asgi_handlers import ASGIRouteHandler
    from litestar.openapi.spec import SecurityRequirement
    from litestar.types import (
        AfterRequestHookHandler,
        AfterResponseHookHandler,
        BeforeRequestHookHandler,
        EmptyType,
        ExceptionHandlersMap,
        Guard,
        Middleware,
        PathType,
    )


@dataclass
class StaticFilesConfig:
    """Configuration for static file service.

    To enable static files, pass an instance of this class to the :class:`Litestar <litestar.app.Litestar>` constructor using
    the 'static_files_config' key.
    """

    path: str
    """Path to serve static files from.

    Note that the path cannot contain path parameters.
    """
    directories: list[PathType]
    """A list of directories to serve files from."""
    html_mode: bool = False
    """Flag dictating whether serving html.

    If true, the default file will be 'index.html'.
    """
    name: str | None = None
    """An optional string identifying the static files handler."""
    file_system: Any = BaseLocalFileSystem()  # noqa: RUF009
    """The file_system spec to use for serving files.

    Notes:
        - A file_system is a class that adheres to the
            :class:`FileSystemProtocol <litestar.types.FileSystemProtocol>`.
        - You can use any of the file systems exported from the
            [fsspec](https://filesystem-spec.readthedocs.io/en/latest/) library for this purpose.
    """
    opt: dict[str, Any] | None = None
    """A string key dictionary of arbitrary values that will be added to the static files handler."""
    guards: list[Guard] | None = None
    """A list of :class:`Guard <litestar.types.Guard>` callables."""
    exception_handlers: ExceptionHandlersMap | None = None
    """A dictionary that maps handler functions to status codes and/or exception types."""
    send_as_attachment: bool = False
    """Whether to send the file as an attachment."""

    def __post_init__(self) -> None:
        _validate_config(path=self.path, directories=self.directories, file_system=self.file_system)
        self.path = normalize_path(self.path)
        warn_deprecation(
            "2.6.0",
            kind="class",
            deprecated_name="StaticFilesConfig",
            removal_in="3.0",
            alternative="create_static_files_router",
            info='Replace static_files_config=[StaticFilesConfig(path="/static", directories=["assets"])] with '
            'route_handlers=[..., create_static_files_router(path="/static", directories=["assets"])]',
        )

    def to_static_files_app(self) -> ASGIRouteHandler:
        """Return an ASGI app serving static files based on the config.

        Returns:
            :class:`StaticFiles <litestar.static_files.StaticFiles>`
        """
        static_files = StaticFiles(
            is_html_mode=self.html_mode,
            directories=self.directories,
            file_system=self.file_system,
            send_as_attachment=self.send_as_attachment,
        )
        return asgi(
            path=self.path,
            name=self.name,
            is_static=True,
            opt=self.opt,
            guards=self.guards,
            exception_handlers=self.exception_handlers,
        )(static_files)


def create_static_files_router(
    path: str,
    directories: list[PathType],
    file_system: Any = None,
    send_as_attachment: bool = False,
    html_mode: bool = False,
    name: str = "static",
    after_request: AfterRequestHookHandler | None = None,
    after_response: AfterResponseHookHandler | None = None,
    before_request: BeforeRequestHookHandler | None = None,
    cache_control: CacheControlHeader | None = None,
    exception_handlers: ExceptionHandlersMap | None = None,
    guards: list[Guard] | None = None,
    include_in_schema: bool | EmptyType = False,
    middleware: Sequence[Middleware] | None = None,
    opt: dict[str, Any] | None = None,
    security: Sequence[SecurityRequirement] | None = None,
    tags: Sequence[str] | None = None,
    router_class: type[Router] = Router,
    resolve_symlinks: bool = True,
) -> Router:
    """Create a router with handlers to serve static files.

    Args:
        path: Path to serve static files under
        directories: Directories to serve static files from
        file_system: A *file system* implementing
            :class:`~litestar.types.FileSystemProtocol`.
            `fsspec <https://filesystem-spec.readthedocs.io/en/latest/>`_ can be passed
            here as well
        send_as_attachment: Whether to send the file as an attachment
        html_mode: When in HTML:
            - Serve an ``index.html`` file from ``/``
            - Serve ``404.html`` when a file could not be found
        name: Name to pass to the generated handlers
        after_request: ``after_request`` handlers passed to the router
        after_response: ``after_response`` handlers passed to the router
        before_request: ``before_request`` handlers passed to the router
        cache_control: ``cache_control`` passed to the router
        exception_handlers: Exception handlers passed to the router
        guards: Guards  passed to the router
        include_in_schema: Include the routes / router in the OpenAPI schema
        middleware: Middlewares passed to the router
        opt: Opts passed to the router
        security: Security options passed to the router
        tags: ``tags`` passed to the router
        router_class: The class used to construct a router from
        resolve_symlinks: Resolve symlinks of ``directories``
    """

    if file_system is None:
        file_system = BaseLocalFileSystem()

    _validate_config(path=path, directories=directories, file_system=file_system)
    path = normalize_path(path)

    headers = None
    if cache_control:
        headers = {cache_control.HEADER_NAME: cache_control.to_header()}

    static_files = StaticFiles(
        is_html_mode=html_mode,
        directories=directories,
        file_system=file_system,
        send_as_attachment=send_as_attachment,
        resolve_symlinks=resolve_symlinks,
        headers=headers,
    )

    @get("{file_path:path}", name=name)
    async def get_handler(file_path: PurePath) -> ASGIFileResponse:
        return await static_files.handle(path=file_path.as_posix(), is_head_response=False)

    @head("/{file_path:path}", name=f"{name}/head")
    async def head_handler(file_path: PurePath) -> ASGIFileResponse:
        return await static_files.handle(path=file_path.as_posix(), is_head_response=True)

    handlers = [get_handler, head_handler]

    if html_mode:

        @get("/", name=f"{name}/index")
        async def index_handler() -> ASGIFileResponse:
            return await static_files.handle(path="/", is_head_response=False)

        handlers.append(index_handler)

    return router_class(
        after_request=after_request,
        after_response=after_response,
        before_request=before_request,
        cache_control=cache_control,
        exception_handlers=exception_handlers,
        guards=guards,
        include_in_schema=include_in_schema,
        middleware=middleware,
        opt=opt,
        path=path,
        route_handlers=handlers,
        security=security,
        tags=tags,
    )


def _validate_config(path: str, directories: list[PathType], file_system: Any) -> None:
    if not path:
        raise ImproperlyConfiguredException("path must be a non-zero length string,")

    if not directories or not any(bool(d) for d in directories):
        raise ImproperlyConfiguredException("directories must include at least one path.")

    if "{" in path:
        raise ImproperlyConfiguredException("path parameters are not supported for static files")

    if not (callable(getattr(file_system, "info", None)) and callable(getattr(file_system, "open", None))):
        raise ImproperlyConfiguredException("file_system must adhere to the FileSystemProtocol type")
