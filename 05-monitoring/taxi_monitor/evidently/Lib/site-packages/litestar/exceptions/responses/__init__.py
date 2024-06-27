from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from litestar import MediaType, Request, Response
from litestar.exceptions import HTTPException, LitestarException
from litestar.exceptions.responses import _debug_response
from litestar.serialization import encode_json, get_serializer
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR

__all__ = (
    "ExceptionResponseContent",
    "create_exception_response",
    "create_debug_response",
)


@dataclass
class ExceptionResponseContent:
    """Represent the contents of an exception-response."""

    status_code: int
    """Exception status code."""
    detail: str
    """Exception details or message."""
    media_type: MediaType | str
    """Media type of the response."""
    headers: dict[str, str] | None = field(default=None)
    """Headers to attach to the response."""
    extra: dict[str, Any] | list[Any] | None = field(default=None)
    """An extra mapping to attach to the exception."""

    def to_response(self, request: Request | None = None) -> Response:
        """Create a response from the model attributes.

        Returns:
            A response instance.
        """

        content: Any = {k: v for k, v in asdict(self).items() if k not in ("headers", "media_type") and v is not None}
        type_encoders = _debug_response._get_type_encoders_for_request(request) if request is not None else None

        if self.media_type != MediaType.JSON:
            content = encode_json(content, get_serializer(type_encoders))

        return Response(
            content=content,
            headers=self.headers,
            status_code=self.status_code,
            media_type=self.media_type,
            type_encoders=type_encoders,
        )


def create_exception_response(request: Request[Any, Any, Any], exc: Exception) -> Response:
    """Construct a response from an exception.

    Notes:
        - For instances of :class:`HTTPException <litestar.exceptions.HTTPException>` or other exception classes that have a
          ``status_code`` attribute (e.g. Starlette exceptions), the status code is drawn from the exception, otherwise
          response status is ``HTTP_500_INTERNAL_SERVER_ERROR``.

    Args:
        request: The request that triggered the exception.
        exc: An exception.

    Returns:
        Response: HTTP response constructed from exception details.
    """
    headers: dict[str, Any] | None
    extra: dict[str, Any] | list | None

    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        headers = exc.headers
        extra = exc.extra
    else:
        status_code = HTTP_500_INTERNAL_SERVER_ERROR
        headers = None
        extra = None

    detail = (
        exc.detail
        if isinstance(exc, LitestarException) and status_code != HTTP_500_INTERNAL_SERVER_ERROR
        else "Internal Server Error"
    )

    try:
        media_type = request.route_handler.media_type
    except (KeyError, AttributeError):
        media_type = MediaType.JSON

    content = ExceptionResponseContent(
        status_code=status_code,
        detail=detail,
        headers=headers,
        extra=extra,
        media_type=media_type,
    )
    return content.to_response(request=request)


def create_debug_response(request: Request, exc: Exception) -> Response:
    """Create a debug response from an exception.

    Args:
        request: The request that triggered the exception.
        exc: An exception.

    Returns:
        Response: Debug response constructed from exception details.
    """
    return _debug_response.create_debug_response(request, exc)
