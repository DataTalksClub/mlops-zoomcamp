from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Iterable

from litestar.constants import (
    HTTP_RESPONSE_BODY,
    HTTP_RESPONSE_START,
)
from litestar.data_extractors import (
    ConnectionDataExtractor,
    RequestExtractorField,
    ResponseDataExtractor,
    ResponseExtractorField,
)
from litestar.enums import ScopeType
from litestar.exceptions import ImproperlyConfiguredException
from litestar.middleware.base import AbstractMiddleware, DefineMiddleware
from litestar.serialization import encode_json
from litestar.utils.empty import value_or_default
from litestar.utils.scope import get_serializer_from_scope
from litestar.utils.scope.state import ScopeState

__all__ = ("LoggingMiddleware", "LoggingMiddlewareConfig")


if TYPE_CHECKING:
    from litestar.connection import Request
    from litestar.types import (
        ASGIApp,
        Logger,
        Message,
        Receive,
        Scope,
        Send,
        Serializer,
    )

try:
    from structlog.types import BindableLogger

    structlog_installed = True
except ImportError:
    BindableLogger = object  # type: ignore[assignment, misc]
    structlog_installed = False


class LoggingMiddleware(AbstractMiddleware):
    """Logging middleware."""

    logger: Logger

    def __init__(self, app: ASGIApp, config: LoggingMiddlewareConfig) -> None:
        """Initialize ``LoggingMiddleware``.

        Args:
            app: The ``next`` ASGI app to call.
            config: An instance of LoggingMiddlewareConfig.
        """
        super().__init__(
            app=app, scopes={ScopeType.HTTP}, exclude=config.exclude, exclude_opt_key=config.exclude_opt_key
        )
        self.is_struct_logger = structlog_installed
        self.config = config

        self.request_extractor = ConnectionDataExtractor(
            extract_body="body" in self.config.request_log_fields,
            extract_client="client" in self.config.request_log_fields,
            extract_content_type="content_type" in self.config.request_log_fields,
            extract_cookies="cookies" in self.config.request_log_fields,
            extract_headers="headers" in self.config.request_log_fields,
            extract_method="method" in self.config.request_log_fields,
            extract_path="path" in self.config.request_log_fields,
            extract_path_params="path_params" in self.config.request_log_fields,
            extract_query="query" in self.config.request_log_fields,
            extract_scheme="scheme" in self.config.request_log_fields,
            obfuscate_cookies=self.config.request_cookies_to_obfuscate,
            obfuscate_headers=self.config.request_headers_to_obfuscate,
            parse_body=self.is_struct_logger,
            parse_query=self.is_struct_logger,
            skip_parse_malformed_body=True,
        )
        self.response_extractor = ResponseDataExtractor(
            extract_body="body" in self.config.response_log_fields,
            extract_headers="headers" in self.config.response_log_fields,
            extract_status_code="status_code" in self.config.response_log_fields,
            obfuscate_cookies=self.config.response_cookies_to_obfuscate,
            obfuscate_headers=self.config.response_headers_to_obfuscate,
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI callable.

        Args:
            scope: The ASGI connection scope.
            receive: The ASGI receive function.
            send: The ASGI send function.

        Returns:
            None
        """
        if not hasattr(self, "logger"):
            self.logger = scope["app"].get_logger(self.config.logger_name)
            self.is_struct_logger = structlog_installed and repr(self.logger).startswith("<BoundLoggerLazyProxy")

        if self.config.response_log_fields:
            send = self.create_send_wrapper(scope=scope, send=send)

        if self.config.request_log_fields:
            await self.log_request(scope=scope, receive=receive)

        await self.app(scope, receive, send)

    async def log_request(self, scope: Scope, receive: Receive) -> None:
        """Extract request data and log the message.

        Args:
            scope: The ASGI connection scope.
            receive: ASGI receive callable

        Returns:
            None
        """
        extracted_data = await self.extract_request_data(request=scope["app"].request_class(scope, receive))
        self.log_message(values=extracted_data)

    def log_response(self, scope: Scope) -> None:
        """Extract the response data and log the message.

        Args:
            scope: The ASGI connection scope.

        Returns:
            None
        """
        extracted_data = self.extract_response_data(scope=scope)
        self.log_message(values=extracted_data)

    def log_message(self, values: dict[str, Any]) -> None:
        """Log a message.

        Args:
            values: Extract values to log.

        Returns:
            None
        """
        message = values.pop("message")
        if self.is_struct_logger:
            self.logger.info(message, **values)
        else:
            value_strings = [f"{key}={value}" for key, value in values.items()]
            log_message = f"{message}: {', '.join(value_strings)}"
            self.logger.info(log_message)

    def _serialize_value(self, serializer: Serializer | None, value: Any) -> Any:
        if not self.is_struct_logger and isinstance(value, (dict, list, tuple, set)):
            value = encode_json(value, serializer)
        return value.decode("utf-8", errors="backslashreplace") if isinstance(value, bytes) else value

    async def extract_request_data(self, request: Request) -> dict[str, Any]:
        """Create a dictionary of values for the message.

        Args:
            request: A :class:`Request <litestar.connection.Request>` instance.

        Returns:
            An dict.
        """

        data: dict[str, Any] = {"message": self.config.request_log_message}
        serializer = get_serializer_from_scope(request.scope)

        extracted_data = await self.request_extractor.extract(connection=request, fields=self.config.request_log_fields)

        for key in self.config.request_log_fields:
            data[key] = self._serialize_value(serializer, extracted_data.get(key))
        return data

    def extract_response_data(self, scope: Scope) -> dict[str, Any]:
        """Extract data from the response.

        Args:
            scope: The ASGI connection scope.

        Returns:
            An dict.
        """
        data: dict[str, Any] = {"message": self.config.response_log_message}
        serializer = get_serializer_from_scope(scope)
        connection_state = ScopeState.from_scope(scope)
        extracted_data = self.response_extractor(
            messages=(
                # NOTE: we don't pop the start message from the logging context in case
                #   there are multiple body messages to be logged
                connection_state.log_context[HTTP_RESPONSE_START],
                connection_state.log_context.pop(HTTP_RESPONSE_BODY),
            ),
        )
        response_body_compressed = value_or_default(connection_state.response_compressed, False)
        for key in self.config.response_log_fields:
            value: Any
            value = extracted_data.get(key)
            if key == "body" and response_body_compressed:
                if self.config.include_compressed_body:
                    data[key] = value
                continue
            data[key] = self._serialize_value(serializer, value)
        return data

    def create_send_wrapper(self, scope: Scope, send: Send) -> Send:
        """Create a ``send`` wrapper, which handles logging response data.

        Args:
            scope: The ASGI connection scope.
            send: The ASGI send function.

        Returns:
            An ASGI send function.
        """
        connection_state = ScopeState.from_scope(scope)

        async def send_wrapper(message: Message) -> None:
            if message["type"] == HTTP_RESPONSE_START:
                connection_state.log_context[HTTP_RESPONSE_START] = message
            elif message["type"] == HTTP_RESPONSE_BODY:
                connection_state.log_context[HTTP_RESPONSE_BODY] = message
                self.log_response(scope=scope)

                if not message["more_body"]:
                    connection_state.log_context.clear()

            await send(message)

        return send_wrapper


@dataclass
class LoggingMiddlewareConfig:
    """Configuration for ``LoggingMiddleware``"""

    exclude: str | list[str] | None = field(default=None)
    """List of paths to exclude from logging."""
    exclude_opt_key: str | None = field(default=None)
    """An identifier to use on routes to disable logging for a particular route."""
    include_compressed_body: bool = field(default=False)
    """Include body of compressed response in middleware. If `"body"` not set in.
    :attr:`response_log_fields <LoggingMiddlewareConfig.response_log_fields>` this config value is ignored.
    """
    logger_name: str = field(default="litestar")
    """Name of the logger to retrieve using `app.get_logger("<name>")`."""
    request_cookies_to_obfuscate: set[str] = field(default_factory=lambda: {"session"})
    """Request cookie keys to obfuscate.

    Obfuscated values are replaced with '*****'.
    """
    request_headers_to_obfuscate: set[str] = field(default_factory=lambda: {"Authorization", "X-API-KEY"})
    """Request header keys to obfuscate.

    Obfuscated values are replaced with '*****'.
    """
    response_cookies_to_obfuscate: set[str] = field(default_factory=lambda: {"session"})
    """Response cookie keys to obfuscate.

    Obfuscated values are replaced with '*****'.
    """
    response_headers_to_obfuscate: set[str] = field(default_factory=lambda: {"Authorization", "X-API-KEY"})
    """Response header keys to obfuscate.

    Obfuscated values are replaced with '*****'.
    """
    request_log_message: str = field(default="HTTP Request")
    """Log message to prepend when logging a request."""
    response_log_message: str = field(default="HTTP Response")
    """Log message to prepend when logging a response."""
    request_log_fields: Iterable[RequestExtractorField] = field(
        default=(
            "path",
            "method",
            "content_type",
            "headers",
            "cookies",
            "query",
            "path_params",
            "body",
        )
    )
    """Fields to extract and log from the request.

    Notes:
        -  The order of fields in the iterable determines the order of the log message logged out.
            Thus, re-arranging the log-message is as simple as changing the iterable.
        -  To turn off logging of requests, use and empty iterable.
    """
    response_log_fields: Iterable[ResponseExtractorField] = field(
        default=(
            "status_code",
            "cookies",
            "headers",
            "body",
        )
    )
    """Fields to extract and log from the response. The order of fields in the iterable determines the order of the log
    message logged out.

    Notes:
        -  The order of fields in the iterable determines the order of the log message logged out.
            Thus, re-arranging the log-message is as simple as changing the iterable.
        -  To turn off logging of responses, use and empty iterable.
    """
    middleware_class: type[LoggingMiddleware] = field(default=LoggingMiddleware)
    """Middleware class to use.

    Should be a subclass of [litestar.middleware.LoggingMiddleware].
    """

    def __post_init__(self) -> None:
        """Override default Pydantic type conversion for iterables.

        Args:
            value: An iterable

        Returns:
            The `value` argument cast as a tuple.
        """
        if not isinstance(self.response_log_fields, Iterable):
            raise ImproperlyConfiguredException("response_log_fields must be a valid Iterable")

        if not isinstance(self.request_log_fields, Iterable):
            raise ImproperlyConfiguredException("request_log_fields must be a valid Iterable")

        self.response_log_fields = tuple(self.response_log_fields)
        self.request_log_fields = tuple(self.request_log_fields)

    @property
    def middleware(self) -> DefineMiddleware:
        """Use this property to insert the config into a middleware list on one of the application layers.

        Examples:
            .. code-block::  python

                from litestar import Litestar, Request, get
                from litestar.logging import LoggingConfig
                from litestar.middleware.logging import LoggingMiddlewareConfig

                logging_config = LoggingConfig()

                logging_middleware_config = LoggingMiddlewareConfig()


                @get("/")
                def my_handler(request: Request) -> None: ...


                app = Litestar(
                    route_handlers=[my_handler],
                    logging_config=logging_config,
                    middleware=[logging_middleware_config.middleware],
                )

        Returns:
            An instance of DefineMiddleware including ``self`` as the config kwarg value.
        """
        return DefineMiddleware(self.middleware_class, config=self)
