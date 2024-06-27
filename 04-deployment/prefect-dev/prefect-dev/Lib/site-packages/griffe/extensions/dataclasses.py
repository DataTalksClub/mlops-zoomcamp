"""Built-in extension adding support for dataclasses.

This extension re-creates `__init__` methods of dataclasses
during static analysis.
"""

from __future__ import annotations

import ast
from contextlib import suppress
from functools import lru_cache
from typing import Any, cast

from griffe.dataclasses import Attribute, Class, Decorator, Function, Module, Parameter, Parameters
from griffe.enumerations import ParameterKind
from griffe.expressions import (
    Expr,
    ExprAttribute,
    ExprCall,
    ExprDict,
)
from griffe.extensions.base import Extension


def _dataclass_decorator(decorators: list[Decorator]) -> Expr | None:
    for decorator in decorators:
        if isinstance(decorator.value, Expr) and decorator.value.canonical_path == "dataclasses.dataclass":
            return decorator.value
    return None


def _expr_args(expr: Expr) -> dict[str, str | Expr]:
    args = {}
    if isinstance(expr, ExprCall):
        for argument in expr.arguments:
            try:
                args[argument.name] = argument.value  # type: ignore[union-attr]
            except AttributeError:
                # Argument is a unpacked variable.
                with suppress(Exception):
                    collection = expr.function.parent.modules_collection  # type: ignore[attr-defined]
                    var = collection[argument.value.canonical_path]  # type: ignore[union-attr]
                    args.update(_expr_args(var.value))
    elif isinstance(expr, ExprDict):
        args.update({ast.literal_eval(str(key)): value for key, value in zip(expr.keys, expr.values)})
    return args


def _dataclass_arguments(decorators: list[Decorator]) -> dict[str, Any]:
    if (expr := _dataclass_decorator(decorators)) and isinstance(expr, ExprCall):
        return _expr_args(expr)
    return {}


def _field_arguments(attribute: Attribute) -> dict[str, Any]:
    if attribute.value:
        value = attribute.value
        if isinstance(value, ExprAttribute):
            value = value.last
        if isinstance(value, ExprCall) and value.canonical_path == "dataclasses.field":
            return _expr_args(value)
    return {}


@lru_cache(maxsize=None)
def _dataclass_parameters(class_: Class) -> list[Parameter]:
    # Fetch `@dataclass` arguments if any.
    dec_args = _dataclass_arguments(class_.decorators)

    # Parameters not added to `__init__`, return empty list.
    if dec_args.get("init") == "False":
        return []

    # All parameters marked as keyword-only.
    kw_only = dec_args.get("kw_only") == "True"

    # Iterate on current attributes to find parameters.
    parameters = []
    for member in class_.members.values():
        if member.is_attribute:
            member = cast(Attribute, member)

            # Attributes that have labels for these characteristics are
            # not class parameters:
            #   - @property
            #   - @cached_property
            #   - ClassVar annotation
            if "property" in member.labels or (
                # TODO: It is better to explicitly check for ClassVar, but
                # Visitor.handle_attribute unwraps it from the annotation.
                # Maybe create internal_labels and store classvar in there.
                "class-attribute" in member.labels and "instance-attribute" not in member.labels
            ):
                continue

            # Start of keyword-only parameters.
            if isinstance(member.annotation, Expr) and member.annotation.canonical_path == "dataclasses.KW_ONLY":
                kw_only = True
                continue

            # Fetch `field` arguments if any.
            field_args = _field_arguments(member)

            # Parameter not added to `__init__`, skip it.
            if field_args.get("init") == "False":
                continue

            # Determine parameter kind.
            kind = (
                ParameterKind.keyword_only
                if kw_only or field_args.get("kw_only") == "True"
                else ParameterKind.positional_or_keyword
            )

            # Determine parameter default.
            if "default_factory" in field_args:
                default = ExprCall(function=field_args["default_factory"], arguments=[])
            else:
                default = field_args.get("default", None if field_args else member.value)

            # Add parameter to the list.
            parameters.append(
                Parameter(
                    member.name,
                    annotation=member.annotation,
                    kind=kind,
                    default=default,
                    docstring=member.docstring,
                ),
            )

    return parameters


def _reorder_parameters(parameters: list[Parameter]) -> list[Parameter]:
    # De-duplicate, overwriting previous parameters.
    params_dict = {param.name: param for param in parameters}

    # Re-order, putting positional-only in front and keyword-only at the end.
    pos_only = []
    pos_kw = []
    kw_only = []
    for param in params_dict.values():
        if param.kind is ParameterKind.positional_only:
            pos_only.append(param)
        elif param.kind is ParameterKind.keyword_only:
            kw_only.append(param)
        else:
            pos_kw.append(param)
    return pos_only + pos_kw + kw_only


def _set_dataclass_init(class_: Class) -> None:
    # Retrieve parameters from all parent dataclasses.
    parameters = []
    try:
        mro = class_.mro()
    except ValueError:
        mro = ()  # type: ignore[assignment]
    for parent in reversed(mro):
        if _dataclass_decorator(parent.decorators):
            parameters.extend(_dataclass_parameters(parent))
            # At least one parent dataclass makes the current class a dataclass:
            # that's how `dataclasses.is_dataclass` works.
            class_.labels.add("dataclass")

    # If the class is not decorated with `@dataclass`, skip it.
    if not _dataclass_decorator(class_.decorators):
        return

    # Add current class parameters.
    parameters.extend(_dataclass_parameters(class_))

    # Create `__init__` method with re-ordered parameters.
    init = Function(
        "__init__",
        lineno=0,
        endlineno=0,
        parent=class_,
        parameters=Parameters(
            Parameter(name="self", annotation=None, kind=ParameterKind.positional_or_keyword, default=None),
            *_reorder_parameters(parameters),
        ),
        returns="None",
    )
    class_.set_member("__init__", init)


def _del_members_annotated_as_initvar(class_: Class) -> None:
    # Definitions annotated as InitVar are not class members
    attributes = [member for member in class_.members.values() if isinstance(member, Attribute)]
    for attribute in attributes:
        if isinstance(attribute.annotation, Expr) and attribute.annotation.canonical_path == "dataclasses.InitVar":
            class_.del_member(attribute.name)


def _apply_recursively(mod_cls: Module | Class, processed: set[str]) -> None:
    if mod_cls.canonical_path in processed:
        return
    processed.add(mod_cls.canonical_path)
    if isinstance(mod_cls, Class):
        if "__init__" not in mod_cls.members:
            _set_dataclass_init(mod_cls)
            _del_members_annotated_as_initvar(mod_cls)
        for member in mod_cls.members.values():
            if not member.is_alias and member.is_class:
                _apply_recursively(member, processed)  # type: ignore[arg-type]
    elif isinstance(mod_cls, Module):
        for member in mod_cls.members.values():
            if not member.is_alias and (member.is_module or member.is_class):
                _apply_recursively(member, processed)  # type: ignore[arg-type]


class DataclassesExtension(Extension):
    """Built-in extension adding support for dataclasses.

    This extension creates `__init__` methods of dataclasses
    if they don't already exist.
    """

    def on_package_loaded(self, *, pkg: Module) -> None:
        """Hook for loaded packages.

        Parameters:
            pkg: The loaded package.
        """
        _apply_recursively(pkg, set())
