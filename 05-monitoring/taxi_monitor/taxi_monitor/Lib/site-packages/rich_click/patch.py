"""The command line interface."""

# ruff: noqa: D103

from typing import Optional

import click

import rich_click.rich_command
from rich_click.decorators import command as _rich_command
from rich_click.decorators import group as _rich_group
from rich_click.rich_command import RichCommand, RichCommandCollection, RichGroup, RichMultiCommand
from rich_click.rich_help_configuration import RichHelpConfiguration


class _PatchedRichCommand(RichCommand):
    pass


class _PatchedRichMultiCommand(RichMultiCommand, _PatchedRichCommand):
    pass


class _PatchedRichCommandCollection(RichCommandCollection, _PatchedRichCommand):
    pass


class _PatchedRichGroup(RichGroup, _PatchedRichCommand):
    pass


def rich_command(*args, **kwargs):  # type: ignore[no-untyped-def]
    kwargs.setdefault("cls", _PatchedRichCommand)
    return _rich_command(*args, **kwargs)


def rich_group(*args, **kwargs):  # type: ignore[no-untyped-def]
    kwargs.setdefault("cls", _PatchedRichGroup)
    return _rich_group(*args, **kwargs)


def patch(rich_config: Optional[RichHelpConfiguration] = None) -> None:
    """Patch Click internals to use rich-click types."""
    rich_click.rich_command.OVERRIDES_GUARD = True
    click.group = rich_group
    click.command = rich_command
    click.Group = _PatchedRichGroup  # type: ignore[misc]
    click.Command = _PatchedRichCommand  # type: ignore[misc]
    click.CommandCollection = _PatchedRichCommandCollection  # type: ignore[misc]
    if "MultiCommand" in dir(click):
        click.MultiCommand = _PatchedRichMultiCommand  # type: ignore[assignment,misc,unused-ignore]
    if rich_config is not None:
        rich_config.dump_to_globals()
