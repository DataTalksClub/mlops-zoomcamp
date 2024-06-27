"""This module contains data encoders/serializers and decoders/deserializers.

The available formats are:

- `JSON`: see the [`JSONEncoder`][griffe.encoders.JSONEncoder] and [`json_decoder`][griffe.encoders.json_decoder].
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path, PosixPath, WindowsPath
from typing import TYPE_CHECKING, Any, Callable

from griffe import expressions
from griffe.dataclasses import (
    Alias,
    Attribute,
    Class,
    Decorator,
    Docstring,
    Function,
    Module,
    Object,
    Parameter,
    Parameters,
)
from griffe.enumerations import DocstringSectionKind, Kind, ParameterKind

if TYPE_CHECKING:
    from enum import Enum

    from griffe.enumerations import Parser


def _enum_value(obj: Enum) -> str | int:
    return obj.value


_json_encoder_map: dict[type, Callable[[Any], Any]] = {
    Path: str,
    PosixPath: str,
    WindowsPath: str,
    ParameterKind: _enum_value,
    Kind: _enum_value,
    DocstringSectionKind: _enum_value,
    set: sorted,
}


class JSONEncoder(json.JSONEncoder):
    """JSON encoder.

    JSON encoders can be used directly, or through
    the [`json.dump`][] or [`json.dumps`][] methods.

    Examples:
        >>> from griffe.encoders import JSONEncoder
        >>> JSONEncoder(full=True).encode(..., **kwargs)

        >>> import json
        >>> from griffe.encoders import JSONEncoder
        >>> json.dumps(..., cls=JSONEncoder, full=True, **kwargs)
    """

    def __init__(
        self,
        *args: Any,
        full: bool = False,
        docstring_parser: Parser | None = None,
        docstring_options: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the encoder.

        Parameters:
            *args: See [`json.JSONEncoder`][].
            full: Whether to dump full data or base data.
                If you plan to reload the data in Python memory
                using the [`json_decoder`][griffe.encoders.json_decoder],
                you don't need the full data as it can be infered again
                using the base data. If you want to feed a non-Python
                tool instead, dump the full data.
            docstring_parser: Deprecated. The docstring parser to use. By default, no parsing is done.
            docstring_options: Deprecated. Additional docstring parsing options.
            **kwargs: See [`json.JSONEncoder`][].
        """
        super().__init__(*args, **kwargs)
        self.full: bool = full

        # TODO: Remove at some point.
        self.docstring_parser: Parser | None = docstring_parser
        self.docstring_options: dict[str, Any] = docstring_options or {}
        if docstring_parser is not None:
            warnings.warn("Parameter `docstring_parser` is deprecated and has no effect.", stacklevel=1)
        if docstring_options is not None:
            warnings.warn("Parameter `docstring_options` is deprecated and has no effect.", stacklevel=1)

    def default(self, obj: Any) -> Any:
        """Return a serializable representation of the given object.

        Parameters:
            obj: The object to serialize.

        Returns:
            A serializable representation.
        """
        try:
            return obj.as_dict(full=self.full)
        except AttributeError:
            return _json_encoder_map.get(type(obj), super().default)(obj)


def _load_docstring(obj_dict: dict) -> Docstring | None:
    if "docstring" in obj_dict:
        return Docstring(**obj_dict["docstring"])
    return None


def _load_decorators(obj_dict: dict) -> list[Decorator]:
    return [Decorator(**dec) for dec in obj_dict.get("decorators", [])]


def _load_expression(expression: dict) -> expressions.Expr:
    # The expression class name is stored in the `cls` key-value.
    cls = getattr(expressions, expression.pop("cls"))
    expr = cls(**expression)

    # For attributes, we need to re-attach names (`values`) together,
    # as a single linked list, from right to left:
    # in `a.b.c`, `c` links to `b` which links to `a`.
    # In `(a or b).c` however, `c` does not link to `(a or b)`,
    # as `(a or b)` is not a name and wouldn't allow to resolve `c`.
    if cls is expressions.ExprAttribute:
        previous = None
        for value in expr.values:
            if previous is not None:
                value.parent = previous
            if isinstance(value, expressions.ExprName):
                previous = value
    return expr


def _load_parameter(obj_dict: dict[str, Any]) -> Parameter:
    return Parameter(
        obj_dict["name"],
        annotation=obj_dict["annotation"],
        kind=ParameterKind(obj_dict["kind"]),
        default=obj_dict["default"],
        docstring=_load_docstring(obj_dict),
    )


def _attach_parent_to_expr(expr: expressions.Expr | str | None, parent: Module | Class) -> None:
    if not isinstance(expr, expressions.Expr):
        return
    for elem in expr:
        if isinstance(elem, expressions.ExprName):
            elem.parent = parent
        elif isinstance(elem, expressions.ExprAttribute) and isinstance(elem.first, expressions.ExprName):
            elem.first.parent = parent


def _attach_parent_to_exprs(obj: Class | Function | Attribute, parent: Module | Class) -> None:
    # Every name and attribute expression must be reattached
    # to its parent Griffe object (using its `parent` attribute),
    # to allow resolving names.
    if isinstance(obj, Class):
        if obj.docstring:
            _attach_parent_to_expr(obj.docstring.value, parent)
        for decorator in obj.decorators:
            _attach_parent_to_expr(decorator.value, parent)
    elif isinstance(obj, Function):
        if obj.docstring:
            _attach_parent_to_expr(obj.docstring.value, parent)
        for decorator in obj.decorators:
            _attach_parent_to_expr(decorator.value, parent)
        for param in obj.parameters:
            _attach_parent_to_expr(param.annotation, parent)
            _attach_parent_to_expr(param.default, parent)
        _attach_parent_to_expr(obj.returns, parent)
    elif isinstance(obj, Attribute):
        if obj.docstring:
            _attach_parent_to_expr(obj.docstring.value, parent)
        _attach_parent_to_expr(obj.value, parent)


def _load_module(obj_dict: dict[str, Any]) -> Module:
    module = Module(name=obj_dict["name"], filepath=Path(obj_dict["filepath"]), docstring=_load_docstring(obj_dict))
    for module_member in obj_dict.get("members", []):
        module.set_member(module_member.name, module_member)
        _attach_parent_to_exprs(module_member, module)
    module.labels |= set(obj_dict.get("labels", ()))
    return module


def _load_class(obj_dict: dict[str, Any]) -> Class:
    class_ = Class(
        name=obj_dict["name"],
        lineno=obj_dict["lineno"],
        endlineno=obj_dict.get("endlineno"),
        docstring=_load_docstring(obj_dict),
        decorators=_load_decorators(obj_dict),
        bases=obj_dict["bases"],
    )
    for class_member in obj_dict.get("members", []):
        class_.set_member(class_member.name, class_member)
        _attach_parent_to_exprs(class_member, class_)
    class_.labels |= set(obj_dict.get("labels", ()))
    _attach_parent_to_exprs(class_, class_)
    return class_


def _load_function(obj_dict: dict[str, Any]) -> Function:
    function = Function(
        name=obj_dict["name"],
        parameters=Parameters(*obj_dict["parameters"]),
        returns=obj_dict["returns"],
        decorators=_load_decorators(obj_dict),
        lineno=obj_dict["lineno"],
        endlineno=obj_dict.get("endlineno"),
        docstring=_load_docstring(obj_dict),
    )
    function.labels |= set(obj_dict.get("labels", ()))
    return function


def _load_attribute(obj_dict: dict[str, Any]) -> Attribute:
    attribute = Attribute(
        name=obj_dict["name"],
        lineno=obj_dict["lineno"],
        endlineno=obj_dict.get("endlineno"),
        docstring=_load_docstring(obj_dict),
        value=obj_dict.get("value"),
        annotation=obj_dict.get("annotation"),
    )
    attribute.labels |= set(obj_dict.get("labels", ()))
    return attribute


def _load_alias(obj_dict: dict[str, Any]) -> Alias:
    return Alias(
        name=obj_dict["name"],
        target=obj_dict["target_path"],
        lineno=obj_dict["lineno"],
        endlineno=obj_dict.get("endlineno"),
    )


_loader_map: dict[Kind, Callable[[dict[str, Any]], Module | Class | Function | Attribute | Alias]] = {
    Kind.MODULE: _load_module,
    Kind.CLASS: _load_class,
    Kind.FUNCTION: _load_function,
    Kind.ATTRIBUTE: _load_attribute,
    Kind.ALIAS: _load_alias,
}


def json_decoder(obj_dict: dict[str, Any]) -> dict[str, Any] | Object | Alias | Parameter | str | expressions.Expr:
    """Decode dictionaries as data classes.

    The [`json.loads`][] method walks the tree from bottom to top.

    Examples:
        >>> import json
        >>> from griffe.encoders import json_decoder
        >>> json.loads(..., object_hook=json_decoder)

    Parameters:
        obj_dict: The dictionary to decode.

    Returns:
        An instance of a data class.
    """
    # Load expressions.
    if "cls" in obj_dict:
        return _load_expression(obj_dict)

    # Load objects and parameters.
    if "kind" in obj_dict:
        try:
            kind = Kind(obj_dict["kind"])
        except ValueError:
            return _load_parameter(obj_dict)
        return _loader_map[kind](obj_dict)

    # Return dict as is.
    return obj_dict


__all__ = ["JSONEncoder", "json_decoder"]
