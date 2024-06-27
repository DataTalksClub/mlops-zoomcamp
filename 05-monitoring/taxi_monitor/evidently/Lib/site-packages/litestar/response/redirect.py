from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, Any, Iterable, Literal

from litestar.constants import REDIRECT_ALLOWED_MEDIA_TYPES, REDIRECT_STATUS_CODES
from litestar.enums import MediaType
from litestar.exceptions import ImproperlyConfiguredException
from litestar.response.base import ASGIResponse, Response
from litestar.status_codes import HTTP_302_FOUND
from litestar.utils import url_quote
from litestar.utils.deprecation import warn_deprecation
from litestar.utils.helpers import get_enum_string_value

if TYPE_CHECKING:
    from litestar.app import Litestar
    from litestar.background_tasks import BackgroundTask, BackgroundTasks
    from litestar.connection import Request
    from litestar.datastructures import Cookie
    from litestar.types import ResponseCookies, ResponseHeaders, TypeEncodersMap

__all__ = (
    "ASGIRedirectResponse",
    "Redirect",
)


RedirectStatusType = Literal[301, 302, 303, 307, 308]
"""Acceptable status codes for redirect responses."""


class ASGIRedirectResponse(ASGIResponse):
    """A low-level ASGI redirect response class."""

    def __init__(
        self,
        path: str | bytes,
        media_type: str | None = None,
        status_code: RedirectStatusType | None = None,
        headers: dict[str, Any] | None = None,
        encoded_headers: Iterable[tuple[bytes, bytes]] | None = None,
        background: BackgroundTask | BackgroundTasks | None = None,
        body: bytes | str = b"",
        content_length: int | None = None,
        cookies: Iterable[Cookie] | None = None,
        encoding: str = "utf-8",
        is_head_response: bool = False,
    ) -> None:
        headers = {**(headers or {}), "location": url_quote(path)}
        media_type = media_type or MediaType.TEXT
        status_code = status_code or HTTP_302_FOUND

        if status_code not in REDIRECT_STATUS_CODES:
            raise ImproperlyConfiguredException(
                f"{status_code} is not a valid for this response. "
                f"Redirect responses should have one of "
                f"the following status codes: {', '.join([str(s) for s in REDIRECT_STATUS_CODES])}"
            )

        if media_type not in REDIRECT_ALLOWED_MEDIA_TYPES:
            raise ImproperlyConfiguredException(
                f"{media_type} media type is not supported yet. "
                f"Media type should be one of "
                f"the following values: {', '.join([str(s) for s in REDIRECT_ALLOWED_MEDIA_TYPES])}"
            )

        super().__init__(
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
            is_head_response=is_head_response,
            encoding=encoding,
            cookies=cookies,
            content_length=content_length,
            body=body,
            encoded_headers=encoded_headers,
        )


class Redirect(Response[Any]):
    """A redirect response."""

    __slots__ = ("url",)

    def __init__(
        self,
        path: str,
        *,
        background: BackgroundTask | BackgroundTasks | None = None,
        cookies: ResponseCookies | None = None,
        encoding: str = "utf-8",
        headers: ResponseHeaders | None = None,
        media_type: str | MediaType | None = None,
        status_code: RedirectStatusType | None = None,
        type_encoders: TypeEncodersMap | None = None,
    ) -> None:
        """Initialize the response.

        Args:
            path: A path to redirect to.
            background: A background task or tasks to be run after the response is sent.
            cookies: A list of :class:`Cookie <.datastructures.Cookie>` instances to be set under the response
                ``Set-Cookie`` header.
            encoding: The encoding to be used for the response headers.
            headers: A string keyed dictionary of response headers. Header keys are insensitive.
            media_type: A value for the response ``Content-Type`` header.
            status_code: An HTTP status code. The status code should be one of 301, 302, 303, 307 or 308,
                otherwise an exception will be raised.
            type_encoders: A mapping of types to callables that transform them into types supported for serialization.

        Raises:
            ImproperlyConfiguredException: Either if status code is not a redirect status code or media type is not
                supported.
        """
        self.url = path
        if status_code is None:
            status_code = HTTP_302_FOUND
        super().__init__(
            background=background,
            content=b"",
            cookies=cookies,
            encoding=encoding,
            headers=headers,
            media_type=media_type,
            status_code=status_code,
            type_encoders=type_encoders,
        )

    def to_asgi_response(
        self,
        app: Litestar | None,
        request: Request,
        *,
        background: BackgroundTask | BackgroundTasks | None = None,
        cookies: Iterable[Cookie] | None = None,
        encoded_headers: Iterable[tuple[bytes, bytes]] | None = None,
        headers: dict[str, str] | None = None,
        is_head_response: bool = False,
        media_type: MediaType | str | None = None,
        status_code: int | None = None,
        type_encoders: TypeEncodersMap | None = None,
    ) -> ASGIResponse:
        headers = {**headers, **self.headers} if headers is not None else self.headers
        cookies = self.cookies if cookies is None else itertools.chain(self.cookies, cookies)
        media_type = get_enum_string_value(self.media_type or media_type or MediaType.TEXT)

        if app is not None:
            warn_deprecation(
                version="2.1",
                deprecated_name="app",
                kind="parameter",
                removal_in="3.0.0",
                alternative="request.app",
            )

        return ASGIRedirectResponse(
            path=self.url,
            background=self.background or background,
            body=b"",
            content_length=None,
            cookies=cookies,
            encoded_headers=encoded_headers,
            encoding=self.encoding,
            headers=headers,
            is_head_response=is_head_response,
            media_type=media_type,
            status_code=self.status_code or status_code,  # type:ignore[arg-type]
        )
