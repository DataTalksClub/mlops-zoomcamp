from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar.connection import ASGIConnection
from litestar.enums import ScopeType
from litestar.routes.base import BaseRoute

if TYPE_CHECKING:
    from litestar.handlers.asgi_handlers import ASGIRouteHandler
    from litestar.types import Receive, Scope, Send


class ASGIRoute(BaseRoute):
    """An ASGI route, handling a single ``ASGIRouteHandler``"""

    __slots__ = ("route_handler",)

    def __init__(
        self,
        *,
        path: str,
        route_handler: ASGIRouteHandler,
    ) -> None:
        """Initialize the route.

        Args:
            path: The path for the route.
            route_handler: An instance of :class:`~.handlers.ASGIRouteHandler`.
        """
        self.route_handler = route_handler
        super().__init__(
            path=path,
            scope_type=ScopeType.ASGI,
            handler_names=[route_handler.handler_name],
        )

    async def handle(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI app that authorizes the connection and then awaits the handler function.

        Args:
            scope: The ASGI connection scope.
            receive: The ASGI receive function.
            send: The ASGI send function.

        Returns:
            None
        """

        if self.route_handler.resolve_guards():
            connection = ASGIConnection["ASGIRouteHandler", Any, Any, Any](scope=scope, receive=receive)
            await self.route_handler.authorize_connection(connection=connection)

        await self.route_handler.fn(scope=scope, receive=receive, send=send)
