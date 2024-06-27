from __future__ import annotations

import itertools
import re
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Iterable, Literal, Mapping, TypeVar, overload

from litestar.datastructures.cookie import Cookie
from litestar.datastructures.headers import ETag, MutableScopeHeaders
from litestar.enums import MediaType, OpenAPIMediaType
from litestar.exceptions import ImproperlyConfiguredException
from litestar.serialization import default_serializer, encode_json, encode_msgpack, get_serializer
from litestar.status_codes import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_304_NOT_MODIFIED
from litestar.types.empty import Empty
from litestar.utils.deprecation import deprecated, warn_deprecation
from litestar.utils.helpers import get_enum_string_value

if TYPE_CHECKING:
    from typing import Optional

    from litestar.app import Litestar
    from litestar.background_tasks import BackgroundTask, BackgroundTasks
    from litestar.connection import Request
    from litestar.types import (
        HTTPResponseBodyEvent,
        HTTPResponseStartEvent,
        Receive,
        ResponseCookies,
        ResponseHeaders,
        Scope,
        Send,
        Serializer,
        TypeEncodersMap,
    )

__all__ = ("ASGIResponse", "Response")

T = TypeVar("T")

MEDIA_TYPE_APPLICATION_JSON_PATTERN = re.compile(r"^application/(?:.+\+)?json")


class ASGIResponse:
    """A low-level ASGI response class."""

    __slots__ = (
        "background",
        "body",
        "content_length",
        "encoding",
        "is_head_response",
        "status_code",
        "_encoded_cookies",
        "headers",
    )

    _should_set_content_length: ClassVar[bool] = True
    """A flag to indicate whether the content-length header should be set by default or not."""

    def __init__(
        self,
        *,
        background: BackgroundTask | BackgroundTasks | None = None,
        body: bytes | str = b"",
        content_length: int | None = None,
        cookies: Iterable[Cookie] | None = None,
        encoded_headers: Iterable[tuple[bytes, bytes]] | None = None,
        encoding: str = "utf-8",
        headers: dict[str, Any] | Iterable[tuple[str, str]] | None = None,
        is_head_response: bool = False,
        media_type: MediaType | str | None = None,
        status_code: int | None = None,
    ) -> None:
        """A low-level ASGI response class.

        Args:
            background: A background task or a list of background tasks to be executed after the response is sent.
            body: encoded content to send in the response body.
            content_length: The response content length.
            cookies: The response cookies.
            encoded_headers: The response headers.
            encoding: The response encoding.
            headers: The response headers.
            is_head_response: A boolean indicating if the response is a HEAD response.
            media_type: The response media type.
            status_code: The response status code.
        """
        body = body.encode() if isinstance(body, str) else body
        status_code = status_code or HTTP_200_OK
        self.headers = MutableScopeHeaders()

        if encoded_headers is not None:
            warn_deprecation("3.0", kind="parameter", deprecated_name="encoded_headers", alternative="headers")
            for header_name, header_value in encoded_headers:
                self.headers.add(header_name.decode("latin-1"), header_value.decode("latin-1"))

        if headers is not None:
            for k, v in headers.items() if isinstance(headers, dict) else headers:
                self.headers.add(k, v)  # pyright: ignore

        media_type = get_enum_string_value(media_type or MediaType.JSON)

        status_allows_body = (
            status_code not in {HTTP_204_NO_CONTENT, HTTP_304_NOT_MODIFIED} and status_code >= HTTP_200_OK
        )

        if content_length is None:
            content_length = len(body)

        if not status_allows_body or is_head_response:
            if body and body != b"null":
                raise ImproperlyConfiguredException(
                    "response content is not supported for HEAD responses and responses with a status code "
                    "that does not allow content (304, 204, < 200)"
                )
            body = b""
        else:
            self.headers.setdefault(
                "content-type", (f"{media_type}; charset={encoding}" if media_type.startswith("text/") else media_type)
            )

            if self._should_set_content_length:
                self.headers.setdefault("content-length", str(content_length))

        self.background = background
        self.body = body
        self.content_length = content_length
        self._encoded_cookies = tuple(
            cookie.to_encoded_header() for cookie in (cookies or ()) if not cookie.documentation_only
        )
        self.encoding = encoding
        self.is_head_response = is_head_response
        self.status_code = status_code

    @property
    @deprecated("3.0", kind="property", alternative="encode_headers()")
    def encoded_headers(self) -> list[tuple[bytes, bytes]]:
        return self.encode_headers()

    def encode_headers(self) -> list[tuple[bytes, bytes]]:
        return [*self.headers.headers, *self._encoded_cookies]

    async def after_response(self) -> None:
        """Execute after the response is sent.

        Returns:
            None
        """
        if self.background is not None:
            await self.background()

    async def start_response(self, send: Send) -> None:
        """Emit the start event of the response. This event includes the headers and status codes.

        Args:
            send: The ASGI send function.

        Returns:
            None
        """
        event: HTTPResponseStartEvent = {
            "type": "http.response.start",
            "status": self.status_code,
            "headers": self.encode_headers(),
        }
        await send(event)

    async def send_body(self, send: Send, receive: Receive) -> None:
        """Emit the response body.

        Args:
            send: The ASGI send function.
            receive: The ASGI receive function.

        Notes:
            - Response subclasses should customize this method if there is a need to customize sending data.

        Returns:
            None
        """
        event: HTTPResponseBodyEvent = {"type": "http.response.body", "body": self.body, "more_body": False}
        await send(event)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI callable of the ``Response``.

        Args:
            scope: The ASGI connection scope.
            receive: The ASGI receive function.
            send: The ASGI send function.

        Returns:
            None
        """
        await self.start_response(send=send)

        if self.is_head_response:
            event: HTTPResponseBodyEvent = {"type": "http.response.body", "body": b"", "more_body": False}
            await send(event)
        else:
            await self.send_body(send=send, receive=receive)

        await self.after_response()


class Response(Generic[T]):
    """Base Litestar HTTP response class, used as the basis for all other response classes."""

    __slots__ = (
        "background",
        "content",
        "cookies",
        "encoding",
        "headers",
        "media_type",
        "status_code",
        "response_type_encoders",
    )

    content: T
    type_encoders: Optional[TypeEncodersMap] = None  # noqa: UP007

    def __init__(
        self,
        content: T,
        *,
        background: BackgroundTask | BackgroundTasks | None = None,
        cookies: ResponseCookies | None = None,
        encoding: str = "utf-8",
        headers: ResponseHeaders | None = None,
        media_type: MediaType | OpenAPIMediaType | str | None = None,
        status_code: int | None = None,
        type_encoders: TypeEncodersMap | None = None,
    ) -> None:
        """Initialize the response.

        Args:
            content: A value for the response body that will be rendered into bytes string.
            status_code: An HTTP status code.
            media_type: A value for the response ``Content-Type`` header.
            background: A :class:`BackgroundTask <.background_tasks.BackgroundTask>` instance or
                :class:`BackgroundTasks <.background_tasks.BackgroundTasks>` to execute after the response is finished.
                Defaults to ``None``.
            headers: A string keyed dictionary of response headers. Header keys are insensitive.
            cookies: A list of :class:`Cookie <.datastructures.Cookie>` instances to be set under the response
                ``Set-Cookie`` header.
            encoding: The encoding to be used for the response headers.
            type_encoders: A mapping of types to callables that transform them into types supported for serialization.
        """
        self.content = content
        self.background = background
        self.cookies: list[Cookie] = (
            [Cookie(key=key, value=value) for key, value in cookies.items()]
            if isinstance(cookies, Mapping)
            else list(cookies or [])
        )
        self.encoding = encoding
        self.headers: dict[str, Any] = (
            dict(headers) if isinstance(headers, Mapping) else {h.name: h.value for h in headers or {}}
        )
        self.media_type = media_type
        self.status_code = status_code
        self.response_type_encoders = {**(self.type_encoders or {}), **(type_encoders or {})}

    @overload
    def set_cookie(self, /, cookie: Cookie) -> None: ...

    @overload
    def set_cookie(
        self,
        key: str,
        value: str | None = None,
        max_age: int | None = None,
        expires: int | None = None,
        path: str = "/",
        domain: str | None = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: Literal["lax", "strict", "none"] = "lax",
    ) -> None: ...

    def set_cookie(  # type: ignore[misc]
        self,
        key: str | Cookie,
        value: str | None = None,
        max_age: int | None = None,
        expires: int | None = None,
        path: str = "/",
        domain: str | None = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: Literal["lax", "strict", "none"] = "lax",
    ) -> None:
        """Set a cookie on the response. If passed a :class:`Cookie <.datastructures.Cookie>` instance, keyword
        arguments will be ignored.

        Args:
            key: Key for the cookie or a :class:`Cookie <.datastructures.Cookie>` instance.
            value: Value for the cookie, if none given defaults to empty string.
            max_age: Maximal age of the cookie before its invalidated.
            expires: Seconds from now until the cookie expires.
            path: Path fragment that must exist in the request url for the cookie to be valid. Defaults to ``/``.
            domain: Domain for which the cookie is valid.
            secure: Https is required for the cookie.
            httponly: Forbids javascript to access the cookie via ``document.cookie``.
            samesite: Controls whether a cookie is sent with cross-site requests. Defaults to ``lax``.

        Returns:
            None.
        """
        if not isinstance(key, Cookie):
            key = Cookie(
                domain=domain,
                expires=expires,
                httponly=httponly,
                key=key,
                max_age=max_age,
                path=path,
                samesite=samesite,
                secure=secure,
                value=value,
            )
        self.cookies.append(key)

    def set_header(self, key: str, value: Any) -> None:
        """Set a header on the response.

        Args:
            key: Header key.
            value: Header value.

        Returns:
            None.
        """
        self.headers[key] = value

    def set_etag(self, etag: str | ETag) -> None:
        """Set an etag header.

        Args:
            etag: An etag value.

        Returns:
            None
        """
        self.headers["etag"] = etag.to_header() if isinstance(etag, ETag) else etag

    def delete_cookie(
        self,
        key: str,
        path: str = "/",
        domain: str | None = None,
    ) -> None:
        """Delete a cookie.

        Args:
            key: Key of the cookie.
            path: Path of the cookie.
            domain: Domain of the cookie.

        Returns:
            None.
        """
        cookie = Cookie(key=key, path=path, domain=domain, expires=0, max_age=0)
        self.cookies = [c for c in self.cookies if c != cookie]
        self.cookies.append(cookie)

    def render(self, content: Any, media_type: str, enc_hook: Serializer = default_serializer) -> bytes:
        """Handle the rendering of content into a bytes string.

        Returns:
            An encoded bytes string
        """
        if isinstance(content, bytes):
            return content

        if content is Empty:
            raise RuntimeError("The `Empty` sentinel cannot be used as response content")

        try:
            if media_type.startswith("text/") and not content:
                return b""

            if isinstance(content, str):
                return content.encode(self.encoding)

            if media_type == MediaType.MESSAGEPACK:
                return encode_msgpack(content, enc_hook)

            if MEDIA_TYPE_APPLICATION_JSON_PATTERN.match(
                media_type,
            ):
                return encode_json(content, enc_hook)

            raise ImproperlyConfiguredException(f"unsupported media_type {media_type} for content {content!r}")
        except (AttributeError, ValueError, TypeError) as e:
            raise ImproperlyConfiguredException("Unable to serialize response content") from e

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
        """Create an ASGIResponse from a Response instance.

        Args:
            app: The :class:`Litestar <.app.Litestar>` application instance.
            background: Background task(s) to be executed after the response is sent.
            cookies: A list of cookies to be set on the response.
            encoded_headers: A list of already encoded headers.
            headers: Additional headers to be merged with the response headers. Response headers take precedence.
            is_head_response: Whether the response is a HEAD response.
            media_type: Media type for the response. If ``media_type`` is already set on the response, this is ignored.
            request: The :class:`Request <.connection.Request>` instance.
            status_code: Status code for the response. If ``status_code`` is already set on the response, this is
            type_encoders: A dictionary of type encoders to use for encoding the response content.

        Returns:
            An ASGIResponse instance.
        """

        if app is not None:
            warn_deprecation(
                version="2.1",
                deprecated_name="app",
                kind="parameter",
                removal_in="3.0.0",
                alternative="request.app",
            )

        headers = {**headers, **self.headers} if headers is not None else self.headers
        cookies = self.cookies if cookies is None else itertools.chain(self.cookies, cookies)

        if type_encoders:
            type_encoders = {**type_encoders, **(self.response_type_encoders or {})}
        else:
            type_encoders = self.response_type_encoders

        media_type = get_enum_string_value(self.media_type or media_type or MediaType.JSON)

        return ASGIResponse(
            background=self.background or background,
            body=self.render(self.content, media_type, get_serializer(type_encoders)),
            cookies=cookies,
            encoded_headers=encoded_headers,
            encoding=self.encoding,
            headers=headers,
            is_head_response=is_head_response,
            media_type=media_type,
            status_code=self.status_code or status_code,
        )
