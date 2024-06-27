from __future__ import annotations

import pdb  # noqa: T100
from inspect import getmro
from sys import exc_info
from traceback import format_exception
from typing import TYPE_CHECKING, Any, Type, cast

from litestar.enums import ScopeType
from litestar.exceptions import HTTPException, LitestarException, WebSocketException
from litestar.exceptions.responses import create_exception_response
from litestar.exceptions.responses._debug_response import (
    create_debug_response,
)
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR
from litestar.utils.deprecation import warn_deprecation
from litestar.utils.empty import value_or_raise
from litestar.utils.scope.state import ScopeState

if TYPE_CHECKING:
    from starlette.exceptions import HTTPException as StarletteHTTPException

    from litestar import Response
    from litestar.app import Litestar
    from litestar.connection import Request
    from litestar.handlers import BaseRouteHandler
    from litestar.logging import BaseLoggingConfig
    from litestar.types import (
        ASGIApp,
        ExceptionHandler,
        ExceptionHandlersMap,
        Logger,
        Message,
        Receive,
        Scope,
        Send,
    )
    from litestar.types.asgi_types import WebSocketCloseEvent

__all__ = ("ExceptionHandlerMiddleware",)


def get_exception_handler(exception_handlers: ExceptionHandlersMap, exc: Exception) -> ExceptionHandler | None:
    """Given a dictionary that maps exceptions and status codes to handler functions, and an exception, returns the
    appropriate handler if existing.

    Status codes are given preference over exception type.

    If no status code match exists, each class in the MRO of the exception type is checked and
    the first matching handler is returned.

    Finally, if a ``500`` handler is registered, it will be returned for any exception that isn't a
    subclass of :class:`HTTPException <litestar.exceptions.HTTPException>`.

    Args:
        exception_handlers: Mapping of status codes and exception types to handlers.
        exc: Exception Instance to be resolved to a handler.

    Returns:
        Optional exception handler callable.
    """
    if not exception_handlers:
        return None

    default_handler: ExceptionHandler | None = None
    if isinstance(exc, HTTPException):
        if exception_handler := exception_handlers.get(exc.status_code):
            return exception_handler
    else:
        default_handler = exception_handlers.get(HTTP_500_INTERNAL_SERVER_ERROR)

    return next(
        (exception_handlers[cast("Type[Exception]", cls)] for cls in getmro(type(exc)) if cls in exception_handlers),
        default_handler,
    )


def _starlette_exception_handler(request: Request[Any, Any, Any], exc: StarletteHTTPException) -> Response:
    return create_exception_response(
        request=request,
        exc=HTTPException(
            detail=exc.detail,
            status_code=exc.status_code,
            headers=exc.headers,
        ),
    )


class ExceptionHandlerMiddleware:
    """Middleware used to wrap an ASGIApp inside a try catch block and handle any exceptions raised.

    This used in multiple layers of Litestar.
    """

    def __init__(
        self, app: ASGIApp, debug: bool | None, exception_handlers: ExceptionHandlersMap | None = None
    ) -> None:
        """Initialize ``ExceptionHandlerMiddleware``.

        Args:
            app: The ``next`` ASGI app to call.
            debug: Whether ``debug`` mode is enabled. Deprecated. Debug mode will be inferred from the request scope
            exception_handlers: A dictionary mapping status codes and/or exception types to handler functions.

        .. deprecated:: 2.0.0
            The ``debug`` parameter is deprecated. It will be inferred from the request scope

        .. deprecated:: 2.9.0
            The ``exception_handlers`` parameter is deprecated. It will be inferred from the application or the
            route handler.
        """
        self.app = app
        self.exception_handlers = exception_handlers
        self.debug = debug

        if debug is not None:
            warn_deprecation(
                "2.0.0",
                deprecated_name="debug",
                kind="parameter",
                info="Debug mode will be inferred from the request scope",
                removal_in="3.0.0",
            )

        if exception_handlers is not None:
            warn_deprecation(
                "2.9.0",
                deprecated_name="exception_handlers",
                kind="parameter",
                info="It will be inferred from the application or the route handler",
                removal_in="3.0.0",
            )

        self._get_debug = self._get_debug_scope if debug is None else lambda *a: debug

    @staticmethod
    def _get_debug_scope(scope: Scope) -> bool:
        return scope["app"].debug

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI-callable.

        Args:
            scope: The ASGI connection scope.
            receive: The ASGI receive function.
            send: The ASGI send function.

        Returns:
            None
        """
        scope_state = ScopeState.from_scope(scope)

        async def capture_response_started(event: Message) -> None:
            if event["type"] == "http.response.start":
                scope_state.response_started = True
            await send(event)

        try:
            await self.app(scope, receive, capture_response_started)
        except Exception as e:
            if scope_state.response_started:
                raise LitestarException("Exception caught after response started") from e

            litestar_app = scope["app"]

            if litestar_app.logging_config and (logger := litestar_app.logger):
                self.handle_exception_logging(logger=logger, logging_config=litestar_app.logging_config, scope=scope)

            for hook in litestar_app.after_exception:
                await hook(e, scope)

            if litestar_app.pdb_on_exception:
                pdb.post_mortem()

            if scope["type"] == ScopeType.HTTP:
                await self.handle_request_exception(
                    litestar_app=litestar_app, scope=scope, receive=receive, send=send, exc=e
                )
            else:
                await self.handle_websocket_exception(send=send, exc=e)

    async def handle_request_exception(
        self, litestar_app: Litestar, scope: Scope, receive: Receive, send: Send, exc: Exception
    ) -> None:
        """Handle exception raised inside 'http' scope routes.

        Args:
            litestar_app: The litestar app instance.
            scope: The ASGI connection scope.
            receive: The ASGI receive function.
            send: The ASGI send function.
            exc: The caught exception.

        Returns:
            None.
        """

        exception_handlers = (
            value_or_raise(ScopeState.from_scope(scope).exception_handlers)
            if self.exception_handlers is None
            else self.exception_handlers
        )
        exception_handler = get_exception_handler(exception_handlers, exc) or self.default_http_exception_handler
        request: Request[Any, Any, Any] = litestar_app.request_class(scope=scope, receive=receive, send=send)
        response = exception_handler(request, exc)
        route_handler: BaseRouteHandler | None = scope.get("route_handler")
        type_encoders = route_handler.resolve_type_encoders() if route_handler else litestar_app.type_encoders
        await response.to_asgi_response(app=None, request=request, type_encoders=type_encoders)(
            scope=scope, receive=receive, send=send
        )

    @staticmethod
    async def handle_websocket_exception(send: Send, exc: Exception) -> None:
        """Handle exception raised inside 'websocket' scope routes.

        Args:
            send: The ASGI send function.
            exc: The caught exception.

        Returns:
            None.
        """
        code = 4000 + HTTP_500_INTERNAL_SERVER_ERROR
        reason = "Internal Server Error"
        if isinstance(exc, WebSocketException):
            code = exc.code
            reason = exc.detail
        elif isinstance(exc, LitestarException):
            reason = exc.detail

        event: WebSocketCloseEvent = {"type": "websocket.close", "code": code, "reason": reason}
        await send(event)

    def default_http_exception_handler(self, request: Request, exc: Exception) -> Response[Any]:
        """Handle an HTTP exception by returning the appropriate response.

        Args:
            request: An HTTP Request instance.
            exc: The caught exception.

        Returns:
            An HTTP response.
        """
        status_code = exc.status_code if isinstance(exc, HTTPException) else HTTP_500_INTERNAL_SERVER_ERROR
        if status_code == HTTP_500_INTERNAL_SERVER_ERROR and self._get_debug_scope(request.scope):
            return create_debug_response(request=request, exc=exc)
        return create_exception_response(request=request, exc=exc)

    def handle_exception_logging(self, logger: Logger, logging_config: BaseLoggingConfig, scope: Scope) -> None:
        """Handle logging - if the litestar app has a logging config in place.

        Args:
            logger: A logger instance.
            logging_config: Logging Config instance.
            scope: The ASGI connection scope.

        Returns:
            None
        """
        if (
            logging_config.log_exceptions == "always"
            or (logging_config.log_exceptions == "debug" and self._get_debug_scope(scope))
        ) and logging_config.exception_logging_handler:
            logging_config.exception_logging_handler(logger, scope, format_exception(*exc_info()))
