"""This module contains utilities for extracting information from nodes."""

from __future__ import annotations

from ast import AST
from typing import Iterator

from griffe.exceptions import LastNodeError
from griffe.logger import get_logger

logger = get_logger(__name__)


def ast_kind(node: AST) -> str:
    """Return the kind of an AST node.

    Parameters:
        node: The AST node.

    Returns:
        The node kind.
    """
    return node.__class__.__name__.lower()


def ast_children(node: AST) -> Iterator[AST]:
    """Return the children of an AST node.

    Parameters:
        node: The AST node.

    Yields:
        The node children.
    """
    for field_name in node._fields:
        try:
            field = getattr(node, field_name)
        except AttributeError:
            continue
        if isinstance(field, AST):
            field.parent = node  # type: ignore[attr-defined]
            yield field
        elif isinstance(field, list):
            for child in field:
                if isinstance(child, AST):
                    child.parent = node  # type: ignore[attr-defined]
                    yield child


def ast_previous_siblings(node: AST) -> Iterator[AST]:
    """Return the previous siblings of this node, starting from the closest.

    Parameters:
        node: The AST node.

    Yields:
        The previous siblings.
    """
    for sibling in ast_children(node.parent):  # type: ignore[attr-defined]
        if sibling is not node:
            yield sibling
        else:
            return


def ast_next_siblings(node: AST) -> Iterator[AST]:
    """Return the next siblings of this node, starting from the closest.

    Parameters:
        node: The AST node.

    Yields:
        The next siblings.
    """
    siblings = ast_children(node.parent)  # type: ignore[attr-defined]
    for sibling in siblings:
        if sibling is node:
            break
    yield from siblings


def ast_siblings(node: AST) -> Iterator[AST]:
    """Return the siblings of this node.

    Parameters:
        node: The AST node.

    Yields:
        The siblings.
    """
    siblings = ast_children(node.parent)  # type: ignore[attr-defined]
    for sibling in siblings:
        if sibling is not node:
            yield sibling
        else:
            break
    yield from siblings


def ast_previous(node: AST) -> AST:
    """Return the previous sibling of this node.

    Parameters:
        node: The AST node.

    Raises:
        LastNodeError: When the node does not have previous siblings.

    Returns:
        The sibling.
    """
    try:
        *_, last = ast_previous_siblings(node)
    except ValueError:
        raise LastNodeError("there is no previous node") from None
    return last


def ast_next(node: AST) -> AST:
    """Return the next sibling of this node.

    Parameters:
        node: The AST node.

    Raises:
        LastNodeError: When the node does not have next siblings.

    Returns:
        The sibling.
    """
    try:
        return next(ast_next_siblings(node))
    except StopIteration:
        raise LastNodeError("there is no next node") from None


def ast_first_child(node: AST) -> AST:
    """Return the first child of this node.

    Parameters:
        node: The AST node.

    Raises:
        LastNodeError: When the node does not have children.

    Returns:
        The child.
    """
    try:
        return next(ast_children(node))
    except StopIteration as error:
        raise LastNodeError("there are no children node") from error


def ast_last_child(node: AST) -> AST:
    """Return the lasts child of this node.

    Parameters:
        node: The AST node.

    Raises:
        LastNodeError: When the node does not have children.

    Returns:
        The child.
    """
    try:
        *_, last = ast_children(node)
    except ValueError as error:
        raise LastNodeError("there are no children node") from error
    return last


__all__ = [
    "ast_children",
    "ast_first_child",
    "ast_kind",
    "ast_last_child",
    "ast_next",
    "ast_next_siblings",
    "ast_previous",
    "ast_previous_siblings",
    "ast_siblings",
]
