"""General utility functions."""

from __future__ import annotations

import os.path
import sys
from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from types import ModuleType

__all__ = (
    "import_string",
    "module_to_os_path",
)


def module_to_os_path(dotted_path: str = "app") -> Path:
    """Find Module to OS Path.

    Return a path to the base directory of the project or the module
    specified by `dotted_path`.

    Args:
        dotted_path: The path to the module. Defaults to "app".

    Raises:
        TypeError: The module could not be found.

    Returns:
        Path: The path to the module.
    """
    try:
        if (src := find_spec(dotted_path)) is None:  # pragma: no cover
            raise TypeError(f"Couldn't find the path for {dotted_path}")
    except ModuleNotFoundError as e:
        raise TypeError(f"Couldn't find the path for {dotted_path}") from e

    return Path(str(src.origin).rsplit(os.path.sep + "__init__.py", maxsplit=1)[0])


def import_string(dotted_path: str) -> Any:
    """Dotted Path Import.

    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.

    Args:
        dotted_path: The path of the module to import.

    Raises:
        ImportError: Could not import the module.

    Returns:
        object: The imported object.
    """

    def _is_loaded(module: ModuleType | None) -> bool:
        spec = getattr(module, "__spec__", None)
        initializing = getattr(spec, "_initializing", False)
        return bool(module and spec and not initializing)

    def _cached_import(module_path: str, class_name: str) -> Any:
        """Import and cache a class from a module.

        Args:
            module_path: dotted path to module.
            class_name: Class or function name.

        Returns:
            object: The imported class or function
        """
        # Check whether module is loaded and fully initialized.
        module = sys.modules.get(module_path)
        if not _is_loaded(module):
            module = import_module(module_path)
        return getattr(module, class_name)

    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError as e:
        msg = "%s doesn't look like a module path"
        raise ImportError(msg, dotted_path) from e

    try:
        return _cached_import(module_path, class_name)
    except AttributeError as e:
        msg = "Module '%s' does not define a '%s' attribute/class"
        raise ImportError(msg, module_path, class_name) from e
