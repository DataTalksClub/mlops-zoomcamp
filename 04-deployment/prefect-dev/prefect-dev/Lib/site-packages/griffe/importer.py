"""This module contains utilities to dynamically import objects."""

from __future__ import annotations

import sys
from contextlib import contextmanager
from importlib import import_module
from typing import TYPE_CHECKING, Any, Iterator, Sequence

if TYPE_CHECKING:
    from pathlib import Path


def _error_details(error: BaseException, objpath: str) -> str:
    return f"With sys.path = {sys.path!r}, accessing {objpath!r} raises {error.__class__.__name__}: {error}"


@contextmanager
def sys_path(*paths: str | Path) -> Iterator[None]:
    """Redefine `sys.path` temporarily.

    Parameters:
        *paths: The paths to use when importing modules.
            If no paths are given, keep `sys.path` untouched.

    Yields:
        Nothing.
    """
    if not paths:
        yield
        return
    old_path = sys.path
    sys.path = [str(path) for path in paths]
    try:
        yield
    finally:
        sys.path = old_path


def dynamic_import(import_path: str, import_paths: Sequence[str | Path] | None = None) -> Any:
    """Dynamically import the specified object.

    It can be a module, class, method, function, attribute,
    nested arbitrarily.

    It works like this:

    - for a given object path `a.b.x.y`
    - it tries to import `a.b.x.y` as a module (with `importlib.import_module`)
    - if it fails, it tries again with `a.b.x`, storing `y`
    - then `a.b`, storing `x.y`
    - then `a`, storing `b.x.y`
    - if nothing worked, it raises an error
    - if one of the iteration worked, it moves on, and...
    - it tries to get the remaining (stored) parts with `getattr`
    - for example it gets `b` from `a`, then `x` from `b`, etc.
    - if a single attribute access fails, it raises an error
    - if everything worked, it returns the last obtained attribute

    Since the function potentially tries multiple things before succeeding,
    all errors happening along the way are recorded, and re-emitted with
    an `ImportError` when it fails, to let users know what was tried.

    IMPORTANT: The paths given through the `import_paths` parameter are used
    to temporarily patch `sys.path`: this function is therefore not thread-safe.

    IMPORTANT: The paths given as `import_paths` must be *correct*.
    The contents of `sys.path` must be consistent to what a user of the imported code
    would expect. Given a set of paths, if the import fails for a user, it will fail here too,
    with potentially unintuitive errors. If we wanted to make this function more robust,
    we could add a loop to "roll the window" of given paths, shifting them to the left
    (for example: `("/a/a", "/a/b", "/a/c/")`, then `("/a/b", "/a/c", "/a/a/")`,
    then `("/a/c", "/a/a", "/a/b/")`), to make sure each entry is given highest priority
    at least once, maintaining relative order, but we deem this unncessary for now.

    Parameters:
        import_path: The path of the object to import.
        import_paths: The (sys) paths to import the object from.

    Raises:
        ModuleNotFoundError: When the object's module could not be found.
        ImportError: When there was an import error or when couldn't get the attribute.

    Returns:
        The imported object.
    """
    module_parts: list[str] = import_path.split(".")
    object_parts: list[str] = []
    errors = []

    with sys_path(*(import_paths or ())):
        while module_parts:
            module_path = ".".join(module_parts)
            try:
                module = import_module(module_path)
            except BaseException as error:  # noqa: BLE001
                # pyo3's PanicException can only be caught with BaseException.
                # We do want to catch base exceptions anyway (exit, interrupt, etc.).
                errors.append(_error_details(error, module_path))
                object_parts.insert(0, module_parts.pop(-1))
            else:
                break
        else:
            raise ImportError("; ".join(errors))

        # Sometimes extra dependencies are not installed,
        # so importing the leaf module fails with a ModuleNotFoundError,
        # or later `getattr` triggers additional code that fails.
        # In these cases, and for consistency, we always re-raise an ImportError
        # instead of an any other exception (it's called "dynamic import" after all).
        # See https://github.com/mkdocstrings/mkdocstrings/issues/380
        value = module
        for part in object_parts:
            try:
                value = getattr(value, part)
            except BaseException as error:  # noqa: BLE001
                errors.append(_error_details(error, module_path + ":" + ".".join(object_parts)))
                raise ImportError("; ".join(errors))  # noqa: B904,TRY200

    return value


__all__ = ["dynamic_import", "sys_path"]
