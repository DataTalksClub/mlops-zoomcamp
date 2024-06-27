from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Dict, Generic, Iterable, Sequence, cast

from litestar.middleware.base import DefineMiddleware
from litestar.middleware.session.base import BaseBackendConfig, BaseSessionBackendT
from litestar.openapi.spec import Components, SecurityRequirement, SecurityScheme
from litestar.security.base import AbstractSecurityConfig, UserType
from litestar.security.session_auth.middleware import MiddlewareWrapper, SessionAuthMiddleware

__all__ = ("SessionAuth",)

if TYPE_CHECKING:
    from litestar.connection import ASGIConnection
    from litestar.di import Provide
    from litestar.types import ControllerRouterHandler, Guard, Method, Scopes, SyncOrAsyncUnion, TypeEncodersMap


@dataclass
class SessionAuth(Generic[UserType, BaseSessionBackendT], AbstractSecurityConfig[UserType, Dict[str, Any]]):
    """Session Based Security Backend."""

    session_backend_config: BaseBackendConfig[BaseSessionBackendT]  # pyright: ignore
    """A session backend config."""
    retrieve_user_handler: Callable[[Any, ASGIConnection], SyncOrAsyncUnion[Any | None]]
    """Callable that receives the ``auth`` value from the authentication middleware and returns a ``user`` value.

    Notes:
        - User and Auth can be any arbitrary values specified by the security backend.
        - The User and Auth values will be set by the middleware as ``scope["user"]`` and ``scope["auth"]`` respectively.
          Once provided, they can access via the ``connection.user`` and ``connection.auth`` properties.
        - The callable can be sync or async. If it is sync, it will be wrapped to support async.

    """

    authentication_middleware_class: type[SessionAuthMiddleware] = field(default=SessionAuthMiddleware)  # pyright: ignore
    """The authentication middleware class to use.

    Must inherit from :class:`SessionAuthMiddleware <litestar.security.session_auth.middleware.SessionAuthMiddleware>`
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

    @property
    def middleware(self) -> DefineMiddleware:
        """Use this property to insert the config into a middleware list on one of the application layers.

        Examples:
            .. code-block:: python

                from typing import Any
                from os import urandom

                from litestar import Litestar, Request, get
                from litestar_session import SessionAuth


                async def retrieve_user_from_session(session: dict[str, Any]) -> Any:
                    # implement logic here to retrieve a ``user`` datum given the session dictionary
                    ...


                session_auth_config = SessionAuth(
                    secret=urandom(16), retrieve_user_handler=retrieve_user_from_session
                )


                @get("/")
                def my_handler(request: Request) -> None: ...


                app = Litestar(route_handlers=[my_handler], middleware=[session_auth_config.middleware])


        Returns:
            An instance of DefineMiddleware including ``self`` as the config kwarg value.
        """
        return DefineMiddleware(MiddlewareWrapper, config=self)

    @property
    def session_backend(self) -> BaseSessionBackendT:
        """Create a session backend.

        Returns:
            A subclass of :class:`BaseSessionBackend <litestar.middleware.session.base.BaseSessionBackend>`
        """
        return self.session_backend_config._backend_class(config=self.session_backend_config)  # pyright: ignore

    @property
    def openapi_components(self) -> Components:
        """Create OpenAPI documentation for the Session Authentication schema used.

        Returns:
            An :class:`Components <litestar.openapi.spec.components.Components>` instance.
        """
        return Components(
            security_schemes={
                "sessionCookie": SecurityScheme(
                    type="apiKey",
                    name=self.session_backend_config.key,
                    security_scheme_in="cookie",  # pyright: ignore
                    description="Session cookie authentication.",
                )
            }
        )

    @property
    def security_requirement(self) -> SecurityRequirement:
        """Return OpenAPI 3.1.

        :data:`SecurityRequirement <.openapi.spec.SecurityRequirement>` for the auth
        backend.

        Returns:
            An OpenAPI 3.1 :data:`SecurityRequirement <.openapi.spec.SecurityRequirement>` dictionary.
        """
        return {"sessionCookie": []}
