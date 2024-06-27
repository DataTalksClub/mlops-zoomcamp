import sys
from typing import IO, TYPE_CHECKING, Any, Optional

import click

from rich_click.rich_help_configuration import RichHelpConfiguration


if TYPE_CHECKING:
    from rich.console import Console
    from rich.highlighter import Highlighter


if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    cached_property = property


def create_console(config: RichHelpConfiguration, file: Optional[IO[str]] = None) -> "Console":
    """
    Create a Rich Console configured from Rich Help Configuration.

    Args:
    ----
        config: Rich Help Configuration instance
        file: Optional IO stream to write Rich Console output
            Defaults to None.
    """
    from rich.console import Console
    from rich.theme import Theme

    console = Console(
        theme=Theme(
            {
                "option": config.style_option,
                "command": config.style_command,
                "argument": config.style_argument,
                "switch": config.style_switch,
                "metavar": config.style_metavar,
                "metavar_sep": config.style_metavar_separator,
                "usage": config.style_usage,
            }
        ),
        color_system=config.color_system,
        force_terminal=config.force_terminal,
        file=file,
        width=config.width,
        legacy_windows=config.legacy_windows,
    )
    if isinstance(config.max_width, int):
        console.width = min(config.max_width, console.size.width)
    return console


class RichHelpFormatter(click.HelpFormatter):
    """
    Rich Help Formatter.

    This class is a container for the help configuration and Rich Console that
    are used internally by the help and error printing methods.
    """

    console: "Console"
    """Rich Console created from the help configuration.

    This console is meant only for use with the formatter and should
    not be created directly
    """

    def __init__(
        self,
        indent_increment: int = 2,
        width: Optional[int] = None,
        max_width: Optional[int] = None,
        *args: Any,
        console: Optional["Console"] = None,
        config: Optional[RichHelpConfiguration] = None,
        file: Optional[IO[str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Create Rich Help Formatter.

        Args:
        ----
            indent_increment: Passed to click.HelpFormatter.
            width: Passed to click.HelpFormatter. Overrides config.width if not None.
            max_width: Passed to click.HelpFormatter. Overrides config.max_width if not None.
            *args: Args passed to click.HelpFormatter.
            console: Use an external console.
            config: RichHelpConfiguration. If None, then build config from globals.
            file: Stream to output to in the Rich Console. If None, use stdout.
            **kwargs: Kwargs passed to click.HelpFormatter.
        """
        if config is not None:
            self.config = config
            # Rich config overrides width and max width if set.
        else:
            self.config = RichHelpConfiguration.load_from_globals()

        self.console = console or create_console(self.config, file=file)

        # TODO: Revisit this. I don't think this does anything.
        if width is None:
            width = self.config.width
        if max_width is None:
            max_width = self.config.max_width

        super().__init__(indent_increment, width, max_width, *args, **kwargs)

    @cached_property
    def highlighter(self) -> "Highlighter":
        if self.config.highlighter is not None:
            return self.config.highlighter
        else:
            from rich.highlighter import RegexHighlighter

            class HighlighterClass(RegexHighlighter):
                highlights = self.config.highlighter_patterns

            return HighlighterClass()

    def write(self, *objects: Any, **kwargs: Any) -> None:
        self.console.print(*objects, **kwargs)

    def write_usage(self, prog: str, args: str = "", prefix: Optional[str] = None) -> None:
        from rich_click.rich_help_rendering import get_rich_usage

        get_rich_usage(formatter=self, prog=prog, args=args, prefix=prefix)

    def write_abort(self) -> None:
        """Print richly formatted abort error."""
        self.console.print(self.config.aborted_text, style=self.config.style_aborted)
