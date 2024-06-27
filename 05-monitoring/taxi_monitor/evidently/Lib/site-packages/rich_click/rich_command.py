import errno
import os
import sys
import warnings
from typing import TYPE_CHECKING, Any, Callable, List, Mapping, Optional, Sequence, TextIO, Type, Union, cast, overload

import click

# Group, Command, and CommandCollection need to be imported directly,
# or else rich_click.cli.patch() causes a recursion error.
from click import CommandCollection, Group
from click.utils import PacifyFlushWrapper, make_str

from rich_click._compat_click import CLICK_IS_BEFORE_VERSION_8X, CLICK_IS_BEFORE_VERSION_9X
from rich_click.rich_context import RichContext
from rich_click.rich_help_configuration import RichHelpConfiguration
from rich_click.rich_help_formatter import RichHelpFormatter


if TYPE_CHECKING:
    from rich.console import Console


# TLDR: if a subcommand overrides one of the methods called by `RichCommand.format_help`,
# then the text won't render properly. The fix is to not rely on the composability of the API,
# and to instead force everything to use RichCommand's methods.
OVERRIDES_GUARD: bool = False


class RichCommand(click.Command):
    """
    Richly formatted click Command.

    Inherits click.Command and overrides help and error methods
    to print richly formatted output.

    This class can be used as a mixin for other click command objects.
    """

    context_class: Type[RichContext] = RichContext
    _formatter: Optional[RichHelpFormatter] = None

    def __init__(self, *args: Any, **kwargs: Any):
        """Create Rich Command instance."""
        super().__init__(*args, **kwargs)
        self._register_rich_context_settings_from_callback()

    def _register_rich_context_settings_from_callback(self) -> None:
        if self.callback is not None:
            if hasattr(self.callback, "__rich_context_settings__"):
                rich_context_settings = getattr(self.callback, "__rich_context_settings__", {})
                for k, v in rich_context_settings.items():
                    self.context_settings.setdefault(k, v)
                del self.callback.__rich_context_settings__

    @property
    def console(self) -> Optional["Console"]:
        """
        Rich Console.

        This is a separate instance from the help formatter that allows full control of the
        console configuration.

        See `rich_config` decorator for how to apply the settings.
        """
        return self.context_settings.get("rich_console")

    @property
    def help_config(self) -> Optional[RichHelpConfiguration]:
        """Rich Help Configuration."""
        import warnings

        warnings.warn(
            "RichCommand.help_config is deprecated. Please use the click.Context's help config instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        cfg = self.context_settings.get("rich_help_config")
        if isinstance(cfg, Mapping):
            return RichHelpConfiguration(**cfg)
        return cfg

    def _generate_rich_help_config(self) -> RichHelpConfiguration:
        """
        Use for error handling when a Context is not available.

        If the Context is available, then the help configuration in the Context
        should be preferred.
        """
        cfg = self.context_settings.get("rich_help_config", {})
        try:
            if isinstance(cfg, Mapping):
                return RichHelpConfiguration.load_from_globals(**cfg)
            elif isinstance(cfg, RichHelpConfiguration):
                return cfg
        except Exception as e:
            click.echo(f"{e.__class__.__name__}{e.args}", file=sys.stderr)
        return RichHelpConfiguration()

    def main(
        self,
        args: Optional[Sequence[str]] = None,
        prog_name: Optional[str] = None,
        complete_var: Optional[str] = None,
        standalone_mode: bool = True,
        windows_expand_args: bool = True,
        **extra: Any,
    ) -> Any:
        # It's not feasible to use super().main() in this context and retain exact parity in behavior.
        # The reason why is explained in a comment in click's source code in the "except Exit as e" block.

        if args is None:
            if CLICK_IS_BEFORE_VERSION_8X:
                from click.utils import get_os_args  # type: ignore[attr-defined]

                args: Sequence[str] = get_os_args()  # type: ignore[no-redef]
            else:
                args = sys.argv[1:]

                if os.name == "nt" and windows_expand_args:
                    from click.utils import _expand_args

                    args = _expand_args(args)
        else:
            args = list(args)

        if TYPE_CHECKING:
            assert args is not None

        if prog_name is None:
            if CLICK_IS_BEFORE_VERSION_8X:
                prog_name = make_str(os.path.basename(sys.argv[0] if sys.argv else __file__))
            else:
                from click.utils import _detect_program_name

                prog_name = _detect_program_name()

        # Process shell completion requests and exit early.
        if CLICK_IS_BEFORE_VERSION_8X:
            from click.core import _bashcomplete  # type: ignore[attr-defined]

            _bashcomplete(self, prog_name, complete_var)
        else:
            self._main_shell_completion(extra, prog_name, complete_var)

        ctx = None

        try:
            try:
                with self.make_context(prog_name, args, **extra) as ctx:
                    rv = self.invoke(ctx)
                    if not standalone_mode:
                        return rv
                    # it's not safe to `ctx.exit(rv)` here!
                    # note that `rv` may actually contain data like "1" which
                    # has obvious effects
                    # more subtle case: `rv=[None, None]` can come out of
                    # chained commands which all returned `None` -- so it's not
                    # even always obvious that `rv` indicates success/failure
                    # by its truthiness/falsiness
                    ctx.exit()
            except (EOFError, KeyboardInterrupt):
                click.echo(file=sys.stderr)
                raise click.exceptions.Abort() from None
            except click.exceptions.ClickException as e:
                if not standalone_mode:
                    raise
                if ctx is not None:
                    config = ctx.help_config
                else:
                    config = self._generate_rich_help_config()
                formatter = self.context_class.formatter_class(config=config, file=sys.stderr)
                from rich_click.rich_help_rendering import rich_format_error

                rich_format_error(e, formatter)
                sys.exit(e.exit_code)
            except OSError as e:
                if e.errno == errno.EPIPE:
                    sys.stdout = cast(TextIO, PacifyFlushWrapper(sys.stdout))
                    sys.stderr = cast(TextIO, PacifyFlushWrapper(sys.stderr))
                    sys.exit(1)
                else:
                    raise
        except click.exceptions.Exit as e:
            if standalone_mode:
                sys.exit(e.exit_code)
            else:
                return e.exit_code
        except click.exceptions.Abort:
            if not standalone_mode:
                raise
            try:
                if ctx is not None:
                    config = ctx.help_config
                else:
                    config = self._generate_rich_help_config()
                formatter = self.context_class.formatter_class(config=config)
            except Exception:
                click.echo("Aborted!", file=sys.stderr)
            else:
                formatter.write_abort()
            finally:
                sys.exit(1)

    # Mypy complains about Liskov substitution principle violations.
    # We opt to ignore mypy here.

    def format_help(self, ctx: RichContext, formatter: RichHelpFormatter) -> None:  # type: ignore[override]
        if OVERRIDES_GUARD:
            prevent_incompatible_overrides(self, "RichCommand", ctx, formatter)
        else:
            self.format_usage(ctx, formatter)
            self.format_help_text(ctx, formatter)
            self.format_options(ctx, formatter)
            self.format_epilog(ctx, formatter)

    def format_help_text(self, ctx: RichContext, formatter: RichHelpFormatter) -> None:  # type: ignore[override]
        from rich_click.rich_help_rendering import get_rich_help_text

        get_rich_help_text(self, ctx, formatter)

    # TODO:
    #  Switching from base click to rich click causes mypy problems.
    #  Either we: (a) swap MRO (incompatible with click 9, without handling 8 and 9 differently)
    #  or (b) we allow issues when users attempt multiple inheritance with a RichCommand
    #  or (c) we use incorrect types here.
    #  We are looking for a solution that fixes all 3. For now, we opt for (c).
    def format_options(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        from rich_click.rich_help_rendering import get_rich_options

        get_rich_options(self, ctx, formatter)  # type: ignore[arg-type]

    def format_epilog(self, ctx: RichContext, formatter: RichHelpFormatter) -> None:  # type: ignore[override]
        from rich_click.rich_help_rendering import get_rich_epilog

        get_rich_epilog(self, ctx, formatter)

    def make_context(
        self,
        info_name: Optional[str],
        args: List[str],
        parent: Optional[click.Context] = None,
        **extra: Any,
    ) -> RichContext:
        if CLICK_IS_BEFORE_VERSION_8X:
            # Reimplement Click 8.x logic.

            for key, value in self.context_settings.items():
                if key not in extra:
                    extra[key] = value

            ctx = self.context_class(self, info_name=info_name, parent=parent, **extra)

            with ctx.scope(cleanup=False):
                self.parse_args(ctx, args)
            return ctx

        else:
            return super().make_context(info_name, args, parent, **extra)  # type: ignore[return-value]


if CLICK_IS_BEFORE_VERSION_9X:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning, module="click")
        from click import MultiCommand

else:

    MultiCommand = Group  # type: ignore[misc,assignment]


class RichMultiCommand(RichCommand, MultiCommand):
    """
    Richly formatted click MultiCommand.

    Inherits click.MultiCommand and overrides help and error methods
    to print richly formatted output.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize RichMultiCommand class."""
        MultiCommand.__init__(self, *args, **kwargs)
        self._register_rich_context_settings_from_callback()

    def format_commands(self, ctx: RichContext, formatter: RichHelpFormatter) -> None:  # type: ignore[override]
        from rich_click.rich_help_rendering import get_rich_commands

        get_rich_commands(self, ctx, formatter)

    def format_options(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        from rich_click.rich_help_rendering import get_rich_options

        get_rich_options(self, ctx, formatter)  # type: ignore[arg-type]

        self.format_commands(ctx, formatter)  # type: ignore[arg-type]

    def format_help(self, ctx: RichContext, formatter: RichHelpFormatter) -> None:  # type: ignore[override]
        if OVERRIDES_GUARD:
            prevent_incompatible_overrides(self, "RichMultiCommand", ctx, formatter)
        else:
            self.format_usage(ctx, formatter)
            self.format_help_text(ctx, formatter)
            self.format_options(ctx, formatter)
            self.format_epilog(ctx, formatter)


class RichGroup(RichMultiCommand, Group):
    """
    Richly formatted click Group.

    Inherits click.Group and overrides help and error methods
    to print richly formatted output.
    """

    command_class: Optional[Type[RichCommand]] = RichCommand
    group_class: Optional[Union[Type[Group], Type[type]]] = type

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize RichGroup class."""
        Group.__init__(self, *args, **kwargs)
        self._register_rich_context_settings_from_callback()

    @overload
    def command(self, __func: Callable[..., Any]) -> RichCommand: ...

    @overload
    def command(self, *args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], RichCommand]: ...

    def command(self, *args: Any, **kwargs: Any) -> Union[Callable[[Callable[..., Any]], RichCommand], RichCommand]:
        # This method override is required for Click 7.x compatibility.
        # (The command_class ClassVar was not added until 8.0.)
        if CLICK_IS_BEFORE_VERSION_8X:
            kwargs.setdefault("cls", self.command_class)
        return super().command(*args, **kwargs)  # type: ignore[no-any-return]

    @overload
    def group(self, __func: Callable[..., Any]) -> "RichGroup": ...

    @overload
    def group(self, *args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], "RichGroup"]: ...

    def group(self, *args: Any, **kwargs: Any) -> Union[Callable[[Callable[..., Any]], "RichGroup"], "RichGroup"]:
        # This method override is required for Click 7.x compatibility.
        # (The group_class ClassVar was not added until 8.0.)
        if CLICK_IS_BEFORE_VERSION_8X:
            if self.group_class is type:
                kwargs.setdefault("cls", self.__class__)
            else:
                kwargs.setdefault("cls", self.group_class)
        return super().group(*args, **kwargs)  # type: ignore[no-any-return]

    def format_help(self, ctx: RichContext, formatter: RichHelpFormatter) -> None:  # type: ignore[override]
        if OVERRIDES_GUARD:
            prevent_incompatible_overrides(self, "RichGroup", ctx, formatter)
        else:
            self.format_usage(ctx, formatter)
            self.format_help_text(ctx, formatter)
            self.format_options(ctx, formatter)
            self.format_epilog(ctx, formatter)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Alias for :meth:`main`."""
        # Include this here because I run into a false warning
        # in the PyCharm IDE otherwise; for some reason PyCharm doesn't
        # seem to think RichGroups are callable. (No issues with Mypy, though.)
        return super().__call__(*args, **kwargs)


class RichCommandCollection(CommandCollection, RichGroup):
    """
    Richly formatted click CommandCollection.

    Inherits click.CommandCollection and overrides help and error methods
    to print richly formatted output.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize RichCommandCollection class."""
        CommandCollection.__init__(self, *args, **kwargs)
        self._register_rich_context_settings_from_callback()

    def format_help(self, ctx: RichContext, formatter: RichHelpFormatter) -> None:  # type: ignore[override]
        if OVERRIDES_GUARD:
            prevent_incompatible_overrides(self, "RichCommandCollection", ctx, formatter)
        else:
            self.format_usage(ctx, formatter)
            self.format_help_text(ctx, formatter)
            self.format_options(ctx, formatter)
            self.format_epilog(ctx, formatter)


def prevent_incompatible_overrides(
    cmd: RichCommand, class_name: str, ctx: RichContext, formatter: RichHelpFormatter
) -> None:
    """For use by the rich-click CLI."""
    import rich_click.patch
    from rich_click.utils import method_is_from_subclass_of

    cls: Type[RichCommand] = getattr(rich_click.patch, f"_Patched{class_name}")

    for method_name in ["format_usage", "format_help_text", "format_options", "format_epilog"]:
        if method_is_from_subclass_of(cmd.__class__, cls, method_name):
            getattr(RichCommand, method_name)(cmd, ctx, formatter)
        else:
            getattr(cmd, method_name)(ctx, formatter)

    if hasattr(cmd.__class__, "format_commands"):
        if method_is_from_subclass_of(cmd.__class__, cls, "format_commands"):
            getattr(RichMultiCommand, "format_commands")(cmd, ctx, formatter)
