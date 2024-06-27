"""This module exports "breaking changes" related utilities."""

from __future__ import annotations

import contextlib
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, Iterator

from colorama import Fore, Style

from griffe.enumerations import BreakageKind, ExplanationStyle, ParameterKind
from griffe.exceptions import AliasResolutionError
from griffe.git import WORKTREE_PREFIX
from griffe.logger import get_logger

if TYPE_CHECKING:
    from griffe.dataclasses import Alias, Attribute, Class, Function, Object

POSITIONAL = frozenset((ParameterKind.positional_only, ParameterKind.positional_or_keyword))
KEYWORD = frozenset((ParameterKind.keyword_only, ParameterKind.positional_or_keyword))
POSITIONAL_KEYWORD_ONLY = frozenset((ParameterKind.positional_only, ParameterKind.keyword_only))
VARIADIC = frozenset((ParameterKind.var_positional, ParameterKind.var_keyword))

logger = get_logger(__name__)


class Breakage:
    """Breakages can explain what broke from a version to another."""

    kind: BreakageKind

    def __init__(self, obj: Object, old_value: Any, new_value: Any, details: str = "") -> None:
        """Initialize the breakage.

        Parameters:
            obj: The object related to the breakage.
            old_value: The old value.
            new_value: The new, incompatible value.
            details: Some details about the breakage.
        """
        self.obj = obj
        self.old_value = old_value
        self.new_value = new_value
        self.details = details

    def __str__(self) -> str:
        return self.kind.value

    def __repr__(self) -> str:
        return self.kind.name

    def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
        """Return this object's data as a dictionary.

        Parameters:
            full: Whether to return full info, or just base info.
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        return {
            "kind": self.kind,
            "object_path": self.obj.path,
            "old_value": self.old_value,
            "new_value": self.new_value,
        }

    def explain(self, style: ExplanationStyle = ExplanationStyle.ONE_LINE) -> str:
        """Explain the breakage by showing old and new value.

        Parameters:
            style: The explanation style to use.

        Returns:
            An explanation.
        """
        return getattr(self, f"_explain_{style.value}")()

    @property
    def _filepath(self) -> Path:
        if self.obj.is_alias:
            return self.obj.parent.filepath  # type: ignore[union-attr,return-value]
        return self.obj.filepath  # type: ignore[return-value]

    @property
    def _relative_filepath(self) -> Path:
        if self.obj.is_alias:
            return self.obj.parent.relative_filepath  # type: ignore[union-attr]
        return self.obj.relative_filepath

    @property
    def _relative_package_filepath(self) -> Path:
        if self.obj.is_alias:
            return self.obj.parent.relative_package_filepath  # type: ignore[union-attr]
        return self.obj.relative_package_filepath

    @property
    def _location(self) -> Path:
        # Absolute file path probably means temporary worktree.
        # We use our worktree prefix to remove some components
        # of the path on the left (`/tmp/griffe-worktree-*/griffe_*/repo`).
        if self._relative_filepath.is_absolute():
            parts = self._relative_filepath.parts
            for index, part in enumerate(parts):
                if part.startswith(WORKTREE_PREFIX):
                    return Path(*parts[index + 2 :])
        return self._relative_filepath

    @property
    def _canonical_path(self) -> str:
        if self.obj.is_alias:
            return self.obj.path
        return self.obj.canonical_path

    @property
    def _module_path(self) -> str:
        if self.obj.is_alias:
            return self.obj.parent.module.path  # type: ignore[union-attr]
        return self.obj.module.path

    @property
    def _relative_path(self) -> str:
        return self._canonical_path[len(self._module_path) + 1 :] or "<module>"

    @property
    def _lineno(self) -> int:
        # If the object was removed, and we are able to get the location (file path)
        # as a relative path, then we use 0 instead of the original line number
        # (it helps when checking current sources, and avoids pointing to now missing contents).
        if self.kind is BreakageKind.OBJECT_REMOVED and self._relative_filepath != self._location:
            return 0
        if self.obj.is_alias:
            return self.obj.alias_lineno or 0  # type: ignore[attr-defined]
        return self.obj.lineno or 0

    def _format_location(self) -> str:
        return f"{Style.BRIGHT}{self._location}{Style.RESET_ALL}:{self._lineno}"

    def _format_title(self) -> str:
        return self._relative_path

    def _format_kind(self) -> str:
        return f"{Fore.YELLOW}{self.kind.value}{Fore.RESET}"

    def _format_old_value(self) -> str:
        return str(self.old_value)

    def _format_new_value(self) -> str:
        return str(self.new_value)

    def _explain_oneline(self) -> str:
        explanation = f"{self._format_location()}: {self._format_title()}: {self._format_kind()}"
        old = self._format_old_value()
        new = self._format_new_value()
        if old and new:
            change = f"{old} -> {new}"
        elif old:
            change = old
        elif new:
            change = new
        else:
            change = ""
        if change:
            return f"{explanation}: {change}"
        return explanation

    def _explain_verbose(self) -> str:
        lines = [f"{self._format_location()}: {self._format_title()}:"]
        kind = self._format_kind()
        old = self._format_old_value()
        new = self._format_new_value()
        if old or new:
            lines.append(f"{kind}:")
        else:
            lines.append(kind)
        if old:
            lines.append(f"  Old: {old}")
        if new:
            lines.append(f"  New: {new}")
        if self.details:
            lines.append(f"  Details: {self.details}")
        lines.append("")
        return "\n".join(lines)

    def _explain_markdown(self) -> str:
        return self._explain_oneline()

    def _explain_github(self) -> str:
        return self._explain_oneline()


class ParameterMovedBreakage(Breakage):
    """Specific breakage class for moved parameters."""

    kind: BreakageKind = BreakageKind.PARAMETER_MOVED

    def _format_title(self) -> str:
        return f"{self._relative_path}({Fore.BLUE}{self.old_value.name}{Fore.RESET})"

    def _format_old_value(self) -> str:
        return ""

    def _format_new_value(self) -> str:
        return ""


class ParameterRemovedBreakage(Breakage):
    """Specific breakage class for removed parameters."""

    kind: BreakageKind = BreakageKind.PARAMETER_REMOVED

    def _format_title(self) -> str:
        return f"{self._relative_path}({Fore.BLUE}{self.old_value.name}{Fore.RESET})"

    def _format_old_value(self) -> str:
        return ""

    def _format_new_value(self) -> str:
        return ""


class ParameterChangedKindBreakage(Breakage):
    """Specific breakage class for parameters whose kind changed."""

    kind: BreakageKind = BreakageKind.PARAMETER_CHANGED_KIND

    def _format_title(self) -> str:
        return f"{self._relative_path}({Fore.BLUE}{self.old_value.name}{Fore.RESET})"

    def _format_old_value(self) -> str:
        return str(self.old_value.kind.value)

    def _format_new_value(self) -> str:
        return str(self.new_value.kind.value)


class ParameterChangedDefaultBreakage(Breakage):
    """Specific breakage class for parameters whose default value changed."""

    kind: BreakageKind = BreakageKind.PARAMETER_CHANGED_DEFAULT

    def _format_title(self) -> str:
        return f"{self._relative_path}({Fore.BLUE}{self.old_value.name}{Fore.RESET})"

    def _format_old_value(self) -> str:
        return str(self.old_value.default)

    def _format_new_value(self) -> str:
        return str(self.new_value.default)


class ParameterChangedRequiredBreakage(Breakage):
    """Specific breakage class for parameters which became required."""

    kind: BreakageKind = BreakageKind.PARAMETER_CHANGED_REQUIRED

    def _format_title(self) -> str:
        return f"{self._relative_path}({Fore.BLUE}{self.old_value.name}{Fore.RESET})"

    def _format_old_value(self) -> str:
        return ""

    def _format_new_value(self) -> str:
        return ""


class ParameterAddedRequiredBreakage(Breakage):
    """Specific breakage class for new parameters added as required."""

    kind: BreakageKind = BreakageKind.PARAMETER_ADDED_REQUIRED

    def _format_title(self) -> str:
        return f"{self._relative_path}({Fore.BLUE}{self.new_value.name}{Fore.RESET})"

    def _format_old_value(self) -> str:
        return ""

    def _format_new_value(self) -> str:
        return ""


class ReturnChangedTypeBreakage(Breakage):
    """Specific breakage class for return values which changed type."""

    kind: BreakageKind = BreakageKind.RETURN_CHANGED_TYPE


class ObjectRemovedBreakage(Breakage):
    """Specific breakage class for removed objects."""

    kind: BreakageKind = BreakageKind.OBJECT_REMOVED

    def _format_old_value(self) -> str:
        return ""

    def _format_new_value(self) -> str:
        return ""


class ObjectChangedKindBreakage(Breakage):
    """Specific breakage class for objects whose kind changed."""

    kind: BreakageKind = BreakageKind.OBJECT_CHANGED_KIND

    def _format_old_value(self) -> str:
        return self.old_value.value

    def _format_new_value(self) -> str:
        return self.new_value.value


class AttributeChangedTypeBreakage(Breakage):
    """Specific breakage class for attributes whose type changed."""

    kind: BreakageKind = BreakageKind.ATTRIBUTE_CHANGED_TYPE


class AttributeChangedValueBreakage(Breakage):
    """Specific breakage class for attributes whose value changed."""

    kind: BreakageKind = BreakageKind.ATTRIBUTE_CHANGED_VALUE


class ClassRemovedBaseBreakage(Breakage):
    """Specific breakage class for removed base classes."""

    kind: BreakageKind = BreakageKind.CLASS_REMOVED_BASE

    def _format_old_value(self) -> str:
        return "[" + ", ".join(base.canonical_path for base in self.old_value) + "]"

    def _format_new_value(self) -> str:
        return "[" + ", ".join(base.canonical_path for base in self.new_value) + "]"


# TODO: Check decorators? Maybe resolved by extensions and/or dynamic analysis.
def _class_incompatibilities(
    old_class: Class,
    new_class: Class,
    *,
    seen_paths: set[str],
) -> Iterable[Breakage]:
    yield from ()
    if new_class.bases != old_class.bases and len(new_class.bases) < len(old_class.bases):
        yield ClassRemovedBaseBreakage(new_class, old_class.bases, new_class.bases)
    yield from _member_incompatibilities(old_class, new_class, seen_paths=seen_paths)


# TODO: Check decorators? Maybe resolved by extensions and/or dynamic analysis.
def _function_incompatibilities(old_function: Function, new_function: Function) -> Iterator[Breakage]:
    new_param_names = [param.name for param in new_function.parameters]
    param_kinds = {param.kind for param in new_function.parameters}
    has_variadic_args = ParameterKind.var_positional in param_kinds
    has_variadic_kwargs = ParameterKind.var_keyword in param_kinds

    for old_index, old_param in enumerate(old_function.parameters):
        # Check if the parameter was removed.
        if old_param.name not in new_function.parameters:
            swallowed = (
                (old_param.kind is ParameterKind.keyword_only and has_variadic_kwargs)
                or (old_param.kind is ParameterKind.positional_only and has_variadic_args)
                or (old_param.kind is ParameterKind.positional_or_keyword and has_variadic_args and has_variadic_kwargs)
            )
            if not swallowed:
                yield ParameterRemovedBreakage(new_function, old_param, None)
            continue

        # Check if the parameter became required.
        new_param = new_function.parameters[old_param.name]
        if new_param.required and not old_param.required:
            yield ParameterChangedRequiredBreakage(new_function, old_param, new_param)

        # Check if the parameter was moved.
        if old_param.kind in POSITIONAL and new_param.kind in POSITIONAL:
            new_index = new_param_names.index(old_param.name)
            if new_index != old_index:
                details = f"position: from {old_index} to {new_index} ({new_index - old_index:+})"
                yield ParameterMovedBreakage(new_function, old_param, new_param, details=details)

        # Check if the parameter changed kind.
        if old_param.kind is not new_param.kind:
            incompatible_kind = any(
                (
                    # positional-only to keyword-only
                    old_param.kind is ParameterKind.positional_only and new_param.kind is ParameterKind.keyword_only,
                    # keyword-only to positional-only
                    old_param.kind is ParameterKind.keyword_only and new_param.kind is ParameterKind.positional_only,
                    # positional or keyword to positional-only/keyword-only
                    old_param.kind is ParameterKind.positional_or_keyword and new_param.kind in POSITIONAL_KEYWORD_ONLY,
                    # not keyword-only to variadic keyword, without variadic positional
                    new_param.kind is ParameterKind.var_keyword
                    and old_param.kind is not ParameterKind.keyword_only
                    and not has_variadic_args,
                    # not positional-only to variadic positional, without variadic keyword
                    new_param.kind is ParameterKind.var_positional
                    and old_param.kind is not ParameterKind.positional_only
                    and not has_variadic_kwargs,
                ),
            )
            if incompatible_kind:
                yield ParameterChangedKindBreakage(new_function, old_param, new_param)

        # Check if the parameter changed default.
        breakage = ParameterChangedDefaultBreakage(new_function, old_param, new_param)
        non_required = not old_param.required and not new_param.required
        non_variadic = old_param.kind not in VARIADIC and new_param.kind not in VARIADIC
        if non_required and non_variadic:
            try:
                if old_param.default != new_param.default:
                    yield breakage
            except Exception:  # noqa: BLE001 (equality checks sometimes fail, e.g. numpy arrays)
                # NOTE: Emitting breakage on a failed comparison could be a preference.
                yield breakage

    # Check if required parameters were added.
    for new_param in new_function.parameters:
        if new_param.name not in old_function.parameters and new_param.required:
            yield ParameterAddedRequiredBreakage(new_function, None, new_param)

    if not _returns_are_compatible(old_function, new_function):
        yield ReturnChangedTypeBreakage(new_function, old_function.returns, new_function.returns)


def _attribute_incompatibilities(old_attribute: Attribute, new_attribute: Attribute) -> Iterable[Breakage]:
    # TODO: Use beartype.peps.resolve_pep563 and beartype.door.is_subhint?
    # if old_attribute.annotation is not None and new_attribute.annotation is not None:
    #     if not is_subhint(new_attribute.annotation, old_attribute.annotation):
    if old_attribute.value != new_attribute.value:
        if new_attribute.value is None:
            yield AttributeChangedValueBreakage(new_attribute, old_attribute.value, "unset")
        else:
            yield AttributeChangedValueBreakage(new_attribute, old_attribute.value, new_attribute.value)


def _alias_incompatibilities(
    old_obj: Object | Alias,
    new_obj: Object | Alias,
    *,
    seen_paths: set[str],
) -> Iterable[Breakage]:
    try:
        old_member = old_obj.target if old_obj.is_alias else old_obj  # type: ignore[union-attr]
        new_member = new_obj.target if new_obj.is_alias else new_obj  # type: ignore[union-attr]
    except AliasResolutionError:
        logger.debug(f"API check: {old_obj.path} | {new_obj.path}: skip alias with unknown target")
        return

    yield from _type_based_yield(old_member, new_member, seen_paths=seen_paths)


def _member_incompatibilities(
    old_obj: Object | Alias,
    new_obj: Object | Alias,
    *,
    seen_paths: set[str] | None = None,
) -> Iterator[Breakage]:
    seen_paths = set() if seen_paths is None else seen_paths
    for name, old_member in old_obj.all_members.items():
        if not old_member.is_public:
            logger.debug(f"API check: {old_obj.path}.{name}: skip non-public object")
            continue
        logger.debug(f"API check: {old_obj.path}.{name}")
        try:
            new_member = new_obj.all_members[name]
        except KeyError:
            if (not old_member.is_alias and old_member.is_module) or old_member.is_public:
                yield ObjectRemovedBreakage(old_member, old_member, None)  # type: ignore[arg-type]
        else:
            yield from _type_based_yield(old_member, new_member, seen_paths=seen_paths)


def _type_based_yield(
    old_member: Object | Alias,
    new_member: Object | Alias,
    *,
    seen_paths: set[str],
) -> Iterator[Breakage]:
    if old_member.path in seen_paths:
        return
    seen_paths.add(old_member.path)
    if old_member.is_alias or new_member.is_alias:
        # Should be first, since there can be the case where there is an alias and another kind of object, which may
        # not be a breaking change
        yield from _alias_incompatibilities(
            old_member,
            new_member,
            seen_paths=seen_paths,
        )
    elif new_member.kind != old_member.kind:
        yield ObjectChangedKindBreakage(new_member, old_member.kind, new_member.kind)  # type: ignore[arg-type]
    elif old_member.is_module:
        yield from _member_incompatibilities(
            old_member,
            new_member,
            seen_paths=seen_paths,
        )
    elif old_member.is_class:
        yield from _class_incompatibilities(
            old_member,  # type: ignore[arg-type]
            new_member,  # type: ignore[arg-type]
            seen_paths=seen_paths,
        )
    elif old_member.is_function:
        yield from _function_incompatibilities(old_member, new_member)  # type: ignore[arg-type]
    elif old_member.is_attribute:
        yield from _attribute_incompatibilities(old_member, new_member)  # type: ignore[arg-type]


def _returns_are_compatible(old_function: Function, new_function: Function) -> bool:
    # We consider that a return value of `None` only is not a strong contract,
    # it just means that the function returns nothing. We don't expect users
    # to be asserting that the return value is `None`.
    # Therefore we don't consider it a breakage if the return changes from `None`
    # to something else: the function just gained a return value.
    if old_function.returns is None:
        return True

    if new_function.returns is None:
        # NOTE: Should it be configurable to allow/disallow removing a return type?
        return False

    with contextlib.suppress(AttributeError):
        if new_function.returns == old_function.returns:
            return True

    # TODO: Use beartype.peps.resolve_pep563 and beartype.door.is_subhint?
    return True


_sentinel = object()


def find_breaking_changes(
    old_obj: Object | Alias,
    new_obj: Object | Alias,
    *,
    ignore_private: bool = _sentinel,  # type: ignore[assignment]
) -> Iterator[Breakage]:
    """Find breaking changes between two versions of the same API.

    The function will iterate recursively on all objects
    and yield breaking changes with detailed information.

    Parameters:
        old_obj: The old version of an object.
        new_obj: The new version of an object.

    Yields:
        Breaking changes.

    Examples:
        >>> import sys, griffe
        >>> new = griffe.load("pkg")
        >>> old = griffe.load_git("pkg", "1.2.3")
        >>> for breakage in griffe.find_breaking_changes(old, new)
        ...     print(breakage.explain(style=style), file=sys.stderr)
    """
    if ignore_private is not _sentinel:
        warnings.warn(
            "The `ignore_private` parameter is deprecated and will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2,
        )
    yield from _member_incompatibilities(old_obj, new_obj)


__all__ = [
    "AttributeChangedTypeBreakage",
    "AttributeChangedValueBreakage",
    "Breakage",
    "BreakageKind",
    "ClassRemovedBaseBreakage",
    "ExplanationStyle",
    "find_breaking_changes",
    "ObjectChangedKindBreakage",
    "ObjectRemovedBreakage",
    "ParameterAddedRequiredBreakage",
    "ParameterChangedDefaultBreakage",
    "ParameterChangedKindBreakage",
    "ParameterChangedRequiredBreakage",
    "ParameterMovedBreakage",
    "ParameterRemovedBreakage",
    "ReturnChangedTypeBreakage",
]
