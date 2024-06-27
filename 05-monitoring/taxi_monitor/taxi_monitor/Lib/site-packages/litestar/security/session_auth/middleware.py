from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Sequence

from litestar.exceptions import NotAuthorizedException
from litestar.middleware._internal.exceptions import ExceptionHandlerMiddleware
from litestar.middleware.authentication import (
    AbstractAuthenticationMiddleware,
    AuthenticationResult,
)
from litestar.types import Empty, Method, Scopes

__all__ = ("MiddlewareWrapper", "SessionAuthMiddleware")

if TYPE_CHECKING:
    from litestar.connection import ASGIConnection
    from litestar.security.session_auth.auth import SessionAuth
    from litestar.types import ASGIApp, Receive, Scope, Send


class MiddlewareWrapper:
    """Wrapper class that serves as the middleware entry point."""

    def __init__(self, app: ASGIApp, config: SessionAuth[Any, Any]) -> None:
        """Wrap the SessionAuthMiddleware inside ExceptionHandlerMiddleware, and it wraps this inside SessionMiddleware.
        This allows the auth middleware to raise exceptions and still have the response handled, while having the
        session cleared.

        Args:
            app: An ASGIApp, this value is the next ASGI handler to call in the middleware stack.
            config: An instance of SessionAuth.
        """
        self.app = app
        self.config = config
        self.has_wrapped_middleware = False

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Handle creating a middleware stack and calling it.

        Args:
            scope: The ASGI connection scope.
            receive: The ASGI receive function.
            send: The ASGI send function.

        Returns:
            None
        """
        if not self.has_wrapped_middleware:
            auth_middleware = self.config.authentication_middleware_class(
                app=self.app,
                exclude=self.config.exclude,
                exclude_http_methods=self.config.exclude_http_methods,
                exclude_opt_key=self.config.exclude_opt_key,
                scopes=self.config.scopes,
                retrieve_user_handler=self.config.retrieve_user_handler,  # type: ignore[arg-type]
            )
            exception_middleware = ExceptionHandlerMiddleware(app=auth_middleware, debug=None)
            self.app = self.config.session_backend_config.middleware.middleware(
                app=exception_middleware,
                backend=self.config.session_backend,
            )
            self.has_wrapped_middleware = True
        await self.app(scope, receive, send)


class SessionAuthMiddleware(AbstractAuthenticationMiddleware):
    """Session Authentication Middleware."""

    def __init__(
        self,
        app: ASGIApp,
        exclude: str | list[str] | None,
        exclude_http_methods: Sequence[Method] | None,
        exclude_opt_key: str,
        retrieve_user_handler: Callable[[dict[str, Any], ASGIConnection[Any, Any, Any, Any]], Awaitable[Any]],
        scopes: Scopes | None,
    ) -> None:
        """Session based authentication middleware.

        Args:
            app: An ASGIApp, this value is the next ASGI handler to call in the middleware stack.
            exclude: A pattern or list of patterns to skip in the authentication middleware.
            exclude_http_methods: A sequence of http methods that do not require authentication.
            exclude_opt_key: An identifier to use on routes to disable authentication and authorization checks for a particular route.
            scopes: ASGI scopes processed by the authentication middleware.
            retrieve_user_handler: Callable that receives the ``session`` value from the authentication middleware and returns a ``user`` value.
        """
        super().__init__(
            app=app,
            exclude=exclude,
            exclude_from_auth_key=exclude_opt_key,
            exclude_http_methods=exclude_http_methods,
            scopes=scopes,
        )
        self.retrieve_user_handler = retrieve_user_handler

    async def authenticate_request(self, connection: ASGIConnection[Any, Any, Any, Any]) -> AuthenticationResult:
        """Authenticate an incoming connection.

        Args:
            connection: An :class:`ASGIConnection <.connection.ASGIConnection>` instance.

        Raises:
            NotAuthorizedException: if session data is empty or user is not found.

        Returns:
            :class:`AuthenticationResult <.middleware.authentication.AuthenticationResult>`
        """
        if not connection.session or connection.scope["session"] is Empty:
            # the assignment of 'Empty' forces the session middleware to clear session data.
            connection.scope["session"] = Empty
            raise NotAuthorizedException("no session data found")

        user = await self.retrieve_user_handler(connection.session, connection)

        if not user:
            connection.scope["session"] = Empty
            raise NotAuthorizedException("no user correlating to session found")

        return AuthenticationResult(user=user, auth=connection.session)
