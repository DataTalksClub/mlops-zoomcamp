from enum import Enum

__all__ = (
    "CompressionEncoding",
    "HttpMethod",
    "MediaType",
    "OpenAPIMediaType",
    "ParamType",
    "RequestEncodingType",
    "ScopeType",
)


class HttpMethod(str, Enum):
    """An Enum for HTTP methods."""

    DELETE = "DELETE"
    GET = "GET"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    POST = "POST"
    PUT = "PUT"
    TRACE = "TRACE"


class MediaType(str, Enum):
    """An Enum for ``Content-Type`` header values."""

    JSON = "application/json"
    MESSAGEPACK = "application/x-msgpack"
    HTML = "text/html"
    TEXT = "text/plain"
    CSS = "text/css"
    XML = "application/xml"


class OpenAPIMediaType(str, Enum):
    """An Enum for OpenAPI specific response ``Content-Type`` header values."""

    OPENAPI_YAML = "application/vnd.oai.openapi"
    OPENAPI_JSON = "application/vnd.oai.openapi+json"


class RequestEncodingType(str, Enum):
    """An Enum for request ``Content-Type`` header values designating encoding formats."""

    JSON = "application/json"
    MESSAGEPACK = "application/x-msgpack"
    MULTI_PART = "multipart/form-data"
    URL_ENCODED = "application/x-www-form-urlencoded"


class ScopeType(str, Enum):
    """An Enum for the 'http' key stored under Scope.

    Notes:
        - ``asgi`` is used by Litestar internally and is not part of the specification.
    """

    HTTP = "http"
    WEBSOCKET = "websocket"
    ASGI = "asgi"


class ParamType(str, Enum):
    """An Enum for the types of parameters a request can receive."""

    PATH = "path"
    QUERY = "query"
    COOKIE = "cookie"
    HEADER = "header"


class CompressionEncoding(str, Enum):
    """An Enum for supported compression encodings."""

    GZIP = "gzip"
    BROTLI = "br"


class ASGIExtension(str, Enum):
    """ASGI extension keys: https://asgi.readthedocs.io/en/latest/extensions.html"""

    WS_DENIAL = "websocket.http.response"
    SERVER_PUSH = "http.response.push"
    ZERO_COPY_SEND_EXTENSION = "http.response.zerocopysend"
    PATH_SEND = "http.response.pathsend"
    TLS = "tls"
    EARLY_HINTS = "http.response.early_hint"
    HTTP_TRAILERS = "http.response.trailers"
