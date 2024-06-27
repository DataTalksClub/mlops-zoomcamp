"""Litestar CLI."""

from __future__ import annotations

from importlib.util import find_spec

if find_spec("rich_click") is not None:  # pragma: no cover
    import rich_click

    rich_click.rich_click.USE_RICH_MARKUP = True
    rich_click.rich_click.USE_MARKDOWN = False
    rich_click.rich_click.SHOW_ARGUMENTS = True
    rich_click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
    rich_click.rich_click.STYLE_ERRORS_SUGGESTION = "magenta italic"
    rich_click.rich_click.ERRORS_SUGGESTION = ""
    rich_click.rich_click.ERRORS_EPILOGUE = ""
    rich_click.rich_click.MAX_WIDTH = 80
    rich_click.rich_click.SHOW_METAVARS_COLUMN = True
    rich_click.rich_click.APPEND_METAVARS_HELP = True


from .main import litestar_group

__all__ = ["litestar_group"]
