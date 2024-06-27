"""This module defines introspection mechanisms.

Sometimes we cannot get the source code of a module or an object,
typically built-in modules like `itertools`. The only way to know
what they are made of is to actually import them and inspect their contents.

Sometimes, even if the source code is available, loading the object is desired
because it was created or modified dynamically, and our node visitor is not
powerful enough to infer all these dynamic modifications. In this case,
we always try to visit the code first, and only then we load the object
to update the data with introspection.

This module exposes a public function, [`inspect()`][griffe.agents.inspector.inspect],
which inspects the module using [`inspect.getmembers()`][inspect.getmembers],
and returns a new [`Module`][griffe.dataclasses.Module] instance,
populating its members recursively, by using a [`NodeVisitor`][ast.NodeVisitor]-like class.

The inspection agent works similarly to the regular "node visitor" agent,
in that it maintains a state with the current object being handled,
and recursively handle its members.
"""

from __future__ import annotations

import ast
from inspect import Parameter as SignatureParameter
from inspect import Signature, cleandoc, getsourcelines
from inspect import signature as getsignature
from typing import TYPE_CHECKING, Any, Sequence

from griffe.agents.nodes import ObjectNode
from griffe.collections import LinesCollection, ModulesCollection
from griffe.dataclasses import Alias, Attribute, Class, Docstring, Function, Module, Parameter, Parameters
from griffe.enumerations import ObjectKind, ParameterKind
from griffe.expressions import safe_get_annotation
from griffe.extensions.base import Extensions, load_extensions
from griffe.importer import dynamic_import
from griffe.logger import get_logger

if TYPE_CHECKING:
    from pathlib import Path

    from griffe.enumerations import Parser
    from griffe.expressions import Expr


logger = get_logger(__name__)
empty = Signature.empty


def inspect(
    module_name: str,
    *,
    filepath: Path | None = None,
    import_paths: Sequence[str | Path] | None = None,
    extensions: Extensions | None = None,
    parent: Module | None = None,
    docstring_parser: Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
) -> Module:
    """Inspect a module.

    Parameters:
        module_name: The module name (as when importing [from] it).
        filepath: The module file path.
        import_paths: Paths to import the module from.
        extensions: The extensions to use when inspecting the module.
        parent: The optional parent of this module.
        docstring_parser: The docstring parser to use. By default, no parsing is done.
        docstring_options: Additional docstring parsing options.
        lines_collection: A collection of source code lines.
        modules_collection: A collection of modules.

    Returns:
        The module, with its members populated.
    """
    return Inspector(
        module_name,
        filepath,
        extensions or load_extensions(),
        parent,
        docstring_parser=docstring_parser,
        docstring_options=docstring_options,
        lines_collection=lines_collection,
        modules_collection=modules_collection,
    ).get_module(import_paths)


class Inspector:
    """This class is used to instantiate an inspector.

    Inspectors iterate on objects members to extract data from them.
    """

    def __init__(
        self,
        module_name: str,
        filepath: Path | None,
        extensions: Extensions,
        parent: Module | None = None,
        docstring_parser: Parser | None = None,
        docstring_options: dict[str, Any] | None = None,
        lines_collection: LinesCollection | None = None,
        modules_collection: ModulesCollection | None = None,
    ) -> None:
        """Initialize the inspector.

        Parameters:
            module_name: The module name.
            filepath: The optional filepath.
            extensions: Extensions to use when inspecting.
            parent: The module parent.
            docstring_parser: The docstring parser to use.
            docstring_options: The docstring parsing options.
            lines_collection: A collection of source code lines.
            modules_collection: A collection of modules.
        """
        super().__init__()
        self.module_name: str = module_name
        self.filepath: Path | None = filepath
        self.extensions: Extensions = extensions.attach_inspector(self)
        self.parent: Module | None = parent
        self.current: Module | Class = None  # type: ignore[assignment]
        self.docstring_parser: Parser | None = docstring_parser
        self.docstring_options: dict[str, Any] = docstring_options or {}
        self.lines_collection: LinesCollection = lines_collection or LinesCollection()
        self.modules_collection: ModulesCollection = modules_collection or ModulesCollection()

    def _get_docstring(self, node: ObjectNode) -> Docstring | None:
        try:
            # Access `__doc__` directly to avoid taking the `__doc__` attribute from a parent class.
            value = getattr(node.obj, "__doc__", None)
        except Exception:  # noqa: BLE001  # getattr can trigger exceptions
            return None
        if value is None:
            return None
        try:
            # We avoid `inspect.getdoc` to avoid getting
            # the `__doc__` attribute from a parent class,
            # but we still want to clean the doc.
            cleaned = cleandoc(value)
        except AttributeError:
            # Triggered on method descriptors.
            return None
        return Docstring(
            cleaned,
            parser=self.docstring_parser,
            parser_options=self.docstring_options,
        )

    def _get_linenos(self, node: ObjectNode) -> tuple[int, int] | tuple[None, None]:
        # Line numbers won't be useful if we don't have the source code.
        if not self.filepath or self.filepath not in self.lines_collection:
            return None, None
        try:
            lines, lineno = getsourcelines(node.obj)
        except (OSError, TypeError):
            return None, None
        return lineno, lineno + "".join(lines).rstrip().count("\n")

    def get_module(self, import_paths: Sequence[str | Path] | None = None) -> Module:
        """Build and return the object representing the module attached to this inspector.

        This method triggers a complete inspection of the module members.

        Parameters:
            import_paths: Paths replacing `sys.path` to import the module.

        Returns:
            A module instance.
        """
        import_path = self.module_name
        if self.parent is not None:
            import_path = f"{self.parent.path}.{import_path}"

        # Make sure `import_paths` is a list, in case we want to `insert` into it.
        import_paths = list(import_paths or ())

        # If the thing we want to import has a filepath,
        # we make sure to insert the right parent directory
        # at the front of our list of import paths.
        # We do this by counting the number of dots `.` in the import path,
        # corresponding to slashes `/` in the filesystem,
        # and go up in the file tree the same number of times.
        if self.filepath:
            parent_path = self.filepath.parent
            for _ in range(import_path.count(".")):
                parent_path = parent_path.parent
            # Climb up one more time for `__init__` modules.
            if self.filepath.stem == "__init__":
                parent_path = parent_path.parent
            if parent_path not in import_paths:
                import_paths.insert(0, parent_path)

        value = dynamic_import(import_path, import_paths)

        # We successfully imported the given object,
        # and we now create the object tree with all the necessary nodes,
        # from the root of the package to this leaf object.
        parent_node = None
        if self.parent is not None:
            for part in self.parent.path.split("."):
                parent_node = ObjectNode(None, name=part, parent=parent_node)
        module_node = ObjectNode(value, self.module_name, parent=parent_node)

        self.inspect(module_node)
        return self.current.module

    def inspect(self, node: ObjectNode) -> None:
        """Extend the base inspection with extensions.

        Parameters:
            node: The node to inspect.
        """
        for before_inspector in self.extensions.before_inspection:
            before_inspector.inspect(node)
        getattr(self, f"inspect_{node.kind}", self.generic_inspect)(node)
        for after_inspector in self.extensions.after_inspection:
            after_inspector.inspect(node)

    def generic_inspect(self, node: ObjectNode) -> None:
        """Extend the base generic inspection with extensions.

        Parameters:
            node: The node to inspect.
        """
        for before_inspector in self.extensions.before_children_inspection:
            before_inspector.inspect(node)

        for child in node.children:
            if target_path := child.alias_target_path:
                # If the child is an actual submodule of the current module,
                # and has no `__file__` set, we won't find it on the disk so we must inspect it now.
                # For that we instantiate a new inspector and use it to inspect the submodule,
                # then assign the submodule as member of the current module.
                # If the submodule has a `__file__` set, the loader should find it on the disk,
                # so we skip it here (no member, no alias, just skip it).
                if child.is_module and target_path == f"{self.current.path}.{child.name}":
                    if not hasattr(child.obj, "__file__"):
                        logger.debug(f"Module {target_path} is not discoverable on disk, inspecting right now")
                        inspector = Inspector(
                            child.name,
                            filepath=None,
                            parent=self.current.module,
                            extensions=self.extensions,
                            docstring_parser=self.docstring_parser,
                            docstring_options=self.docstring_options,
                            lines_collection=self.lines_collection,
                            modules_collection=self.modules_collection,
                        )
                        try:
                            inspector.inspect_module(child)
                        finally:
                            self.extensions.attach_inspector(self)
                        self.current.set_member(child.name, inspector.current.module)
                # Otherwise, alias the object.
                else:
                    self.current.set_member(child.name, Alias(child.name, target_path))
            else:
                self.inspect(child)

        for after_inspector in self.extensions.after_children_inspection:
            after_inspector.inspect(node)

    def inspect_module(self, node: ObjectNode) -> None:
        """Inspect a module.

        Parameters:
            node: The node to inspect.
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
        self.generic_inspect(node)
        self.extensions.call("on_members", node=node, obj=module)
        self.extensions.call("on_module_members", node=node, mod=module)

    def inspect_class(self, node: ObjectNode) -> None:
        """Inspect a class.

        Parameters:
            node: The node to inspect.
        """
        self.extensions.call("on_node", node=node)
        self.extensions.call("on_class_node", node=node)

        bases = []
        for base in node.obj.__bases__:
            if base is object:
                continue
            bases.append(f"{base.__module__}.{base.__qualname__}")

        lineno, endlineno = self._get_linenos(node)
        class_ = Class(
            name=node.name,
            docstring=self._get_docstring(node),
            bases=bases,
            lineno=lineno,
            endlineno=endlineno,
        )
        self.current.set_member(node.name, class_)
        self.current = class_
        self.extensions.call("on_instance", node=node, obj=class_)
        self.extensions.call("on_class_instance", node=node, cls=class_)
        self.generic_inspect(node)
        self.extensions.call("on_members", node=node, obj=class_)
        self.extensions.call("on_class_members", node=node, cls=class_)
        self.current = self.current.parent  # type: ignore[assignment]

    def inspect_staticmethod(self, node: ObjectNode) -> None:
        """Inspect a static method.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node, {"staticmethod"})

    def inspect_classmethod(self, node: ObjectNode) -> None:
        """Inspect a class method.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node, {"classmethod"})

    def inspect_method_descriptor(self, node: ObjectNode) -> None:
        """Inspect a method descriptor.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node, {"method descriptor"})

    def inspect_builtin_method(self, node: ObjectNode) -> None:
        """Inspect a builtin method.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node, {"builtin"})

    def inspect_method(self, node: ObjectNode) -> None:
        """Inspect a method.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node)

    def inspect_coroutine(self, node: ObjectNode) -> None:
        """Inspect a coroutine.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node, {"async"})

    def inspect_builtin_function(self, node: ObjectNode) -> None:
        """Inspect a builtin function.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node, {"builtin"})

    def inspect_function(self, node: ObjectNode) -> None:
        """Inspect a function.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node)

    def inspect_cached_property(self, node: ObjectNode) -> None:
        """Inspect a cached property.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node, {"cached", "property"})

    def inspect_property(self, node: ObjectNode) -> None:
        """Inspect a property.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node, {"property"})

    def handle_function(self, node: ObjectNode, labels: set | None = None) -> None:
        """Handle a function.

        Parameters:
            node: The node to inspect.
            labels: Labels to add to the data object.
        """
        self.extensions.call("on_node", node=node)
        self.extensions.call("on_function_node", node=node)

        try:
            signature = getsignature(node.obj)
        except Exception:  # noqa: BLE001
            # so many exceptions can be raised here:
            # AttributeError, NameError, RuntimeError, ValueError, TokenError, TypeError
            parameters = None
            returns = None
        else:
            parameters = Parameters(
                *[_convert_parameter(parameter, parent=self.current) for parameter in signature.parameters.values()],
            )
            return_annotation = signature.return_annotation
            returns = (
                None
                if return_annotation is empty
                else _convert_object_to_annotation(return_annotation, parent=self.current)
            )

        lineno, endlineno = self._get_linenos(node)

        obj: Attribute | Function
        labels = labels or set()
        if "property" in labels:
            obj = Attribute(
                name=node.name,
                value=None,
                annotation=returns,
                docstring=self._get_docstring(node),
                lineno=lineno,
                endlineno=endlineno,
            )
        else:
            obj = Function(
                name=node.name,
                parameters=parameters,
                returns=returns,
                docstring=self._get_docstring(node),
                lineno=lineno,
                endlineno=endlineno,
            )
        obj.labels |= labels
        self.current.set_member(node.name, obj)
        self.extensions.call("on_instance", node=node, obj=obj)
        if obj.is_attribute:
            self.extensions.call("on_attribute_instance", node=node, attr=obj)
        else:
            self.extensions.call("on_function_instance", node=node, func=obj)

    def inspect_attribute(self, node: ObjectNode) -> None:
        """Inspect an attribute.

        Parameters:
            node: The node to inspect.
        """
        self.handle_attribute(node)

    def handle_attribute(self, node: ObjectNode, annotation: str | Expr | None = None) -> None:
        """Handle an attribute.

        Parameters:
            node: The node to inspect.
            annotation: A potentiel annotation.
        """
        self.extensions.call("on_node", node=node)
        self.extensions.call("on_attribute_node", node=node)

        # TODO: to improve
        parent = self.current
        labels: set[str] = set()

        if parent.kind is ObjectKind.MODULE:
            labels.add("module")
        elif parent.kind is ObjectKind.CLASS:
            labels.add("class")
        elif parent.kind is ObjectKind.FUNCTION:
            if parent.name != "__init__":
                return
            parent = parent.parent
            labels.add("instance")

        try:
            value = repr(node.obj)
        except Exception:  # noqa: BLE001
            value = None
        try:
            docstring = self._get_docstring(node)
        except Exception:  # noqa: BLE001
            docstring = None

        attribute = Attribute(
            name=node.name,
            value=value,
            annotation=annotation,
            docstring=docstring,
        )
        attribute.labels |= labels
        parent.set_member(node.name, attribute)

        if node.name == "__all__":
            parent.exports = set(node.obj)
        self.extensions.call("on_instance", node=node, obj=attribute)
        self.extensions.call("on_attribute_instance", node=node, attr=attribute)


_kind_map = {
    SignatureParameter.POSITIONAL_ONLY: ParameterKind.positional_only,
    SignatureParameter.POSITIONAL_OR_KEYWORD: ParameterKind.positional_or_keyword,
    SignatureParameter.VAR_POSITIONAL: ParameterKind.var_positional,
    SignatureParameter.KEYWORD_ONLY: ParameterKind.keyword_only,
    SignatureParameter.VAR_KEYWORD: ParameterKind.var_keyword,
}


def _convert_parameter(parameter: SignatureParameter, parent: Module | Class) -> Parameter:
    name = parameter.name
    annotation = (
        None if parameter.annotation is empty else _convert_object_to_annotation(parameter.annotation, parent=parent)
    )
    kind = _kind_map[parameter.kind]
    if parameter.default is empty:
        default = None
    elif hasattr(parameter.default, "__name__"):
        # avoid repr containing chevrons and memory addresses
        default = parameter.default.__name__
    else:
        default = repr(parameter.default)
    return Parameter(name, annotation=annotation, kind=kind, default=default)


def _convert_object_to_annotation(obj: Any, parent: Module | Class) -> str | Expr | None:
    # even when *we* import future annotations,
    # the object from which we get a signature
    # can come from modules which did *not* import them,
    # so inspect.signature returns actual Python objects
    # that we must deal with
    if not isinstance(obj, str):
        if hasattr(obj, "__name__"):  # noqa: SIM108
            # simple types like int, str, custom classes, etc.
            obj = obj.__name__
        else:
            # other, more complex types: hope for the best
            obj = repr(obj)
    try:
        annotation_node = compile(obj, mode="eval", filename="<>", flags=ast.PyCF_ONLY_AST, optimize=2)
    except SyntaxError:
        return obj
    return safe_get_annotation(annotation_node.body, parent=parent)  # type: ignore[attr-defined]


__all__ = ["inspect", "Inspector"]
