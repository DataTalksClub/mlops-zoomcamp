from __future__ import annotations

from pathlib import Path

try:
    import rich_click as click
except ImportError:
    import click  # type: ignore[no-redef]

from click import Path as ClickPath

from ._utils import LitestarEnv, LitestarExtensionGroup
from .commands import core, schema, sessions

__all__ = ("litestar_group",)


@click.group(cls=LitestarExtensionGroup, context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--app", "app_path", help="Module path to a Litestar application")
@click.option(
    "--app-dir",
    help="Look for APP in the specified directory, by adding this to the PYTHONPATH. Defaults to the current working directory.",
    default=None,
    type=ClickPath(dir_okay=True, file_okay=False, path_type=Path),
    show_default=False,
)
@click.pass_context
def litestar_group(ctx: click.Context, app_path: str | None, app_dir: Path | None = None) -> None:
    """Litestar CLI."""
    if ctx.obj is None:  # env has not been loaded yet, so we can lazy load it
        ctx.obj = lambda: LitestarEnv.from_env(app_path, app_dir=app_dir)


# add sub commands here

litestar_group.add_command(core.info_command)  # pyright: ignore
litestar_group.add_command(core.run_command)  # pyright: ignore
litestar_group.add_command(core.routes_command)  # pyright: ignore
litestar_group.add_command(core.version_command)  # pyright: ignore
litestar_group.add_command(sessions.sessions_group)  # pyright: ignore
litestar_group.add_command(schema.schema_group)  # pyright: ignore
