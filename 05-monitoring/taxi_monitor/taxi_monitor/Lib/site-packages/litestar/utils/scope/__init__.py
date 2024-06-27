from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar.serialization import get_serializer
from litestar.utils.deprecation import warn_deprecation
from litestar.utils.scope.state import delete_litestar_scope_state as _delete_litestar_scope_state
from litestar.utils.scope.state import get_litestar_scope_state as _get_litestar_scope_state
from litestar.utils.scope.state import set_litestar_scope_state as _set_litestar_scope_state

if TYPE_CHECKING:
    from litestar.types import Scope, Serializer

__all__ = ("get_serializer_from_scope",)


def get_serializer_from_scope(scope: Scope) -> Serializer:
    """Return a serializer given a scope object.

    Args:
        scope: The ASGI connection scope.

    Returns:
        A serializer function
    """
    route_handler = scope["route_handler"]
    app = scope["app"]

    if hasattr(route_handler, "resolve_type_encoders"):
        type_encoders = route_handler.resolve_type_encoders()
    else:
        type_encoders = app.type_encoders or {}

    if response_class := (
        route_handler.resolve_response_class()  # pyright: ignore
        if hasattr(route_handler, "resolve_response_class")
        else app.response_class
    ):
        type_encoders = {**type_encoders, **(response_class.type_encoders or {})}

    return get_serializer(type_encoders)


_deprecated_names = {
    "get_litestar_scope_state": _get_litestar_scope_state,
    "set_litestar_scope_state": _set_litestar_scope_state,
    "delete_litestar_scope_state": _delete_litestar_scope_state,
}


def __getattr__(name: str) -> Any:
    if name in _deprecated_names:
        warn_deprecation(
            deprecated_name=f"litestar.utils.scope.{name}",
            version="2.4",
            kind="import",
            removal_in="3.0",
            info=f"'litestar.utils.scope.{name}' is deprecated. The Litestar scope state is private and should not be "
            f"used. Plugin authors should maintain their own scope state namespace.",
        )
        return globals()["_deprecated_names"][name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")  # pragma: no cover
