"""This module contains utilities for extracting information from nodes."""

from __future__ import annotations

import ast
import sys
from typing import TYPE_CHECKING

from griffe.logger import get_logger

# TODO: Remove once support for Python 3.8 is dropped.
if sys.version_info < (3, 9):
    from astunparse import unparse
else:
    from ast import unparse

if TYPE_CHECKING:
    from pathlib import Path

logger = get_logger(__name__)


def get_value(node: ast.AST | None) -> str | None:
    """Get the string representation of a node.

    Parameters:
        node: The node to represent.

    Returns:
        The representing code for the node.
    """
    if node is None:
        return None
    return unparse(node)


def safe_get_value(node: ast.AST | None, filepath: str | Path | None = None) -> str | None:
    """Safely (no exception) get the string representation of a node.

    Parameters:
        node: The node to represent.
        filepath: An optional filepath from where the node comes.

    Returns:
        The representing code for the node.
    """
    try:
        return get_value(node)
    except Exception as error:
        message = f"Failed to represent node {node}"
        if filepath:
            message += f" at {filepath}:{node.lineno}"  # type: ignore[union-attr]
        message += f": {error}"
        logger.exception(message)
        return None


__all__ = ["get_value", "safe_get_value"]
