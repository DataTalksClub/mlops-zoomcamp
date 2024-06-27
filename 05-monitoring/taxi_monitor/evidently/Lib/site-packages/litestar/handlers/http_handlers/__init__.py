from __future__ import annotations

from .base import HTTPRouteHandler, route
from .decorators import delete, get, head, patch, post, put

__all__ = (
    "HTTPRouteHandler",
    "delete",
    "get",
    "head",
    "patch",
    "post",
    "put",
    "route",
)
