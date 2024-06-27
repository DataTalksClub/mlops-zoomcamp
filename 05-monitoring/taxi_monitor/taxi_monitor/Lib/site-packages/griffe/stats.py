"""This module contains utilities to compute loading statistics."""

from __future__ import annotations

import warnings
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any

from griffe.enumerations import Kind

if TYPE_CHECKING:
    from griffe.dataclasses import Alias, Object
    from griffe.loader import GriffeLoader


def __getattr__(name: str) -> Any:
    if name == "stats":
        warnings.warn(
            "The 'stats' function was made into a class and renamed 'Stats'.",
            DeprecationWarning,
            stacklevel=2,
        )
        return Stats
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


class Stats:
    """Load statistics for a Griffe loader."""

    def __init__(self, loader: GriffeLoader) -> None:
        """Initialiwe the stats object.

        Parameters:
            loader: The loader to compute stats for.
        """
        self.loader = loader
        modules_by_extension = defaultdict(
            int,
            {
                "": 0,
                ".py": 0,
                ".pyi": 0,
                ".pyc": 0,
                ".pyo": 0,
                ".pyd": 0,
                ".so": 0,
            },
        )
        top_modules = loader.modules_collection.members.values()
        self.by_kind = {
            Kind.MODULE: 0,
            Kind.CLASS: 0,
            Kind.FUNCTION: 0,
            Kind.ATTRIBUTE: 0,
        }
        self.packages = len(top_modules)
        self.modules_by_extension = modules_by_extension
        self.lines = sum(len(lines) for lines in loader.lines_collection.values())
        self.time_spent_visiting = 0
        self.time_spent_inspecting = 0
        self.time_spent_serializing = 0
        for module in top_modules:
            self._itercount(module)

    def _itercount(self, root: Object | Alias) -> None:
        if root.is_alias:
            return
        self.by_kind[root.kind] += 1
        if root.is_module:
            if isinstance(root.filepath, Path):
                self.modules_by_extension[root.filepath.suffix] += 1
            elif root.filepath is None:
                self.modules_by_extension[""] += 1
        for member in root.members.values():
            self._itercount(member)

    def as_text(self) -> str:
        """Format the statistics as text.

        Returns:
            Text stats.
        """
        lines = []
        packages = self.packages
        modules = self.by_kind[Kind.MODULE]
        classes = self.by_kind[Kind.CLASS]
        functions = self.by_kind[Kind.FUNCTION]
        attributes = self.by_kind[Kind.ATTRIBUTE]
        objects = sum((modules, classes, functions, attributes))
        lines.append("Statistics")
        lines.append("---------------------")
        lines.append("Number of loaded objects")
        lines.append(f"  Modules: {modules}")
        lines.append(f"  Classes: {classes}")
        lines.append(f"  Functions: {functions}")
        lines.append(f"  Attributes: {attributes}")
        lines.append(f"  Total: {objects} across {packages} packages")
        per_ext = self.modules_by_extension
        builtin = per_ext[""]
        regular = per_ext[".py"]
        stubs = per_ext[".pyi"]
        compiled = modules - builtin - regular - stubs
        lines.append("")
        lines.append(f"Total number of lines: {self.lines}")
        lines.append("")
        lines.append("Modules")
        lines.append(f"  Builtin: {builtin}")
        lines.append(f"  Compiled: {compiled}")
        lines.append(f"  Regular: {regular}")
        lines.append(f"  Stubs: {stubs}")
        lines.append("  Per extension:")
        for ext, number in sorted(per_ext.items()):
            if ext:
                lines.append(f"    {ext}: {number}")

        visit_time = self.time_spent_visiting / 1000
        inspect_time = self.time_spent_inspecting / 1000
        total_time = visit_time + inspect_time
        visit_percent = visit_time / total_time * 100
        inspect_percent = inspect_time / total_time * 100

        force_inspection = self.loader.force_inspection
        visited_modules = 0 if force_inspection else regular
        try:
            visit_time_per_module = visit_time / visited_modules
        except ZeroDivisionError:
            visit_time_per_module = 0

        inspected_modules = builtin + compiled + (regular if force_inspection else 0)
        try:
            inspect_time_per_module = inspect_time / inspected_modules
        except ZeroDivisionError:
            inspect_time_per_module = 0

        lines.append("")
        lines.append(
            f"Time spent visiting modules ({visited_modules}): "
            f"{visit_time}ms, {visit_time_per_module:.02f}ms/module ({visit_percent:.02f}%)",
        )
        lines.append(
            f"Time spent inspecting modules ({inspected_modules}): "
            f"{inspect_time}ms, {inspect_time_per_module:.02f}ms/module ({inspect_percent:.02f}%)",
        )

        serialize_time = self.time_spent_serializing / 1000
        serialize_time_per_module = serialize_time / modules
        lines.append(f"Time spent serializing: {serialize_time}ms, {serialize_time_per_module:.02f}ms/module")

        return "\n".join(lines)


__all__ = ["Stats"]
