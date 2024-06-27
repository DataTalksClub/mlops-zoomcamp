"""This module contains the data classes that represent Python objects.

The different objects are modules, classes, functions, and attribute
(variables like module/class/instance attributes).
"""

from __future__ import annotations

import inspect
import warnings
from collections import defaultdict
from contextlib import suppress
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Any, Callable, Literal, Sequence, Union, cast

from griffe.c3linear import c3linear_merge
from griffe.docstrings.parsers import parse
from griffe.enumerations import Kind, ParameterKind, Parser
from griffe.exceptions import AliasResolutionError, BuiltinModuleError, CyclicAliasError, NameResolutionError
from griffe.expressions import ExprCall, ExprName
from griffe.logger import get_logger
from griffe.mixins import ObjectAliasMixin

if TYPE_CHECKING:
    from griffe.collections import LinesCollection, ModulesCollection
    from griffe.docstrings.dataclasses import DocstringSection
    from griffe.expressions import Expr

from functools import cached_property

logger = get_logger(__name__)


class Decorator:
    """This class represents decorators."""

    def __init__(self, value: str | Expr, *, lineno: int | None, endlineno: int | None) -> None:
        """Initialize the decorator.

        Parameters:
            value: The decorator code.
            lineno: The starting line number.
            endlineno: The ending line number.
        """
        self.value: str | Expr = value
        """The decorator value (as a Griffe expression or string)."""
        self.lineno: int | None = lineno
        """The starting line number of the decorator."""
        self.endlineno: int | None = endlineno
        """The ending line number of the decorator."""

    @property
    def callable_path(self) -> str:
        """The path of the callable used as decorator."""
        value = self.value.function if isinstance(self.value, ExprCall) else self.value
        return value if isinstance(value, str) else value.canonical_path

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
        """Return this decorator's data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        return {
            "value": self.value,
            "lineno": self.lineno,
            "endlineno": self.endlineno,
        }


class Docstring:
    """This class represents docstrings."""

    def __init__(
        self,
        value: str,
        *,
        lineno: int | None = None,
        endlineno: int | None = None,
        parent: Object | None = None,
        parser: Literal["google", "numpy", "sphinx"] | Parser | None = None,
        parser_options: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the docstring.

        Parameters:
            value: The docstring value.
            lineno: The starting line number.
            endlineno: The ending line number.
            parent: The parent object on which this docstring is attached.
            parser: The docstring parser to use. By default, no parsing is done.
            parser_options: Additional docstring parsing options.
        """
        self.value: str = inspect.cleandoc(value.rstrip())
        """The original value of the docstring, cleaned by `inspect.cleandoc`."""
        self.lineno: int | None = lineno
        """The starting line number of the docstring."""
        self.endlineno: int | None = endlineno
        """The ending line number of the docstring."""
        self.parent: Object | None = parent
        """The object this docstring is attached to."""
        self.parser: Literal["google", "numpy", "sphinx"] | Parser | None = parser
        """The selected docstring parser."""
        self.parser_options: dict[str, Any] = parser_options or {}
        """The configured parsing options."""

    @property
    def lines(self) -> list[str]:
        """The lines of the docstring."""
        return self.value.split("\n")

    @cached_property
    def parsed(self) -> list[DocstringSection]:
        """The docstring sections, parsed into structured data."""
        return self.parse()

    def parse(
        self,
        parser: Literal["google", "numpy", "sphinx"] | Parser | None = None,
        **options: Any,
    ) -> list[DocstringSection]:
        """Parse the docstring into structured data.

        Parameters:
            parser: The docstring parser to use.
                In order: use the given parser, or the self parser, or no parser (return a single text section).
            **options: Additional docstring parsing options.

        Returns:
            The parsed docstring as a list of sections.
        """
        return parse(self, parser or self.parser, **(options or self.parser_options))

    def as_dict(
        self,
        *,
        full: bool = False,
        docstring_parser: Parser | None = None,
        **kwargs: Any,  # noqa: ARG002
    ) -> dict[str, Any]:
        """Return this docstring's data as a dictionary.

        Parameters:
            full: Whether to return full info, or just base info.
            docstring_parser: Deprecated. The docstring parser to parse the docstring with. By default, no parsing is done.
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        # TODO: Remove at some point.
        if docstring_parser is not None:
            warnings.warn("Parameter `docstring_parser` is deprecated and has no effect.", stacklevel=1)

        base: dict[str, Any] = {
            "value": self.value,
            "lineno": self.lineno,
            "endlineno": self.endlineno,
        }
        if full:
            base["parsed"] = self.parsed
        return base


class Parameter:
    """This class represent a function parameter."""

    def __init__(
        self,
        name: str,
        *,
        annotation: str | Expr | None = None,
        kind: ParameterKind | None = None,
        default: str | Expr | None = None,
        docstring: Docstring | None = None,
    ) -> None:
        """Initialize the parameter.

        Parameters:
            name: The parameter name.
            annotation: The parameter annotation, if any.
            kind: The parameter kind.
            default: The parameter default, if any.
            docstring: The parameter docstring.
        """
        self.name: str = name
        """The parameter name."""
        self.annotation: str | Expr | None = annotation
        """The parameter type annotation."""
        self.kind: ParameterKind | None = kind
        """The parameter kind."""
        self.default: str | Expr | None = default
        """The parameter default value."""
        self.docstring: Docstring | None = docstring
        """The parameter docstring."""
        # The parent function is set in `Function.__init__`,
        # when the parameters are assigned to the function.
        self.function: Function | None = None
        """The parent function of the parameter."""

    def __str__(self) -> str:
        param = f"{self.name}: {self.annotation} = {self.default}"
        if self.kind:
            return f"[{self.kind.value}] {param}"
        return param

    def __repr__(self) -> str:
        return f"Parameter(name={self.name!r}, annotation={self.annotation!r}, kind={self.kind!r}, default={self.default!r})"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Parameter):
            return NotImplemented
        return (
            self.name == __value.name
            and self.annotation == __value.annotation
            and self.kind == __value.kind
            and self.default == __value.default
        )

    @property
    def required(self) -> bool:
        """Whether this parameter is required."""
        return self.default is None

    def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
        """Return this parameter's data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base: dict[str, Any] = {
            "name": self.name,
            "annotation": self.annotation,
            "kind": self.kind,
            "default": self.default,
        }
        if self.docstring:
            base["docstring"] = self.docstring.as_dict(full=full)
        return base


class Parameters:
    """This class is a container for parameters.

    It allows to get parameters using their position (index) or their name:

    ```pycon
    >>> parameters = Parameters(Parameter("hello"))
    >>> parameters[0] is parameters["hello"]
    True
    ```
    """

    def __init__(self, *parameters: Parameter) -> None:
        """Initialize the parameters container.

        Parameters:
            *parameters: The initial parameters to add to the container.
        """
        self._parameters_list: list[Parameter] = []
        self._parameters_dict: dict[str, Parameter] = {}
        for parameter in parameters:
            self.add(parameter)

    def __repr__(self) -> str:
        return f"Parameters({', '.join(repr(param) for param in self._parameters_list)})"

    def __getitem__(self, name_or_index: int | str) -> Parameter:
        if isinstance(name_or_index, int):
            return self._parameters_list[name_or_index]
        return self._parameters_dict[name_or_index.lstrip("*")]

    def __len__(self):
        return len(self._parameters_list)

    def __iter__(self):
        return iter(self._parameters_list)

    def __contains__(self, param_name: str):
        return param_name.lstrip("*") in self._parameters_dict

    def add(self, parameter: Parameter) -> None:
        """Add a parameter to the container.

        Parameters:
            parameter: The function parameter to add.

        Raises:
            ValueError: When a parameter with the same name is already present.
        """
        if parameter.name not in self._parameters_dict:
            self._parameters_dict[parameter.name] = parameter
            self._parameters_list.append(parameter)
        else:
            raise ValueError(f"parameter {parameter.name} already present")


class Object(ObjectAliasMixin):
    """An abstract class representing a Python object."""

    kind: Kind
    """The object kind."""
    is_alias: bool = False
    """Whether this object is an alias."""
    is_collection: bool = False
    """Whether this object is a (modules) collection."""
    inherited: bool = False
    """Whether this object (alias) is inherited.

    Objects can never be inherited, only aliases can.
    """

    def __init__(
        self,
        name: str,
        *,
        lineno: int | None = None,
        endlineno: int | None = None,
        runtime: bool = True,
        docstring: Docstring | None = None,
        parent: Module | Class | None = None,
        lines_collection: LinesCollection | None = None,
        modules_collection: ModulesCollection | None = None,
    ) -> None:
        """Initialize the object.

        Parameters:
            name: The object name, as declared in the code.
            lineno: The object starting line, or None for modules. Lines start at 1.
            endlineno: The object ending line (inclusive), or None for modules.
            runtime: Whether this object is present at runtime or not.
            docstring: The object docstring.
            parent: The object parent.
            lines_collection: A collection of source code lines.
            modules_collection: A collection of modules.
        """
        self.name: str = name
        """The object name."""

        self.lineno: int | None = lineno
        """The starting line number of the object."""

        self.endlineno: int | None = endlineno
        """The ending line number of the object."""

        self.docstring: Docstring | None = docstring
        """The object docstring."""

        self.parent: Module | Class | None = parent
        """The parent of the object (none if top module)."""

        self.members: dict[str, Object | Alias] = {}
        """The object members (modules, classes, functions, attributes)."""

        self.labels: set[str] = set()
        """The object labels (`property`, `dataclass`, etc.)."""

        self.imports: dict[str, str] = {}
        """The other objects imported by this object.

        Keys are the names within the object (`from ... import ... as AS_NAME`),
        while the values are the actual names of the objects (`from ... import REAL_NAME as ...`).
        """

        self.exports: set[str] | list[str | ExprName] | None = None
        """The names of the objects exported by this (module) object through the `__all__` variable.

        Exports can contain string (object names) or resolvable names,
        like other lists of exports coming from submodules:

        ```python
        from .submodule import __all__ as submodule_all

        __all__ = ["hello", *submodule_all]
        ```

        Exports get expanded by the loader before it expands wildcards and resolves aliases.
        """

        self.aliases: dict[str, Alias] = {}
        """The aliases pointing to this object."""

        self.runtime: bool = runtime
        """Whether this object is available at runtime.

        Typically, type-guarded objects (under an `if TYPE_CHECKING` condition)
        are not available at runtime.
        """

        self.extra: dict[str, dict[str, Any]] = defaultdict(dict)
        """Namespaced dictionaries storing extra metadata for this object, used by extensions."""

        self.public: bool | None = None
        """Whether this object is public."""

        self.deprecated: str | None = None
        """Whether this object is deprecated (boolean or deprecation message)."""

        self._lines_collection: LinesCollection | None = lines_collection
        self._modules_collection: ModulesCollection | None = modules_collection

        # attach the docstring to this object
        if docstring:
            docstring.parent = self

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r}, {self.lineno!r}, {self.endlineno!r})"

    def __bool__(self) -> bool:
        # Prevent using `__len__`.
        return True

    def __len__(self) -> int:
        return len(self.members) + sum(len(member) for member in self.members.values())

    @property
    def has_docstring(self) -> bool:
        """Whether this object has a docstring (empty or not)."""
        return bool(self.docstring)

    @property
    def has_docstrings(self) -> bool:
        """Whether this object or any of its members has a docstring (empty or not)."""
        if self.has_docstring:
            return True
        return any(member.has_docstrings for member in self.members.values())

    def member_is_exported(self, member: Object | Alias, *, explicitely: bool = True) -> bool:  # noqa: ARG002
        """Deprecated. Use [`member.is_exported`][griffe.dataclasses.Object.is_exported] instead."""
        warnings.warn(
            "Method `member_is_exported` is deprecated. Use `member.is_exported` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return member.is_exported

    def is_kind(self, kind: str | Kind | set[str | Kind]) -> bool:
        """Tell if this object is of the given kind.

        Parameters:
            kind: An instance or set of kinds (strings or enumerations).

        Raises:
            ValueError: When an empty set is given as argument.

        Returns:
            True or False.
        """
        if isinstance(kind, set):
            if not kind:
                raise ValueError("kind must not be an empty set")
            return self.kind in (knd if isinstance(knd, Kind) else Kind(knd) for knd in kind)
        if isinstance(kind, str):
            kind = Kind(kind)
        return self.kind is kind

    @cached_property
    def inherited_members(self) -> dict[str, Alias]:
        """Members that are inherited from base classes.

        This method is part of the consumer API:
        do not use when producing Griffe trees!
        """
        if not isinstance(self, Class):
            return {}
        try:
            mro = self.mro()
        except ValueError as error:
            logger.debug(error)
            return {}
        inherited_members = {}
        for base in reversed(mro):
            for name, member in base.members.items():
                if name not in self.members:
                    inherited_members[name] = Alias(name, member, parent=self, inherited=True)
        return inherited_members

    @property
    def is_module(self) -> bool:
        """Whether this object is a module."""
        return self.kind is Kind.MODULE

    @property
    def is_class(self) -> bool:
        """Whether this object is a class."""
        return self.kind is Kind.CLASS

    @property
    def is_function(self) -> bool:
        """Whether this object is a function."""
        return self.kind is Kind.FUNCTION

    @property
    def is_attribute(self) -> bool:
        """Whether this object is an attribute."""
        return self.kind is Kind.ATTRIBUTE

    @property
    def is_init_module(self) -> bool:
        """Whether this object is an `__init__.py` module."""
        return False

    @property
    def is_package(self) -> bool:
        """Whether this object is a package (top module)."""
        return False

    @property
    def is_subpackage(self) -> bool:
        """Whether this object is a subpackage."""
        return False

    @property
    def is_namespace_package(self) -> bool:
        """Whether this object is a namespace package (top folder, no `__init__.py`)."""
        return False

    @property
    def is_namespace_subpackage(self) -> bool:
        """Whether this object is a namespace subpackage."""
        return False

    def has_labels(self, *labels: str | set[str]) -> bool:
        """Tell if this object has all the given labels.

        Parameters:
            *labels: Labels that must be present.

        Returns:
            True or False.
        """
        # TODO: Remove at some point.
        all_labels = set()
        for label in labels:
            if isinstance(label, str):
                all_labels.add(label)
            else:
                warnings.warn(
                    "Passing a set of labels to `has_labels` is deprecated. Pass multiple strings instead.",
                    DeprecationWarning,
                    stacklevel=2,
                )
                all_labels.update(label)
        return all_labels.issubset(self.labels)

    def filter_members(self, *predicates: Callable[[Object | Alias], bool]) -> dict[str, Object | Alias]:
        """Filter and return members based on predicates.

        Parameters:
            *predicates: A list of predicates, i.e. callables accepting a member as argument and returning a boolean.

        Returns:
            A dictionary of members.
        """
        if not predicates:
            return self.members
        members: dict[str, Object | Alias] = {}
        for name, member in self.members.items():
            if all(predicate(member) for predicate in predicates):
                members[name] = member
        return members

    @property
    def module(self) -> Module:
        """The parent module of this object.

        Raises:
            ValueError: When the object is not a module and does not have a parent.
        """
        if isinstance(self, Module):
            return self
        if self.parent is not None:
            return self.parent.module
        raise ValueError(f"Object {self.name} does not have a parent module")

    @property
    def package(self) -> Module:
        """The absolute top module (the package) of this object."""
        module = self.module
        while module.parent:
            module = module.parent  # type: ignore[assignment]  # always a module
        return module

    @property
    def filepath(self) -> Path | list[Path]:
        """The file path (or directory list for namespace packages) where this object was defined."""
        return self.module.filepath

    @property
    def relative_package_filepath(self) -> Path:
        """The file path where this object was defined, relative to the top module path.

        Raises:
            ValueError: When the relative path could not be computed.
        """
        package_path = self.package.filepath

        # Current "module" is a namespace package.
        if isinstance(self.filepath, list):
            # Current package is a namespace package.
            if isinstance(package_path, list):
                for pkg_path in package_path:
                    for self_path in self.filepath:
                        with suppress(ValueError):
                            return self_path.relative_to(pkg_path.parent)

            # Current package is a regular package.
            # NOTE: Technically it makes no sense to have a namespace package
            # under a non-namespace one, so we should never enter this branch.
            else:
                for self_path in self.filepath:
                    with suppress(ValueError):
                        return self_path.relative_to(package_path.parent.parent)
            raise ValueError

        # Current package is a namespace package,
        # and current module is a regular module or package.
        if isinstance(package_path, list):
            for pkg_path in package_path:
                with suppress(ValueError):
                    return self.filepath.relative_to(pkg_path.parent)
            raise ValueError

        # Current package is a regular package,
        # and current module is a regular module or package,
        # try to compute the path relative to the parent folder
        # of the package (search path).
        return self.filepath.relative_to(package_path.parent.parent)

    @property
    def relative_filepath(self) -> Path:
        """The file path where this object was defined, relative to the current working directory.

        If this object's file path is not relative to the current working directory, return its absolute path.

        Raises:
            ValueError: When the relative path could not be computed.
        """
        cwd = Path.cwd()
        if isinstance(self.filepath, list):
            for self_path in self.filepath:
                with suppress(ValueError):
                    return self_path.relative_to(cwd)
            raise ValueError(f"No directory in {self.filepath!r} is relative to the current working directory {cwd}")
        try:
            return self.filepath.relative_to(cwd)
        except ValueError:
            return self.filepath

    @property
    def path(self) -> str:
        """The dotted path of this object.

        On regular objects (not aliases), the path is the canonical path.
        """
        return self.canonical_path

    @property
    def canonical_path(self) -> str:
        """The full dotted path of this object.

        The canonical path is the path where the object was defined (not imported).
        """
        if self.parent is None:
            return self.name
        return ".".join((self.parent.path, self.name))

    @property
    def modules_collection(self) -> ModulesCollection:
        """The modules collection attached to this object or its parents.

        Raises:
            ValueError: When no modules collection can be found in the object or its parents.
        """
        if self._modules_collection is not None:
            return self._modules_collection
        if self.parent is None:
            raise ValueError("no modules collection in this object or its parents")
        return self.parent.modules_collection

    @property
    def lines_collection(self) -> LinesCollection:
        """The lines collection attached to this object or its parents.

        Raises:
            ValueError: When no modules collection can be found in the object or its parents.
        """
        if self._lines_collection is not None:
            return self._lines_collection
        if self.parent is None:
            raise ValueError("no lines collection in this object or its parents")
        return self.parent.lines_collection

    @property
    def lines(self) -> list[str]:
        """The lines containing the source of this object."""
        try:
            filepath = self.filepath
        except BuiltinModuleError:
            return []
        if isinstance(filepath, list):
            return []
        try:
            lines = self.lines_collection[filepath]
        except KeyError:
            return []
        if self.is_module:
            return lines
        if self.lineno is None or self.endlineno is None:
            return []
        return lines[self.lineno - 1 : self.endlineno]

    @property
    def source(self) -> str:
        """The source code of this object."""
        return dedent("\n".join(self.lines))

    def resolve(self, name: str) -> str:
        """Resolve a name within this object's and parents' scope.

        Parameters:
            name: The name to resolve.

        Raises:
            NameResolutionError: When the name could not be resolved.

        Returns:
            The resolved name.
        """
        # Name is a member this object.
        if name in self.members:
            if self.members[name].is_alias:
                return self.members[name].target_path  # type: ignore[union-attr]
            return self.members[name].path

        # Name was imported.
        if name in self.imports:
            return self.imports[name]

        # Name unknown and no more parent scope.
        if self.parent is None:
            # could be a built-in
            raise NameResolutionError(f"{name} could not be resolved in the scope of {self.path}")

        # Name is parent, non-module object.
        # NOTE: possibly useless branch.
        if name == self.parent.name and not self.parent.is_module:
            return self.parent.path

        # Recurse in parent.
        return self.parent.resolve(name)

    def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:
        """Return this object's data as a dictionary.

        Parameters:
            full: Whether to return full info, or just base info.
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base = {
            "kind": self.kind,
            "name": self.name,
        }

        if full:
            base.update(
                {
                    "path": self.path,
                    "filepath": self.filepath,
                    "relative_filepath": self.relative_filepath,
                    "relative_package_filepath": self.relative_package_filepath,
                },
            )

        if self.lineno is not None:
            base["lineno"] = self.lineno
        if self.endlineno is not None:
            base["endlineno"] = self.endlineno
        if self.docstring:
            base["docstring"] = self.docstring

        # doing this last for a prettier JSON dump
        base["labels"] = self.labels
        base["members"] = [member.as_dict(full=full, **kwargs) for member in self.members.values()]

        return base


class Alias(ObjectAliasMixin):
    """This class represents an alias, or indirection, to an object declared in another module.

    Aliases represent objects that are in the scope of a module or class,
    but were imported from another module.

    They behave almost exactly like regular objects, to a few exceptions:

    - line numbers are those of the alias, not the target
    - the path is the alias path, not the canonical one
    - the name can be different from the target's
    - if the target can be resolved, the kind is the target's kind
    - if the target cannot be resolved, the kind becomes [Kind.ALIAS][griffe.dataclasses.Kind]
    """

    is_alias: bool = True
    is_collection: bool = False

    def __init__(
        self,
        name: str,
        target: str | Object | Alias,
        *,
        lineno: int | None = None,
        endlineno: int | None = None,
        runtime: bool = True,
        parent: Module | Class | Alias | None = None,
        inherited: bool = False,
    ) -> None:
        """Initialize the alias.

        Parameters:
            name: The alias name.
            target: If it's a string, the target resolution is delayed until accessing the target property.
                If it's an object, or even another alias, the target is immediately set.
            lineno: The alias starting line number.
            endlineno: The alias ending line number.
            runtime: Whether this alias is present at runtime or not.
            parent: The alias parent.
            inherited: Whether this alias wraps an inherited member.
        """
        self.name: str = name
        """The alias name."""

        self.alias_lineno: int | None = lineno
        """The starting line number of the alias."""

        self.alias_endlineno: int | None = endlineno
        """The ending line number of the alias."""

        self.runtime: bool = runtime
        """Whether this alias is available at runtime."""

        self.inherited: bool = inherited
        """Whether this alias represents an inherited member."""

        self.public: bool | None = None
        """Whether this alias is public."""

        self.deprecated: str | bool | None = None
        """Whether this alias is deprecated (boolean or deprecation message)."""

        self._parent: Module | Class | Alias | None = parent
        self._passed_through: bool = False

        self.target_path: str
        """The path of this alias' target."""

        if isinstance(target, str):
            self._target: Object | Alias | None = None
            self.target_path = target
        else:
            self._target = target
            self.target_path = target.path
            self._update_target_aliases()

    def __repr__(self) -> str:
        return f"Alias({self.name!r}, {self.target_path!r})"

    def __bool__(self) -> bool:
        # Prevent using `__len__`.
        return True

    def __len__(self) -> int:
        return 1

    # SPECIAL PROXIES -------------------------------
    # The following methods and properties exist on the target(s),
    # but we must handle them in a special way.

    @property
    def kind(self) -> Kind:
        """The target's kind, or `Kind.ALIAS` if the target cannot be resolved."""
        # custom behavior to avoid raising exceptions
        try:
            return self.final_target.kind
        except (AliasResolutionError, CyclicAliasError):
            return Kind.ALIAS

    @property
    def has_docstring(self) -> bool:
        """Whether this alias' target has a non-empty docstring."""
        try:
            return self.final_target.has_docstring
        except (AliasResolutionError, CyclicAliasError):
            return False

    @property
    def has_docstrings(self) -> bool:
        """Whether this alias' target or any of its members has a non-empty docstring."""
        try:
            return self.final_target.has_docstrings
        except (AliasResolutionError, CyclicAliasError):
            return False

    @property
    def parent(self) -> Module | Class | Alias | None:
        """The parent of this alias."""
        return self._parent

    @parent.setter
    def parent(self, value: Module | Class | Alias) -> None:
        self._parent = value
        self._update_target_aliases()

    @property
    def path(self) -> str:
        """The dotted path / import path of this object."""
        return ".".join((self.parent.path, self.name))  # type: ignore[union-attr]  # we assume there's always a parent

    @property
    def modules_collection(self) -> ModulesCollection:
        """The modules collection attached to the alias parents."""
        # no need to forward to the target
        return self.parent.modules_collection  # type: ignore[union-attr]  # we assume there's always a parent

    @cached_property
    def members(self) -> dict[str, Object | Alias]:
        """The target's members (modules, classes, functions, attributes)."""
        final_target = self.final_target

        # We recreate aliases to maintain a correct hierarchy,
        # and therefore correct paths. The path of an alias member
        # should be the path of the alias plus the member's name,
        # not the original member's path.
        return {
            name: Alias(name, target=member, parent=self, inherited=False)
            for name, member in final_target.members.items()
        }

    @cached_property
    def inherited_members(self) -> dict[str, Alias]:
        """Members that are inherited from base classes.

        Each inherited member of the target will be wrapped in an alias,
        to preserve correct object access paths.

        This method is part of the consumer API:
        do not use when producing Griffe trees!
        """
        final_target = self.final_target

        # We recreate aliases to maintain a correct hierarchy,
        # and therefore correct paths. The path of an alias member
        # should be the path of the alias plus the member's name,
        # not the original member's path.
        return {
            name: Alias(name, target=member, parent=self, inherited=True)
            for name, member in final_target.inherited_members.items()
        }

    def as_json(self, *, full: bool = False, **kwargs: Any) -> str:
        """Return this target's data as a JSON string.

        Parameters:
            full: Whether to return full info, or just base info.
            **kwargs: Additional serialization options passed to encoder.

        Returns:
            A JSON string.
        """
        try:
            return self.final_target.as_json(full=full, **kwargs)
        except (AliasResolutionError, CyclicAliasError):
            return super().as_json(full=full, **kwargs)

    # GENERIC OBJECT PROXIES --------------------------------
    # The following methods and properties exist on the target(s).
    # We first try to reach the final target, trigerring alias resolution errors
    # and cyclic aliases errors early. We avoid recursing in the alias chain.

    @property
    def extra(self) -> dict:
        """Namespaced dictionaries storing extra metadata for this object, used by extensions."""
        return self.final_target.extra

    @property
    def lineno(self) -> int | None:
        """The starting line number of the target object."""
        return self.final_target.lineno

    @property
    def endlineno(self) -> int | None:
        """The ending line number of the target object."""
        return self.final_target.endlineno

    @property
    def docstring(self) -> Docstring | None:
        """The target docstring."""
        return self.final_target.docstring

    @docstring.setter
    def docstring(self, docstring: Docstring | None) -> None:
        self.final_target.docstring = docstring

    @property
    def labels(self) -> set[str]:
        """The target labels (`property`, `dataclass`, etc.)."""
        return self.final_target.labels

    @property
    def imports(self) -> dict[str, str]:
        """The other objects imported by this alias' target.

        Keys are the names within the object (`from ... import ... as AS_NAME`),
        while the values are the actual names of the objects (`from ... import REAL_NAME as ...`).
        """
        return self.final_target.imports

    @property
    def exports(self) -> set[str] | list[str | ExprName] | None:
        """The names of the objects exported by this (module) object through the `__all__` variable.

        Exports can contain string (object names) or resolvable names,
        like other lists of exports coming from submodules:

        ```python
        from .submodule import __all__ as submodule_all

        __all__ = ["hello", *submodule_all]
        ```

        Exports get expanded by the loader before it expands wildcards and resolves aliases.
        """
        return self.final_target.exports

    @property
    def aliases(self) -> dict[str, Alias]:
        """The aliases pointing to this object."""
        return self.final_target.aliases

    def member_is_exported(self, member: Object | Alias, *, explicitely: bool = True) -> bool:  # noqa: ARG002
        """Deprecated. Use [`member.is_exported`][griffe.dataclasses.Alias.is_exported] instead."""
        warnings.warn(
            "Method `member_is_exported` is deprecated. Use `member.is_exported` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return member.is_exported

    def is_kind(self, kind: str | Kind | set[str | Kind]) -> bool:
        """Tell if this object is of the given kind.

        Parameters:
            kind: An instance or set of kinds (strings or enumerations).

        Raises:
            ValueError: When an empty set is given as argument.

        Returns:
            True or False.
        """
        return self.final_target.is_kind(kind)

    @property
    def is_module(self) -> bool:
        """Whether this object is a module."""
        return self.final_target.is_module

    @property
    def is_class(self) -> bool:
        """Whether this object is a class."""
        return self.final_target.is_class

    @property
    def is_function(self) -> bool:
        """Whether this object is a function."""
        return self.final_target.is_function

    @property
    def is_attribute(self) -> bool:
        """Whether this object is an attribute."""
        return self.final_target.is_attribute

    def has_labels(self, *labels: str | set[str]) -> bool:
        """Tell if this object has all the given labels.

        Parameters:
            *labels: Labels that must be present.

        Returns:
            True or False.
        """
        return self.final_target.has_labels(*labels)

    def filter_members(self, *predicates: Callable[[Object | Alias], bool]) -> dict[str, Object | Alias]:
        """Filter and return members based on predicates.

        Parameters:
            *predicates: A list of predicates, i.e. callables accepting a member as argument and returning a boolean.

        Returns:
            A dictionary of members.
        """
        return self.final_target.filter_members(*predicates)

    @property
    def module(self) -> Module:
        """The parent module of this object.

        Raises:
            ValueError: When the object is not a module and does not have a parent.
        """
        return self.final_target.module

    @property
    def package(self) -> Module:
        """The absolute top module (the package) of this object."""
        return self.final_target.package

    @property
    def filepath(self) -> Path | list[Path]:
        """The file path (or directory list for namespace packages) where this object was defined."""
        return self.final_target.filepath

    @property
    def relative_filepath(self) -> Path:
        """The file path where this object was defined, relative to the current working directory.

        If this object's file path is not relative to the current working directory, return its absolute path.

        Raises:
            ValueError: When the relative path could not be computed.
        """
        return self.final_target.relative_filepath

    @property
    def relative_package_filepath(self) -> Path:
        """The file path where this object was defined, relative to the top module path.

        Raises:
            ValueError: When the relative path could not be computed.
        """
        return self.final_target.relative_package_filepath

    @property
    def canonical_path(self) -> str:
        """The full dotted path of this object.

        The canonical path is the path where the object was defined (not imported).
        """
        return self.final_target.canonical_path

    @property
    def lines_collection(self) -> LinesCollection:
        """The lines collection attached to this object or its parents.

        Raises:
            ValueError: When no modules collection can be found in the object or its parents.
        """
        return self.final_target.lines_collection

    @property
    def lines(self) -> list[str]:
        """The lines containing the source of this object."""
        return self.final_target.lines

    @property
    def source(self) -> str:
        """The source code of this object."""
        return self.final_target.source

    def resolve(self, name: str) -> str:
        """Resolve a name within this object's and parents' scope.

        Parameters:
            name: The name to resolve.

        Raises:
            NameResolutionError: When the name could not be resolved.

        Returns:
            The resolved name.
        """
        return self.final_target.resolve(name)

    def get_member(self, key: str | Sequence[str]) -> Object | Alias:  # noqa: D102
        return self.final_target.get_member(key)

    def set_member(self, key: str | Sequence[str], value: Object | Alias) -> None:  # noqa: D102
        return self.final_target.set_member(key, value)

    def del_member(self, key: str | Sequence[str]) -> None:  # noqa: D102
        return self.final_target.del_member(key)

    # SPECIFIC MODULE/CLASS/FUNCTION/ATTRIBUTE PROXIES ---------------
    # These methods and properties exist on targets of specific kind.
    # We first try to reach the final target, trigerring alias resolution errors
    # and cyclic aliases errors early. We avoid recursing in the alias chain.

    @property
    def _filepath(self) -> Path | list[Path] | None:
        return cast(Module, self.final_target)._filepath

    @property
    def bases(self) -> list[Expr | str]:
        """The class bases."""
        return cast(Class, self.final_target).bases

    @property
    def decorators(self) -> list[Decorator]:
        """The class/function decorators."""
        return cast(Union[Class, Function], self.target).decorators

    @property
    def imports_future_annotations(self) -> bool:
        """Whether this module import future annotations."""
        return cast(Module, self.final_target).imports_future_annotations

    @property
    def is_init_module(self) -> bool:
        """Whether this module is an `__init__.py` module."""
        return cast(Module, self.final_target).is_init_module

    @property
    def is_package(self) -> bool:
        """Whether this module is a package (top module)."""
        return cast(Module, self.final_target).is_package

    @property
    def is_subpackage(self) -> bool:
        """Whether this module is a subpackage."""
        return cast(Module, self.final_target).is_subpackage

    @property
    def is_namespace_package(self) -> bool:
        """Whether this module is a namespace package (top folder, no `__init__.py`)."""
        return cast(Module, self.final_target).is_namespace_package

    @property
    def is_namespace_subpackage(self) -> bool:
        """Whether this module is a namespace subpackage."""
        return cast(Module, self.final_target).is_namespace_subpackage

    @property
    def overloads(self) -> dict[str, list[Function]] | list[Function] | None:
        """The overloaded signatures declared in this class/module or for this function."""
        return cast(Union[Module, Class, Function], self.final_target).overloads

    @overloads.setter
    def overloads(self, overloads: list[Function] | None) -> None:
        cast(Union[Module, Class, Function], self.final_target).overloads = overloads

    @property
    def parameters(self) -> Parameters:
        """The parameters of the current function or `__init__` method for classes.

        This property can fetch inherited members,
        and therefore is part of the consumer API:
        do not use when producing Griffe trees!
        """
        return cast(Union[Class, Function], self.final_target).parameters

    @property
    def returns(self) -> str | Expr | None:
        """The function return type annotation."""
        return cast(Function, self.final_target).returns

    @returns.setter
    def returns(self, returns: str | Expr | None) -> None:
        cast(Function, self.final_target).returns = returns

    @property
    def setter(self) -> Function | None:
        """The setter linked to this function (property)."""
        return cast(Function, self.final_target).setter

    @property
    def deleter(self) -> Function | None:
        """The deleter linked to this function (property)."""
        return cast(Function, self.final_target).deleter

    @property
    def value(self) -> str | Expr | None:
        """The attribute value."""
        return cast(Attribute, self.final_target).value

    @property
    def annotation(self) -> str | Expr | None:
        """The attribute type annotation."""
        return cast(Attribute, self.final_target).annotation

    @annotation.setter
    def annotation(self, annotation: str | Expr | None) -> None:
        cast(Attribute, self.final_target).annotation = annotation

    @property
    def resolved_bases(self) -> list[Object]:
        """Resolved class bases.

        This method is part of the consumer API:
        do not use when producing Griffe trees!
        """
        return cast(Class, self.final_target).resolved_bases

    def mro(self) -> list[Class]:
        """Return a list of classes in order corresponding to Python's MRO."""
        return cast(Class, self.final_target).mro()

    # SPECIFIC ALIAS METHOD AND PROPERTIES -----------------
    # These methods and properties do not exist on targets,
    # they are specific to aliases.

    @property
    def target(self) -> Object | Alias:
        """The resolved target (actual object), if possible.

        Upon accessing this property, if the target is not already resolved,
        a lookup is done using the modules collection to find the target.
        """
        if not self.resolved:
            self.resolve_target()
        return self._target  # type: ignore[return-value]  # cannot return None, exception is raised

    @target.setter
    def target(self, value: Object | Alias) -> None:
        if value is self or value.path == self.path:
            raise CyclicAliasError([self.target_path])
        self._target = value
        self.target_path = value.path
        if self.parent is not None:
            self._target.aliases[self.path] = self

    @property
    def final_target(self) -> Object:
        """The final, resolved target, if possible.

        This will iterate through the targets until a non-alias object is found.
        """
        # Here we quickly iterate on the alias chain,
        # remembering which path we've seen already to detect cycles.

        # The cycle detection is needed because alias chains can be created
        # as already resolved, and can contain cycles.

        # using a dict as an ordered set
        paths_seen: dict[str, None] = {}
        target = self
        while target.is_alias:
            if target.path in paths_seen:
                raise CyclicAliasError([*paths_seen, target.path])
            paths_seen[target.path] = None
            target = target.target  # type: ignore[assignment]
        return target  # type: ignore[return-value]

    def resolve_target(self) -> None:
        """Resolve the target.

        Raises:
            AliasResolutionError: When the target cannot be resolved.
                It happens when the target does not exist,
                or could not be loaded (unhandled dynamic object?),
                or when the target is from a module that was not loaded
                and added to the collection.
            CyclicAliasError: When the resolved target is the alias itself.
        """
        # Here we try to resolve the whole alias chain recursively.
        # We detect cycles by setting a "passed through" state variable
        # on each alias as we pass through it. Passing a second time
        # through an alias will raise a CyclicAliasError.

        # If a single link of the chain cannot be resolved,
        # the whole chain stays unresolved. This prevents
        # bad surprises later, in code that checks if
        # an alias is resolved by checking only
        # the first link of the chain.
        if self._passed_through:
            raise CyclicAliasError([self.target_path])
        self._passed_through = True
        try:
            self._resolve_target()
        finally:
            self._passed_through = False

    def _resolve_target(self) -> None:
        try:
            resolved = self.modules_collection.get_member(self.target_path)
        except KeyError as error:
            raise AliasResolutionError(self) from error
        if resolved is self:
            raise CyclicAliasError([self.target_path])
        if resolved.is_alias and not resolved.resolved:
            try:
                resolved.resolve_target()
            except CyclicAliasError as error:
                raise CyclicAliasError([self.target_path, *error.chain]) from error
        self._target = resolved
        if self.parent is not None:
            self._target.aliases[self.path] = self  # type: ignore[union-attr]  # we just set the target

    def _update_target_aliases(self) -> None:
        with suppress(AttributeError, AliasResolutionError, CyclicAliasError):
            self._target.aliases[self.path] = self  # type: ignore[union-attr]

    @property
    def resolved(self) -> bool:
        """Whether this alias' target is resolved."""
        return self._target is not None

    @property
    def wildcard(self) -> str | None:
        """The module on which the wildcard import is performed (if any)."""
        if self.name.endswith("/*"):
            return self.target_path
        return None

    def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
        """Return this alias' data as a dictionary.

        Parameters:
            full: Whether to return full info, or just base info.
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base = {
            "kind": Kind.ALIAS,
            "name": self.name,
            "target_path": self.target_path,
        }

        if full:
            base["path"] = self.path

        if self.alias_lineno:
            base["lineno"] = self.alias_lineno
        if self.alias_endlineno:
            base["endlineno"] = self.alias_endlineno

        return base


class Module(Object):
    """The class representing a Python module."""

    kind = Kind.MODULE

    def __init__(self, *args: Any, filepath: Path | list[Path] | None = None, **kwargs: Any) -> None:
        """Initialize the module.

        Parameters:
            *args: See [`griffe.dataclasses.Object`][].
            filepath: The module file path (directory for namespace [sub]packages, none for builtin modules).
            **kwargs: See [`griffe.dataclasses.Object`][].
        """
        super().__init__(*args, **kwargs)
        self._filepath: Path | list[Path] | None = filepath
        self.overloads: dict[str, list[Function]] = defaultdict(list)
        """The overloaded signature declared in this module."""

    def __repr__(self) -> str:
        try:
            return f"Module({self.filepath!r})"
        except BuiltinModuleError:
            return f"Module({self.name!r})"

    @property
    def filepath(self) -> Path | list[Path]:
        """The file path of this module.

        Raises:
            BuiltinModuleError: When the instance filepath is None.
        """
        if self._filepath is None:
            raise BuiltinModuleError(self.name)
        return self._filepath

    @property
    def imports_future_annotations(self) -> bool:
        """Whether this module import future annotations."""
        return (
            "annotations" in self.members
            and self.members["annotations"].is_alias
            and self.members["annotations"].target_path == "__future__.annotations"  # type: ignore[union-attr]
        )

    @property
    def is_init_module(self) -> bool:
        """Whether this module is an `__init__.py` module."""
        if isinstance(self.filepath, list):
            return False
        try:
            return self.filepath.name.split(".", 1)[0] == "__init__"
        except BuiltinModuleError:
            return False

    @property
    def is_package(self) -> bool:
        """Whether this module is a package (top module)."""
        return not bool(self.parent) and self.is_init_module

    @property
    def is_subpackage(self) -> bool:
        """Whether this module is a subpackage."""
        return bool(self.parent) and self.is_init_module

    @property
    def is_namespace_package(self) -> bool:
        """Whether this module is a namespace package (top folder, no `__init__.py`)."""
        try:
            return self.parent is None and isinstance(self.filepath, list)
        except BuiltinModuleError:
            return False

    @property
    def is_namespace_subpackage(self) -> bool:
        """Whether this module is a namespace subpackage."""
        try:
            return (
                self.parent is not None
                and isinstance(self.filepath, list)
                and (
                    cast(Module, self.parent).is_namespace_package or cast(Module, self.parent).is_namespace_subpackage
                )
            )
        except BuiltinModuleError:
            return False

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return this module's data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base = super().as_dict(**kwargs)
        if isinstance(self._filepath, list):
            base["filepath"] = [str(path) for path in self._filepath]
        elif self._filepath:
            base["filepath"] = str(self._filepath)
        else:
            base["filepath"] = None
        return base


class Class(Object):
    """The class representing a Python class."""

    kind = Kind.CLASS

    def __init__(
        self,
        *args: Any,
        bases: Sequence[Expr | str] | None = None,
        decorators: list[Decorator] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the class.

        Parameters:
            *args: See [`griffe.dataclasses.Object`][].
            bases: The list of base classes, if any.
            decorators: The class decorators, if any.
            **kwargs: See [`griffe.dataclasses.Object`][].
        """
        super().__init__(*args, **kwargs)
        self.bases: list[Expr | str] = list(bases) if bases else []
        """The class bases."""
        self.decorators: list[Decorator] = decorators or []
        """The class decorators."""
        self.overloads: dict[str, list[Function]] = defaultdict(list)
        """The overloaded signatures declared in this class."""

    @property
    def parameters(self) -> Parameters:
        """The parameters of this class' `__init__` method, if any.

        This property fetches inherited members,
        and therefore is part of the consumer API:
        do not use when producing Griffe trees!
        """
        try:
            return self.all_members["__init__"].parameters  # type: ignore[union-attr]
        except KeyError:
            return Parameters()

    @cached_property
    def resolved_bases(self) -> list[Object]:
        """Resolved class bases.

        This method is part of the consumer API:
        do not use when producing Griffe trees!
        """
        resolved_bases = []
        for base in self.bases:
            base_path = base if isinstance(base, str) else base.canonical_path
            try:
                resolved_base = self.modules_collection[base_path]
                if resolved_base.is_alias:
                    resolved_base = resolved_base.final_target
            except (AliasResolutionError, CyclicAliasError, KeyError):
                logger.debug(f"Base class {base_path} is not loaded, or not static, it cannot be resolved")
            else:
                resolved_bases.append(resolved_base)
        return resolved_bases

    def _mro(self, seen: tuple[str, ...] = ()) -> list[Class]:
        seen = (*seen, self.path)
        bases: list[Class] = [base for base in self.resolved_bases if base.is_class]  # type: ignore[misc]
        if not bases:
            return [self]
        for base in bases:
            if base.path in seen:
                cycle = " -> ".join(seen) + f" -> {base.path}"
                raise ValueError(f"Cannot compute C3 linearization, inheritance cycle detected: {cycle}")
        return [self, *c3linear_merge(*[base._mro(seen) for base in bases], bases)]

    def mro(self) -> list[Class]:
        """Return a list of classes in order corresponding to Python's MRO."""
        return self._mro()[1:]  # remove self

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return this class' data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base = super().as_dict(**kwargs)
        base["bases"] = self.bases
        base["decorators"] = [dec.as_dict(**kwargs) for dec in self.decorators]
        return base


class Function(Object):
    """The class representing a Python function."""

    kind = Kind.FUNCTION

    def __init__(
        self,
        *args: Any,
        parameters: Parameters | None = None,
        returns: str | Expr | None = None,
        decorators: list[Decorator] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the function.

        Parameters:
            *args: See [`griffe.dataclasses.Object`][].
            parameters: The function parameters.
            returns: The function return annotation.
            decorators: The function decorators, if any.
            **kwargs: See [`griffe.dataclasses.Object`][].
        """
        super().__init__(*args, **kwargs)
        self.parameters: Parameters = parameters or Parameters()
        """The function parameters."""
        self.returns: str | Expr | None = returns
        """The function return type annotation."""
        self.decorators: list[Decorator] = decorators or []
        """The function decorators."""
        self.setter: Function | None = None
        """The setter linked to this function (property)."""
        self.deleter: Function | None = None
        """The deleter linked to this function (property)."""
        self.overloads: list[Function] | None = None
        """The overloaded signatures of this function."""

        for parameter in self.parameters:
            parameter.function = self

    @property
    def annotation(self) -> str | Expr | None:
        """The type annotation of the returned value."""
        return self.returns

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return this function's data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base = super().as_dict(**kwargs)
        base["decorators"] = [dec.as_dict(**kwargs) for dec in self.decorators]
        base["parameters"] = [param.as_dict(**kwargs) for param in self.parameters]
        base["returns"] = self.returns
        return base


class Attribute(Object):
    """The class representing a Python module/class/instance attribute."""

    kind = Kind.ATTRIBUTE

    def __init__(
        self,
        *args: Any,
        value: str | Expr | None = None,
        annotation: str | Expr | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the function.

        Parameters:
            *args: See [`griffe.dataclasses.Object`][].
            value: The attribute value, if any.
            annotation: The attribute annotation, if any.
            **kwargs: See [`griffe.dataclasses.Object`][].
        """
        super().__init__(*args, **kwargs)
        self.value: str | Expr | None = value
        """The attribute value."""
        self.annotation: str | Expr | None = annotation
        """The attribute type annotation."""

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return this function's data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base = super().as_dict(**kwargs)
        if self.value is not None:
            base["value"] = self.value
        if self.annotation is not None:
            base["annotation"] = self.annotation
        return base


__all__ = [
    "Alias",
    "Attribute",
    "Class",
    "Decorator",
    "Docstring",
    "Function",
    "Kind",
    "Module",
    "Object",
    "Parameter",
    "ParameterKind",
    "ParameterKind",
    "Parameters",
]
