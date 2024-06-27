"""This module contains the code allowing to find modules."""

# NOTE: It might be possible to replace a good part of this module's logic
# with utilities from `importlib` (however the util in question is private):
# >>> from importlib.util import _find_spec
# >>> _find_spec("griffe.agents", _find_spec("griffe", None).submodule_search_locations)
# ModuleSpec(
#     name='griffe.agents',
#     loader=<_frozen_importlib_external.SourceFileLoader object at 0x7fa5f34e8110>,
#     origin='/media/data/dev/griffe/src/griffe/agents/__init__.py',
#     submodule_search_locations=['/media/data/dev/griffe/src/griffe/agents'],
# )

from __future__ import annotations

import ast
import os
import re
import sys
from collections import defaultdict
from contextlib import suppress
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Iterator, Sequence, Tuple

from griffe.exceptions import UnhandledEditableModuleError
from griffe.logger import get_logger

if TYPE_CHECKING:
    from typing import Pattern

    from griffe.dataclasses import Module


NamePartsType = Tuple[str, ...]
NamePartsAndPathType = Tuple[NamePartsType, Path]
logger = get_logger(__name__)
_editable_editables_patterns = [re.compile(pat) for pat in (r"^__editables_\w+\.py$", r"^_editable_impl_\w+\.py$")]
_editable_setuptools_patterns = [re.compile(pat) for pat in (r"^__editable__\w+\.py$",)]
_editable_scikit_build_core_patterns = [re.compile(pat) for pat in (r"^_\w+_editable.py$",)]
_editable_meson_python_patterns = [re.compile(pat) for pat in (r"^_\w+_editable_loader.py$",)]


def _match_pattern(string: str, patterns: Sequence[Pattern]) -> bool:
    return any(pattern.match(string) for pattern in patterns)


@dataclass
class Package:
    """This class is a simple placeholder used during the process of finding packages.

    Parameters:
        name: The package name.
        path: The package path(s).
        stubs: An optional path to the related stubs file (.pyi).
    """

    name: str
    """Package name."""
    path: Path
    """Package folder path."""
    stubs: Path | None = None
    """Package stubs file."""


@dataclass
class NamespacePackage:
    """This class is a simple placeholder used during the process of finding packages.

    Parameters:
        name: The package name.
        path: The package paths.
    """

    name: str
    """Namespace package name."""
    path: list[Path]
    """Namespace package folder paths."""


class ModuleFinder:
    """The Griffe finder, allowing to find modules on the file system."""

    accepted_py_module_extensions: ClassVar[list[str]] = [".py", ".pyc", ".pyo", ".pyd", ".pyi", ".so"]
    """List of extensions supported by the finder."""
    extensions_set: ClassVar[set[str]] = set(accepted_py_module_extensions)
    """Set of extensions supported by the finder."""

    def __init__(self, search_paths: Sequence[str | Path] | None = None) -> None:
        """Initialize the finder.

        Parameters:
            search_paths: Optional paths to search into.
        """
        self._paths_contents: dict[Path, list[Path]] = {}
        self.search_paths: list[Path] = []
        """The finder search paths."""

        # Optimization: pre-compute Paths to relieve CPU when joining paths.
        for path in search_paths or sys.path:
            self.append_search_path(Path(path))

        self._always_scan_for: dict[str, list[Path]] = defaultdict(list)
        self._extend_from_pth_files()

    def append_search_path(self, path: Path) -> None:
        """Append a search path.

        The path will be resolved (absolute, normalized).
        The path won't be appended if it is already in the search paths list.

        Parameters:
            path: The path to append.
        """
        path = path.resolve()
        if path not in self.search_paths:
            self.search_paths.append(path)

    def insert_search_path(self, position: int, path: Path) -> None:
        """Insert a search path at the given position.

        The path will be resolved (absolute, normalized).
        The path won't be inserted if it is already in the search paths list.

        Parameters:
            position: The insert position in the list.
            path: The path to insert.
        """
        path = path.resolve()
        if path not in self.search_paths:
            self.search_paths.insert(position, path)

    def find_spec(
        self,
        module: str | Path,
        *,
        try_relative_path: bool = True,
        find_stubs_package: bool = False,
    ) -> tuple[str, Package | NamespacePackage]:
        """Find the top module of a module.

        If a Path is passed, only try to find the module as a file path.
        If a string is passed, first try to find the module as a file path,
        then look into the search paths.

        Parameters:
            module: The module name or path.
            try_relative_path: Whether to try finding the module as a relative path,
                when the given module is not already a path.
            find_stubs_package: Whether to search for stubs-only package.
                If both the package and its stubs are found, they'll be merged together.
                If only the stubs are found, they'll be used as the package itself.

        Raises:
            FileNotFoundError: When a Path was passed and the module could not be found:

                - the directory has no `__init__.py` file in it
                - the path does not exist

            ModuleNotFoundError: When a string was passed and the module could not be found:

                - no `module/__init__.py`
                - no `module.py`
                - no `module.pth`
                - no `module` directory (namespace packages)
                - or unsupported .pth file

        Returns:
            The name of the module, and an instance representing its (namespace) package.
        """
        module_path: Path | list[Path]
        if isinstance(module, Path):
            module_name, module_path = self._module_name_path(module)
            top_module_name = self._top_module_name(module_path)
        elif try_relative_path:
            try:
                module_name, module_path = self._module_name_path(Path(module))
            except FileNotFoundError:
                module_name = module
                top_module_name = module.split(".", 1)[0]
            else:
                top_module_name = self._top_module_name(module_path)
        else:
            module_name = module
            top_module_name = module.split(".", 1)[0]

        # Only search for actual package, let exceptions bubble up.
        if not find_stubs_package:
            return module_name, self.find_package(top_module_name)

        # Search for both package and stubs-only package.
        try:
            package = self.find_package(top_module_name)
        except ModuleNotFoundError:
            package = None
        try:
            stubs = self.find_package(top_module_name + "-stubs")
        except ModuleNotFoundError:
            stubs = None

        # None found, raise error.
        if package is None and stubs is None:
            raise ModuleNotFoundError(top_module_name)

        # Both found, assemble them to be merged later.
        if package and stubs:
            if isinstance(package, Package) and isinstance(stubs, Package):
                package.stubs = stubs.path
            elif isinstance(package, NamespacePackage) and isinstance(stubs, NamespacePackage):
                package.path += stubs.path
            return module_name, package

        # Return either one.
        return module_name, package or stubs  # type: ignore[return-value]

    def find_package(self, module_name: str) -> Package | NamespacePackage:
        """Find a package or namespace package.

        Parameters:
            module_name: The module name.

        Raises:
            ModuleNotFoundError: When the module cannot be found.

        Returns:
            A package or namespace package wrapper.
        """
        filepaths = [
            Path(module_name),
            # TODO: Handle .py[cod] and .so files?
            # This would be needed for package that are composed
            # solely of a file with such an extension.
            Path(f"{module_name}.py"),
        ]

        real_module_name = module_name
        if real_module_name.endswith("-stubs"):
            real_module_name = real_module_name[:-6]
        namespace_dirs = []
        for path in self.search_paths:
            path_contents = self._contents(path)
            if path_contents:
                for choice in filepaths:
                    abs_path = path / choice
                    if abs_path in path_contents:
                        if abs_path.suffix:
                            stubs = abs_path.with_suffix(".pyi")
                            return Package(real_module_name, abs_path, stubs if stubs.exists() else None)
                        init_module = abs_path / "__init__.py"
                        if init_module.exists() and not _is_pkg_style_namespace(init_module):
                            stubs = init_module.with_suffix(".pyi")
                            return Package(real_module_name, init_module, stubs if stubs.exists() else None)
                        init_module = abs_path / "__init__.pyi"
                        if init_module.exists():
                            # Stubs package
                            return Package(real_module_name, init_module, None)
                        namespace_dirs.append(abs_path)

        if namespace_dirs:
            return NamespacePackage(module_name, namespace_dirs)

        raise ModuleNotFoundError(module_name)

    def iter_submodules(
        self,
        path: Path | list[Path],
        seen: set | None = None,
    ) -> Iterator[NamePartsAndPathType]:
        """Iterate on a module's submodules, if any.

        Parameters:
            path: The module path.
            seen: If not none, this set is used to skip some files.
                The goal is to replicate the behavior of Python by
                only using the first packages (with `__init__` modules)
                of the same name found in different namespace packages.
                As soon as we find an `__init__` module, we add its parent
                path to the `seen` set, which will be reused when scanning
                the next namespace packages.

        Yields:
            name_parts (tuple[str, ...]): The parts of a submodule name.
            filepath (Path): A submodule filepath.
        """
        if isinstance(path, list):
            # We never enter this condition again in recursive calls,
            # so we just have to set `seen` once regardless of its value.
            seen = set()
            for path_elem in path:
                yield from self.iter_submodules(path_elem, seen)
            return

        if path.stem == "__init__":
            path = path.parent
        # Optimization: just check if the file name ends with .py[icod]/.so
        # (to distinguish it from a directory), not if it's an actual file.
        elif path.suffix in self.extensions_set:
            return

        # `seen` is only set when we scan a list of paths (namespace package).
        # `skip` is used to prevent yielding modules
        # of a regular subpackage that we already yielded
        # from another part of the namespace.
        skip = set(seen or ())

        for subpath in self._filter_py_modules(path):
            rel_subpath = subpath.relative_to(path)
            if rel_subpath.parent in skip:
                logger.debug(f"Skip {subpath}, another module took precedence")
                continue
            py_file = rel_subpath.suffix == ".py"
            stem = rel_subpath.stem
            if not py_file:
                # .py[cod] and .so files look like `name.cpython-38-x86_64-linux-gnu.ext`
                stem = stem.split(".", 1)[0]
            if stem == "__init__":
                # Optimization: since it's a relative path, if it has only one part
                # and is named __init__, it means it's the starting path
                # (no need to compare it against starting path).
                if len(rel_subpath.parts) == 1:
                    continue
                yield rel_subpath.parts[:-1], subpath
                if seen is not None:
                    seen.add(rel_subpath.parent)
            elif py_file:
                yield rel_subpath.with_suffix("").parts, subpath
            else:
                yield rel_subpath.with_name(stem).parts, subpath

    def submodules(self, module: Module) -> list[NamePartsAndPathType]:
        """Return the list of a module's submodules.

        Parameters:
            module: The parent module.

        Returns:
            A list of tuples containing the parts of the submodule name and its path.
        """
        return sorted(
            chain(
                self.iter_submodules(module.filepath),
                self.iter_submodules(self._always_scan_for[module.name]),
            ),
            key=_module_depth,
        )

    def _module_name_path(self, path: Path) -> tuple[str, Path]:
        # Always return absolute paths to avoid working-directory-dependent issues.
        path = path.absolute()
        if path.is_dir():
            for ext in self.accepted_py_module_extensions:
                module_path = path / f"__init__{ext}"
                if module_path.exists():
                    return path.name, module_path
            return path.name, path
        if path.exists():
            if path.stem == "__init__":
                return path.parent.name, path
            return path.stem, path
        raise FileNotFoundError

    def _contents(self, path: Path) -> list[Path]:
        if path not in self._paths_contents:
            try:
                self._paths_contents[path] = list(path.iterdir())
            except (FileNotFoundError, NotADirectoryError):
                self._paths_contents[path] = []
        return self._paths_contents[path]

    def _append_search_path(self, path: Path) -> None:
        if path not in self.search_paths:
            self.search_paths.append(path)

    def _extend_from_pth_files(self) -> None:
        for path in self.search_paths:
            for item in self._contents(path):
                if item.suffix == ".pth":
                    for directory in _handle_pth_file(item):
                        if scan := directory.always_scan_for:
                            self._always_scan_for[scan].append(directory.path.joinpath(scan))
                        self.append_search_path(directory.path)

    def _filter_py_modules(self, path: Path) -> Iterator[Path]:
        for root, dirs, files in os.walk(path, topdown=True):
            # Optimization: modify dirs in-place to exclude `__pycache__` directories.
            dirs[:] = [dir for dir in dirs if dir != "__pycache__"]
            for relfile in files:
                if os.path.splitext(relfile)[1] in self.extensions_set:
                    yield Path(root, relfile)

    def _top_module_name(self, path: Path) -> str:
        # First find if a parent is in search paths.
        parent_path = path if path.is_dir() else path.parent
        # Always resolve parent path to compare for relativeness against resolved search paths.
        parent_path = parent_path.resolve()
        for search_path in self.search_paths:
            with suppress(ValueError, IndexError):
                rel_path = parent_path.relative_to(search_path.resolve())
                return rel_path.parts[0]
        # If not, get the highest directory with an `__init__` module,
        # add its parent to search paths and return it.
        while parent_path.parent != parent_path and (parent_path.parent / "__init__.py").exists():
            parent_path = parent_path.parent
        self.insert_search_path(0, parent_path.parent)
        return parent_path.name


_re_pkgresources = re.compile(r"(?:__import__\([\"']pkg_resources[\"']\).declare_namespace\(__name__\))")
_re_pkgutil = re.compile(r"(?:__path__ = __import__\([\"']pkgutil[\"']\).extend_path\(__path__, __name__\))")
_re_import_line = re.compile(r"^import[ \t]+\w+$")


# TODO: For more robustness, we should load and minify the AST
# to search for particular call statements.
def _is_pkg_style_namespace(init_module: Path) -> bool:
    code = init_module.read_text(encoding="utf8")
    return bool(_re_pkgresources.search(code) or _re_pkgutil.search(code))


def _module_depth(name_parts_and_path: NamePartsAndPathType) -> int:
    return len(name_parts_and_path[0])


@dataclass
class _SP:
    path: Path
    always_scan_for: str = ""


def _handle_pth_file(path: Path) -> list[_SP]:
    # Support for .pth files pointing to directories.
    # From https://docs.python.org/3/library/site.html:
    # A path configuration file is a file whose name has the form name.pth
    # and exists in one of the four directories mentioned above;
    # its contents are additional items (one per line) to be added to sys.path.
    # Non-existing items are never added to sys.path,
    # and no check is made that the item refers to a directory rather than a file.
    # No item is added to sys.path more than once.
    # Blank lines and lines beginning with # are skipped.
    # Lines starting with import (followed by space or tab) are executed.
    directories = []
    for line in path.read_text(encoding="utf8").strip().replace(";", "\n").splitlines(keepends=False):
        line = line.strip()  # noqa: PLW2901
        if _re_import_line.match(line):
            editable_module = path.parent / f"{line[len('import'):].lstrip()}.py"
            with suppress(UnhandledEditableModuleError):
                return _handle_editable_module(editable_module)
        if line and not line.startswith("#") and os.path.exists(line):
            directories.append(_SP(Path(line)))
    return directories


def _handle_editable_module(path: Path) -> list[_SP]:
    if _match_pattern(path.name, (*_editable_editables_patterns, *_editable_scikit_build_core_patterns)):
        # Support for how 'editables' write these files:
        # example line: `F.map_module('griffe', '/media/data/dev/griffe/src/griffe/__init__.py')`.
        # And how 'scikit-build-core' writes these files:
        # example line: `install({'griffe': '/media/data/dev/griffe/src/griffe/__init__.py'}, {'cmake_example': ...}, None, False, True)`.
        try:
            editable_lines = path.read_text(encoding="utf8").strip().splitlines(keepends=False)
        except FileNotFoundError as error:
            raise UnhandledEditableModuleError(path) from error
        new_path = Path(editable_lines[-1].split("'")[3])
        if new_path.name.startswith("__init__"):
            return [_SP(new_path.parent.parent)]
        return [_SP(new_path)]
    if _match_pattern(path.name, _editable_setuptools_patterns):
        # Support for how 'setuptools' writes these files:
        # example line: `MAPPING = {'griffe': '/media/data/dev/griffe/src/griffe', 'briffe': '/media/data/dev/griffe/src/briffe'}`.
        # with annotation: `MAPPING: dict[str, str] = {...}`.
        parsed_module = ast.parse(path.read_text())
        for node in parsed_module.body:
            if isinstance(node, ast.Assign):
                target = node.targets[0]
            elif isinstance(node, ast.AnnAssign):
                target = node.target
            else:
                continue
            if isinstance(target, ast.Name) and target.id == "MAPPING" and isinstance(node.value, ast.Dict):  # type: ignore[attr-defined]
                return [_SP(Path(cst.value).parent) for cst in node.value.values if isinstance(cst, ast.Constant)]  # type: ignore[attr-defined]
    if _match_pattern(path.name, _editable_meson_python_patterns):
        # Support for how 'meson-python' writes these files:
        # example line: `install({'package', 'module1'}, '/media/data/dev/griffe/build/cp311', ["path"], False)`.
        # Compiled modules then found in the cp311 folder, under src/package.
        parsed_module = ast.parse(path.read_text())
        for node in parsed_module.body:
            if (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "install"
                and isinstance(node.value.args[1], ast.Constant)
            ):
                build_path = Path(node.value.args[1].value, "src")
                pkg_name = next(build_path.iterdir()).name
                return [_SP(build_path, always_scan_for=pkg_name)]
    raise UnhandledEditableModuleError(path)


__all__ = ["ModuleFinder", "NamespacePackage", "Package"]
