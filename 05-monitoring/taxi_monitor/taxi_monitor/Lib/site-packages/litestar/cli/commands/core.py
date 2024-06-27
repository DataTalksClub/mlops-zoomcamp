from __future__ import annotations

import inspect
import multiprocessing
import os
import subprocess
import sys
from contextlib import AbstractContextManager, ExitStack, contextmanager
from typing import TYPE_CHECKING, Any, Iterator

try:
    import rich_click as click
except ImportError:
    import click  # type: ignore[no-redef]
from rich.tree import Tree

from litestar.app import DEFAULT_OPENAPI_CONFIG
from litestar.cli._utils import (
    UVICORN_INSTALLED,
    LitestarEnv,
    console,
    create_ssl_files,
    isatty,
    remove_default_schema_routes,
    remove_routes_with_patterns,
    show_app_info,
    validate_ssl_file_paths,
)
from litestar.routes import ASGIRoute, HTTPRoute, WebSocketRoute
from litestar.utils.helpers import unwrap_partial

__all__ = ("info_command", "routes_command", "run_command")

if TYPE_CHECKING:
    from litestar import Litestar


@contextmanager
def _server_lifespan(app: Litestar) -> Iterator[None]:
    """Context manager handling the ASGI server lifespan.

    It will be entered just before the ASGI server is started through the CLI.
    """
    with ExitStack() as exit_stack:
        for manager in app._server_lifespan_managers:
            if not isinstance(manager, AbstractContextManager):
                manager = manager(app)  # type: ignore[assignment]
            exit_stack.enter_context(manager)  # type: ignore[arg-type]

        yield


def _convert_uvicorn_args(args: dict[str, Any]) -> list[str]:
    process_args = []
    for arg, value in args.items():
        if isinstance(value, bool):
            if value:
                process_args.append(f"--{arg}")
        elif isinstance(value, tuple):
            process_args.extend(f"--{arg}={item}" for item in value)
        else:
            process_args.append(f"--{arg}={value}")

    return process_args


def _run_uvicorn_in_subprocess(
    *,
    env: LitestarEnv,
    host: str | None,
    port: int | None,
    workers: int | None,
    reload: bool,
    reload_dirs: tuple[str, ...] | None,
    reload_include: tuple[str, ...] | None,
    reload_exclude: tuple[str, ...] | None,
    fd: int | None,
    uds: str | None,
    certfile_path: str | None,
    keyfile_path: str | None,
) -> None:
    process_args: dict[str, Any] = {
        "reload": reload,
        "host": host,
        "port": port,
        "workers": workers,
        "factory": env.is_app_factory,
    }
    if fd is not None:
        process_args["fd"] = fd
    if uds is not None:
        process_args["uds"] = uds
    if reload_dirs:
        process_args["reload-dir"] = reload_dirs
    if reload_include:
        process_args["reload-include"] = reload_include
    if reload_exclude:
        process_args["reload-exclude"] = reload_exclude
    if certfile_path is not None:
        process_args["ssl-certfile"] = certfile_path
    if keyfile_path is not None:
        process_args["ssl-keyfile"] = keyfile_path
    subprocess.run(
        [sys.executable, "-m", "uvicorn", env.app_path, *_convert_uvicorn_args(process_args)],  # noqa: S603
        check=True,
    )


class CommaSplittedPath(click.Path):
    """A Click Path that splits the input string by commas.

    .. versionadded:: 2.8.0
    """

    envvar_list_splitter = ","


@click.command(name="version")
@click.option("-s", "--short", help="Exclude release level and serial information", is_flag=True, default=False)
def version_command(short: bool) -> None:
    """Show the currently installed Litestar version."""
    from litestar import __version__

    click.echo(__version__.formatted(short=short))


@click.command(name="info")
def info_command(app: Litestar) -> None:
    """Show information about the detected Litestar app."""

    show_app_info(app)


@click.command(name="run")
@click.option("-r", "--reload", help="Reload server on changes", default=False, is_flag=True, envvar="LITESTAR_RELOAD")
@click.option(
    "-R",
    "--reload-dir",
    help="Directories to watch for file changes",
    type=CommaSplittedPath(),
    multiple=True,
    envvar="LITESTAR_RELOAD_DIRS",
)
@click.option(
    "-I",
    "--reload-include",
    help="Glob patterns for files to include when watching for file changes",
    type=CommaSplittedPath(),
    multiple=True,
    envvar="LITESTAR_RELOAD_INCLUDES",
)
@click.option(
    "-E",
    "--reload-exclude",
    help="Glob patterns for files to exclude when watching for file changes",
    type=CommaSplittedPath(),
    multiple=True,
    envvar="LITESTAR_RELOAD_EXCLUDES",
)
@click.option(
    "-p", "--port", help="Serve under this port", type=int, default=8000, show_default=True, envvar="LITESTAR_PORT"
)
@click.option(
    "-W",
    "--wc",
    "--web-concurrency",
    help="The number of HTTP workers to launch",
    type=click.IntRange(min=1, max=multiprocessing.cpu_count() + 1),
    show_default=True,
    default=1,
    envvar=["LITESTAR_WEB_CONCURRENCY", "WEB_CONCURRENCY"],
)
@click.option(
    "-H", "--host", help="Server under this host", default="127.0.0.1", show_default=True, envvar="LITESTAR_HOST"
)
@click.option(
    "-F",
    "--fd",
    "--file-descriptor",
    help="Bind to a socket from this file descriptor.",
    type=int,
    default=None,
    show_default=True,
    envvar="LITESTAR_FILE_DESCRIPTOR",
)
@click.option(
    "-U",
    "--uds",
    "--unix-domain-socket",
    help="Bind to a UNIX domain socket.",
    default=None,
    show_default=True,
    envvar="LITESTAR_UNIX_DOMAIN_SOCKET",
)
@click.option("-d", "--debug", help="Run app in debug mode", is_flag=True, envvar="LITESTAR_DEBUG")
@click.option("-P", "--pdb", "--use-pdb", help="Drop into PDB on an exception", is_flag=True, envvar="LITESTAR_PDB")
@click.option("--ssl-certfile", help="Location of the SSL cert file", default=None, envvar="LITESTAR_SSL_CERT_PATH")
@click.option("--ssl-keyfile", help="Location of the SSL key file", default=None, envvar="LITESTAR_SSL_KEY_PATH")
@click.option(
    "--create-self-signed-cert",
    help="If certificate and key are not found at specified locations, create a self-signed certificate and a key",
    is_flag=True,
    envvar="LITESTAR_CREATE_SELF_SIGNED_CERT",
)
def run_command(
    reload: bool,
    port: int,
    wc: int,
    host: str,
    fd: int | None,
    uds: str | None,
    debug: bool,
    reload_dir: tuple[str, ...],
    reload_include: tuple[str, ...],
    reload_exclude: tuple[str, ...],
    pdb: bool,
    ssl_certfile: str | None,
    ssl_keyfile: str | None,
    create_self_signed_cert: bool,
    ctx: click.Context,
) -> None:
    """Run a Litestar app; requires ``uvicorn``.

    The app can be either passed as a module path in the form of <module name>.<submodule>:<app instance or factory>,
    set as an environment variable LITESTAR_APP with the same format or automatically discovered from one of these
    canonical paths: app.py, asgi.py, application.py or app/__init__.py. When auto-discovering application factories,
    functions with the name ``create_app`` are considered, or functions that are annotated as returning a ``Litestar``
    instance.
    """

    if debug:
        os.environ["LITESTAR_DEBUG"] = "1"

    if pdb:
        os.environ["LITESTAR_PDB"] = "1"
    quiet_console = os.getenv("LITESTAR_QUIET_CONSOLE") or False
    if not UVICORN_INSTALLED:
        console.print(
            r"uvicorn is not installed. Please install the standard group, litestar\[standard], to use this command."
        )
        sys.exit(1)

    if callable(ctx.obj):
        ctx.obj = ctx.obj()
    else:
        if debug:
            ctx.obj.app.debug = True
        if pdb:
            ctx.obj.app.pdb_on_exception = True

    env: LitestarEnv = ctx.obj
    app = env.app

    reload = reload or bool(reload_dir) or bool(reload_include) or bool(reload_exclude)
    workers = wc

    certfile_path, keyfile_path = (
        create_ssl_files(ssl_certfile, ssl_keyfile, host)
        if create_self_signed_cert
        else validate_ssl_file_paths(ssl_certfile, ssl_keyfile)
    )

    if not quiet_console and isatty():
        console.rule("[yellow]Starting server process", align="left")
        show_app_info(app)
    with _server_lifespan(app):
        if workers == 1 and not reload:
            import uvicorn

            # A guard statement at the beginning of this function prevents uvicorn from being unbound
            # See "reportUnboundVariable in:
            # https://microsoft.github.io/pyright/#/configuration?id=type-check-diagnostics-settings
            uvicorn.run(  # pyright: ignore
                app=env.app_path,
                host=host,
                port=port,
                fd=fd,
                uds=uds,
                factory=env.is_app_factory,
                ssl_certfile=certfile_path,
                ssl_keyfile=keyfile_path,
            )
        else:
            # invoke uvicorn in a subprocess to be able to use the --reload flag. see
            # https://github.com/litestar-org/litestar/issues/1191 and https://github.com/encode/uvicorn/issues/1045
            if sys.gettrace() is not None:
                console.print(
                    "[yellow]Debugger detected. Breakpoints might not work correctly inside route handlers when running"
                    " with the --reload or --workers options[/]"
                )

            _run_uvicorn_in_subprocess(
                env=env,
                host=host,
                port=port,
                workers=workers,
                reload=reload,
                reload_dirs=reload_dir,
                reload_include=reload_include,
                reload_exclude=reload_exclude,
                fd=fd,
                uds=uds,
                certfile_path=certfile_path,
                keyfile_path=keyfile_path,
            )


@click.command(name="routes")
@click.option("--schema", help="Include schema routes", is_flag=True, default=False)
@click.option("--exclude", help="routes to exclude via regex", type=str, is_flag=False, multiple=True)
def routes_command(app: Litestar, exclude: tuple[str, ...], schema: bool) -> None:  # pragma: no cover
    """Display information about the application's routes."""

    sorted_routes = sorted(app.routes, key=lambda r: r.path)
    if not schema:
        openapi_config = app.openapi_config or DEFAULT_OPENAPI_CONFIG
        sorted_routes = remove_default_schema_routes(sorted_routes, openapi_config)
    if exclude is not None:
        sorted_routes = remove_routes_with_patterns(sorted_routes, exclude)

    console.print(_RouteTree(sorted_routes))


class _RouteTree(Tree):
    def __init__(self, routes: list[HTTPRoute | ASGIRoute | WebSocketRoute]) -> None:
        super().__init__("", hide_root=True)
        self._routes = routes
        self._build()

    def _build(self) -> None:
        for route in self._routes:
            if isinstance(route, HTTPRoute):
                self._handle_http_route(route)
            elif isinstance(route, WebSocketRoute):
                self._handle_websocket_route(route)
            else:
                self._handle_asgi_route(route)

    def _handle_asgi_like_route(self, route: ASGIRoute | WebSocketRoute, route_type: str) -> None:
        branch = self.add(f"[green]{route.path}[/green] ({route_type})")
        branch.add(f"[blue]{route.route_handler.name or route.route_handler.handler_name}[/blue]")

    def _handle_asgi_route(self, route: ASGIRoute) -> None:
        self._handle_asgi_like_route(route, route_type="ASGI")

    def _handle_websocket_route(self, route: WebSocketRoute) -> None:
        self._handle_asgi_like_route(route, route_type="WS")

    def _handle_http_route(self, route: HTTPRoute) -> None:
        branch = self.add(f"[green]{route.path}[/green] (HTTP)")
        for handler in route.route_handlers:
            handler_info = [
                f"[blue]{handler.name or handler.handler_name}[/blue]",
            ]

            if inspect.iscoroutinefunction(unwrap_partial(handler.fn)):
                handler_info.append("[magenta]async[/magenta]")
            else:
                handler_info.append("[yellow]sync[/yellow]")

            handler_info.append(f'[cyan]{", ".join(sorted(handler.http_methods))}[/cyan]')

            if len(handler.paths) > 1:
                for path in handler.paths:
                    branch.add(" ".join([f"[green]{path}[green]", *handler_info]))
            else:
                branch.add(" ".join(handler_info))
