from __future__ import annotations

import contextlib
import importlib
import inspect
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from functools import wraps
from importlib.util import find_spec
from itertools import chain
from os import getenv
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Generator, Iterable, Sequence, TypeVar, cast

try:
    from rich_click import RichCommand as Command
    from rich_click import RichGroup as Group
except ImportError:
    from click import Command, Group  # type: ignore[assignment]

from click import ClickException, Context, pass_context
from rich import get_console
from rich.table import Table
from typing_extensions import ParamSpec, get_type_hints

from litestar import Litestar, __version__
from litestar.middleware import DefineMiddleware
from litestar.utils import get_name

if sys.version_info >= (3, 10):
    from importlib.metadata import entry_points
else:
    from importlib_metadata import entry_points


if TYPE_CHECKING:
    from litestar.openapi import OpenAPIConfig
    from litestar.routes import ASGIRoute, HTTPRoute, WebSocketRoute
    from litestar.types import AnyCallable


UVICORN_INSTALLED = find_spec("uvicorn") is not None
JSBEAUTIFIER_INSTALLED = find_spec("jsbeautifier") is not None


__all__ = (
    "UVICORN_INSTALLED",
    "JSBEAUTIFIER_INSTALLED",
    "LoadedApp",
    "LitestarCLIException",
    "LitestarEnv",
    "LitestarExtensionGroup",
    "LitestarGroup",
    "show_app_info",
)


P = ParamSpec("P")
T = TypeVar("T")


AUTODISCOVERY_FILE_NAMES = ["app", "application"]

console = get_console()


class LitestarCLIException(ClickException):
    """Base class for Litestar CLI exceptions."""

    def __init__(self, message: str) -> None:
        """Initialize exception and style error message."""
        super().__init__(message)


@dataclass
class LitestarEnv:
    """Information about the current Litestar environment variables."""

    app_path: str
    app: Litestar
    cwd: Path
    host: str | None = None
    port: int | None = None
    is_app_factory: bool = False

    @classmethod
    def from_env(cls, app_path: str | None, app_dir: Path | None = None) -> LitestarEnv:
        """Load environment variables.

        If ``python-dotenv`` is installed, use it to populate environment first
        """
        cwd = Path().cwd() if app_dir is None else app_dir
        cwd_str_path = str(cwd)
        if cwd_str_path not in sys.path:
            sys.path.append(cwd_str_path)

        with contextlib.suppress(ImportError):
            import dotenv

            dotenv.load_dotenv()
        app_path = app_path or getenv("LITESTAR_APP")
        app_name = getenv("LITESTAR_APP_NAME") or "Litestar"
        quiet_console = getenv("LITESTAR_QUIET_CONSOLE") or False
        if app_path and getenv("LITESTAR_APP") is None:
            os.environ["LITESTAR_APP"] = app_path
        if app_path:
            if not quiet_console and isatty():
                console.print(f"Using {app_name} app from env: [bright_blue]{app_path!r}")
            loaded_app = _load_app_from_path(app_path)
        else:
            loaded_app = _autodiscover_app(cwd)

        port = getenv("LITESTAR_PORT")

        return cls(
            app_path=loaded_app.app_path,
            app=loaded_app.app,
            host=getenv("LITESTAR_HOST"),
            port=int(port) if port else None,
            is_app_factory=loaded_app.is_factory,
            cwd=cwd,
        )


@dataclass
class LoadedApp:
    """Information about a loaded Litestar app."""

    app: Litestar
    app_path: str
    is_factory: bool


class LitestarGroup(Group):  # pyright: ignore
    """:class:`click.Group` subclass that automatically injects ``app`` and ``env` kwargs into commands that request it.

    Use this as the ``cls`` for :class:`click.Group` if you're extending the internal CLI with a group. For ``command``s
    added directly to the root group this is not needed.
    """

    def __init__(
        self,
        name: str | None = None,
        commands: dict[str, Command] | Sequence[Command] | None = None,
        **attrs: Any,
    ) -> None:
        """Init ``LitestarGroup``"""
        self.group_class = LitestarGroup
        super().__init__(name=name, commands=commands, **attrs)

    def add_command(self, cmd: Command, name: str | None = None) -> None:  # type: ignore[override]
        """Add command.

        If necessary, inject ``app`` and ``env`` kwargs
        """
        if cmd.callback:
            cmd.callback = _inject_args(cmd.callback)
        super().add_command(cmd)

    def command(self, *args: Any, **kwargs: Any) -> Callable[[AnyCallable], Command] | Command:  # type: ignore[override]
        # For some reason, even when copying the overloads + signature from click 1:1, mypy goes haywire
        """Add a function as a command.

        If necessary, inject ``app`` and ``env`` kwargs
        """

        def decorator(f: AnyCallable) -> Command:
            f = _inject_args(f)
            return cast("Command", Group.command(self, *args, **kwargs)(f))

        return decorator


class LitestarExtensionGroup(LitestarGroup):
    """``LitestarGroup`` subclass that will load Litestar-CLI extensions from the `litestar.commands` entry_point.

    This group class should not be used on any group besides the root ``litestar_group``.
    """

    def __init__(
        self,
        name: str | None = None,
        commands: dict[str, Command] | Sequence[Command] | None = None,
        **attrs: Any,
    ) -> None:
        """Init ``LitestarExtensionGroup``"""
        super().__init__(name=name, commands=commands, **attrs)
        self._prepare_done = False

        for entry_point in entry_points(group="litestar.commands"):
            command = entry_point.load()
            _wrap_commands([command])
            self.add_command(command, entry_point.name)

    def _prepare(self, ctx: Context) -> None:
        if self._prepare_done:
            return

        if isinstance(ctx.obj, LitestarEnv):
            env: LitestarEnv | None = ctx.obj
        else:
            try:
                env = ctx.obj = LitestarEnv.from_env(ctx.params.get("app_path"), ctx.params.get("app_dir"))
            except LitestarCLIException:
                env = None

        if env:
            for plugin in env.app.plugins.cli:
                plugin.on_cli_init(self)

        self._prepare_done = True

    def make_context(  # type: ignore[override]
        self,
        info_name: str | None,
        args: list[str],
        parent: Context | None = None,
        **extra: Any,
    ) -> Context:
        ctx = super().make_context(info_name, args, parent, **extra)
        self._prepare(ctx)
        return ctx

    def list_commands(self, ctx: Context) -> list[str]:
        self._prepare(ctx)
        return super().list_commands(ctx)


def _inject_args(func: Callable[P, T]) -> Callable[P, T]:
    """Inject the app instance into a ``Command``"""
    params = inspect.signature(func).parameters

    @wraps(func)
    def wrapped(ctx: Context, /, *args: P.args, **kwargs: P.kwargs) -> T:
        needs_app = "app" in params
        needs_env = "env" in params
        if needs_env or needs_app:
            # only resolve this if actually requested. Commands that don't need an env or app should be able to run
            # without
            if not isinstance(ctx.obj, LitestarEnv):
                ctx.obj = ctx.obj()
            env = ctx.ensure_object(LitestarEnv)
            if needs_app:
                kwargs["app"] = env.app
            if needs_env:
                kwargs["env"] = env

        if "ctx" in params:
            kwargs["ctx"] = ctx

        return func(*args, **kwargs)

    return pass_context(wrapped)


def _wrap_commands(commands: Iterable[Command]) -> None:
    for command in commands:
        if hasattr(command, "commands"):
            _wrap_commands(command.commands.values())  # pyright: ignore[reportGeneralTypeIssues]
        elif command.callback:
            command.callback = _inject_args(command.callback)


def _bool_from_env(key: str, default: bool = False) -> bool:
    value = getenv(key)
    if not value:
        return default
    value = value.lower()
    return value in ("true", "1")


def _load_app_from_path(app_path: str) -> LoadedApp:
    module_path, app_name = app_path.split(":")
    module = importlib.import_module(module_path)
    app = getattr(module, app_name)
    is_factory = False
    if not isinstance(app, Litestar) and callable(app):
        app = app()
        is_factory = True
    return LoadedApp(app=app, app_path=app_path, is_factory=is_factory)


def _path_to_dotted_path(path: Path) -> str:
    if path.stem == "__init__":
        path = path.parent
    return ".".join(path.with_suffix("").parts)


def _arbitrary_autodiscovery_paths(base_dir: Path) -> Generator[Path, None, None]:
    yield from _autodiscovery_paths(base_dir, arbitrary=False)
    for path in base_dir.iterdir():
        if path.name.startswith(".") or path.name.startswith("_"):
            continue
        if path.is_file() and path.suffix == ".py":
            yield path


def _autodiscovery_paths(base_dir: Path, arbitrary: bool = True) -> Generator[Path, None, None]:
    for name in AUTODISCOVERY_FILE_NAMES:
        path = base_dir / name

        if path.exists() or path.with_suffix(".py").exists():
            yield path
        if arbitrary and path.is_dir():
            yield from _arbitrary_autodiscovery_paths(path)


def _autodiscover_app(cwd: Path) -> LoadedApp:
    app_name = getenv("LITESTAR_APP_NAME") or "Litestar"
    quiet_console = getenv("LITESTAR_QUIET_CONSOLE") or False
    for file_path in _autodiscovery_paths(cwd):
        import_path = _path_to_dotted_path(file_path.relative_to(cwd))
        module = importlib.import_module(import_path)

        for attr, value in chain(
            [("app", getattr(module, "app", None)), ("application", getattr(module, "application", None))],
            module.__dict__.items(),
        ):
            if isinstance(value, Litestar):
                app_string = f"{import_path}:{attr}"
                os.environ["LITESTAR_APP"] = app_string
                if not quiet_console and isatty():
                    console.print(f"Using {app_name} app from [bright_blue]{app_string}")
                return LoadedApp(app=value, app_path=app_string, is_factory=False)

        if hasattr(module, "create_app"):
            app_string = f"{import_path}:create_app"
            os.environ["LITESTAR_APP"] = app_string
            if not quiet_console and isatty():
                console.print(f"Using {app_name} factory from [bright_blue]{app_string}")
            return LoadedApp(app=module.create_app(), app_path=app_string, is_factory=True)

        for attr, value in module.__dict__.items():
            if not callable(value):
                continue
            return_annotation = (
                get_type_hints(value, include_extras=True).get("return") if hasattr(value, "__annotations__") else None
            )
            if not return_annotation:
                continue
            if return_annotation in ("Litestar", Litestar):
                app_string = f"{import_path}:{attr}"
                os.environ["LITESTAR_APP"] = app_string
                if not quiet_console and sys.stdout.isatty():
                    console.print(f"Using {app_name} factory from [bright_blue]{app_string}")
                return LoadedApp(app=value(), app_path=f"{app_string}", is_factory=True)

    raise LitestarCLIException(f"Could not find {app_name} instance or factory")


def _format_is_enabled(value: Any) -> str:
    """Return a coloured string `"Enabled" if ``value`` is truthy, else "Disabled"."""
    return "[green]Enabled[/]" if value else "[red]Disabled[/]"


def show_app_info(app: Litestar) -> None:  # pragma: no cover
    """Display basic information about the application and its configuration."""

    table = Table(show_header=False)
    table.add_column("title", style="cyan")
    table.add_column("value", style="bright_blue")

    table.add_row("Litestar version", f"{__version__.major}.{__version__.minor}.{__version__.patch}")
    table.add_row("Debug mode", _format_is_enabled(app.debug))
    table.add_row("Python Debugger on exception", _format_is_enabled(app.pdb_on_exception))
    table.add_row("CORS", _format_is_enabled(app.cors_config))
    table.add_row("CSRF", _format_is_enabled(app.csrf_config))
    if app.allowed_hosts:
        allowed_hosts = app.allowed_hosts

        table.add_row("Allowed hosts", ", ".join(allowed_hosts.allowed_hosts))

    openapi_enabled = _format_is_enabled(app.openapi_config)
    if app.openapi_config:
        path = (
            app.openapi_config.openapi_controller.path
            if app.openapi_config.openapi_controller
            else app.openapi_config.path or "/schema"
        )
        openapi_enabled += f" path=[yellow]{path}"
    table.add_row("OpenAPI", openapi_enabled)

    table.add_row("Compression", app.compression_config.backend if app.compression_config else "[red]Disabled")

    if app.template_engine:
        table.add_row("Template engine", type(app.template_engine).__name__)

    if app.static_files_config:
        static_files_configs = app.static_files_config
        static_files_info = [
            f"path=[yellow]{static_files.path}[/] dirs=[yellow]{', '.join(map(str, static_files.directories))}[/] "
            f"html_mode={_format_is_enabled(static_files.html_mode)}"
            for static_files in static_files_configs
        ]
        table.add_row("Static files", "\n".join(static_files_info))

    middlewares = []
    for middleware in app.middleware:
        updated_middleware = middleware.middleware if isinstance(middleware, DefineMiddleware) else middleware
        middlewares.append(get_name(updated_middleware))
    if middlewares:
        table.add_row("Middlewares", ", ".join(middlewares))

    console.print(table)


def validate_ssl_file_paths(certfile_arg: str | None, keyfile_arg: str | None) -> tuple[str, str] | tuple[None, None]:
    """Validate whether given paths exist, are not directories and were both provided or none was. Return the resolved paths.

    Args:
        certfile_arg: path argument for the certificate file
        keyfile_arg: path argument for the key file

    Returns:
        tuple of resolved paths converted to str or tuple of None's if no argument was provided
    """
    if certfile_arg is None and keyfile_arg is None:
        return (None, None)

    resolved_paths = []

    for argname, arg in {"--ssl-certfile": certfile_arg, "--ssl-keyfile": keyfile_arg}.items():
        if arg is None:
            raise LitestarCLIException(f"No value provided for {argname}")
        path = Path(arg).resolve()
        if path.is_dir():
            raise LitestarCLIException(f"Path provided for {argname} is a directory: {path}")
        if not path.exists():
            raise LitestarCLIException(f"File provided for {argname} was not found: {path}")
        resolved_paths.append(str(path))

    return tuple(resolved_paths)  # type: ignore[return-value]


def create_ssl_files(
    certfile_arg: str | None, keyfile_arg: str | None, common_name: str = "localhost"
) -> tuple[str, str]:
    """Validate whether both files were provided, are not directories, their parent dirs exist and either both files exists or none does.
    If neither file exists, create a self-signed ssl certificate and a passwordless key at the location.

    Args:
        certfile_arg: path argument for the certificate file
        keyfile_arg: path argument for the key file
        common_name: the CN to be used as cert issuer and subject

    Returns:
        resolved paths of the found or generated files
    """
    resolved_paths = []

    for argname, arg in {"--ssl-certfile": certfile_arg, "--ssl-keyfile": keyfile_arg}.items():
        if arg is None:
            raise LitestarCLIException(f"No value provided for {argname}")
        path = Path(arg).resolve()
        if path.is_dir():
            raise LitestarCLIException(f"Path provided for {argname} is a directory: {path}")
        if not (parent_dir := path.parent).exists():
            raise LitestarCLIException(
                f"Could not create file, parent directory for {argname} doesn't exist: {parent_dir}"
            )
        resolved_paths.append(path)

    if (not resolved_paths[0].exists()) ^ (not resolved_paths[1].exists()):
        raise LitestarCLIException(
            "Both certificate and key file must exists or both must not exists when using --create-self-signed-cert"
        )

    if (not resolved_paths[0].exists()) and (not resolved_paths[1].exists()):
        _generate_self_signed_cert(resolved_paths[0], resolved_paths[1], common_name)

    return (str(resolved_paths[0]), str(resolved_paths[1]))


def _generate_self_signed_cert(certfile_path: Path, keyfile_path: Path, common_name: str) -> None:
    """Create a self-signed certificate using the cryptography modules at given paths"""
    try:
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.x509.oid import NameOID
    except ImportError as err:
        raise LitestarCLIException(
            "Cryptography must be installed when using --create-self-signed-cert\nPlease install the litestar[cryptography] extras"
        ) from err

    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Development Certificate"),
        ]
    )

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(tz=timezone.utc))
        .not_valid_after(datetime.now(tz=timezone.utc) + timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(common_name)]), critical=False)
        .add_extension(x509.ExtendedKeyUsage([x509.OID_SERVER_AUTH]), critical=False)
        .sign(key, hashes.SHA256(), default_backend())
    )

    with certfile_path.open("wb") as cert_file:
        cert_file.write(cert.public_bytes(serialization.Encoding.PEM))

    with keyfile_path.open("wb") as key_file:
        key_file.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )


def remove_routes_with_patterns(
    routes: list[HTTPRoute | ASGIRoute | WebSocketRoute], patterns: tuple[str, ...]
) -> list[HTTPRoute | ASGIRoute | WebSocketRoute]:
    regex_routes = []
    valid_patterns = []
    for pattern in patterns:
        try:
            check_pattern = re.compile(pattern)
            valid_patterns.append(check_pattern)
        except re.error as e:
            console.print(f"Error: {e}. Invalid regex pattern supplied: '{pattern}'. Omitting from querying results.")

    for route in routes:
        checked_pattern_route_matches = []
        for pattern_compile in valid_patterns:
            matches = pattern_compile.match(route.path)
            checked_pattern_route_matches.append(matches)

        if not any(checked_pattern_route_matches):
            regex_routes.append(route)

    return regex_routes


def remove_default_schema_routes(
    routes: list[HTTPRoute | ASGIRoute | WebSocketRoute], openapi_config: OpenAPIConfig
) -> list[HTTPRoute | ASGIRoute | WebSocketRoute]:
    schema_path = (
        (openapi_config.path or "/schema")
        if openapi_config.openapi_controller is None
        else openapi_config.openapi_controller.path
    )
    return remove_routes_with_patterns(routes, (schema_path,))


def isatty() -> bool:
    """Detect if a terminal is TTY enabled.

    This is a convenience wrapper around the built in system methods.  This allows for easier testing of TTY/non-TTY modes.
    """
    return sys.stdout.isatty()
