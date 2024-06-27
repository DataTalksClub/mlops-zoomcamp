"""Code parsing and data extraction utilies.

This module exposes a public function, [`visit()`][griffe.agents.visitor.visit],
which parses the module code using [`parse()`][ast.parse],
and returns a new [`Module`][griffe.dataclasses.Module] instance,
populating its members recursively, by using a [`NodeVisitor`][ast.NodeVisitor]-like class.
"""

from __future__ import annotations

import ast
from contextlib import suppress
from typing import TYPE_CHECKING, Any

from griffe.agents.nodes import (
    ast_children,
    ast_kind,
    ast_next,
    get_docstring,
    get_instance_names,
    get_names,
    get_parameters,
    relative_to_absolute,
    safe_get__all__,
)
from griffe.collections import LinesCollection, ModulesCollection
from griffe.dataclasses import Alias, Attribute, Class, Decorator, Docstring, Function, Module, Parameter, Parameters
from griffe.enumerations import Kind
from griffe.exceptions import AliasResolutionError, CyclicAliasError, LastNodeError
from griffe.expressions import (
    Expr,
    ExprName,
    safe_get_annotation,
    safe_get_base_class,
    safe_get_condition,
    safe_get_expression,
)
from griffe.extensions.base import Extensions, load_extensions

if TYPE_CHECKING:
    from pathlib import Path

    from griffe.enumerations import Parser


builtin_decorators = {
    "property": "property",
    "staticmethod": "staticmethod",
    "classmethod": "classmethod",
}

stdlib_decorators = {
    "abc.abstractmethod": {"abstractmethod"},
    "functools.cache": {"cached"},
    "functools.cached_property": {"cached", "property"},
    "cached_property.cached_property": {"cached", "property"},
    "functools.lru_cache": {"cached"},
    "dataclasses.dataclass": {"dataclass"},
}
typing_overload = {"typing.overload", "typing_extensions.overload"}


def visit(
    module_name: str,
    filepath: Path,
    code: str,
    *,
    extensions: Extensions | None = None,
    parent: Module | None = None,
    docstring_parser: Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
) -> Module:
    """Parse and visit a module file.

    Parameters:
        module_name: The module name (as when importing [from] it).
        filepath: The module file path.
        code: The module contents.
        extensions: The extensions to use when visiting the AST.
        parent: The optional parent of this module.
        docstring_parser: The docstring parser to use. By default, no parsing is done.
        docstring_options: Additional docstring parsing options.
        lines_collection: A collection of source code lines.
        modules_collection: A collection of modules.

    Returns:
        The module, with its members populated.
    """
    return Visitor(
        module_name,
        filepath,
        code,
        extensions or load_extensions(),
        parent,
        docstring_parser=docstring_parser,
        docstring_options=docstring_options,
        lines_collection=lines_collection,
        modules_collection=modules_collection,
    ).get_module()


class Visitor:
    """This class is used to instantiate a visitor.

    Visitors iterate on AST nodes to extract data from them.
    """

    def __init__(
        self,
        module_name: str,
        filepath: Path,
        code: str,
        extensions: Extensions,
        parent: Module | None = None,
        docstring_parser: Parser | None = None,
        docstring_options: dict[str, Any] | None = None,
        lines_collection: LinesCollection | None = None,
        modules_collection: ModulesCollection | None = None,
    ) -> None:
        """Initialize the visitor.

        Parameters:
            module_name: The module name.
            filepath: The module filepath.
            code: The module source code.
            extensions: The extensions to use when visiting.
            parent: An optional parent for the final module object.
            docstring_parser: The docstring parser to use.
            docstring_options: The docstring parsing options.
            lines_collection: A collection of source code lines.
            modules_collection: A collection of modules.
        """
        super().__init__()
        self.module_name: str = module_name
        self.filepath: Path = filepath
        self.code: str = code
        self.extensions: Extensions = extensions.attach_visitor(self)
        self.parent: Module | None = parent
        self.current: Module | Class = None  # type: ignore[assignment]
        self.docstring_parser: Parser | None = docstring_parser
        self.docstring_options: dict[str, Any] = docstring_options or {}
        self.lines_collection: LinesCollection = lines_collection or LinesCollection()
        self.modules_collection: ModulesCollection = modules_collection or ModulesCollection()
        self.type_guarded: bool = False

    def _get_docstring(self, node: ast.AST, *, strict: bool = False) -> Docstring | None:
        value, lineno, endlineno = get_docstring(node, strict=strict)
        if value is None:
            return None
        return Docstring(
            value,
            lineno=lineno,
            endlineno=endlineno,
            parser=self.docstring_parser,
            parser_options=self.docstring_options,
        )

    def get_module(self) -> Module:
        """Build and return the object representing the module attached to this visitor.

        This method triggers a complete visit of the module nodes.

        Returns:
            A module instance.
        """
        # optimization: equivalent to ast.parse, but with optimize=1 to remove assert statements
        # TODO: with options, could use optimize=2 to remove docstrings
        top_node = compile(self.code, mode="exec", filename=str(self.filepath), flags=ast.PyCF_ONLY_AST, optimize=1)
        self.visit(top_node)
        return self.current.module

    def visit(self, node: ast.AST) -> None:
        """Extend the base visit with extensions.

        Parameters:
            node: The node to visit.
        """
        for before_visitor in self.extensions.before_visit:
            before_visitor.visit(node)
        getattr(self, f"visit_{ast_kind(node)}", self.generic_visit)(node)
        for after_visitor in self.extensions.after_visit:
            after_visitor.visit(node)

    def generic_visit(self, node: ast.AST) -> None:
        """Extend the base generic visit with extensions.

        Parameters:
            node: The node to visit.
        """
        for before_visitor in self.extensions.before_children_visit:
            before_visitor.visit(node)
        for child in ast_children(node):
            self.visit(child)
        for after_visitor in self.extensions.after_children_visit:
            after_visitor.visit(node)

    def visit_module(self, node: ast.Module) -> None:
        """Visit a module node.

        Parameters:
            node: The node to visit.
        """
        self.extensions.call("on_node", node=node)
        self.extensions.call("on_module_node", node=node)
        self.current = module = Module(
            name=self.module_name,
            filepath=self.filepath,
            parent=self.parent,
            docstring=self._get_docstring(node),
            lines_collection=self.lines_collection,
            modules_collection=self.modules_collection,
        )
        self.extensions.call("on_instance", node=node, obj=module)
        self.extensions.call("on_module_instance", node=node, mod=module)
        self.generic_visit(node)
        self.extensions.call("on_members", node=node, obj=module)
        self.extensions.call("on_module_members", node=node, mod=module)

    def visit_classdef(self, node: ast.ClassDef) -> None:
        """Visit a class definition node.

        Parameters:
            node: The node to visit.
        """
        self.extensions.call("on_node", node=node)
        self.extensions.call("on_class_node", node=node)

        # handle decorators
        decorators = []
        if node.decorator_list:
            lineno = node.decorator_list[0].lineno
            for decorator_node in node.decorator_list:
                decorators.append(
                    Decorator(
                        safe_get_expression(decorator_node, parent=self.current, parse_strings=False),  # type: ignore[arg-type]
                        lineno=decorator_node.lineno,
                        endlineno=decorator_node.end_lineno,
                    ),
                )
        else:
            lineno = node.lineno

        # handle base classes
        bases = []
        if node.bases:
            for base in node.bases:
                bases.append(safe_get_base_class(base, parent=self.current))

        class_ = Class(
            name=node.name,
            lineno=lineno,
            endlineno=node.end_lineno,
            docstring=self._get_docstring(node),
            decorators=decorators,
            bases=bases,  # type: ignore[arg-type]
            runtime=not self.type_guarded,
        )
        class_.labels |= self.decorators_to_labels(decorators)
        self.current.set_member(node.name, class_)
        self.current = class_
        self.extensions.call("on_instance", node=node, obj=class_)
        self.extensions.call("on_class_instance", node=node, cls=class_)
        self.generic_visit(node)
        self.extensions.call("on_members", node=node, obj=class_)
        self.extensions.call("on_class_members", node=node, cls=class_)
        self.current = self.current.parent  # type: ignore[assignment]

    def decorators_to_labels(self, decorators: list[Decorator]) -> set[str]:
        """Build and return a set of labels based on decorators.

        Parameters:
            decorators: The decorators to check.

        Returns:
            A set of labels.
        """
        labels = set()
        for decorator in decorators:
            callable_path = decorator.callable_path
            if callable_path in builtin_decorators:
                labels.add(builtin_decorators[callable_path])
            elif callable_path in stdlib_decorators:
                labels |= stdlib_decorators[callable_path]
        return labels

    def get_base_property(self, decorators: list[Decorator], function: Function) -> str | None:
        """Check decorators to return the base property in case of setters and deleters.

        Parameters:
            decorators: The decorators to check.

        Returns:
            base_property: The property for which the setter/deleted is set.
            property_function: Either `"setter"` or `"deleter"`.
        """
        for decorator in decorators:
            try:
                path, prop_function = decorator.callable_path.rsplit(".", 1)
            except ValueError:
                continue
            property_setter_or_deleter = (
                prop_function in {"setter", "deleter"}
                and path == function.path
                and self.current.get_member(function.name).has_labels("property")
            )
            if property_setter_or_deleter:
                return prop_function
        return None

    def handle_function(self, node: ast.AsyncFunctionDef | ast.FunctionDef, labels: set | None = None) -> None:
        """Handle a function definition node.

        Parameters:
            node: The node to visit.
            labels: Labels to add to the data object.
        """
        self.extensions.call("on_node", node=node)
        self.extensions.call("on_function_node", node=node)

        labels = labels or set()

        # handle decorators
        decorators = []
        overload = False
        if node.decorator_list:
            lineno = node.decorator_list[0].lineno
            for decorator_node in node.decorator_list:
                decorator_value = safe_get_expression(decorator_node, parent=self.current, parse_strings=False)
                if decorator_value is None:
                    continue
                decorator = Decorator(
                    decorator_value,
                    lineno=decorator_node.lineno,
                    endlineno=decorator_node.end_lineno,
                )
                decorators.append(decorator)
                overload |= decorator.callable_path in typing_overload
        else:
            lineno = node.lineno

        labels |= self.decorators_to_labels(decorators)

        if "property" in labels:
            attribute = Attribute(
                name=node.name,
                value=None,
                annotation=safe_get_annotation(node.returns, parent=self.current),
                lineno=node.lineno,
                endlineno=node.end_lineno,
                docstring=self._get_docstring(node),
                runtime=not self.type_guarded,
            )
            attribute.labels |= labels
            self.current.set_member(node.name, attribute)
            self.extensions.call("on_instance", node=node, obj=attribute)
            self.extensions.call("on_attribute_instance", node=node, attr=attribute)
            return

        # handle parameters
        parameters = Parameters(
            *[
                Parameter(
                    name,
                    kind=kind,
                    annotation=safe_get_annotation(annotation, parent=self.current),
                    default=default
                    if isinstance(default, str)
                    else safe_get_expression(default, parent=self.current, parse_strings=False),
                )
                for name, annotation, kind, default in get_parameters(node.args)
            ],
        )

        function = Function(
            name=node.name,
            lineno=lineno,
            endlineno=node.end_lineno,
            parameters=parameters,
            returns=safe_get_annotation(node.returns, parent=self.current),
            decorators=decorators,
            docstring=self._get_docstring(node),
            runtime=not self.type_guarded,
            parent=self.current,
        )

        property_function = self.get_base_property(decorators, function)

        if overload:
            self.current.overloads[function.name].append(function)
        elif property_function:
            base_property: Function = self.current.members[node.name]  # type: ignore[assignment]
            if property_function == "setter":
                base_property.setter = function
                base_property.labels.add("writable")
            elif property_function == "deleter":
                base_property.deleter = function
                base_property.labels.add("deletable")
        else:
            self.current.set_member(node.name, function)
            if self.current.kind in {Kind.MODULE, Kind.CLASS} and self.current.overloads[function.name]:
                function.overloads = self.current.overloads[function.name]
                del self.current.overloads[function.name]

        function.labels |= labels

        self.extensions.call("on_instance", node=node, obj=function)
        self.extensions.call("on_function_instance", node=node, func=function)
        if self.current.kind is Kind.CLASS and function.name == "__init__":
            self.current = function  # type: ignore[assignment]  # temporary assign a function
            self.generic_visit(node)
            self.current = self.current.parent  # type: ignore[assignment]

    def visit_functiondef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition node.

        Parameters:
            node: The node to visit.
        """
        self.handle_function(node)

    def visit_asyncfunctiondef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit an async function definition node.

        Parameters:
            node: The node to visit.
        """
        self.handle_function(node, labels={"async"})

    def visit_import(self, node: ast.Import) -> None:
        """Visit an import node.

        Parameters:
            node: The node to visit.
        """
        for name in node.names:
            alias_path = name.name if name.asname else name.name.split(".", 1)[0]
            alias_name = name.asname or alias_path.split(".", 1)[0]
            self.current.imports[alias_name] = alias_path
            self.current.set_member(
                alias_name,
                Alias(
                    alias_name,
                    alias_path,
                    lineno=node.lineno,
                    endlineno=node.end_lineno,
                    runtime=not self.type_guarded,
                ),
            )

    def visit_importfrom(self, node: ast.ImportFrom) -> None:
        """Visit an "import from" node.

        Parameters:
            node: The node to visit.
        """
        for name in node.names:
            if not node.module and node.level == 1 and not name.asname and self.current.module.is_init_module:
                # special case: when being in `a/__init__.py` and doing `from . import b`,
                # we are effectively creating a member `b` in `a` that is pointing to `a.b`
                # -> cyclic alias! in that case, we just skip it, as both the member and module
                # have the same name and can be accessed the same way
                continue

            alias_path = relative_to_absolute(node, name, self.current.module)
            if name.name == "*":
                alias_name = alias_path.replace(".", "/")
                alias_path = alias_path.replace(".*", "")
            else:
                alias_name = name.asname or name.name
                self.current.imports[alias_name] = alias_path
            # Do not create aliases pointing to themselves (it happens with
            # `from package.current_module import Thing as Thing` or
            # `from . import thing as thing`).
            if alias_path != f"{self.current.path}.{alias_name}":
                self.current.set_member(
                    alias_name,
                    Alias(
                        alias_name,
                        alias_path,
                        lineno=node.lineno,
                        endlineno=node.end_lineno,
                        runtime=not self.type_guarded,
                    ),
                )

    def handle_attribute(
        self,
        node: ast.Assign | ast.AnnAssign,
        annotation: str | Expr | None = None,
    ) -> None:
        """Handle an attribute (assignment) node.

        Parameters:
            node: The node to visit.
            annotation: A potential annotation.
        """
        self.extensions.call("on_node", node=node)
        self.extensions.call("on_attribute_node", node=node)
        parent = self.current
        labels = set()

        if parent.kind is Kind.MODULE:
            try:
                names = get_names(node)
            except KeyError:  # unsupported nodes, like subscript
                return
            labels.add("module-attribute")
        elif parent.kind is Kind.CLASS:
            try:
                names = get_names(node)
            except KeyError:  # unsupported nodes, like subscript
                return

            if isinstance(annotation, Expr) and annotation.is_classvar:
                # explicit classvar: class attribute only
                annotation = annotation.slice  # type: ignore[attr-defined]
                labels.add("class-attribute")
            elif node.value:
                # attribute assigned at class-level: available in instances as well
                labels.add("class-attribute")
                labels.add("instance-attribute")
            else:
                # annotated attribute only: not available at class-level
                labels.add("instance-attribute")

        elif parent.kind is Kind.FUNCTION:
            if parent.name != "__init__":
                return
            try:
                names = get_instance_names(node)
            except KeyError:  # unsupported nodes, like subscript
                return
            parent = parent.parent  # type: ignore[assignment]
            labels.add("instance-attribute")

        if not names:
            return

        value = safe_get_expression(node.value, parent=self.current, parse_strings=False)

        try:
            docstring = self._get_docstring(ast_next(node), strict=True)
        except (LastNodeError, AttributeError):
            docstring = None

        for name in names:
            # TODO: handle assigns like x.y = z
            # we need to resolve x.y and add z in its member
            if "." in name:
                continue

            if name in parent.members:
                # assigning multiple times
                # TODO: might be better to inspect
                if isinstance(node.parent, (ast.If, ast.ExceptHandler)):  # type: ignore[union-attr]
                    continue  # prefer "no-exception" case

                existing_member = parent.members[name]
                with suppress(AliasResolutionError, CyclicAliasError):
                    labels |= existing_member.labels
                    # forward previous docstring and annotation instead of erasing them
                    if existing_member.docstring and not docstring:
                        docstring = existing_member.docstring
                    with suppress(AttributeError):
                        if existing_member.annotation and not annotation:  # type: ignore[union-attr]
                            annotation = existing_member.annotation  # type: ignore[union-attr]

            attribute = Attribute(
                name=name,
                value=value,
                annotation=annotation,
                lineno=node.lineno,
                endlineno=node.end_lineno,
                docstring=docstring,
                runtime=not self.type_guarded,
            )
            attribute.labels |= labels
            parent.set_member(name, attribute)

            if name == "__all__":
                with suppress(AttributeError):
                    parent.exports = [
                        name if isinstance(name, str) else ExprName(name.name, parent=name.parent)
                        for name in safe_get__all__(node, self.current)  # type: ignore[arg-type]
                    ]
            self.extensions.call("on_instance", node=node, obj=attribute)
            self.extensions.call("on_attribute_instance", node=node, attr=attribute)

    def visit_assign(self, node: ast.Assign) -> None:
        """Visit an assignment node.

        Parameters:
            node: The node to visit.
        """
        self.handle_attribute(node)

    def visit_annassign(self, node: ast.AnnAssign) -> None:
        """Visit an annotated assignment node.

        Parameters:
            node: The node to visit.
        """
        self.handle_attribute(node, safe_get_annotation(node.annotation, parent=self.current))

    def visit_augassign(self, node: ast.AugAssign) -> None:
        """Visit an augmented assignment node.

        Parameters:
            node: The node to visit.
        """
        with suppress(AttributeError):
            all_augment = (
                node.target.id == "__all__"  # type: ignore[union-attr]
                and self.current.is_module
                and isinstance(node.op, ast.Add)
            )
            if all_augment:
                # we assume exports is not None at this point
                self.current.exports.extend(  # type: ignore[union-attr]
                    [
                        name if isinstance(name, str) else ExprName(name.name, parent=name.parent)
                        for name in safe_get__all__(node, self.current)  # type: ignore[arg-type]
                    ],
                )

    def visit_if(self, node: ast.If) -> None:
        """Visit an "if" node.

        Parameters:
            node: The node to visit.
        """
        if isinstance(node.parent, (ast.Module, ast.ClassDef)):  # type: ignore[attr-defined]
            condition = safe_get_condition(node.test, parent=self.current, log_level=None)
            if str(condition) in {"typing.TYPE_CHECKING", "TYPE_CHECKING"}:
                self.type_guarded = True
        self.generic_visit(node)
        self.type_guarded = False


__all__ = ["visit", "Visitor"]
