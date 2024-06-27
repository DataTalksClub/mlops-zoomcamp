from __future__ import annotations

from http import HTTPStatus
from typing import Any

from litestar.exceptions.base_exceptions import LitestarException
from litestar.status_codes import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE,
)

__all__ = (
    "ClientException",
    "HTTPException",
    "ImproperlyConfiguredException",
    "InternalServerException",
    "MethodNotAllowedException",
    "NoRouteMatchFoundException",
    "NotAuthorizedException",
    "NotFoundException",
    "PermissionDeniedException",
    "ServiceUnavailableException",
    "TemplateNotFoundException",
    "TooManyRequestsException",
    "ValidationException",
)


class HTTPException(LitestarException):
    """Base exception for HTTP error responses.

    These exceptions carry information to construct an HTTP response.
    """

    status_code: int = HTTP_500_INTERNAL_SERVER_ERROR
    """Exception status code."""
    detail: str
    """Exception details or message."""
    headers: dict[str, str] | None
    """Headers to attach to the response."""
    extra: dict[str, Any] | list[Any] | None
    """An extra mapping to attach to the exception."""

    def __init__(
        self,
        *args: Any,
        detail: str = "",
        status_code: int | None = None,
        headers: dict[str, str] | None = None,
        extra: dict[str, Any] | list[Any] | None = None,
    ) -> None:
        """Initialize ``HTTPException``.

        Set ``detail`` and ``args`` if not provided.

        Args:
            *args: if ``detail`` kwarg not provided, first arg should be error detail.
            detail: Exception details or message. Will default to args[0] if not provided.
            status_code: Exception HTTP status code.
            headers: Headers to set on the response.
            extra: An extra mapping to attach to the exception.
        """
        super().__init__(*args, detail=detail)
        self.status_code = status_code or self.status_code
        self.extra = extra
        self.headers = headers
        if not self.detail:
            self.detail = HTTPStatus(self.status_code).phrase
        self.args = (f"{self.status_code}: {self.detail}", *self.args)

    def __repr__(self) -> str:
        return f"{self.status_code} - {self.__class__.__name__} - {self.detail}"

    def __str__(self) -> str:
        return " ".join(self.args).strip()


class ImproperlyConfiguredException(HTTPException, ValueError):
    """Application has improper configuration."""


class ClientException(HTTPException):
    """Client error."""

    status_code: int = HTTP_400_BAD_REQUEST


class ValidationException(ClientException, ValueError):
    """Client data validation error."""


class NotAuthorizedException(ClientException):
    """Request lacks valid authentication credentials for the requested resource."""

    status_code = HTTP_401_UNAUTHORIZED


class PermissionDeniedException(ClientException):
    """Request understood, but not authorized."""

    status_code = HTTP_403_FORBIDDEN


class NotFoundException(ClientException, ValueError):
    """Cannot find the requested resource."""

    status_code = HTTP_404_NOT_FOUND


class MethodNotAllowedException(ClientException):
    """Server knows the request method, but the target resource doesn't support this method."""

    status_code = HTTP_405_METHOD_NOT_ALLOWED


class TooManyRequestsException(ClientException):
    """Request limits have been exceeded."""

    status_code = HTTP_429_TOO_MANY_REQUESTS


class InternalServerException(HTTPException):
    """Server encountered an unexpected condition that prevented it from fulfilling the request."""

    status_code: int = HTTP_500_INTERNAL_SERVER_ERROR


class ServiceUnavailableException(InternalServerException):
    """Server is not ready to handle the request."""

    status_code = HTTP_503_SERVICE_UNAVAILABLE


class NoRouteMatchFoundException(InternalServerException):
    """A route with the given name could not be found."""


class TemplateNotFoundException(InternalServerException):
    """Referenced template could not be found."""

    def __init__(self, *args: Any, template_name: str) -> None:
        """Initialize ``TemplateNotFoundException``.

        Args:
            *args (Any): Passed through to ``super().__init__()`` - should not include ``detail``.
            template_name (str): Name of template that could not be found.
        """
        super().__init__(*args, detail=f"Template {template_name} not found.")
