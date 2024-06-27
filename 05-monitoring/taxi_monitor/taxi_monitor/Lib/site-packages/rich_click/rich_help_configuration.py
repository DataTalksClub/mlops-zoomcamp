import os
from dataclasses import dataclass, field
from os import getenv
from types import ModuleType
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, TypeVar, Union

from typing_extensions import Literal

from rich_click.utils import CommandGroupDict, OptionGroupDict, truthy


if TYPE_CHECKING:
    import rich.align
    import rich.box
    import rich.highlighter
    import rich.padding
    import rich.style


T = TypeVar("T", bound="RichHelpConfiguration")


def force_terminal_default() -> Optional[bool]:
    """Use as the default factory for `force_terminal`."""
    env_vars = ["FORCE_COLOR", "PY_COLORS", "GITHUB_ACTIONS"]
    for env_var in env_vars:
        if env_var in os.environ:
            return truthy(getenv(env_var))
    else:
        return None


def terminal_width_default() -> Optional[int]:
    """Use as the default factory for `width` and `max_width`."""
    width = getenv("TERMINAL_WIDTH")
    if width:
        try:
            return int(width)
        except ValueError:
            import warnings

            warnings.warn("Environment variable `TERMINAL_WIDTH` cannot be cast to an integer.", UserWarning)
            return None
    return None


@dataclass
class RichHelpConfiguration:
    """
    Rich Help Configuration class.

    When merging multiple RichHelpConfigurations together, user-defined values always
    take precedence over the class's defaults. When there are multiple user-defined values
    for a given field, the right-most field is used.
    """

    # FIND:
    # (?<field>[a-zA-Z_]+): (?<typ>.*?) = field\(default=.*?\)
    # REPLACE:
    # ${field}: ${typ} = field(default_factory=_get_default(\"\U${field}\E\"))

    # Default styles
    style_option: "rich.style.StyleType" = field(default="bold cyan")
    style_argument: "rich.style.StyleType" = field(default="bold cyan")
    style_command: "rich.style.StyleType" = field(default="bold cyan")
    style_switch: "rich.style.StyleType" = field(default="bold green")
    style_metavar: "rich.style.StyleType" = field(default="bold yellow")
    style_metavar_append: "rich.style.StyleType" = field(default="dim yellow")
    style_metavar_separator: "rich.style.StyleType" = field(default="dim")
    style_header_text: "rich.style.StyleType" = field(default="")
    style_epilog_text: "rich.style.StyleType" = field(default="")
    style_footer_text: "rich.style.StyleType" = field(default="")
    style_usage: "rich.style.StyleType" = field(default="yellow")
    style_usage_command: "rich.style.StyleType" = field(default="bold")
    style_deprecated: "rich.style.StyleType" = field(default="red")
    style_helptext_first_line: "rich.style.StyleType" = field(default="")
    style_helptext: "rich.style.StyleType" = field(default="dim")
    style_option_help: "rich.style.StyleType" = field(default="")
    style_option_default: "rich.style.StyleType" = field(default="dim")
    style_option_envvar: "rich.style.StyleType" = field(default="dim yellow")
    style_required_short: "rich.style.StyleType" = field(default="red")
    style_required_long: "rich.style.StyleType" = field(default="dim red")
    style_options_panel_border: "rich.style.StyleType" = field(default="dim")
    style_options_panel_box: Optional[Union[str, "rich.box.Box"]] = field(default="ROUNDED")
    align_options_panel: "rich.align.AlignMethod" = field(default="left")
    style_options_table_show_lines: bool = field(default=False)
    style_options_table_leading: int = field(default=0)
    style_options_table_pad_edge: bool = field(default=False)
    style_options_table_padding: "rich.padding.PaddingDimensions" = field(default_factory=lambda: (0, 1))
    style_options_table_box: Optional[Union[str, "rich.box.Box"]] = field(default="")
    style_options_table_row_styles: Optional[List["rich.style.StyleType"]] = field(default=None)
    style_options_table_border_style: Optional["rich.style.StyleType"] = field(default=None)
    style_commands_panel_border: "rich.style.StyleType" = field(default="dim")
    style_commands_panel_box: Optional[Union[str, "rich.box.Box"]] = field(default="ROUNDED")
    align_commands_panel: "rich.align.AlignMethod" = field(default="left")
    style_commands_table_show_lines: bool = field(default=False)
    style_commands_table_leading: int = field(default=0)
    style_commands_table_pad_edge: bool = field(default=False)
    style_commands_table_padding: "rich.padding.PaddingDimensions" = field(default_factory=lambda: (0, 1))
    style_commands_table_box: Optional[Union[str, "rich.box.Box"]] = field(default="")
    style_commands_table_row_styles: Optional[List["rich.style.StyleType"]] = field(default=None)
    style_commands_table_border_style: Optional["rich.style.StyleType"] = field(default=None)
    style_commands_table_column_width_ratio: Optional[Union[Tuple[None, None], Tuple[int, int]]] = field(
        default_factory=lambda: (None, None)
    )
    style_errors_panel_border: "rich.style.StyleType" = field(default="red")
    style_errors_panel_box: Optional[Union[str, "rich.box.Box"]] = field(default="ROUNDED")
    align_errors_panel: "rich.align.AlignMethod" = field(default="left")
    style_errors_suggestion: "rich.style.StyleType" = field(default="dim")
    style_errors_suggestion_command: "rich.style.StyleType" = field(default="blue")
    style_aborted: "rich.style.StyleType" = field(default="red")
    width: Optional[int] = field(default_factory=terminal_width_default)
    max_width: Optional[int] = field(default_factory=terminal_width_default)
    color_system: Optional[Literal["auto", "standard", "256", "truecolor", "windows"]] = field(default="auto")
    force_terminal: Optional[bool] = field(default_factory=force_terminal_default)

    # Fixed strings
    header_text: Optional[str] = field(default=None)
    footer_text: Optional[str] = field(default=None)
    deprecated_string: str = field(default="(Deprecated) ")
    default_string: str = field(default="[default: {}]")
    envvar_string: str = field(default="[env var: {}]")
    required_short_string: str = field(default="*")
    required_long_string: str = field(default="[required]")
    range_string: str = field(default=" [{}]")
    append_metavars_help_string: str = field(default="({})")
    arguments_panel_title: str = field(default="Arguments")
    options_panel_title: str = field(default="Options")
    commands_panel_title: str = field(default="Commands")
    errors_panel_title: str = field(default="Error")
    errors_suggestion: Optional[str] = field(default=None)
    """Defaults to Try 'cmd -h' for help. Set to False to disable."""
    errors_epilogue: Optional[str] = field(default=None)
    aborted_text: str = field(default="Aborted.")

    # Behaviours
    show_arguments: bool = field(default=False)
    """Show positional arguments"""
    show_metavars_column: bool = field(default=True)
    """Show a column with the option metavar (eg. INTEGER)"""
    append_metavars_help: bool = field(default=False)
    """Append metavar (eg. [TEXT]) after the help text"""
    group_arguments_options: bool = field(default=False)
    """Show arguments with options instead of in own panel"""
    option_envvar_first: bool = field(default=False)
    """Show env vars before option help text instead of after"""
    text_markup: Literal["ansi", "rich", "markdown", None] = "ansi"
    use_markdown: bool = field(default=False)
    """Silently deprecated; use `text_markup` field instead."""
    use_markdown_emoji: bool = field(default=True)
    """Parse emoji codes in markdown :smile:"""
    use_rich_markup: bool = field(default=False)
    """Silently deprecated; use `text_markup` field instead."""
    command_groups: Dict[str, List[CommandGroupDict]] = field(default_factory=lambda: {})
    """Define sorted groups of panels to display subcommands"""
    option_groups: Dict[str, List[OptionGroupDict]] = field(default_factory=lambda: {})
    """Define sorted groups of panels to display options and arguments"""
    use_click_short_help: bool = field(default=False)
    """Use click's default function to truncate help text"""
    highlighter: Optional["rich.highlighter.Highlighter"] = field(default=None, repr=False, compare=False)
    """(Deprecated) Rich regex highlighter for help highlighting"""

    highlighter_patterns: List[str] = field(
        default_factory=lambda: [
            r"(^|[^\w\-])(?P<switch>-([^\W0-9][\w\-]*\w|[^\W0-9]))",
            r"(^|[^\w\-])(?P<option>--([^\W0-9][\w\-]*\w|[^\W0-9]))",
            r"(?P<metavar><[^>]+>)",
        ]
    )
    """Patterns to use with the option highlighter."""

    legacy_windows: Optional[bool] = field(default=None)

    def __post_init__(self) -> None:  # noqa: D105
        # Todo: Fix this so that the deprecation warning works properly.

        # if self.highlighter is not None:
        #     import warnings
        #
        #     warnings.warn(
        #         "`highlighter` kwarg is deprecated in RichHelpConfiguration."
        #         " Please do one of the following instead: either set highlighter_patterns=[...] if you want"
        #         " to use regex; or for more advanced use cases where you'd like to use a different type"
        #         " of rich.highlighter.Highlighter, subclass the `RichHelpFormatter` and update its `highlighter`.",
        #         DeprecationWarning,
        #         stacklevel=2,
        #     )

        self.__dataclass_fields__.pop("highlighter", None)

    @classmethod
    def load_from_globals(cls, module: Optional[ModuleType] = None, **extra: Any) -> "RichHelpConfiguration":
        """
        Build a RichHelpConfiguration from globals in rich_click.rich_click.

        When building from globals, all fields are treated as having been set by the user,
        meaning they will overwrite other fields when "merged".
        """
        if module is None:
            import rich_click.rich_click as rc

            module = rc
        kw = {}
        for k, v in cls.__dataclass_fields__.items():
            if v.init:
                if hasattr(module, k.upper()):
                    kw[k] = getattr(module, k.upper())
                # Handle lowercase.
                # (May deprecate and move everything to uppercase... unsure.)
                elif k == "highlighter" and hasattr(module, k):
                    kw[k] = getattr(module, k)

        kw.update(extra)
        inst = cls(**kw)
        return inst

    def dump_to_globals(self, module: Optional[ModuleType] = None) -> None:
        if module is None:
            import rich_click.rich_click as rc

            module = rc
        for k, v in self.__dataclass_fields__.items():
            if v.init:
                if hasattr(module, k.upper()):
                    setattr(module, k.upper(), getattr(self, k))


def __getattr__(name: str) -> Any:
    if name == "OptionHighlighter":
        from rich.highlighter import RegexHighlighter

        class OptionHighlighter(RegexHighlighter):
            """Highlights our special options."""

            highlights = [
                r"(^|[^\w\-])(?P<switch>-([^\W0-9][\w\-]*\w|[^\W0-9]))",
                r"(^|[^\w\-])(?P<option>--([^\W0-9][\w\-]*\w|[^\W0-9]))",
                r"(?P<metavar><[^>]+>)",
            ]

        # todo: fix
        # import warnings
        #
        # warnings.warn(
        #     "OptionHighlighter is deprecated and will be removed in a future version.",
        #     DeprecationWarning,
        #     stacklevel=2,
        # )

        globals()["OptionHighlighter"] = OptionHighlighter

        return OptionHighlighter

    else:
        raise AttributeError
