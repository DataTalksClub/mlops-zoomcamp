from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, Sequence

from litestar.exceptions import NotAuthorizedException
from litestar.middleware.authentication import (
    AbstractAuthenticationMiddleware,
    AuthenticationResult,
)
from litestar.security.jwt.token import Token

__all__ = ("JWTAuthenticationMiddleware", "JWTCookieAuthenticationMiddleware")


if TYPE_CHECKING:
    from typing import Any

    from litestar.connection import ASGIConnection
    from litestar.types import ASGIApp, Method, Scopes


class JWTAuthenticationMiddleware(AbstractAuthenticationMiddleware):
    """JWT Authentication middleware.

    This class provides JWT authentication functionalities.
    """

    __slots__ = (
        "algorithm",
        "auth_header",
        "retrieve_user_handler",
        "token_secret",
    )

    def __init__(
        self,
        algorithm: str,
        app: ASGIApp,
        auth_header: str,
        exclude: str | list[str] | None,
        exclude_http_methods: Sequence[Method] | None,
        exclude_opt_key: str,
        retrieve_user_handler: Callable[[Token, ASGIConnection[Any, Any, Any, Any]], Awaitable[Any]],
        scopes: Scopes,
        token_secret: str,
    ) -> None:
        """Check incoming requests for an encoded token in the auth header specified, and if present retrieve the user
        from persistence using the provided function.

        Args:
            algorithm: JWT hashing algorithm to use.
            app: An ASGIApp, this value is the next ASGI handler to call in the middleware stack.
            auth_header: Request header key from which to retrieve the token. E.g. ``Authorization`` or ``X-Api-Key``.
            exclude: A pattern or list of patterns to skip.
            exclude_opt_key: An identifier to use on routes to disable authentication for a particular route.
            exclude_http_methods: A sequence of http methods that do not require authentication.
            retrieve_user_handler: A function that receives a :class:`Token <.security.jwt.Token>` and returns a user,
                which can be any arbitrary value.
            scopes: ASGI scopes processed by the authentication middleware.
            token_secret: Secret for decoding the JWT token. This value should be equivalent to the secret used to
                encode it.
        """
        super().__init__(
            app=app,
            exclude=exclude,
            exclude_from_auth_key=exclude_opt_key,
            exclude_http_methods=exclude_http_methods,
            scopes=scopes,
        )
        self.algorithm = algorithm
        self.auth_header = auth_header
        self.retrieve_user_handler = retrieve_user_handler
        self.token_secret = token_secret

    async def authenticate_request(self, connection: ASGIConnection[Any, Any, Any, Any]) -> AuthenticationResult:
        """Given an HTTP Connection, parse the JWT api key stored in the header and retrieve the user correlating to the
        token from the DB.

        Args:
            connection: An Litestar HTTPConnection instance.

        Returns:
            AuthenticationResult

        Raises:
            NotAuthorizedException: If token is invalid or user is not found.
        """
        auth_header = connection.headers.get(self.auth_header)
        if not auth_header:
            raise NotAuthorizedException("No JWT token found in request header")
        encoded_token = auth_header.partition(" ")[-1]
        return await self.authenticate_token(encoded_token=encoded_token, connection=connection)

    async def authenticate_token(
        self, encoded_token: str, connection: ASGIConnection[Any, Any, Any, Any]
    ) -> AuthenticationResult:
        """Given an encoded JWT token, parse, validate and look up sub within token.

        Args:
            encoded_token: Encoded JWT token.
            connection: An ASGI connection instance.

        Raises:
            NotAuthorizedException: If token is invalid or user is not found.

        Returns:
            AuthenticationResult
        """
        token = Token.decode(
            encoded_token=encoded_token,
            secret=self.token_secret,
            algorithm=self.algorithm,
        )

        user = await self.retrieve_user_handler(token, connection)

        if not user:
            raise NotAuthorizedException()

        return AuthenticationResult(user=user, auth=token)


class JWTCookieAuthenticationMiddleware(JWTAuthenticationMiddleware):
    """Cookie based JWT authentication middleware."""

    __slots__ = ("auth_cookie_key",)

    def __init__(
        self,
        algorithm: str,
        app: ASGIApp,
        auth_cookie_key: str,
        auth_header: str,
        exclude: str | list[str] | None,
        exclude_opt_key: str,
        exclude_http_methods: Sequence[Method] | None,
        retrieve_user_handler: Callable[[Token, ASGIConnection[Any, Any, Any, Any]], Awaitable[Any]],
        scopes: Scopes,
        token_secret: str,
    ) -> None:
        """Check incoming requests for an encoded token in the auth header or cookie name specified, and if present
        retrieves the user from persistence using the provided function.

        Args:
            algorithm: JWT hashing algorithm to use.
            app: An ASGIApp, this value is the next ASGI handler to call in the middleware stack.
            auth_cookie_key: Cookie name from which to retrieve the token. E.g. ``token`` or ``accessToken``.
            auth_header: Request header key from which to retrieve the token. E.g. ``Authorization`` or ``X-Api-Key``.
            exclude: A pattern or list of patterns to skip.
            exclude_opt_key: An identifier to use on routes to disable authentication for a particular route.
            exclude_http_methods: A sequence of http methods that do not require authentication.
            retrieve_user_handler: A function that receives a :class:`Token <.security.jwt.Token>` and returns a user,
                which can be any arbitrary value.
            scopes: ASGI scopes processed by the authentication middleware.
            token_secret: Secret for decoding the JWT token. This value should be equivalent to the secret used to
                encode it.
        """
        super().__init__(
            algorithm=algorithm,
            app=app,
            auth_header=auth_header,
            exclude=exclude,
            exclude_http_methods=exclude_http_methods,
            exclude_opt_key=exclude_opt_key,
            retrieve_user_handler=retrieve_user_handler,
            scopes=scopes,
            token_secret=token_secret,
        )
        self.auth_cookie_key = auth_cookie_key

    async def authenticate_request(self, connection: ASGIConnection[Any, Any, Any, Any]) -> AuthenticationResult:
        """Given an HTTP Connection, parse the JWT api key stored in the header and retrieve the user correlating to the
        token from the DB.

        Args:
            connection: An Litestar HTTPConnection instance.

        Raises:
            NotAuthorizedException: If token is invalid or user is not found.

        Returns:
            AuthenticationResult
        """
        auth_header = connection.headers.get(self.auth_header) or connection.cookies.get(self.auth_cookie_key)
        if not auth_header:
            raise NotAuthorizedException("No JWT token found in request header or cookies")
        encoded_token = auth_header.partition(" ")[-1]
        return await self.authenticate_token(encoded_token=encoded_token, connection=connection)
