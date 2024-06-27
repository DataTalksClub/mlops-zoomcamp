from __future__ import annotations

import inspect
from functools import wraps
from typing import Any, Callable, Literal, TypeVar
from warnings import warn

from typing_extensions import ParamSpec

__all__ = ("deprecated", "warn_deprecation", "check_for_deprecated_parameters")


T = TypeVar("T")
P = ParamSpec("P")
DeprecatedKind = Literal["function", "method", "classmethod", "attribute", "property", "class", "parameter", "import"]


def warn_deprecation(
    version: str,
    deprecated_name: str,
    kind: DeprecatedKind,
    *,
    removal_in: str | None = None,
    alternative: str | None = None,
    info: str | None = None,
    pending: bool = False,
) -> None:
    """Warn about a call to a (soon to be) deprecated function.

    Args:
        version: Polyfactory version where the deprecation will occur.
        deprecated_name: Name of the deprecated function.
        removal_in: Polyfactory version where the deprecated function will be removed.
        alternative: Name of a function that should be used instead.
        info: Additional information.
        pending: Use ``PendingDeprecationWarning`` instead of ``DeprecationWarning``.
        kind: Type of the deprecated thing.
    """
    parts = []

    if kind == "import":
        access_type = "Import of"
    elif kind in {"function", "method"}:
        access_type = "Call to"
    else:
        access_type = "Use of"

    if pending:
        parts.append(f"{access_type} {kind} awaiting deprecation {deprecated_name!r}")
    else:
        parts.append(f"{access_type} deprecated {kind} {deprecated_name!r}")

    parts.extend(
        (
            f"Deprecated in polyfactory {version}",
            f"This {kind} will be removed in {removal_in or 'the next major version'}",
        )
    )
    if alternative:
        parts.append(f"Use {alternative!r} instead")

    if info:
        parts.append(info)

    text = ". ".join(parts)
    warning_class = PendingDeprecationWarning if pending else DeprecationWarning

    warn(text, warning_class, stacklevel=2)


def deprecated(
    version: str,
    *,
    removal_in: str | None = None,
    alternative: str | None = None,
    info: str | None = None,
    pending: bool = False,
    kind: Literal["function", "method", "classmethod", "property"] | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Create a decorator wrapping a function, method or property with a warning call about a (pending) deprecation.

    Args:
        version: Polyfactory version where the deprecation will occur.
        removal_in: Polyfactory version where the deprecated function will be removed.
        alternative: Name of a function that should be used instead.
        info: Additional information.
        pending: Use ``PendingDeprecationWarning`` instead of ``DeprecationWarning``.
        kind: Type of the deprecated callable. If ``None``, will use ``inspect`` to figure
            out if it's a function or method.

    Returns:
        A decorator wrapping the function call with a warning
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
            warn_deprecation(
                version=version,
                deprecated_name=func.__name__,
                info=info,
                alternative=alternative,
                pending=pending,
                removal_in=removal_in,
                kind=kind or ("method" if inspect.ismethod(func) else "function"),
            )
            return func(*args, **kwargs)

        return wrapped

    return decorator


def check_for_deprecated_parameters(
    version: str,
    *,
    parameters: tuple[tuple[str, Any], ...],
    default_value: Any = None,
    removal_in: str | None = None,
    alternative: str | None = None,
    info: str | None = None,
    pending: bool = False,
) -> None:
    """Warn about a call to a (soon to be) deprecated argument to a function.

    Args:
        version: Polyfactory version where the deprecation will occur.
        parameters: Parameters to trigger warning if used.
        default_value: Default value for parameter to detect if supplied or not.
        removal_in: Polyfactory version where the deprecated function will be removed.
        alternative: Name of a function that should be used instead.
        info: Additional information.
        pending: Use ``PendingDeprecationWarning`` instead of ``DeprecationWarning``.
        kind: Type of the deprecated callable. If ``None``, will use ``inspect`` to figure
            out if it's a function or method.
    """
    for parameter_name, value in parameters:
        if value == default_value:
            continue

        warn_deprecation(
            version=version,
            deprecated_name=parameter_name,
            info=info,
            alternative=alternative,
            pending=pending,
            removal_in=removal_in,
            kind="parameter",
        )
