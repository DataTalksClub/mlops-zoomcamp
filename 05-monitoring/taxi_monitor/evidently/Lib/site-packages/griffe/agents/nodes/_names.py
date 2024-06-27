"""This module contains utilities for extracting information from nodes."""

from __future__ import annotations

import ast
from typing import Any, Callable

from griffe.logger import get_logger

logger = get_logger(__name__)


def _get_attribute_name(node: ast.Attribute) -> str:
    return f"{get_name(node.value)}.{node.attr}"


def _get_name_name(node: ast.Name) -> str:
    return node.id


_node_name_map: dict[type, Callable[[Any], str]] = {
    ast.Name: _get_name_name,
    ast.Attribute: _get_attribute_name,
}


def get_name(node: ast.AST) -> str:
    """Extract name from an assignment node.

    Parameters:
        node: The node to extract names from.

    Returns:
        A list of names.
    """
    return _node_name_map[type(node)](node)


def _get_assign_names(node: ast.Assign) -> list[str]:
    names = (get_name(target) for target in node.targets)
    return [name for name in names if name]


def _get_annassign_names(node: ast.AnnAssign) -> list[str]:
    name = get_name(node.target)
    return [name] if name else []


_node_names_map: dict[type, Callable[[Any], list[str]]] = {
    ast.Assign: _get_assign_names,
    ast.AnnAssign: _get_annassign_names,
}


def get_names(node: ast.AST) -> list[str]:
    """Extract names from an assignment node.

    Parameters:
        node: The node to extract names from.

    Returns:
        A list of names.
    """
    return _node_names_map[type(node)](node)


def get_instance_names(node: ast.AST) -> list[str]:
    """Extract names from an assignment node, only for instance attributes.

    Parameters:
        node: The node to extract names from.

    Returns:
        A list of names.
    """
    return [name.split(".", 1)[1] for name in get_names(node) if name.startswith("self.")]


__all__ = ["get_instance_names", "get_name", "get_names"]
