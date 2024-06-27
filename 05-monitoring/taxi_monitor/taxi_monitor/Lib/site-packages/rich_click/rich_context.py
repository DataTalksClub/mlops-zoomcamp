import os
from typing import TYPE_CHECKING, Any, Mapping, Optional, Type, Union

import click
from typing_extensions import Literal, NoReturn

from rich_click.rich_help_configuration import RichHelpConfiguration
from rich_click.rich_help_formatter import RichHelpFormatter


if TYPE_CHECKING:
    from types import TracebackType

    from rich.console import Console


class RichContext(click.Context):
    """Click Context class endowed with Rich superpowers."""

    formatter_class: Type[RichHelpFormatter] = RichHelpFormatter
    console: Optional["Console"] = None
    export_console_as: Literal[None, "html", "svg"] = None

    def __init__(
        self,
        *args: Any,
        rich_console: Optional["Console"] = None,
        rich_help_config: Optional[Union[Mapping[str, Any], RichHelpConfiguration]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Create Rich Context instance.

        Args:
        ----
            *args: Args that get passed to click.Context.
            rich_console: Rich Console. Defaults to None.
            rich_help_config: Rich help configuration.  Defaults to None.
            **kwargs: Kwargs that get passed to click.Context.
        """
        super().__init__(*args, **kwargs)
        parent: Optional[RichContext] = kwargs.pop("parent", None)

        if rich_console is None and hasattr(parent, "console"):
            rich_console = parent.console  # type: ignore[union-attr]

        if rich_console is not None:
            self.console = rich_console

        if rich_help_config is None:
            if hasattr(parent, "help_config"):
                self.help_config = parent.help_config  # type: ignore[has-type,union-attr]
            else:
                self.help_config = RichHelpConfiguration.load_from_globals()
        elif isinstance(rich_help_config, Mapping):
            if hasattr(parent, "help_config"):
                if TYPE_CHECKING:
                    assert parent is not None
                kw = parent.help_config.__dict__.copy()
                kw.update(rich_help_config)
                self.help_config = RichHelpConfiguration(**kw)
            else:
                self.help_config = RichHelpConfiguration.load_from_globals(**rich_help_config)
        else:
            self.help_config = rich_help_config

    def make_formatter(self) -> RichHelpFormatter:
        """Create the Rich Help Formatter."""
        formatter = self.formatter_class(
            width=self.terminal_width,
            max_width=self.max_content_width,
            config=self.help_config,
            console=self.console,
            file=open(os.devnull, "w") if self.export_console_as is not None else None,
        )
        if self.export_console_as is not None:
            if self.console is None:
                self.console = formatter.console
            self.console.record = True
        return formatter

    if TYPE_CHECKING:

        def __enter__(self) -> "RichContext":
            return super().__enter__()  # type: ignore[return-value]

        def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            tb: Optional[TracebackType],
        ) -> None:
            return super().__exit__(exc_type, exc_value, tb)

    def exit(self, code: int = 0) -> NoReturn:
        if self.export_console_as is not None and self.console is not None and self.console.record:
            if self.export_console_as == "html":
                print(self.console.export_html(inline_styles=True, code_format="{code}"))
            elif self.export_console_as == "svg":
                print(self.console.export_svg())
        super().exit(code)
