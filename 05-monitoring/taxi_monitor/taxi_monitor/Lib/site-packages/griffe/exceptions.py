"""This module contains all the exceptions specific to Griffe."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from griffe.dataclasses import Alias


class GriffeError(Exception):
    """The base exception for all Griffe errors."""


class LoadingError(GriffeError):
    """The base exception for all Griffe errors."""


class NameResolutionError(GriffeError):
    """Exception for names that cannot be resolved in a object scope."""


class UnhandledEditableModuleError(GriffeError):
    """Exception for unhandled editables modules, when searching modules."""


class UnimportableModuleError(GriffeError):
    """Exception for modules that cannot be imported."""


class AliasResolutionError(GriffeError):
    """Exception for alias that cannot be resolved."""

    def __init__(self, alias: Alias) -> None:
        """Initialize the exception.

        Parameters:
            alias: The alias that could not be resolved.
        """
        self.alias: Alias = alias
        """The alias that triggered the error."""

        message = f"Could not resolve alias {alias.path} pointing at {alias.target_path}"
        try:
            filepath = alias.parent.relative_filepath  # type: ignore[union-attr]
        except BuiltinModuleError:
            pass
        else:
            message += f" (in {filepath}:{alias.alias_lineno})"
        super().__init__(message)


class CyclicAliasError(GriffeError):
    """Exception raised when a cycle is detected in aliases."""

    def __init__(self, chain: list[str]) -> None:
        """Initialize the exception.

        Parameters:
            chain: The cyclic chain of items (such as target path).
        """
        self.chain: list[str] = chain
        """The chain of aliases that created the cycle."""

        super().__init__("Cyclic aliases detected:\n  " + "\n  ".join(self.chain))


class LastNodeError(GriffeError):
    """Exception raised when trying to access a next or previous node."""


class RootNodeError(GriffeError):
    """Exception raised when trying to use siblings properties on a root node."""


class BuiltinModuleError(GriffeError):
    """Exception raised when trying to access the filepath of a builtin module."""


class ExtensionError(GriffeError):
    """Base class for errors raised by extensions."""


class ExtensionNotLoadedError(ExtensionError):
    """Exception raised when an extension could not be loaded."""


class GitError(GriffeError):
    """Exception raised for errors related to Git."""


__all__ = [
    "AliasResolutionError",
    "BuiltinModuleError",
    "CyclicAliasError",
    "ExtensionError",
    "ExtensionNotLoadedError",
    "GitError",
    "GriffeError",
    "LastNodeError",
    "LoadingError",
    "NameResolutionError",
    "RootNodeError",
    "UnhandledEditableModuleError",
    "UnimportableModuleError",
]
