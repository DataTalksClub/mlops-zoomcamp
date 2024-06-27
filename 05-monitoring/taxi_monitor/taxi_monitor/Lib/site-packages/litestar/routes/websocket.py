from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar.enums import ScopeType
from litestar.exceptions import ImproperlyConfiguredException
from litestar.routes.base import BaseRoute

if TYPE_CHECKING:
    from litestar._kwargs import KwargsModel
    from litestar._kwargs.cleanup import DependencyCleanupGroup
    from litestar.connection import WebSocket
    from litestar.handlers.websocket_handlers import WebsocketRouteHandler
    from litestar.types import Receive, Send, WebSocketScope


class WebSocketRoute(BaseRoute):
    """A websocket route, handling a single ``WebsocketRouteHandler``"""

    __slots__ = (
        "route_handler",
        "handler_parameter_model",
    )

    def __init__(
        self,
        *,
        path: str,
        route_handler: WebsocketRouteHandler,
    ) -> None:
        """Initialize the route.

        Args:
            path: The path for the route.
            route_handler: An instance of :class:`~.handlers.WebsocketRouteHandler`.
        """
        self.route_handler = route_handler
        self.handler_parameter_model: KwargsModel | None = None

        super().__init__(
            path=path,
            scope_type=ScopeType.WEBSOCKET,
            handler_names=[route_handler.handler_name],
        )

    async def handle(self, scope: WebSocketScope, receive: Receive, send: Send) -> None:  # type: ignore[override]
        """ASGI app that creates a WebSocket from the passed in args, and then awaits the handler function.

        Args:
            scope: The ASGI connection scope.
            receive: The ASGI receive function.
            send: The ASGI send function.

        Returns:
            None
        """

        if not self.handler_parameter_model:  # pragma: no cover
            raise ImproperlyConfiguredException("handler parameter model not defined")

        websocket: WebSocket[Any, Any, Any] = self.route_handler.resolve_websocket_class()(
            scope=scope, receive=receive, send=send
        )

        if self.route_handler.resolve_guards():
            await self.route_handler.authorize_connection(connection=websocket)

        parsed_kwargs: dict[str, Any] = {}
        cleanup_group: DependencyCleanupGroup | None = None

        if self.handler_parameter_model.has_kwargs and self.route_handler.signature_model:
            parsed_kwargs = self.handler_parameter_model.to_kwargs(connection=websocket)

            if self.handler_parameter_model.dependency_batches:
                cleanup_group = await self.handler_parameter_model.resolve_dependencies(websocket, parsed_kwargs)

            parsed_kwargs = self.route_handler.signature_model.parse_values_from_connection_kwargs(
                connection=websocket, **parsed_kwargs
            )

        if cleanup_group:
            async with cleanup_group:
                await self.route_handler.fn(**parsed_kwargs)
            await cleanup_group.cleanup()
        else:
            await self.route_handler.fn(**parsed_kwargs)
