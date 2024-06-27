"""Deprecated. This extension provides an hybrid behavior while loading data."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Pattern, Sequence

from griffe.agents.nodes import ObjectNode
from griffe.enumerations import When
from griffe.exceptions import ExtensionError
from griffe.extensions.base import InspectorExtension, VisitorExtension, _load_extension
from griffe.importer import dynamic_import
from griffe.logger import get_logger

if TYPE_CHECKING:
    import ast

    from griffe.agents.visitor import Visitor

logger = get_logger(__name__)


class HybridExtension(VisitorExtension):
    """Inspect during a visit.

    This extension accepts the name of another extension (an inspector)
    and runs it appropriately. It allows to inspect objects
    after having visited them, so as to extract more data.

    Indeed, during the visit, an object might be seen as a simple
    attribute (assignment), when in fact it's a function or a class
    dynamically constructed. In this case, inspecting it will
    provide the desired data.
    """

    when = When.after_all

    def __init__(
        self,
        extensions: Sequence[str | dict[str, Any] | InspectorExtension | type[InspectorExtension]],
        object_paths: Sequence[str | Pattern] | None = None,
    ) -> None:
        """Initialize the extension.

        Parameters:
            extensions: The names or configurations of other inspector extensions.
            object_paths: Optional list of regular expressions to match against objects paths,
                to select which objects to inspect.

        Raises:
            ExtensionError: When the passed extension is not an inspector extension.
        """
        self._extensions: list[InspectorExtension] = [_load_extension(ext) for ext in extensions]  # type: ignore[misc]
        for extension in self._extensions:
            if not isinstance(extension, InspectorExtension):
                raise ExtensionError(
                    f"Extension '{extension}' is not an inspector extension. "
                    "The 'hybrid' extension only accepts inspector extensions. "
                    "If you want to use a visitor extension, just add it normally "
                    "to your extensions configuration, without using 'hybrid'.",
                )
        self.object_paths = [re.compile(op) if isinstance(op, str) else op for op in object_paths or []]
        super().__init__()

    def attach(self, visitor: Visitor) -> None:  # noqa: D102
        super().attach(visitor)
        for extension in self._extensions:
            extension.attach(visitor)  # type: ignore[arg-type]  # tolerate hybrid behavior

    def visit(self, node: ast.AST) -> None:  # noqa: D102
        try:
            just_visited = self.visitor.current.get_member(node.name)  # type: ignore[attr-defined]
        except (KeyError, AttributeError, TypeError):
            return
        if self.object_paths and not any(op.search(just_visited.path) for op in self.object_paths):
            return
        if just_visited.is_alias:
            return
        try:
            value = dynamic_import(just_visited.path)
        except AttributeError:
            # can happen when an object is defined conditionally,
            # for example based on the Python version
            return
        parent = None
        for part in just_visited.path.split(".")[:-1]:
            parent = ObjectNode(None, name=part, parent=parent)
        object_node = ObjectNode(value, name=node.name, parent=parent)  # type: ignore[attr-defined]
        for extension in self._extensions:
            extension.inspect(object_node)


__all__ = ["HybridExtension"]
