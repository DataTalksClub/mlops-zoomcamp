"""The command line interface."""

# ruff: noqa: D103

import os
import sys
from functools import wraps
from gettext import gettext as _
from importlib import import_module
from typing import Any, List, Optional, Tuple, Union

from typing_extensions import Literal


try:
    from importlib import metadata  # type: ignore[import,unused-ignore]
except ImportError:
    # Python < 3.8
    import importlib_metadata as metadata  # type: ignore[no-redef,import-not-found,unused-ignore]

import click

from rich_click.decorators import command as _rich_command
from rich_click.decorators import pass_context
from rich_click.decorators import rich_config as rich_config_decorator
from rich_click.patch import patch as _patch
from rich_click.rich_context import RichContext
from rich_click.rich_help_configuration import RichHelpConfiguration


def entry_points(*, group: str) -> "metadata.EntryPoints":  # type: ignore[name-defined]
    """entry_points function that is compatible with Python 3.7+."""
    if sys.version_info >= (3, 10):
        return metadata.entry_points(group=group)

    epg = metadata.entry_points()

    if sys.version_info < (3, 8) and hasattr(epg, "select"):
        return epg.select(group=group)

    return epg.get(group, [])


@wraps(_patch)
def patch(*args: Any, **kwargs: Any) -> None:
    import warnings

    warnings.warn(
        "`rich_click.cli.patch()` has moved to `rich_click.patch.patch()`."
        " Importing `patch()` from `rich_click.cli` is deprecated; please import from `rich_click.patch` instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    return _patch(*args, **kwargs)


class _RichHelpConfigurationParamType(click.ParamType):

    name = "JSON"

    def __repr__(self) -> str:
        return "JSON"

    def convert(
        self,
        value: Optional[Union[RichHelpConfiguration, str]],
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> Optional[RichHelpConfiguration]:

        if value is None or isinstance(value, RichHelpConfiguration):
            return value
        else:
            try:
                import json

                if value.startswith("@"):
                    with open(value[1:], "r") as f:
                        data = json.load(f)
                else:
                    data = json.loads(value)
                if not isinstance(data, dict):
                    raise ValueError("--rich-config needs to be a JSON.")
                return RichHelpConfiguration.load_from_globals(**data)
            except Exception as e:
                # In normal circumstances, a bad arg to a CLI doesn't
                # prevent the help text from rendering.
                if ctx is not None and ctx.params.get("show_help", False):
                    click.echo(ctx.get_help(), color=ctx.color)
                    ctx.exit()
                else:
                    raise e


def _get_module_path_and_function_name(script: str, suppress_warnings: bool) -> Tuple[str, str]:
    _selected: List[str] = []
    module_path = ""
    function_name = ""

    for s in entry_points(group="console_scripts"):
        if script == s.name:
            if not _selected:
                module_path, function_name = s.value.split(":", 1)
            if suppress_warnings:
                break
            if s.value not in _selected:
                _selected.append(s.value)

    if len(_selected) > 1 and not suppress_warnings:
        # This is an extremely rare edge case that comes up when the user sets the PYTHONPATH themselves.
        if script in sys.argv:
            _args = sys.argv.copy()
            _args[_args.index(script)] = f"{module_path}:{function_name}"
        else:
            _args = ["rich-click", f"{module_path}:{function_name}"]

        click.echo(
            click.style(
                f"WARNING: Multiple entry_points correspond with script '{script}': {_selected!r}."
                "\nThis can happen when an 'egg-info' directory exists, you're using a virtualenv,"
                " and you have set a custom PYTHONPATH."
                f"\n\nThe selected script is '{module_path}:{function_name}', which is being executed now."
                "\n\nIt is safer and recommended that you specify the MODULE:CLICK_COMMAND"
                f" ('{module_path}:{function_name}') instead of the script ('{script}'), like this:"
                f"\n\n>>> rich-click {' '.join(_args)}"
                "\n\nAlternatively, you can pass --suppress-warnings to the rich-click CLI,"
                " which will disable this message.",
                fg="red",
            ),
            file=sys.stderr,
        )

    if ":" in script and not module_path:
        # the path to a function was passed
        module_path, function_name = script.split(":", 1)

    if not module_path:
        raise click.ClickException(f"No such script: {script}")

    return module_path, function_name


@_rich_command("rich-click", context_settings=dict(allow_interspersed_args=False, help_option_names=[]))
@click.argument("script_and_args", nargs=-1, metavar="[SCRIPT | MODULE:CLICK_COMMAND] [-- SCRIPT_ARGS...]")
@click.option(
    "--rich-config",
    "-c",
    type=_RichHelpConfigurationParamType(),
    help="Keyword arguments to pass into the [de]RichHelpConfiguration()[/] used"
    " to render the help text of the command. You can pass either a JSON directly, or a file"
    " prefixed with `@` (for example: '@rich_config.json'). Note that the --rich-config"
    " option is also used to render this help text you're reading right now!",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["html", "svg"], case_sensitive=False),
    help="Optionally render help text as HTML or SVG. By default, help text is rendered normally.",
)
@click.option(
    "--suppress-warnings/--do-not-suppress-warnings",
    is_flag=True,
    default=False,
    hidden=True,
    help="Suppress warnings when there are conflicting entry_points."
    " (This option is hidden because this situation is extremely rare).",
)
@click.option(
    # The rich-click CLI uses a special implementation of --help,
    # which is aware of the --rich-config object.
    "--help",
    "-h",
    "show_help",
    is_eager=True,
    is_flag=True,
    help=_("Show this message and exit."),
    # callback=help_callback
)
@pass_context
@rich_config_decorator(
    help_config={
        "text_markup": "rich",
        "errors_epilogue": "[d]Please run [yellow bold]rich-click --help[/] for usage information.[/]",
    }
)
def main(
    ctx: RichContext,
    script_and_args: List[str],
    output: Literal[None, "html", "svg"],
    suppress_warnings: bool,
    rich_config: Optional[RichHelpConfiguration],
    show_help: bool,
) -> None:
    """
    The [link=https://github.com/ewels/rich-click]rich-click[/] CLI provides attractive help output from any
    tool using [link=https://click.palletsprojects.com/]click[/], formatted with
    [link=https://github.com/Textualize/rich]rich[/].

    The rich-click command line tool can be prepended before any Python package
    using native click to provide attractive richified click help output.

    For example, if you have a package called [argument]my_package[/] that uses click,
    you can run:

    >>> [command]rich-click[/] [argument]my_package[/] [option]--help[/]

    This does not always work if the package is using customised [b]click.group()[/]
    or [b]click.command()[/] classes.
    If in doubt, please suggest to the authors that they use rich_click within their
    tool natively - this will always give a better experience.

    You can also use this tool to print your own RichCommands as HTML with the
    --html flag.
    """  # noqa: D400, D401
    if (show_help or not script_and_args) and not ctx.resilient_parsing:
        if rich_config is not None:
            rich_config.use_markdown = False
            rich_config.use_rich_markup = True
            ctx.help_config = rich_config
        click.echo(ctx.get_help(), color=ctx.color)
        ctx.exit()

    # patch click before importing the program function
    _patch(rich_config=rich_config)

    script, *args = script_and_args

    # import the program function
    try:
        module_path, function_name = _get_module_path_and_function_name(script, suppress_warnings)
        module = import_module(module_path)
    except (ModuleNotFoundError, click.ClickException):
        sys.path.append(os.path.abspath("."))
        # PYTHONPATH can change output of entry_points(group="console_scripts") in rare cases,
        # so we want to rerun the whole search
        module_path, function_name = _get_module_path_and_function_name(script, suppress_warnings)
        module = import_module(module_path)

    function = getattr(module, function_name)

    if output is not None:
        RichContext.export_console_as = output

    prog = module_path.split(".", 1)[0]
    sys.argv = [prog, *args]

    if ctx.resilient_parsing and isinstance(function, click.Command):
        function.main(resilient_parsing=True)
    else:
        function()
