"""This module contains utilities for docstrings parsers."""

from __future__ import annotations

from ast import PyCF_ONLY_AST
from contextlib import suppress
from typing import TYPE_CHECKING, Protocol

from griffe.exceptions import BuiltinModuleError
from griffe.expressions import safe_get_annotation
from griffe.logger import LogLevel, get_logger

if TYPE_CHECKING:
    from griffe.dataclasses import Docstring
    from griffe.expressions import Expr


class WarningCallable(Protocol):
    def __call__(self, docstring: Docstring, offset: int, message: str, log_level: LogLevel = ...) -> None: ...


def warning(name: str) -> WarningCallable:
    """Create and return a warn function.

    Parameters:
        name: The logger name.

    Returns:
        A function used to log parsing warnings.

    This function logs a warning message by prefixing it with the filepath and line number.

    Other parameters: Parameters of the returned function:
        docstring (Docstring): The docstring object.
        offset (int): The offset in the docstring lines.
        message (str): The message to log.
    """
    logger = get_logger(name)

    def warn(docstring: Docstring, offset: int, message: str, log_level: LogLevel = LogLevel.warning) -> None:
        try:
            prefix = docstring.parent.relative_filepath  # type: ignore[union-attr]
        except (AttributeError, ValueError):
            prefix = "<module>"
        except BuiltinModuleError:
            prefix = f"<module: {docstring.parent.module.name}>"  # type: ignore[union-attr]
        log = getattr(logger, log_level.value)
        log(f"{prefix}:{(docstring.lineno or 0)+offset}: {message}")

    return warn


def parse_annotation(
    annotation: str,
    docstring: Docstring,
    log_level: LogLevel = LogLevel.error,
) -> str | Expr:
    """Parse a string into a true name or expression that can be resolved later.

    Parameters:
        annotation: The annotation to parse.
        docstring: The docstring in which the annotation appears.
            The docstring's parent is accessed to bind a resolver to the resulting name/expression.
        log_level: Log level to use to log a message.

    Returns:
        The string unchanged, or a new name or expression.
    """
    with suppress(
        AttributeError,  # docstring has no parent that can be used to resolve names
        SyntaxError,  # annotation contains syntax errors
    ):
        code = compile(annotation, mode="eval", filename="", flags=PyCF_ONLY_AST, optimize=2)
        if code.body:  # type: ignore[attr-defined]
            name_or_expr = safe_get_annotation(
                code.body,  # type: ignore[attr-defined]
                parent=docstring.parent,
                log_level=log_level,
            )
            return name_or_expr or annotation
    return annotation


__all__ = ["parse_annotation", "warning"]
