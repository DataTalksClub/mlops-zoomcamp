from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Iterable, Literal, TypedDict, cast

from litestar._parsers import parse_cookie_string
from litestar.connection.request import Request
from litestar.datastructures.upload_file import UploadFile
from litestar.enums import HttpMethod, RequestEncodingType

__all__ = (
    "ConnectionDataExtractor",
    "ExtractedRequestData",
    "ExtractedResponseData",
    "ResponseDataExtractor",
    "RequestExtractorField",
    "ResponseExtractorField",
)


if TYPE_CHECKING:
    from litestar.connection import ASGIConnection
    from litestar.types import Method
    from litestar.types.asgi_types import HTTPResponseBodyEvent, HTTPResponseStartEvent


def _obfuscate(values: dict[str, Any], fields_to_obfuscate: set[str]) -> dict[str, Any]:
    """Obfuscate values in a dictionary, replacing values with `******`

    Args:
        values: A dictionary of strings
        fields_to_obfuscate: keys to obfuscate

    Returns:
        A dictionary with obfuscated strings
    """
    return {key: "*****" if key.lower() in fields_to_obfuscate else value for key, value in values.items()}


RequestExtractorField = Literal[
    "path", "method", "content_type", "headers", "cookies", "query", "path_params", "body", "scheme", "client"
]

ResponseExtractorField = Literal["status_code", "headers", "body", "cookies"]


class ExtractedRequestData(TypedDict, total=False):
    """Dictionary representing extracted request data."""

    body: Coroutine[Any, Any, Any]
    client: tuple[str, int]
    content_type: tuple[str, dict[str, str]]
    cookies: dict[str, str]
    headers: dict[str, str]
    method: Method
    path: str
    path_params: dict[str, Any]
    query: bytes | dict[str, Any]
    scheme: str


class ConnectionDataExtractor:
    """Utility class to extract data from an :class:`ASGIConnection <litestar.connection.ASGIConnection>`,
    :class:`Request <litestar.connection.Request>` or :class:`WebSocket <litestar.connection.WebSocket>` instance.
    """

    __slots__ = (
        "connection_extractors",
        "request_extractors",
        "parse_body",
        "parse_query",
        "obfuscate_headers",
        "obfuscate_cookies",
        "skip_parse_malformed_body",
    )

    def __init__(
        self,
        extract_body: bool = True,
        extract_client: bool = True,
        extract_content_type: bool = True,
        extract_cookies: bool = True,
        extract_headers: bool = True,
        extract_method: bool = True,
        extract_path: bool = True,
        extract_path_params: bool = True,
        extract_query: bool = True,
        extract_scheme: bool = True,
        obfuscate_cookies: set[str] | None = None,
        obfuscate_headers: set[str] | None = None,
        parse_body: bool = False,
        parse_query: bool = False,
        skip_parse_malformed_body: bool = False,
    ) -> None:
        """Initialize ``ConnectionDataExtractor``

        Args:
            extract_body: Whether to extract body, (for requests only).
            extract_client: Whether to extract the client (host, port) mapping.
            extract_content_type: Whether to extract the content type and any options.
            extract_cookies: Whether to extract cookies.
            extract_headers: Whether to extract headers.
            extract_method: Whether to extract the HTTP method, (for requests only).
            extract_path: Whether to extract the path.
            extract_path_params: Whether to extract path parameters.
            extract_query: Whether to extract query parameters.
            extract_scheme: Whether to extract the http scheme.
            obfuscate_headers: headers keys to obfuscate. Obfuscated values are replaced with '*****'.
            obfuscate_cookies: cookie keys to obfuscate. Obfuscated values are replaced with '*****'.
            parse_body: Whether to parse the body value or return the raw byte string, (for requests only).
            parse_query: Whether to parse query parameters or return the raw byte string.
            skip_parse_malformed_body: Whether to skip parsing the body if it is malformed
        """
        self.parse_body = parse_body
        self.parse_query = parse_query
        self.skip_parse_malformed_body = skip_parse_malformed_body
        self.obfuscate_headers = {h.lower() for h in (obfuscate_headers or set())}
        self.obfuscate_cookies = {c.lower() for c in (obfuscate_cookies or set())}
        self.connection_extractors: dict[str, Callable[[ASGIConnection[Any, Any, Any, Any]], Any]] = {}
        self.request_extractors: dict[RequestExtractorField, Callable[[Request[Any, Any, Any]], Any]] = {}
        if extract_scheme:
            self.connection_extractors["scheme"] = self.extract_scheme
        if extract_client:
            self.connection_extractors["client"] = self.extract_client
        if extract_path:
            self.connection_extractors["path"] = self.extract_path
        if extract_headers:
            self.connection_extractors["headers"] = self.extract_headers
        if extract_cookies:
            self.connection_extractors["cookies"] = self.extract_cookies
        if extract_query:
            self.connection_extractors["query"] = self.extract_query
        if extract_path_params:
            self.connection_extractors["path_params"] = self.extract_path_params
        if extract_method:
            self.request_extractors["method"] = self.extract_method
        if extract_content_type:
            self.request_extractors["content_type"] = self.extract_content_type
        if extract_body:
            self.request_extractors["body"] = self.extract_body

    def __call__(self, connection: ASGIConnection[Any, Any, Any, Any]) -> ExtractedRequestData:
        """Extract data from the connection, returning a dictionary of values.

        Notes:
            - The value for ``body`` - if present - is an unresolved Coroutine and as such should be awaited by the receiver.

        Args:
            connection: An ASGI connection or its subclasses.

        Returns:
            A string keyed dictionary of extracted values.
        """
        extractors = (
            {**self.connection_extractors, **self.request_extractors}  # type: ignore[misc]
            if isinstance(connection, Request)
            else self.connection_extractors
        )
        return cast("ExtractedRequestData", {key: extractor(connection) for key, extractor in extractors.items()})

    async def extract(
        self, connection: ASGIConnection[Any, Any, Any, Any], fields: Iterable[str]
    ) -> ExtractedRequestData:
        extractors = (
            {**self.connection_extractors, **self.request_extractors}  # type: ignore[misc]
            if isinstance(connection, Request)
            else self.connection_extractors
        )
        data = {}
        for key, extractor in extractors.items():
            if key not in fields:
                continue
            if inspect.iscoroutinefunction(extractor):
                value = await extractor(connection)
            else:
                value = extractor(connection)
            data[key] = value
        return cast("ExtractedRequestData", data)

    @staticmethod
    def extract_scheme(connection: ASGIConnection[Any, Any, Any, Any]) -> str:
        """Extract the scheme from an ``ASGIConnection``

        Args:
            connection: An :class:`ASGIConnection <litestar.connection.ASGIConnection>` instance.

        Returns:
            The connection's scope["scheme"] value
        """
        return connection.scope["scheme"]

    @staticmethod
    def extract_client(connection: ASGIConnection[Any, Any, Any, Any]) -> tuple[str, int]:
        """Extract the client from an ``ASGIConnection``

        Args:
            connection: An :class:`ASGIConnection <litestar.connection.ASGIConnection>` instance.

        Returns:
            The connection's scope["client"] value or a default value.
        """
        return connection.scope.get("client") or ("", 0)

    @staticmethod
    def extract_path(connection: ASGIConnection[Any, Any, Any, Any]) -> str:
        """Extract the path from an ``ASGIConnection``

        Args:
            connection: An :class:`ASGIConnection <litestar.connection.ASGIConnection>` instance.

        Returns:
            The connection's scope["path"] value
        """
        return connection.scope["path"]

    def extract_headers(self, connection: ASGIConnection[Any, Any, Any, Any]) -> dict[str, str]:
        """Extract headers from an ``ASGIConnection``

        Args:
            connection: An :class:`ASGIConnection <litestar.connection.ASGIConnection>` instance.

        Returns:
            A dictionary with the connection's headers.
        """
        headers = {k.decode("latin-1"): v.decode("latin-1") for k, v in connection.scope["headers"]}
        return _obfuscate(headers, self.obfuscate_headers) if self.obfuscate_headers else headers

    def extract_cookies(self, connection: ASGIConnection[Any, Any, Any, Any]) -> dict[str, str]:
        """Extract cookies from an ``ASGIConnection``

        Args:
            connection: An :class:`ASGIConnection <litestar.connection.ASGIConnection>` instance.

        Returns:
            A dictionary with the connection's cookies.
        """
        return _obfuscate(connection.cookies, self.obfuscate_cookies) if self.obfuscate_cookies else connection.cookies

    def extract_query(self, connection: ASGIConnection[Any, Any, Any, Any]) -> Any:
        """Extract query from an ``ASGIConnection``

        Args:
            connection: An :class:`ASGIConnection <litestar.connection.ASGIConnection>` instance.

        Returns:
            Either a dictionary with the connection's parsed query string or the raw query byte-string.
        """
        return connection.query_params.dict() if self.parse_query else connection.scope.get("query_string", b"")

    @staticmethod
    def extract_path_params(connection: ASGIConnection[Any, Any, Any, Any]) -> dict[str, Any]:
        """Extract the path parameters from an ``ASGIConnection``

        Args:
            connection: An :class:`ASGIConnection <litestar.connection.ASGIConnection>` instance.

        Returns:
            A dictionary with the connection's path parameters.
        """
        return connection.path_params

    @staticmethod
    def extract_method(request: Request[Any, Any, Any]) -> Method:
        """Extract the method from an ``ASGIConnection``

        Args:
            request: A :class:`Request <litestar.connection.Request>` instance.

        Returns:
            The request's scope["method"] value.
        """
        return request.scope["method"]

    @staticmethod
    def extract_content_type(request: Request[Any, Any, Any]) -> tuple[str, dict[str, str]]:
        """Extract the content-type from an ``ASGIConnection``

        Args:
            request: A :class:`Request <litestar.connection.Request>` instance.

        Returns:
            A tuple containing the request's parsed 'Content-Type' header.
        """
        return request.content_type

    async def extract_body(self, request: Request[Any, Any, Any]) -> Any:
        """Extract the body from an ``ASGIConnection``

        Args:
            request: A :class:`Request <litestar.connection.Request>` instance.

        Returns:
            Either the parsed request body or the raw byte-string.
        """
        if request.method == HttpMethod.GET:
            return None
        if not self.parse_body:
            return await request.body()
        try:
            request_encoding_type = request.content_type[0]
            if request_encoding_type == RequestEncodingType.JSON:
                return await request.json()
            form_data = await request.form()
            if request_encoding_type == RequestEncodingType.URL_ENCODED:
                return dict(form_data)
            return {
                key: repr(value) if isinstance(value, UploadFile) else value for key, value in form_data.multi_items()
            }
        except Exception as exc:
            if self.skip_parse_malformed_body:
                return await request.body()
            raise exc


class ExtractedResponseData(TypedDict, total=False):
    """Dictionary representing extracted response data."""

    body: bytes
    status_code: int
    headers: dict[str, str]
    cookies: dict[str, str]


class ResponseDataExtractor:
    """Utility class to extract data from a ``Message``"""

    __slots__ = ("extractors", "parse_headers", "obfuscate_headers", "obfuscate_cookies")

    def __init__(
        self,
        extract_body: bool = True,
        extract_cookies: bool = True,
        extract_headers: bool = True,
        extract_status_code: bool = True,
        obfuscate_cookies: set[str] | None = None,
        obfuscate_headers: set[str] | None = None,
    ) -> None:
        """Initialize ``ResponseDataExtractor`` with options.

        Args:
            extract_body: Whether to extract the body.
            extract_cookies: Whether to extract the cookies.
            extract_headers: Whether to extract the headers.
            extract_status_code: Whether to extract the status code.
            obfuscate_cookies: cookie keys to obfuscate. Obfuscated values are replaced with '*****'.
            obfuscate_headers: headers keys to obfuscate. Obfuscated values are replaced with '*****'.
        """
        self.obfuscate_headers = {h.lower() for h in (obfuscate_headers or set())}
        self.obfuscate_cookies = {c.lower() for c in (obfuscate_cookies or set())}
        self.extractors: dict[
            ResponseExtractorField, Callable[[tuple[HTTPResponseStartEvent, HTTPResponseBodyEvent]], Any]
        ] = {}
        if extract_body:
            self.extractors["body"] = self.extract_response_body
        if extract_status_code:
            self.extractors["status_code"] = self.extract_status_code
        if extract_headers:
            self.extractors["headers"] = self.extract_headers
        if extract_cookies:
            self.extractors["cookies"] = self.extract_cookies

    def __call__(self, messages: tuple[HTTPResponseStartEvent, HTTPResponseBodyEvent]) -> ExtractedResponseData:
        """Extract data from the response, returning a dictionary of values.

        Args:
            messages: A tuple containing
                :class:`HTTPResponseStartEvent <litestar.types.asgi_types.HTTPResponseStartEvent>`
                and :class:`HTTPResponseBodyEvent <litestar.types.asgi_types.HTTPResponseBodyEvent>`.

        Returns:
            A string keyed dictionary of extracted values.
        """
        return cast("ExtractedResponseData", {key: extractor(messages) for key, extractor in self.extractors.items()})

    @staticmethod
    def extract_response_body(messages: tuple[HTTPResponseStartEvent, HTTPResponseBodyEvent]) -> bytes:
        """Extract the response body from a ``Message``

        Args:
            messages: A tuple containing
                :class:`HTTPResponseStartEvent <litestar.types.asgi_types.HTTPResponseStartEvent>`
                and :class:`HTTPResponseBodyEvent <litestar.types.asgi_types.HTTPResponseBodyEvent>`.

        Returns:
            The Response's body as a byte-string.
        """
        return messages[1]["body"]

    @staticmethod
    def extract_status_code(messages: tuple[HTTPResponseStartEvent, HTTPResponseBodyEvent]) -> int:
        """Extract a status code from a ``Message``

        Args:
            messages: A tuple containing
                :class:`HTTPResponseStartEvent <litestar.types.asgi_types.HTTPResponseStartEvent>`
                and :class:`HTTPResponseBodyEvent <litestar.types.asgi_types.HTTPResponseBodyEvent>`.

        Returns:
            The Response's status-code.
        """
        return messages[0]["status"]

    def extract_headers(self, messages: tuple[HTTPResponseStartEvent, HTTPResponseBodyEvent]) -> dict[str, str]:
        """Extract headers from a ``Message``

        Args:
            messages: A tuple containing
                :class:`HTTPResponseStartEvent <litestar.types.asgi_types.HTTPResponseStartEvent>`
                and :class:`HTTPResponseBodyEvent <litestar.types.asgi_types.HTTPResponseBodyEvent>`.

        Returns:
            The Response's headers dict.
        """
        headers = {
            key.decode("latin-1"): value.decode("latin-1")
            for key, value in filter(lambda x: x[0].lower() != b"set-cookie", messages[0]["headers"])
        }
        return (
            _obfuscate(
                headers,
                self.obfuscate_headers,
            )
            if self.obfuscate_headers
            else headers
        )

    def extract_cookies(self, messages: tuple[HTTPResponseStartEvent, HTTPResponseBodyEvent]) -> dict[str, str]:
        """Extract cookies from a ``Message``

        Args:
            messages: A tuple containing
                :class:`HTTPResponseStartEvent <litestar.types.asgi_types.HTTPResponseStartEvent>`
                and :class:`HTTPResponseBodyEvent <litestar.types.asgi_types.HTTPResponseBodyEvent>`.

        Returns:
            The Response's cookies dict.
        """
        if cookie_string := ";".join(
            [x[1].decode("latin-1") for x in filter(lambda x: x[0].lower() == b"set-cookie", messages[0]["headers"])]
        ):
            parsed_cookies = parse_cookie_string(cookie_string)
            return _obfuscate(parsed_cookies, self.obfuscate_cookies) if self.obfuscate_cookies else parsed_cookies
        return {}
