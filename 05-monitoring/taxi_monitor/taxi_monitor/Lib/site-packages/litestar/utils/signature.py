from __future__ import annotations

import sys
import typing
from copy import deepcopy
from dataclasses import dataclass, replace
from inspect import Signature, getmembers, isclass, ismethod
from itertools import chain
from typing import TYPE_CHECKING, Any, Union

from typing_extensions import Annotated, Self, get_args, get_origin, get_type_hints

from litestar import connection, datastructures, types
from litestar.exceptions import ImproperlyConfiguredException
from litestar.types import Empty
from litestar.typing import FieldDefinition
from litestar.utils.typing import expand_type_var_in_type_hint, unwrap_annotation

if TYPE_CHECKING:
    from typing import Sequence

    from litestar.types import AnyCallable

if sys.version_info < (3, 11):
    from typing import _get_defaults  # type: ignore[attr-defined]
else:

    def _get_defaults(_: Any) -> Any: ...


__all__ = (
    "add_types_to_signature_namespace",
    "get_fn_type_hints",
    "ParsedSignature",
)

_GLOBAL_NAMES = {
    namespace: export
    for namespace, export in chain(
        tuple(getmembers(types)), tuple(getmembers(connection)), tuple(getmembers(datastructures))
    )
    if namespace[0].isupper() and namespace in chain(types.__all__, connection.__all__, datastructures.__all__)  # pyright: ignore
}
"""A mapping of names used for handler signature forward-ref resolution.

This allows users to include these names within an `if TYPE_CHECKING:` block in their handler module.
"""


def _unwrap_implicit_optional_hints(defaults: dict[str, Any], hints: dict[str, Any]) -> dict[str, Any]:
    """Unwrap implicit optional hints.

    On Python<3.11, if a function parameter annotation has a ``None`` default, it is unconditionally wrapped in an
    ``Optional`` type.

    If the annotation is not annotated, then any nested unions are flattened, e.g.,:

    .. code-block:: python

        def foo(a: Optional[Union[str, int]] = None): ...

    ...will become `Union[str, int, NoneType]`.

    However, if the annotation is annotated, then we end up with an optional union around the annotated type, e.g.,:

    .. code-block:: python

        def foo(a: Annotated[Optional[Union[str, int]], ...] = None): ...

    ... becomes `Union[Annotated[Union[str, int, NoneType], ...], NoneType]`

    This function makes the latter case consistent with the former by either removing the outer union if it is redundant
    or flattening the union if it is not. The latter case would become `Annotated[Union[str, int, NoneType], ...]`.

    Args:
        defaults: Mapping of names to default values.
        hints: Mapping of names to types.

    Returns:
        Mapping of names to types.
    """

    def _is_two_arg_optional(origin_: Any, args_: Any) -> bool:
        """Check if a type is a two-argument optional type.

        If the type has been wrapped in `Optional` by `get_type_hints()` it will always be a union of a type and
        `NoneType`.

        See: https://github.com/litestar-org/litestar/pull/2516
        """
        return origin_ is Union and len(args_) == 2 and args_[1] is type(None)

    def _is_any_optional(origin_: Any, args_: tuple[Any, ...]) -> bool:
        """Detect if a type is a union with `NoneType`.

        After detecting that a type is a two-argument optional type, this function can be used to detect if the
        inner type is a union with `NoneType` at all.

        We only want to perform the unwrapping of the optional union if the inner type is optional as well.
        """
        return origin_ is Union and any(arg is type(None) for arg in args_)

    for name, default in defaults.items():
        if default is not None:
            continue

        hint = hints[name]
        origin = get_origin(hint)
        args = get_args(hint)

        if _is_two_arg_optional(origin, args):
            unwrapped_inner, meta, wrappers = unwrap_annotation(args[0])

            if Annotated not in wrappers:
                continue

            inner_args = get_args(unwrapped_inner)

            if not _is_any_optional(get_origin(unwrapped_inner), inner_args):
                # this is where hint is like `Union[Annotated[Union[str, int], ...], NoneType]`, we add the outer union
                # into the inner one, and re-wrap with Annotated
                union_args = (*(inner_args or (unwrapped_inner,)), type(None))
                # calling `__class_getitem__` directly as in earlier py vers it is a syntax error to unpack into
                # the getitem brackets, e.g., Annotated[T, *meta].
                hints[name] = Annotated.__class_getitem__((Union[union_args], *meta))  # type: ignore[attr-defined]
                continue

            # this is where hint is like `Union[Annotated[Union[str, NoneType], ...], NoneType]`, we remove the
            # redundant outer union
            hints[name] = args[0]
    return hints


def get_fn_type_hints(fn: Any, namespace: dict[str, Any] | None = None) -> dict[str, Any]:
    """Resolve type hints for ``fn``.

    Args:
        fn: Callable that is being inspected
        namespace: Extra names for resolution of forward references.

    Returns:
        Mapping of names to types.
    """
    fn_to_inspect: Any = fn

    module_name = fn_to_inspect.__module__

    if isclass(fn_to_inspect):
        fn_to_inspect = fn_to_inspect.__init__

    # detect objects that are not functions and that have a `__call__` method
    if callable(fn_to_inspect) and ismethod(fn_to_inspect.__call__):
        fn_to_inspect = fn_to_inspect.__call__

    # inspect the underlying function for methods
    if hasattr(fn_to_inspect, "__func__"):
        fn_to_inspect = fn_to_inspect.__func__

    # Order important. If a litestar name has been overridden in the function module, we want
    # to use that instead of the litestar one.
    namespace = {
        **_GLOBAL_NAMES,
        **vars(typing),
        **vars(sys.modules[module_name]),
        **(namespace or {}),
    }
    hints = get_type_hints(fn_to_inspect, globalns=namespace, include_extras=True)

    if sys.version_info < (3, 11):
        # see https://github.com/litestar-org/litestar/pull/2516
        defaults = _get_defaults(fn_to_inspect)
        hints = _unwrap_implicit_optional_hints(defaults, hints)

    return hints


@dataclass(frozen=True)
class ParsedSignature:
    """Parsed signature.

    This object is the primary source of handler/dependency signature information.

    The only post-processing that occurs is the conversion of any forward referenced type annotations.
    """

    __slots__ = ("parameters", "return_type", "original_signature")

    parameters: dict[str, FieldDefinition]
    """A mapping of parameter names to ParsedSignatureParameter instances."""
    return_type: FieldDefinition
    """The return annotation of the callable."""
    original_signature: Signature
    """The raw signature as returned by :func:`inspect.signature`"""

    def __deepcopy__(self, memo: dict[str, Any]) -> Self:
        return type(self)(
            parameters={k: deepcopy(v) for k, v in self.parameters.items()},
            return_type=deepcopy(self.return_type),
            original_signature=deepcopy(self.original_signature),
        )

    @classmethod
    def from_fn(cls, fn: AnyCallable, signature_namespace: dict[str, Any]) -> Self:
        """Parse a function signature.

        Args:
            fn: Any callable.
            signature_namespace: mapping of names to types for forward reference resolution

        Returns:
            ParsedSignature
        """
        signature = Signature.from_callable(fn)
        fn_type_hints = get_fn_type_hints(fn, namespace=signature_namespace)
        expanded_type_hints = expand_type_var_in_type_hint(fn_type_hints, signature_namespace)

        return cls.from_signature(signature, expanded_type_hints)

    @classmethod
    def from_signature(cls, signature: Signature, fn_type_hints: dict[str, type]) -> Self:
        """Parse an :class:`inspect.Signature` instance.

        Args:
            signature: An :class:`inspect.Signature` instance.
            fn_type_hints: mapping of types

        Returns:
            ParsedSignature
        """

        parameters = tuple(
            FieldDefinition.from_parameter(parameter=parameter, fn_type_hints=fn_type_hints)
            for name, parameter in signature.parameters.items()
            if name not in ("self", "cls")
        )

        return_type = FieldDefinition.from_annotation(fn_type_hints.get("return", Any))

        return cls(
            parameters={p.name: p for p in parameters},
            return_type=return_type if "return" in fn_type_hints else replace(return_type, annotation=Empty),
            original_signature=signature,
        )


def add_types_to_signature_namespace(
    signature_types: Sequence[Any], signature_namespace: dict[str, Any]
) -> dict[str, Any]:
    """Add types to ith signature namespace mapping.

    Types are added mapped to their `__name__` attribute.

    Args:
        signature_types: A list of types to add to the signature namespace.
        signature_namespace: The signature namespace to add types to.

    Raises:
        ImproperlyConfiguredException: If a type is already defined in the signature namespace.
        AttributeError: If a type does not have a `__name__` attribute.

    Returns:
        The updated signature namespace.
    """
    for typ in signature_types:
        if (name := typ.__name__) in signature_namespace:
            raise ImproperlyConfiguredException(f"Type '{name}' is already defined in the signature namespace")
        signature_namespace[name] = typ
    return signature_namespace
