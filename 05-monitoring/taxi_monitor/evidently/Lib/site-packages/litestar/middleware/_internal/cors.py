from __future__ import annotations

from typing import TYPE_CHECKING

from litestar.constants import DEFAULT_ALLOWED_CORS_HEADERS
from litestar.datastructures import Headers, MutableScopeHeaders
from litestar.enums import HttpMethod, MediaType, ScopeType
from litestar.middleware.base import AbstractMiddleware
from litestar.response import Response
from litestar.status_codes import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST

if TYPE_CHECKING:
    from litestar.config.cors import CORSConfig
    from litestar.types import ASGIApp, Message, Receive, Scope, Send

__all__ = ("CORSMiddleware",)


class CORSMiddleware(AbstractMiddleware):
    """CORS Middleware."""

    def __init__(self, app: ASGIApp, config: CORSConfig) -> None:
        """Middleware that adds CORS validation to the application.

        Args:
            app: The ``next`` ASGI app to call.
            config: An instance of :class:`CORSConfig <litestar.config.cors.CORSConfig>`
        """
        super().__init__(app=app, scopes={ScopeType.HTTP})
        self.config = config

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI callable.

        Args:
            scope: The ASGI connection scope.
            receive: The ASGI receive function.
            send: The ASGI send function.

        Returns:
            None
        """
        headers = Headers.from_scope(scope=scope)
        origin = headers.get("origin")

        if scope["type"] == ScopeType.HTTP and scope["method"] == HttpMethod.OPTIONS and origin:
            request = scope["app"].request_class(scope=scope, receive=receive, send=send)
            asgi_response = self._create_preflight_response(origin=origin, request_headers=headers).to_asgi_response(
                app=None, request=request
            )
            await asgi_response(scope, receive, send)
        elif origin:
            await self.app(scope, receive, self.send_wrapper(send=send, origin=origin, has_cookie="cookie" in headers))
        else:
            await self.app(scope, receive, send)

    def send_wrapper(self, send: Send, origin: str, has_cookie: bool) -> Send:
        """Wrap ``send`` to ensure that state is not disconnected.

        Args:
            has_cookie: Boolean flag dictating if the connection has a cookie set.
            origin: The value of the ``Origin`` header.
            send: The ASGI send function.

        Returns:
            An ASGI send function.
        """

        async def wrapped_send(message: Message) -> None:
            if message["type"] == "http.response.start":
                message.setdefault("headers", [])
                headers = MutableScopeHeaders.from_message(message=message)
                headers.update(self.config.simple_headers)

                if (self.config.is_allow_all_origins and has_cookie) or (
                    not self.config.is_allow_all_origins and self.config.is_origin_allowed(origin=origin)
                ):
                    headers["Access-Control-Allow-Origin"] = origin
                    headers["Vary"] = "Origin"

                headers["Access-Control-Allow-Headers"] = ", ".join(sorted(set(self.config.allow_headers)))

                headers["Access-Control-Allow-Methods"] = ", ".join(sorted(set(self.config.allow_methods)))

            await send(message)

        return wrapped_send

    def _create_preflight_response(self, origin: str, request_headers: Headers) -> Response[str | None]:
        pre_flight_method = request_headers.get("Access-Control-Request-Method")
        failures = []

        if not self.config.is_allow_all_methods and (
            pre_flight_method and pre_flight_method not in self.config.allow_methods
        ):
            failures.append("method")

        response_headers = self.config.preflight_headers.copy()

        if not self.config.is_origin_allowed(origin):
            failures.append("Origin")
        elif response_headers.get("Access-Control-Allow-Origin") != "*":
            response_headers["Access-Control-Allow-Origin"] = origin

        pre_flight_requested_headers = [
            header.strip()
            for header in request_headers.get("Access-Control-Request-Headers", "").split(",")
            if header.strip()
        ]

        if pre_flight_requested_headers:
            if self.config.is_allow_all_headers:
                response_headers["Access-Control-Allow-Headers"] = ", ".join(
                    sorted(set(pre_flight_requested_headers) | DEFAULT_ALLOWED_CORS_HEADERS)  # pyright: ignore
                )
            elif any(header.lower() not in self.config.allow_headers for header in pre_flight_requested_headers):
                failures.append("headers")

        return (
            Response(
                content=f"Disallowed CORS {', '.join(failures)}",
                status_code=HTTP_400_BAD_REQUEST,
                media_type=MediaType.TEXT,
            )
            if failures
            else Response(
                content=None,
                status_code=HTTP_204_NO_CONTENT,
                media_type=MediaType.TEXT,
                headers=response_headers,
            )
        )
