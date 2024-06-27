"""Test helpers and pytest fixtures."""

from __future__ import annotations

import sys
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from importlib import invalidate_caches
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Any, Iterator, Mapping, Sequence

from griffe.agents.inspector import inspect
from griffe.agents.visitor import visit
from griffe.collections import LinesCollection
from griffe.dataclasses import Module, Object
from griffe.loader import GriffeLoader

if TYPE_CHECKING:
    from griffe.collections import ModulesCollection
    from griffe.enumerations import Parser
    from griffe.extensions.base import Extensions

TMPDIR_PREFIX = "griffe_"


@dataclass
class TmpPackage:
    """A temporary package."""

    tmpdir: Path
    """The temporary directory containing the package."""
    name: str
    """The package name, as to dynamically import it."""
    path: Path
    """The package path."""

    def __post_init__(self) -> None:
        self.tmpdir = self.tmpdir.resolve()
        self.path = self.path.resolve()


@contextmanager
def temporary_pyfile(code: str, *, module_name: str = "module") -> Iterator[tuple[str, Path]]:
    """Create a Python file containing the given code in a temporary directory.

    Parameters:
        code: The code to write to the temporary file.
        module_name: The name of the temporary module.

    Yields:
        module_name: The module name, as to dynamically import it.
        module_path: The module path.
    """
    with tempfile.TemporaryDirectory(prefix=TMPDIR_PREFIX) as tmpdir:
        tmpfile = Path(tmpdir) / f"{module_name}.py"
        tmpfile.write_text(dedent(code))
        yield module_name, tmpfile


@contextmanager
def temporary_pypackage(
    package: str,
    modules: Sequence[str] | Mapping[str, str] | None = None,
    *,
    init: bool = True,
    inits: bool = True,
) -> Iterator[TmpPackage]:
    """Create a package containing the given modules in a temporary directory.

    Parameters:
        package: The package name. Example: `"a"` gives
            a package named `a`, while `"a/b"` gives a namespace package
            named `a` with a package inside named `b`.
            If `init` is false, then `b` is also a namespace package.
        modules: Additional modules to create in the package.
            If a list, simply touch the files: `["b.py", "c/d.py", "e/f"]`.
            If a dict, keys are the file names and values their contents:
            `{"b.py": "b = 1", "c/d.py": "print('hey from c')"}`.
        init: Whether to create an `__init__` module in the top package.
        inits: Whether to create `__init__` modules in subpackages.

    Yields:
        A temporary package.
    """
    modules = modules or {}
    if isinstance(modules, list):
        modules = {mod: "" for mod in modules}
    mkdir_kwargs = {"parents": True, "exist_ok": True}
    with tempfile.TemporaryDirectory(prefix=TMPDIR_PREFIX) as tmpdir:
        tmpdirpath = Path(tmpdir)
        package_name = ".".join(Path(package).parts)
        package_path = tmpdirpath / package
        package_path.mkdir(**mkdir_kwargs)
        if init:
            package_path.joinpath("__init__.py").touch()
        for module_name, module_contents in modules.items():  # type: ignore[union-attr]
            current_path = package_path
            for part in Path(module_name).parts:
                if part.endswith((".py", ".pyi")):
                    current_path.joinpath(part).write_text(dedent(module_contents))
                else:
                    current_path /= part
                    current_path.mkdir(**mkdir_kwargs)
                    if inits:
                        current_path.joinpath("__init__.py").touch()
        yield TmpPackage(tmpdirpath, package_name, package_path)


@contextmanager
def temporary_visited_package(
    package: str,
    modules: Sequence[str] | Mapping[str, str] | None = None,
    *,
    init: bool = True,
    extensions: Extensions | None = None,
    docstring_parser: Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
    allow_inspection: bool = False,
    store_source: bool = True,
) -> Iterator[Module]:
    """Create and visit a temporary package.

    Parameters:
        package: The package name. Example: `"a"` gives
            a package named `a`, while `"a/b"` gives a namespace package
            named `a` with a package inside named `b`.
            If `init` is false, then `b` is also a namespace package.
        modules: Additional modules to create in the package.
            If a list, simply touch the files: `["b.py", "c/d.py", "e/f"]`.
            If a dict, keys are the file names and values their contents:
            `{"b.py": "b = 1", "c/d.py": "print('hey from c')"}`.
        init: Whether to create an `__init__` module in the leaf package.
        extensions: The extensions to use.
        docstring_parser: The docstring parser to use. By default, no parsing is done.
        docstring_options: Additional docstring parsing options.
        lines_collection: A collection of source code lines.
        modules_collection: A collection of modules.
        allow_inspection: Whether to allow inspecting modules when visiting them is not possible.
        store_source: Whether to store code source in the lines collection.

    Yields:
        A module.
    """
    with temporary_pypackage(package, modules, init=init) as tmp_package:
        loader = GriffeLoader(
            search_paths=[tmp_package.tmpdir],
            extensions=extensions,
            docstring_parser=docstring_parser,
            docstring_options=docstring_options,
            lines_collection=lines_collection,
            modules_collection=modules_collection,
            allow_inspection=allow_inspection,
            store_source=store_source,
        )
        yield loader.load(tmp_package.name)  # type: ignore[misc]


@contextmanager
def temporary_visited_module(
    code: str,
    *,
    module_name: str = "module",
    extensions: Extensions | None = None,
    parent: Module | None = None,
    docstring_parser: Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
) -> Iterator[Module]:
    """Create and visit a temporary module with the given code.

    Parameters:
        code: The code of the module.
        module_name: The name of the temporary module.
        extensions: The extensions to use when visiting the AST.
        parent: The optional parent of this module.
        docstring_parser: The docstring parser to use. By default, no parsing is done.
        docstring_options: Additional docstring parsing options.
        lines_collection: A collection of source code lines.
        modules_collection: A collection of modules.

    Yields:
        The visited module.
    """
    code = dedent(code)
    with temporary_pyfile(code, module_name=module_name) as (_, path):
        lines_collection = lines_collection or LinesCollection()
        lines_collection[path] = code.splitlines()
        module = visit(
            module_name,
            filepath=path,
            code=code,
            extensions=extensions,
            parent=parent,
            docstring_parser=docstring_parser,
            docstring_options=docstring_options,
            lines_collection=lines_collection,
            modules_collection=modules_collection,
        )
        module.modules_collection[module_name] = module
        yield module


@contextmanager
def temporary_inspected_module(
    code: str,
    *,
    module_name: str = "module",
    import_paths: list[Path] | None = None,
    extensions: Extensions | None = None,
    parent: Module | None = None,
    docstring_parser: Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
) -> Iterator[Module]:
    """Create and inspect a temporary module with the given code.

    Parameters:
        code: The code of the module.
        module_name: The name of the temporary module.
        import_paths: Paths to import the module from.
        extensions: The extensions to use when visiting the AST.
        parent: The optional parent of this module.
        docstring_parser: The docstring parser to use. By default, no parsing is done.
        docstring_options: Additional docstring parsing options.
        lines_collection: A collection of source code lines.
        modules_collection: A collection of modules.

    Yields:
        The inspected module.
    """
    with temporary_pyfile(code, module_name=module_name) as (_, path):
        lines_collection = lines_collection or LinesCollection()
        lines_collection[path] = code.splitlines()
        try:
            module = inspect(
                module_name,
                filepath=path,
                import_paths=import_paths,
                extensions=extensions,
                parent=parent,
                docstring_parser=docstring_parser,
                docstring_options=docstring_options,
                lines_collection=lines_collection,
                modules_collection=modules_collection,
            )
            module.modules_collection[module_name] = module
            yield module
        finally:
            if module_name in sys.modules:
                del sys.modules[module_name]
            invalidate_caches()


def vtree(*objects: Object, return_leaf: bool = False) -> Object:
    """Link objects together, vertically.

    Parameters:
        *objects: A sequence of objects. The first one is at the top of the tree.
        return_leaf: Whether to return the leaf instead of the root.

    Raises:
        ValueError: When no objects are provided.

    Returns:
        The top or leaf object.
    """
    if not objects:
        raise ValueError("At least one object must be provided")
    top = objects[0]
    leaf = top
    for obj in objects[1:]:
        leaf.set_member(obj.name, obj)
        leaf = obj
    return leaf if return_leaf else top


def htree(*objects: Object) -> Object:
    """Link objects together, horizontally.

    Parameters:
        *objects: A sequence of objects. All objects starting at the second become members of the first.

    Raises:
        ValueError: When no objects are provided.

    Returns:
        The first given object, with all the other objects as members of it.
    """
    if not objects:
        raise ValueError("At least one object must be provided")
    top = objects[0]
    for obj in objects[1:]:
        top.set_member(obj.name, obj)
    return top


def module_vtree(path: str, *, leaf_package: bool = True, return_leaf: bool = False) -> Module:
    """Link objects together, vertically.

    Parameters:
        path: The complete module path, like `"a.b.c.d"`.
        leaf_package: Whether the deepest module should also be a package.
        return_leaf: Whether to return the leaf instead of the root.

    Raises:
        ValueError: When no objects are provided.

    Returns:
        The top or leaf module.
    """
    parts = path.split(".")
    modules = [Module(name, filepath=Path(*parts[:index], "__init__.py")) for index, name in enumerate(parts)]
    if not leaf_package:
        try:
            filepath = modules[-1].filepath.with_stem(parts[-1])  # type: ignore[union-attr]
        except AttributeError:  # TODO: remove once Python 3.8 is dropped
            filepath = modules[-1].filepath.with_name(f"{parts[-1]}.py")  # type: ignore[union-attr]
        modules[-1]._filepath = filepath
    return vtree(*modules, return_leaf=return_leaf)  # type: ignore[return-value]


__all__ = [
    "htree",
    "module_vtree",
    "temporary_inspected_module",
    "temporary_pyfile",
    "temporary_pypackage",
    "temporary_visited_module",
    "temporary_visited_package",
    "TmpPackage",
    "vtree",
]
