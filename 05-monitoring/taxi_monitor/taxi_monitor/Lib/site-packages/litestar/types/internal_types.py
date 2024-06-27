from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Literal, NamedTuple

from litestar.utils.deprecation import warn_deprecation

__all__ = (
    "ControllerRouterHandler",
    "PathParameterDefinition",
    "PathParameterDefinition",
    "ReservedKwargs",
    "RouteHandlerMapItem",
    "RouteHandlerType",
)

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    from litestar.app import Litestar
    from litestar.controller import Controller
    from litestar.handlers.asgi_handlers import ASGIRouteHandler
    from litestar.handlers.http_handlers import HTTPRouteHandler
    from litestar.handlers.websocket_handlers import WebsocketRouteHandler
    from litestar.router import Router
    from litestar.template import TemplateConfig
    from litestar.template.config import EngineType
    from litestar.types import Method

ReservedKwargs: TypeAlias = Literal["request", "socket", "headers", "query", "cookies", "state", "data"]
RouteHandlerType: TypeAlias = "HTTPRouteHandler | WebsocketRouteHandler | ASGIRouteHandler"
ControllerRouterHandler: TypeAlias = "type[Controller] | RouteHandlerType | Router | Callable[..., Any]"
RouteHandlerMapItem: TypeAlias = 'dict[Method | Literal["websocket", "asgi"], RouteHandlerType]'
TemplateConfigType: TypeAlias = "TemplateConfig[EngineType]"

# deprecated
_LitestarType: TypeAlias = "Litestar"


class PathParameterDefinition(NamedTuple):
    """Path parameter tuple."""

    name: str
    full: str
    type: type
    parser: Callable[[str], Any] | None


def __getattr__(name: str) -> Any:
    if name == "LitestarType":
        warn_deprecation(
            "2.2.1",
            "LitestarType",
            "import",
            removal_in="3.0.0",
            alternative="Litestar",
        )
        return _LitestarType
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
