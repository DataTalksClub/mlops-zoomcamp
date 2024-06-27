import inspect
import re
from fnmatch import fnmatch
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Tuple, TypeVar, Union, overload

import click

# Due to how rich_click.cli.patch() works, it is safer to import Command types directly
# rather than use the click module e.g. click.Command
from click import Command, Group
from rich import box
from rich.align import Align
from rich.columns import Columns
from rich.console import RenderableType
from rich.emoji import Emoji
from rich.highlighter import RegexHighlighter
from rich.markdown import Markdown
from rich.padding import Padding
from rich.panel import Panel
from rich.style import StyleType
from rich.table import Table
from rich.text import Text
from typing_extensions import Literal

from rich_click._compat_click import CLICK_IS_BEFORE_VERSION_8X, CLICK_IS_BEFORE_VERSION_9X, CLICK_IS_VERSION_80
from rich_click.rich_help_formatter import RichHelpFormatter
from rich_click.utils import CommandGroupDict, OptionGroupDict


# Support rich <= 10.6.0
try:
    from rich.console import group
except ImportError:
    from rich.console import render_group as group  # type: ignore[attr-defined,no-redef]


if CLICK_IS_BEFORE_VERSION_9X:
    # We need to load from here to help with patching.
    from rich_click.rich_command import MultiCommand  # type: ignore[attr-defined]
else:
    MultiCommand = Group  # type: ignore[misc,assignment]


def _make_rich_rext(text: str, style: StyleType, formatter: RichHelpFormatter) -> Union[Markdown, Text]:
    """
    Take a string, remove indentations, and return styled text.
    By default, return the text as a Rich Text with the request style.
    If config.use_rich_markup is True, also parse the text for Rich markup strings.
    If config.use_markdown is True, parse as Markdown.
    Only one of config.use_markdown or config.use_rich_markup can be True.
    If both are True, config.use_markdown takes precedence.

    Args:
    ----
        text (str): Text to style.
        style (StyleType): Rich style to apply.
        formatter: formatter object.

    Returns:
    -------
        MarkdownElement or Text: Styled text object
    """
    config = formatter.config
    # Remove indentations from input text
    text = inspect.cleandoc(text)

    use_ansi = False
    use_markdown = False
    use_rich = False

    if config.use_markdown:
        use_markdown = True
    elif config.use_rich_markup:
        use_rich = True
    elif config.text_markup == "markdown":
        use_markdown = True
    elif config.text_markup == "rich":
        use_rich = True
    elif config.text_markup == "ansi":
        use_ansi = True

    # TODO:
    #  In a future major version release, decouple emojis and markdown.
    #  Decoupling isn't something that is sensible without breaking the API.
    if use_markdown:
        if config.use_markdown_emoji:
            text = Emoji.replace(text)
        return Markdown(text, style=style)
    elif use_rich:
        return formatter.highlighter(Text.from_markup(text, style=style))
    elif use_ansi:
        return formatter.highlighter(Text.from_ansi(text, style=style))
    else:
        return formatter.highlighter(Text(text, style=style))


@group()
def _get_help_text(obj: Union[Command, Group], formatter: RichHelpFormatter) -> Iterable[Union[Markdown, Text]]:
    """
    Build primary help text for a click command or group.
    Returns the prose help text for a command or group, rendered either as a
    Rich Text object or as Markdown.
    If the command is marked as depreciated, the depreciated string will be prepended.

    Args:
    ----
        obj (click.Command or click.Group): Command or group to build help text for.
        formatter: formatter object.

    Yields:
    ------
        Text or Markdown: Multiple styled objects (depreciated, usage)
    """
    if TYPE_CHECKING:
        assert isinstance(obj.help, str)
    config = formatter.config
    # Prepend deprecated status
    if obj.deprecated:
        yield Text(config.deprecated_string, style=config.style_deprecated)

    # Fetch and dedent the help text
    help_text = inspect.cleandoc(obj.help)

    # Trim off anything that comes after \f on its own line
    help_text = help_text.partition("\f")[0]

    # Get the first paragraph
    first_line = help_text.split("\n\n")[0]
    # Remove single linebreaks
    if not config.use_markdown and not first_line.startswith("\b"):
        first_line = first_line.replace("\n", " ")
    yield _make_rich_rext(first_line.strip(), config.style_helptext_first_line, formatter)

    # Get remaining lines, remove single line breaks and format as dim
    remaining_paragraphs = help_text.split("\n\n")[1:]
    if len(remaining_paragraphs) > 0:
        if not config.use_markdown:
            # Remove single linebreaks
            remaining_paragraphs = [
                x.replace("\n", " ").strip() if not x.startswith("\b") else "{}\n".format(x.strip("\b\n"))
                for x in remaining_paragraphs
            ]
            # Join back together
            remaining_lines = "\n".join(remaining_paragraphs)
        else:
            # Join with double linebreaks if markdown
            remaining_lines = "\n\n".join(remaining_paragraphs)

        yield _make_rich_rext(remaining_lines, config.style_helptext, formatter)


def _get_option_help(
    param: Union[click.Argument, click.Option], ctx: click.Context, formatter: RichHelpFormatter
) -> Columns:
    """
    Build primary help text for a click option or argument.
    Returns the prose help text for an option or argument, rendered either
    as a Rich Text object or as Markdown.
    Additional elements are appended to show the default and required status if applicable.

    Args:
    ----
        param (click.Argument or click.Option): Parameter to build help text for.
        ctx (click.Context): Click Context object.
        formatter (RichHelpFormatter): formatter object.

    Returns:
    -------
        Columns: A columns element with multiple styled objects (help, default, required)
    """
    config = formatter.config
    items: List[RenderableType] = []

    if TYPE_CHECKING:
        assert isinstance(param.name, str)

    # Get the environment variable first
    envvar = getattr(param, "envvar", None)
    # https://github.com/pallets/click/blob/0aec1168ac591e159baf6f61026d6ae322c53aaf/src/click/core.py#L2720-L2726
    if envvar is None:
        if (
            getattr(param, "allow_from_autoenv", None)
            and getattr(ctx, "auto_envvar_prefix", None) is not None
            and param.name is not None
        ):
            envvar = f"{ctx.auto_envvar_prefix}_{param.name.upper()}"
    if envvar is not None:
        envvar = ", ".join(envvar) if isinstance(envvar, list) else envvar

    # Environment variable config.before help text
    if getattr(param, "show_envvar", None) and config.option_envvar_first and envvar is not None:
        items.append(Text(config.envvar_string.format(envvar), style=config.style_option_envvar))

    # Main help text
    if getattr(param, "help", None):
        if TYPE_CHECKING:
            assert isinstance(param, click.Option)
            assert hasattr(param, "help")
            assert isinstance(param.help, str)
        paragraphs = param.help.split("\n\n")
        # Remove single linebreaks
        if not config.use_markdown:
            paragraphs = [
                x.replace("\n", " ").strip() if not x.startswith("\b") else "{}\n".format(x.strip("\b\n"))
                for x in paragraphs
            ]
        items.append(_make_rich_rext("\n".join(paragraphs).strip(), config.style_option_help, formatter))

    # Append metavar if requested
    if config.append_metavars_help:
        metavar_str = param.make_metavar()
        # Do it ourselves if this is a positional argument
        if isinstance(param, click.core.Argument) and re.match(rf"\[?{param.name.upper()}]?", metavar_str):
            metavar_str = param.type.name.upper()
        # Attach metavar if param is a positional argument, or if it is a non boolean and non flag option
        if isinstance(param, click.core.Argument) or (metavar_str != "BOOLEAN" and not param.is_flag):
            metavar_str = metavar_str.replace("[", "").replace("]", "")
            items.append(
                Text(
                    config.append_metavars_help_string.format(metavar_str),
                    style=config.style_metavar_append,
                    overflow="fold",
                )
            )

    # Environment variable config.after help text
    if getattr(param, "show_envvar", None) and not config.option_envvar_first and envvar is not None:
        items.append(Text(config.envvar_string.format(envvar), style=config.style_option_envvar))

    # Default value
    # Click 7.x, 8.0, and 8.1 all behave slightly differently when handling the default value help text.
    if not hasattr(param, "show_default"):
        parse_default = False
    elif CLICK_IS_BEFORE_VERSION_8X:
        parse_default = bool(param.default is not None and (param.show_default or getattr(ctx, "show_default", None)))
    elif CLICK_IS_VERSION_80:
        show_default_is_str = isinstance(param.show_default, str)
        parse_default = bool(
            show_default_is_str or (param.default is not None and (param.show_default or ctx.show_default))
        )
    else:
        show_default_is_str = False
        if param.show_default is not None:
            if isinstance(param.show_default, str):
                show_default_is_str = show_default = True
            else:
                show_default = bool(param.show_default)
        else:
            show_default = bool(getattr(ctx, "show_default", False))
        parse_default = bool(show_default_is_str or (show_default and (param.default is not None)))

    if parse_default:
        help_record = param.get_help_record(ctx)
        if TYPE_CHECKING:
            assert isinstance(help_record, tuple)
        default_str_match = re.search(r"\[(?:.+; )?default: (.*)\]", help_record[-1])
        if default_str_match:
            # Don't show the required string, as we show that afterwards anyway
            default_str = default_str_match.group(1).replace("; required", "")
            items.append(
                Text(
                    config.default_string.format(default_str),
                    style=config.style_option_default,
                )
            )

    # Required?
    if param.required:
        items.append(Text(config.required_long_string, style=config.style_required_long))

    # Use Columns - this allows us to group different renderable types
    # (Text, Markdown) onto a single line.
    return Columns(items)


def _make_command_help(help_text: str, formatter: RichHelpFormatter, is_deprecated: bool) -> Union[Text, Markdown]:
    """
    Build cli help text for a click group command.
    That is, when calling help on groups with multiple subcommands
    (not the main help text when calling the subcommand help).
    Returns the first paragraph of help text for a command, rendered either as a
    Rich Text object or as Markdown.
    Ignores single newlines as paragraph markers, looks for double only.

    Args:
    ----
        help_text (str): Help text
        formatter: formatter object
        is_deprecated (bool): Object marked by user as deprecated.

    Returns:
    -------
        Text or Markdown: Styled object
    """
    paragraphs = inspect.cleandoc(help_text).split("\n\n")
    # Remove single linebreaks
    if not formatter.config.use_markdown and not paragraphs[0].startswith("\b"):
        paragraphs[0] = paragraphs[0].replace("\n", " ")
    elif paragraphs[0].startswith("\b"):
        paragraphs[0] = paragraphs[0].replace("\b\n", "")
    help_text = paragraphs[0].strip()
    if is_deprecated:
        # TODO: Format the deprecation text.
        help_text = f"{formatter.config.deprecated_string}{help_text}"
    renderable = _make_rich_rext(help_text, formatter.config.style_option_help, formatter)
    return renderable


def get_rich_usage(formatter: RichHelpFormatter, prog: str, args: str = "", prefix: Optional[str] = None) -> None:
    """Richly render usage text."""
    if prefix is None:
        prefix = "Usage:"

    config = formatter.config

    # Header text if we have it
    if config.header_text:
        formatter.write(
            Padding(
                _make_rich_rext(config.header_text, config.style_header_text, formatter),
                (1, 1, 0, 1),
            ),
        )

    # Highlighter for options and arguments
    class UsageHighlighter(RegexHighlighter):
        highlights = [
            r"(?P<argument>\w+)",
        ]

    usage_highlighter = UsageHighlighter()

    # Print usage
    formatter.write(
        Padding(
            Columns(
                (
                    Text(prefix, style=config.style_usage),
                    Text(prog, style=config.style_usage_command),
                    usage_highlighter(args),
                )
            ),
            1,
        ),
    )


def get_rich_help_text(self: Command, ctx: click.Context, formatter: RichHelpFormatter) -> None:
    """Write rich help text to the formatter if it exists."""
    # Print command / group help if we have some
    if self.help:
        # Print with some padding
        formatter.write(
            Padding(
                Align(_get_help_text(self, formatter), pad=False),
                (0, 1, 1, 1),
            )
        )


GroupType = TypeVar("GroupType", OptionGroupDict, CommandGroupDict)


@overload
def _resolve_groups(
    ctx: click.Context, groups: Dict[str, List[OptionGroupDict]], group_attribute: Literal["options"]
) -> List[OptionGroupDict]: ...


@overload
def _resolve_groups(
    ctx: click.Context, groups: Dict[str, List[CommandGroupDict]], group_attribute: Literal["commands"]
) -> List[CommandGroupDict]: ...


def _resolve_groups(
    ctx: click.Context, groups: Dict[str, List[GroupType]], group_attribute: Literal["commands", "options"]
) -> List[GroupType]:
    """Logic for resolving the groups."""
    cmd_name = ctx.command.name
    _ctx = ctx
    while _ctx.parent is not None:
        _ctx = _ctx.parent
        cmd_name = f"{_ctx.command.name} {cmd_name}"
    # 'command_path' is sometimes the file name, e.g. hello.py.
    # We also want to make sure that the actual command name is supported as well.
    if cmd_name != ctx.command_path:
        paths = [cmd_name, ctx.command_path]
    else:
        paths = [cmd_name]
    # Also handle 'python -m foo' when the user specifies a key of 'foo':
    if ctx.command_path.startswith("python -m "):
        extra = ctx.command_path.replace("python -m ", "", 1)
        paths.append(extra)
    final_groups_list: List[GroupType] = []

    # Assign wildcards, but make sure we do not overwrite anything already defined.
    for _path in paths:
        for mtch in reversed(sorted([_ for _ in groups if fnmatch(_path, _)])):
            wildcard_option_groups = groups[mtch]
            for grp in wildcard_option_groups:
                grp = grp.copy()
                opts = grp.get(group_attribute, []).copy()  # type: ignore[attr-defined]
                for opt in grp.get(group_attribute, []):  # type: ignore[attr-defined]
                    if opt in [
                        _opt
                        for _grp in final_groups_list
                        for _opt in _grp.get(group_attribute, [])  # type: ignore[attr-defined]
                    ]:
                        opts.remove(opt)
                grp[group_attribute] = opts  # type: ignore[typeddict-unknown-key]
                final_groups_list.append(grp)

    final_groups_list.append({group_attribute: []})  # type: ignore[misc]
    return final_groups_list


def get_rich_options(
    obj: Command,
    ctx: click.Context,
    formatter: RichHelpFormatter,
) -> None:
    """Richly render a click Command's options."""
    # Look through config.option_groups for this command
    # stick anything unmatched into a default group at the end
    option_groups = _resolve_groups(ctx=ctx, groups=formatter.config.option_groups, group_attribute="options")
    argument_group_options = []

    for param in obj.get_params(ctx):
        # Skip positional arguments - they don't have opts or helptext and are covered in usage
        # See https://click.palletsprojects.com/en/8.0.x/documentation/#documenting-arguments
        if isinstance(param, click.core.Argument) and not formatter.config.show_arguments:
            continue

        # Skip if option is hidden
        if getattr(param, "hidden", False):
            continue

        # Already mentioned in a config option group
        for option_group in option_groups:
            if any([opt in (option_group.get("options") or []) for opt in param.opts]):
                break

        # No break, no mention - add to the default group
        else:
            if isinstance(param, click.core.Argument) and not formatter.config.group_arguments_options:
                argument_group_options.append(param.opts[0])
            else:
                list_of_option_groups = option_groups[-1]["options"]
                list_of_option_groups.append(param.opts[0])

    # If we're not grouping arguments and we got some, prepend before default options
    if len(argument_group_options) > 0:
        for grp in option_groups:
            if grp.get("name", "") == formatter.config.arguments_panel_title and not grp.get("options"):
                extra_option_group = grp.copy()
                extra_option_group["options"] = argument_group_options
                break
        else:
            extra_option_group: OptionGroupDict = {  # type: ignore[no-redef]
                "name": formatter.config.arguments_panel_title,
                "options": argument_group_options,
            }
        option_groups.insert(len(option_groups) - 1, extra_option_group)

    # Print each option group panel
    for option_group in option_groups:
        options_rows = []
        for opt in option_group.get("options") or []:
            # Get the param
            for param in obj.get_params(ctx):
                if any([opt in param.opts]):
                    break
            # Skip if option is not listed in this group
            else:
                continue

            # Short and long form
            opt_long_strs = []
            opt_short_strs = []
            for idx, opt in enumerate(param.opts):
                opt_str = opt
                try:
                    opt_str += "/" + param.secondary_opts[idx]
                except IndexError:
                    pass

                if isinstance(param, click.core.Argument):
                    opt_long_strs.append(opt_str.upper())
                elif "--" in opt:
                    opt_long_strs.append(opt_str)
                else:
                    opt_short_strs.append(opt_str)

            # Column for a metavar, if we have one
            metavar = Text(style=formatter.config.style_metavar, overflow="fold")
            metavar_str = param.make_metavar()

            if TYPE_CHECKING:
                assert isinstance(param.name, str)
                assert isinstance(param, click.Option)

            # Do it ourselves if this is a positional argument
            if isinstance(param, click.core.Argument) and re.match(rf"\[?{param.name.upper()}]?", metavar_str):
                metavar_str = param.type.name.upper()

            # Attach metavar if param is a positional argument, or if it is a non boolean and non flag option
            if isinstance(param, click.core.Argument) or (
                metavar_str != "BOOLEAN" and not getattr(param, "is_flag", None)
            ):
                metavar.append(metavar_str)

            # Range - from
            # https://github.com/pallets/click/blob/c63c70dabd3f86ca68678b4f00951f78f52d0270/src/click/core.py#L2698-L2706  # noqa: E501
            try:
                # skip count with default range type
                if isinstance(param.type, click.types._NumberRangeBase) and not (
                    param.count and param.type.min == 0 and param.type.max is None
                ):
                    range_str = param.type._describe_range()
                    if range_str:
                        metavar.append(formatter.config.range_string.format(range_str))
            except AttributeError:
                # click.types._NumberRangeBase is only in Click 8x onwards
                pass

            # Required asterisk
            required: Union[Text, str] = ""
            if param.required:
                required = Text(formatter.config.required_short_string, style=formatter.config.style_required_short)

            # Highlighter to make [ | ] and <> dim
            class MetavarHighlighter(RegexHighlighter):
                highlights = [
                    r"^(?P<metavar_sep>(\[|<))",
                    r"(?P<metavar_sep>\|)",
                    r"(?P<metavar_sep>(\]|>)$)",
                ]

            metavar_highlighter = MetavarHighlighter()

            rows = [
                required,
                formatter.highlighter(formatter.highlighter(",".join(opt_long_strs))),
                formatter.highlighter(formatter.highlighter(",".join(opt_short_strs))),
                metavar_highlighter(metavar),
                _get_option_help(param, ctx, formatter),
            ]

            # Remove metavar if specified in config
            if not formatter.config.show_metavars_column:
                rows.pop(3)

            options_rows.append(rows)

        if len(options_rows) > 0:
            t_styles = {
                "show_lines": formatter.config.style_options_table_show_lines,
                "leading": formatter.config.style_options_table_leading,
                "box": formatter.config.style_options_table_box,
                "border_style": formatter.config.style_options_table_border_style,
                "row_styles": formatter.config.style_options_table_row_styles,
                "pad_edge": formatter.config.style_options_table_pad_edge,
                "padding": formatter.config.style_options_table_padding,
            }
            if isinstance(formatter.config.style_options_table_box, str):
                t_styles["box"] = getattr(box, t_styles.pop("box"), None)  # type: ignore[arg-type]
            t_styles.update(option_group.get("table_styles", {}))

            options_table = Table(
                highlight=True,
                show_header=False,
                expand=True,
                **t_styles,  # type: ignore[arg-type]
            )
            # Strip the required column if none are required
            if all([x[0] == "" for x in options_rows]):
                options_rows = [x[1:] for x in options_rows]
            for row in options_rows:
                options_table.add_row(*row)

            kw: Dict[str, Any] = {
                "border_style": formatter.config.style_options_panel_border,
                "title": option_group.get("name", formatter.config.options_panel_title),
                "title_align": formatter.config.align_options_panel,
            }

            if isinstance(formatter.config.style_options_panel_box, str):
                box_style = getattr(box, formatter.config.style_options_panel_box, None)
            else:
                box_style = formatter.config.style_options_panel_box

            if box_style:
                kw["box"] = box_style

            kw.update(option_group.get("panel_styles", {}))

            formatter.write(Panel(options_table, **kw))


def get_rich_commands(
    obj: MultiCommand,
    ctx: click.Context,
    formatter: RichHelpFormatter,
) -> None:
    """Richly render a click Command's options."""
    # Look through config.option_groups for this command
    # stick anything unmatched into a default group at the end

    # Look through COMMAND_GROUPS for this command
    # stick anything unmatched into a default group at the end
    cmd_groups = _resolve_groups(ctx=ctx, groups=formatter.config.command_groups, group_attribute="commands")
    for command in obj.list_commands(ctx):
        for cmd_group in cmd_groups:
            if command in cmd_group.get("commands", []):
                break
        else:
            commands = cmd_groups[-1]["commands"]
            commands.append(command)

    # Print each command group panel
    for cmd_group in cmd_groups:
        t_styles = {
            "show_lines": formatter.config.style_commands_table_show_lines,
            "leading": formatter.config.style_commands_table_leading,
            "box": formatter.config.style_commands_table_box,
            "border_style": formatter.config.style_commands_table_border_style,
            "row_styles": formatter.config.style_commands_table_row_styles,
            "pad_edge": formatter.config.style_commands_table_pad_edge,
            "padding": formatter.config.style_commands_table_padding,
        }
        if isinstance(formatter.config.style_commands_table_box, str):
            t_styles["box"] = getattr(box, t_styles.pop("box"), None)  # type: ignore[arg-type]
        t_styles.update(cmd_group.get("table_styles", {}))

        commands_table = Table(
            highlight=False,
            show_header=False,
            expand=True,
            **t_styles,  # type: ignore[arg-type]
        )
        # Define formatting in first column, as commands don't match highlighter regex
        # and set column ratio for first and second column, if a ratio has been set
        if formatter.config.style_commands_table_column_width_ratio is None:
            table_column_width_ratio: Union[Tuple[None, None], Tuple[int, int]] = (None, None)
        else:
            table_column_width_ratio = formatter.config.style_commands_table_column_width_ratio

        commands_table.add_column(style=formatter.config.style_command, no_wrap=True, ratio=table_column_width_ratio[0])
        commands_table.add_column(
            no_wrap=False,
            ratio=table_column_width_ratio[1],
        )
        for command in cmd_group.get("commands", []):
            # Skip if command does not exist
            if command not in obj.list_commands(ctx):
                continue
            cmd = obj.get_command(ctx, command)
            if TYPE_CHECKING:
                assert cmd is not None
            if cmd.hidden:
                continue
            # Use the truncated short text as with vanilla text if requested
            if formatter.config.use_click_short_help:
                helptext = cmd.get_short_help_str()
            else:
                # Use short_help function argument if used, or the full help
                helptext = cmd.short_help or cmd.help or ""
            commands_table.add_row(command, _make_command_help(helptext, formatter, is_deprecated=cmd.deprecated))
        if commands_table.row_count > 0:

            kw: Dict[str, Any] = {
                "border_style": formatter.config.style_commands_panel_border,
                "title": cmd_group.get("name", formatter.config.commands_panel_title),
                "title_align": formatter.config.align_commands_panel,
            }

            if isinstance(formatter.config.style_commands_panel_box, str):
                box_style = getattr(box, formatter.config.style_commands_panel_box, None)
            else:
                box_style = formatter.config.style_commands_panel_box

            if box_style:
                kw["box"] = box_style

            kw.update(cmd_group.get("panel_styles", {}))
            formatter.write(Panel(commands_table, **kw))


def get_rich_epilog(
    self: Command,
    ctx: click.Context,
    formatter: RichHelpFormatter,
) -> None:
    """Richly render a click Command's epilog if it exists."""
    if self.epilog:
        # Remove single linebreaks, replace double with single
        lines = self.epilog.split("\n\n")
        epilog = "\n".join([x.replace("\n", " ").strip() for x in lines])
        formatter.write(
            Padding(Align(_make_rich_rext(epilog, formatter.config.style_epilog_text, formatter), pad=False), 1)
        )

    # Footer text if we have it
    if formatter.config.footer_text:
        formatter.write(
            Padding(
                _make_rich_rext(formatter.config.footer_text, formatter.config.style_footer_text, formatter),
                (1, 1, 0, 1),
            )
        )


def rich_format_error(self: click.ClickException, formatter: RichHelpFormatter) -> None:
    """
    Print richly formatted click errors.

    Called by custom exception handler to print richly formatted click errors.
    Mimics original click.ClickException.echo() function but with rich formatting.

    Args:
    ----
        self (click.ClickException): Click exception to format.
        formatter: formatter object.
    """
    config = formatter.config
    # Print usage
    if getattr(self, "ctx", None) is not None:
        if TYPE_CHECKING:
            assert hasattr(self, "ctx")
        self.ctx.command.format_usage(self.ctx, formatter)
    if config.errors_suggestion:
        formatter.write(
            Padding(
                config.errors_suggestion,
                (0, 1, 0, 1),
            ),
            style=config.style_errors_suggestion,
        )
    elif (
        config.errors_suggestion is None
        and getattr(self, "ctx", None) is not None
        and self.ctx.command.get_help_option(self.ctx) is not None  # type: ignore[attr-defined]
    ):
        cmd_path = self.ctx.command_path  # type: ignore[attr-defined]
        help_option = self.ctx.help_option_names[0]  # type: ignore[attr-defined]
        formatter.write(
            Padding(
                Columns(
                    (
                        Text("Try"),
                        Text(f"'{cmd_path} {help_option}'", style=config.style_errors_suggestion_command),
                        Text("for help"),
                    )
                ),
                (0, 1, 0, 1),
            ),
            style=config.style_errors_suggestion,
        )

    # A major Python library using click (dbt-core) has its own exception
    # logic that subclasses ClickException, but does not use the message
    # attribute. Checking for the 'message' attribute works to make the
    # rich-click CLI compatible.
    if hasattr(self, "message"):

        kw: Dict[str, Any] = {}

        if isinstance(formatter.config.style_errors_panel_box, str):
            box_style = getattr(box, formatter.config.style_errors_panel_box, None)
        else:
            box_style = formatter.config.style_errors_panel_box

        if box_style:
            kw["box"] = box_style

        formatter.write(
            Padding(
                Panel(
                    formatter.highlighter(self.format_message()),
                    border_style=config.style_errors_panel_border,
                    title=config.errors_panel_title,
                    title_align=config.align_errors_panel,
                    **kw,
                ),
                (0, 0, 1, 0),
            )
        )
    if config.errors_epilogue:
        formatter.write(Padding(config.errors_epilogue, (0, 1, 1, 1)))


def rich_abort_error(formatter: RichHelpFormatter) -> None:
    """Print richly formatted abort error."""
    formatter.write(formatter.config.aborted_text, style=formatter.config.style_aborted)
