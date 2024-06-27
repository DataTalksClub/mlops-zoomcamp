from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Callable, Generic, Iterable, Literal, Sequence, TypeVar, cast

from litestar.datastructures import Cookie
from litestar.enums import MediaType
from litestar.middleware import DefineMiddleware
from litestar.openapi.spec import Components, OAuthFlow, OAuthFlows, SecurityRequirement, SecurityScheme
from litestar.security.base import AbstractSecurityConfig
from litestar.security.jwt.middleware import JWTAuthenticationMiddleware, JWTCookieAuthenticationMiddleware
from litestar.security.jwt.token import Token
from litestar.status_codes import HTTP_201_CREATED
from litestar.types import ControllerRouterHandler, Empty, Guard, Method, Scopes, SyncOrAsyncUnion, TypeEncodersMap

__all__ = ("BaseJWTAuth", "JWTAuth", "JWTCookieAuth", "OAuth2Login", "OAuth2PasswordBearerAuth")


if TYPE_CHECKING:
    from litestar import Response
    from litestar.connection import ASGIConnection
    from litestar.di import Provide


UserType = TypeVar("UserType")


class BaseJWTAuth(Generic[UserType], AbstractSecurityConfig[UserType, Token]):
    """Base class for JWT Auth backends"""

    token_secret: str
    """Key with which to generate the token hash.

    Notes:
        - This value should be kept as a secret and the standard practice is to inject it into the environment.
    """
    retrieve_user_handler: Callable[[Any, ASGIConnection], SyncOrAsyncUnion[Any | None]]
    """Callable that receives the ``auth`` value from the authentication middleware and returns a ``user`` value.

    Notes:
        - User and Auth can be any arbitrary values specified by the security backend.
        - The User and Auth values will be set by the middleware as ``scope["user"]`` and ``scope["auth"]`` respectively.
          Once provided, they can access via the ``connection.user`` and ``connection.auth`` properties.
        - The callable can be sync or async. If it is sync, it will be wrapped to support async.

    """
    algorithm: str
    """Algorithm to use for JWT hashing."""
    auth_header: str
    """Request header key from which to retrieve the token.

    E.g. ``Authorization`` or ``X-Api-Key``.
    """
    default_token_expiration: timedelta
    """The default value for token expiration."""
    openapi_security_scheme_name: str
    """The value to use for the OpenAPI security scheme and security requirements."""
    description: str
    """Description for the OpenAPI security scheme."""
    authentication_middleware_class: type[JWTAuthenticationMiddleware]  # pyright: ignore
    """The authentication middleware class to use.

    Must inherit from :class:`JWTAuthenticationMiddleware`
    """

    @property
    def openapi_components(self) -> Components:
        """Create OpenAPI documentation for the JWT auth schema used.

        Returns:
            An :class:`Components <litestar.openapi.spec.components.Components>` instance.
        """
        return Components(
            security_schemes={
                self.openapi_security_scheme_name: SecurityScheme(
                    type="http",
                    scheme="Bearer",
                    name=self.auth_header,
                    bearer_format="JWT",
                    description=self.description,
                )
            }
        )

    @property
    def security_requirement(self) -> SecurityRequirement:
        """Return OpenAPI 3.1.

        :data:`SecurityRequirement <.openapi.spec.SecurityRequirement>`

        Returns:
            An OpenAPI 3.1
            :data:`SecurityRequirement <.openapi.spec.SecurityRequirement>`
            dictionary.
        """
        return {self.openapi_security_scheme_name: []}

    @property
    def middleware(self) -> DefineMiddleware:
        """Create :class:`JWTAuthenticationMiddleware` wrapped in
        :class:`DefineMiddleware <.middleware.base.DefineMiddleware>`.

        Returns:
            An instance of :class:`DefineMiddleware <.middleware.base.DefineMiddleware>`.
        """
        return DefineMiddleware(
            self.authentication_middleware_class,
            algorithm=self.algorithm,
            auth_header=self.auth_header,
            exclude=self.exclude,
            exclude_opt_key=self.exclude_opt_key,
            exclude_http_methods=self.exclude_http_methods,
            retrieve_user_handler=self.retrieve_user_handler,
            scopes=self.scopes,
            token_secret=self.token_secret,
        )

    def login(
        self,
        identifier: str,
        *,
        response_body: Any = Empty,
        response_media_type: str | MediaType = MediaType.JSON,
        response_status_code: int = HTTP_201_CREATED,
        token_expiration: timedelta | None = None,
        token_issuer: str | None = None,
        token_audience: str | None = None,
        token_unique_jwt_id: str | None = None,
        token_extras: dict[str, Any] | None = None,
        send_token_as_response_body: bool = False,
    ) -> Response[Any]:
        """Create a response with a JWT header.

        Args:
            identifier: Unique identifier of the token subject. Usually this is a user ID or equivalent kind of value.
            response_body: An optional response body to send.
            response_media_type: An optional ``Content-Type``. Defaults to ``application/json``.
            response_status_code: An optional status code for the response. Defaults to ``201``.
            token_expiration: An optional timedelta for the token expiration.
            token_issuer: An optional value of the token ``iss`` field.
            token_audience: An optional value for the token ``aud`` field.
            token_unique_jwt_id: An optional value for the token ``jti`` field.
            token_extras: An optional dictionary to include in the token ``extras`` field.
            send_token_as_response_body: If ``True`` the response will be a dict including the token: ``{ "token": <token> }``
                will be returned as the response body. Note: if a response body is passed this setting will be ignored.

        Returns:
            A :class:`Response <.response.Response>` instance.
        """
        encoded_token = self.create_token(
            identifier=identifier,
            token_expiration=token_expiration,
            token_issuer=token_issuer,
            token_audience=token_audience,
            token_unique_jwt_id=token_unique_jwt_id,
            token_extras=token_extras,
        )

        if response_body is not Empty:
            body = response_body
        elif send_token_as_response_body:
            body = {"token": encoded_token}
        else:
            body = None

        return self.create_response(
            content=body,
            headers={self.auth_header: self.format_auth_header(encoded_token)},
            media_type=response_media_type,
            status_code=response_status_code,
        )

    def create_token(
        self,
        identifier: str,
        token_expiration: timedelta | None = None,
        token_issuer: str | None = None,
        token_audience: str | None = None,
        token_unique_jwt_id: str | None = None,
        token_extras: dict | None = None,
    ) -> str:
        """Create a Token instance from the passed in parameters, persists and returns it.

        Args:
            identifier: Unique identifier of the token subject. Usually this is a user ID or equivalent kind of value.
            token_expiration: An optional timedelta for the token expiration.
            token_issuer: An optional value of the token ``iss`` field.
            token_audience: An optional value for the token ``aud`` field.
            token_unique_jwt_id: An optional value for the token ``jti`` field.
            token_extras: An optional dictionary to include in the token ``extras`` field.

        Returns:
            The created token.
        """
        token = Token(
            sub=identifier,
            exp=(datetime.now(timezone.utc) + (token_expiration or self.default_token_expiration)),
            iss=token_issuer,
            aud=token_audience,
            jti=token_unique_jwt_id,
            extras=token_extras or {},
        )
        return token.encode(secret=self.token_secret, algorithm=self.algorithm)

    def format_auth_header(self, encoded_token: str) -> str:
        """Format a token according to the specified OpenAPI scheme.

        Args:
            encoded_token: An encoded JWT token

        Returns:
            The encoded token formatted for the HTTP headers
        """
        security = self.openapi_components.security_schemes.get(self.openapi_security_scheme_name, None)  # type: ignore[union-attr]
        return f"{security.scheme} {encoded_token}" if isinstance(security, SecurityScheme) else encoded_token


@dataclass
class JWTAuth(Generic[UserType], BaseJWTAuth[UserType]):
    """JWT Authentication Configuration.

    This class is the main entry point to the library, and it includes methods to create the middleware, provide login
    functionality, and create OpenAPI documentation.
    """

    token_secret: str
    """Key with which to generate the token hash.

    Notes:
        - This value should be kept as a secret and the standard practice is to inject it into the environment.
    """
    retrieve_user_handler: Callable[[Any, ASGIConnection], SyncOrAsyncUnion[Any | None]]
    """Callable that receives the ``auth`` value from the authentication middleware and returns a ``user`` value.

    Notes:
        - User and Auth can be any arbitrary values specified by the security backend.
        - The User and Auth values will be set by the middleware as ``scope["user"]`` and ``scope["auth"]`` respectively.
          Once provided, they can access via the ``connection.user`` and ``connection.auth`` properties.
        - The callable can be sync or async. If it is sync, it will be wrapped to support async.

    """
    guards: Iterable[Guard] | None = field(default=None)
    """An iterable of guards to call for requests, providing authorization functionalities."""
    exclude: str | list[str] | None = field(default=None)
    """A pattern or list of patterns to skip in the authentication middleware."""
    exclude_opt_key: str = field(default="exclude_from_auth")
    """An identifier to use on routes to disable authentication and authorization checks for a particular route."""
    exclude_http_methods: Sequence[Method] | None = field(
        default_factory=lambda: cast("Sequence[Method]", ["OPTIONS", "HEAD"])
    )
    """A sequence of http methods that do not require authentication. Defaults to ['OPTIONS', 'HEAD']"""
    scopes: Scopes | None = field(default=None)
    """ASGI scopes processed by the authentication middleware, if ``None``, both ``http`` and ``websocket`` will be
    processed."""
    route_handlers: Iterable[ControllerRouterHandler] | None = field(default=None)
    """An optional iterable of route handlers to register."""
    dependencies: dict[str, Provide] | None = field(default=None)
    """An optional dictionary of dependency providers."""

    type_encoders: TypeEncodersMap | None = field(default=None)
    """A mapping of types to callables that transform them into types supported for serialization."""

    algorithm: str = field(default="HS256")
    """Algorithm to use for JWT hashing."""
    auth_header: str = field(default="Authorization")
    """Request header key from which to retrieve the token.

    E.g. ``Authorization`` or ``X-Api-Key``.
    """
    default_token_expiration: timedelta = field(default_factory=lambda: timedelta(days=1))
    """The default value for token expiration."""
    openapi_security_scheme_name: str = field(default="BearerToken")
    """The value to use for the OpenAPI security scheme and security requirements."""
    description: str = field(default="JWT api-key authentication and authorization.")
    """Description for the OpenAPI security scheme."""
    authentication_middleware_class: type[JWTAuthenticationMiddleware] = field(default=JWTAuthenticationMiddleware)
    """The authentication middleware class to use.

    Must inherit from :class:`JWTAuthenticationMiddleware`
    """


@dataclass
class JWTCookieAuth(Generic[UserType], BaseJWTAuth[UserType]):
    """JWT Cookie Authentication Configuration.

    This class is an alternate entry point to the library, and it includes all the functionality of the :class:`JWTAuth`
    class and adds support for passing JWT tokens ``HttpOnly`` cookies.
    """

    token_secret: str
    """Key with which to generate the token hash.

    Notes:
        - This value should be kept as a secret and the standard practice is to inject it into the environment.
    """
    retrieve_user_handler: Callable[[Any, ASGIConnection], SyncOrAsyncUnion[Any | None]]
    """Callable that receives the ``auth`` value from the authentication middleware and returns a ``user`` value.

    Notes:
        - User and Auth can be any arbitrary values specified by the security backend.
        - The User and Auth values will be set by the middleware as ``scope["user"]`` and ``scope["auth"]`` respectively.
          Once provided, they can access via the ``connection.user`` and ``connection.auth`` properties.
        - The callable can be sync or async. If it is sync, it will be wrapped to support async.

    """
    guards: Iterable[Guard] | None = field(default=None)
    """An iterable of guards to call for requests, providing authorization functionalities."""
    exclude: str | list[str] | None = field(default=None)
    """A pattern or list of patterns to skip in the authentication middleware."""
    exclude_opt_key: str = field(default="exclude_from_auth")
    """An identifier to use on routes to disable authentication and authorization checks for a particular route."""
    scopes: Scopes | None = field(default=None)
    """ASGI scopes processed by the authentication middleware, if ``None``, both ``http`` and ``websocket`` will be
    processed."""
    exclude_http_methods: Sequence[Method] | None = field(
        default_factory=lambda: cast("Sequence[Method]", ["OPTIONS", "HEAD"])
    )
    """A sequence of http methods that do not require authentication. Defaults to ['OPTIONS', 'HEAD']"""
    route_handlers: Iterable[ControllerRouterHandler] | None = field(default=None)
    """An optional iterable of route handlers to register."""
    dependencies: dict[str, Provide] | None = field(default=None)
    """An optional dictionary of dependency providers."""

    type_encoders: TypeEncodersMap | None = field(default=None)
    """A mapping of types to callables that transform them into types supported for serialization."""

    algorithm: str = field(default="HS256")
    """Algorithm to use for JWT hashing."""
    auth_header: str = field(default="Authorization")
    """Request header key from which to retrieve the token.

    E.g. ``Authorization`` or ``X-Api-Key``.
    """
    default_token_expiration: timedelta = field(default_factory=lambda: timedelta(days=1))
    """The default value for token expiration."""
    openapi_security_scheme_name: str = field(default="BearerToken")
    """The value to use for the OpenAPI security scheme and security requirements."""
    key: str = field(default="token")
    """Key for the cookie."""
    path: str = field(default="/")
    """Path fragment that must exist in the request url for the cookie to be valid.

    Defaults to ``/``.
    """
    domain: str | None = field(default=None)
    """Domain for which the cookie is valid."""
    secure: bool | None = field(default=None)
    """Https is required for the cookie."""
    samesite: Literal["lax", "strict", "none"] = field(default="lax")
    """Controls whether or not a cookie is sent with cross-site requests. Defaults to ``lax``. """
    description: str = field(default="JWT cookie-based authentication and authorization.")
    """Description for the OpenAPI security scheme."""
    authentication_middleware_class: type[JWTCookieAuthenticationMiddleware] = field(  # pyright: ignore
        default=JWTCookieAuthenticationMiddleware
    )
    """The authentication middleware class to use. Must inherit from :class:`JWTCookieAuthenticationMiddleware`
    """

    @property
    def openapi_components(self) -> Components:
        """Create OpenAPI documentation for the JWT Cookie auth scheme.

        Returns:
            A :class:`Components <litestar.openapi.spec.components.Components>` instance.
        """
        return Components(
            security_schemes={
                self.openapi_security_scheme_name: SecurityScheme(
                    type="http",
                    scheme="Bearer",
                    name=self.key,
                    security_scheme_in="cookie",
                    bearer_format="JWT",
                    description=self.description,
                )
            }
        )

    @property
    def middleware(self) -> DefineMiddleware:
        """Create :class:`JWTCookieAuthenticationMiddleware` wrapped in
            :class:`DefineMiddleware <.middleware.base.DefineMiddleware>`.

        Returns:
            An instance of :class:`DefineMiddleware <.middleware.base.DefineMiddleware>`.
        """
        return DefineMiddleware(
            self.authentication_middleware_class,
            algorithm=self.algorithm,
            auth_cookie_key=self.key,
            auth_header=self.auth_header,
            exclude=self.exclude,
            exclude_opt_key=self.exclude_opt_key,
            exclude_http_methods=self.exclude_http_methods,
            retrieve_user_handler=self.retrieve_user_handler,
            scopes=self.scopes,
            token_secret=self.token_secret,
        )

    def login(
        self,
        identifier: str,
        *,
        response_body: Any = Empty,
        response_media_type: str | MediaType = MediaType.JSON,
        response_status_code: int = HTTP_201_CREATED,
        token_expiration: timedelta | None = None,
        token_issuer: str | None = None,
        token_audience: str | None = None,
        token_unique_jwt_id: str | None = None,
        token_extras: dict[str, Any] | None = None,
        send_token_as_response_body: bool = False,
    ) -> Response[Any]:
        """Create a response with a JWT header.

        Args:
            identifier: Unique identifier of the token subject. Usually this is a user ID or equivalent kind of value.
            response_body: An optional response body to send.
            response_media_type: An optional 'Content-Type'. Defaults to 'application/json'.
            response_status_code: An optional status code for the response. Defaults to '201 Created'.
            token_expiration: An optional timedelta for the token expiration.
            token_issuer: An optional value of the token ``iss`` field.
            token_audience: An optional value for the token ``aud`` field.
            token_unique_jwt_id: An optional value for the token ``jti`` field.
            token_extras: An optional dictionary to include in the token ``extras`` field.
            send_token_as_response_body: If ``True`` the response will be a dict including the token: ``{ "token": <token> }``
                will be returned as the response body. Note: if a response body is passed this setting will be ignored.

        Returns:
            A :class:`Response <.response.Response>` instance.
        """

        encoded_token = self.create_token(
            identifier=identifier,
            token_expiration=token_expiration,
            token_issuer=token_issuer,
            token_audience=token_audience,
            token_unique_jwt_id=token_unique_jwt_id,
            token_extras=token_extras,
        )
        cookie = Cookie(
            key=self.key,
            path=self.path,
            httponly=True,
            value=self.format_auth_header(encoded_token),
            max_age=int((token_expiration or self.default_token_expiration).total_seconds()),
            secure=self.secure,
            samesite=self.samesite,
            domain=self.domain,
        )

        if response_body is not Empty:
            body = response_body
        elif send_token_as_response_body:
            body = {"token": encoded_token}
        else:
            body = None

        return self.create_response(
            content=body,
            headers={self.auth_header: self.format_auth_header(encoded_token)},
            cookies=[cookie],
            media_type=response_media_type,
            status_code=response_status_code,
        )


@dataclass
class OAuth2Login:
    """OAuth2 Login DTO"""

    access_token: str
    """Valid JWT access token"""
    token_type: str
    """Type of the OAuth token used"""
    refresh_token: str | None = field(default=None)
    """Optional valid refresh token JWT"""
    expires_in: int | None = field(default=None)
    """Expiration time of the token in seconds. """


@dataclass
class OAuth2PasswordBearerAuth(Generic[UserType], BaseJWTAuth[UserType]):
    """OAUTH2 Schema for Password Bearer Authentication.

    This class implements an OAUTH2 authentication flow entry point to the library, and it includes all the
    functionality of the :class:`JWTAuth` class and adds support for passing JWT tokens ``HttpOnly`` cookies.

    ``token_url`` is the only additional argument that is required, and it should point at your login route
    """

    token_secret: str
    """Key with which to generate the token hash.

    Notes:
        - This value should be kept as a secret and the standard practice is to inject it into the environment.
    """
    token_url: str
    """The URL for retrieving a new token."""
    retrieve_user_handler: Callable[[Any, ASGIConnection], SyncOrAsyncUnion[Any | None]]
    """Callable that receives the ``auth`` value from the authentication middleware and returns a ``user`` value.

    Notes:
        - User and Auth can be any arbitrary values specified by the security backend.
        - The User and Auth values will be set by the middleware as ``scope["user"]`` and ``scope["auth"]`` respectively.
          Once provided, they can access via the ``connection.user`` and ``connection.auth`` properties.
        - The callable can be sync or async. If it is sync, it will be wrapped to support async.

    """
    guards: Iterable[Guard] | None = field(default=None)
    """An iterable of guards to call for requests, providing authorization functionalities."""
    exclude: str | list[str] | None = field(default=None)
    """A pattern or list of patterns to skip in the authentication middleware."""
    exclude_opt_key: str = field(default="exclude_from_auth")
    """An identifier to use on routes to disable authentication and authorization checks for a particular route."""
    exclude_http_methods: Sequence[Method] | None = field(
        default_factory=lambda: cast("Sequence[Method]", ["OPTIONS", "HEAD"])
    )
    """A sequence of http methods that do not require authentication. Defaults to ['OPTIONS', 'HEAD']"""
    scopes: Scopes | None = field(default=None)
    """ASGI scopes processed by the authentication middleware, if ``None``, both ``http`` and ``websocket`` will be
    processed."""
    route_handlers: Iterable[ControllerRouterHandler] | None = field(default=None)
    """An optional iterable of route handlers to register."""
    dependencies: dict[str, Provide] | None = field(default=None)
    """An optional dictionary of dependency providers."""
    type_encoders: TypeEncodersMap | None = field(default=None)
    """A mapping of types to callables that transform them into types supported for serialization."""
    algorithm: str = field(default="HS256")
    """Algorithm to use for JWT hashing."""
    auth_header: str = field(default="Authorization")
    """Request header key from which to retrieve the token.

    E.g. ``Authorization`` or 'X-Api-Key'.
    """
    default_token_expiration: timedelta = field(default_factory=lambda: timedelta(days=1))
    """The default value for token expiration."""
    openapi_security_scheme_name: str = field(default="BearerToken")
    """The value to use for the OpenAPI security scheme and security requirements."""
    oauth_scopes: dict[str, str] | None = field(default=None)
    """Oauth Scopes available for the token."""
    key: str = field(default="token")
    """Key for the cookie."""
    path: str = field(default="/")
    """Path fragment that must exist in the request url for the cookie to be valid.

    Defaults to ``/``.
    """
    domain: str | None = field(default=None)
    """Domain for which the cookie is valid."""
    secure: bool | None = field(default=None)
    """Https is required for the cookie."""
    samesite: Literal["lax", "strict", "none"] = field(default="lax")
    """Controls whether or not a cookie is sent with cross-site requests. Defaults to ``lax``. """
    description: str = field(default="OAUTH2 password bearer authentication and authorization.")
    """Description for the OpenAPI security scheme."""
    authentication_middleware_class: type[JWTCookieAuthenticationMiddleware] = field(  # pyright: ignore
        default=JWTCookieAuthenticationMiddleware
    )
    """The authentication middleware class to use.

    Must inherit from :class:`JWTCookieAuthenticationMiddleware`
    """

    @property
    def middleware(self) -> DefineMiddleware:
        """Create ``JWTCookieAuthenticationMiddleware`` wrapped in
            :class:`DefineMiddleware <.middleware.base.DefineMiddleware>`.

        Returns:
            An instance of :class:`DefineMiddleware <.middleware.base.DefineMiddleware>`.
        """
        return DefineMiddleware(
            self.authentication_middleware_class,
            algorithm=self.algorithm,
            auth_cookie_key=self.key,
            auth_header=self.auth_header,
            exclude=self.exclude,
            exclude_opt_key=self.exclude_opt_key,
            exclude_http_methods=self.exclude_http_methods,
            retrieve_user_handler=self.retrieve_user_handler,
            scopes=self.scopes,
            token_secret=self.token_secret,
        )

    @property
    def oauth_flow(self) -> OAuthFlow:
        """Create an OpenAPI OAuth2 flow for the password bearer authentication scheme.

        Returns:
            An :class:`OAuthFlow <litestar.openapi.spec.oauth_flow.OAuthFlow>` instance.
        """
        return OAuthFlow(
            token_url=self.token_url,
            scopes=self.oauth_scopes,
        )

    @property
    def openapi_components(self) -> Components:
        """Create OpenAPI documentation for the OAUTH2 Password bearer auth scheme.

        Returns:
            An :class:`Components <litestar.openapi.spec.components.Components>` instance.
        """
        return Components(
            security_schemes={
                self.openapi_security_scheme_name: SecurityScheme(
                    type="oauth2",
                    scheme="Bearer",
                    name=self.auth_header,
                    security_scheme_in="header",
                    flows=OAuthFlows(password=self.oauth_flow),  # pyright: ignore[reportGeneralTypeIssues]
                    bearer_format="JWT",
                    description=self.description,
                )
            }
        )

    def login(
        self,
        identifier: str,
        *,
        response_body: Any = Empty,
        response_media_type: str | MediaType = MediaType.JSON,
        response_status_code: int = HTTP_201_CREATED,
        token_expiration: timedelta | None = None,
        token_issuer: str | None = None,
        token_audience: str | None = None,
        token_unique_jwt_id: str | None = None,
        token_extras: dict[str, Any] | None = None,
        send_token_as_response_body: bool = True,
    ) -> Response[Any]:
        """Create a response with a JWT header.

        Args:
            identifier: Unique identifier of the token subject. Usually this is a user ID or equivalent kind of value.
            response_body: An optional response body to send.
            response_media_type: An optional ``Content-Type``. Defaults to ``application/json``.
            response_status_code: An optional status code for the response. Defaults to ``201``.
            token_expiration: An optional timedelta for the token expiration.
            token_issuer: An optional value of the token ``iss`` field.
            token_audience: An optional value for the token ``aud`` field.
            token_unique_jwt_id: An optional value for the token ``jti`` field.
            token_extras: An optional dictionary to include in the token ``extras`` field.
            send_token_as_response_body: If ``True`` the response will be an oAuth2 token response dict.
                Note: if a response body is passed this setting will be ignored.

        Returns:
            A :class:`Response <.response.Response>` instance.
        """
        encoded_token = self.create_token(
            identifier=identifier,
            token_expiration=token_expiration,
            token_issuer=token_issuer,
            token_audience=token_audience,
            token_unique_jwt_id=token_unique_jwt_id,
            token_extras=token_extras,
        )
        expires_in = int((token_expiration or self.default_token_expiration).total_seconds())
        cookie = Cookie(
            key=self.key,
            path=self.path,
            httponly=True,
            value=self.format_auth_header(encoded_token),
            max_age=expires_in,
            secure=self.secure,
            samesite=self.samesite,
            domain=self.domain,
        )

        if response_body is not Empty:
            body = response_body
        elif send_token_as_response_body:
            token_dto = OAuth2Login(
                access_token=encoded_token,
                expires_in=expires_in,
                token_type="bearer",  # noqa: S106
            )
            body = asdict(token_dto)
        else:
            body = None

        return self.create_response(
            content=body,
            headers={self.auth_header: self.format_auth_header(encoded_token)},
            cookies=[cookie],
            media_type=response_media_type,
            status_code=response_status_code,
        )
