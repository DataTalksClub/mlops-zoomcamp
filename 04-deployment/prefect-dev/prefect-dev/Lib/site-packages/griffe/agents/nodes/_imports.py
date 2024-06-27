"""This module contains utilities for extracting information from nodes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from griffe.logger import get_logger

if TYPE_CHECKING:
    import ast

    from griffe.dataclasses import Module


logger = get_logger(__name__)


def relative_to_absolute(node: ast.ImportFrom, name: ast.alias, current_module: Module) -> str:
    """Convert a relative import path to an absolute one.

    Parameters:
        node: The "from ... import ..." AST node.
        name: The imported name.
        current_module: The module in which the import happens.

    Returns:
        The absolute import path.
    """
    level = node.level
    if level > 0 and current_module.is_package or current_module.is_subpackage:
        level -= 1
    while level > 0 and current_module.parent is not None:
        current_module = current_module.parent  # type: ignore[assignment]
        level -= 1
    base = current_module.path + "." if node.level > 0 else ""
    node_module = node.module + "." if node.module else ""
    return base + node_module + name.name


__all__ = ["relative_to_absolute"]
