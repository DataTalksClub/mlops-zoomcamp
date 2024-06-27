from __future__ import annotations

from dataclasses import MISSING
from inspect import Signature
from typing import Any, Final
from uuid import uuid4

from msgspec import UnsetType

from litestar.enums import MediaType
from litestar.types import Empty
from litestar.utils.deprecation import warn_deprecation

DEFAULT_ALLOWED_CORS_HEADERS: Final = {"Accept", "Accept-Language", "Content-Language", "Content-Type"}
DEFAULT_CHUNK_SIZE: Final = 1024 * 128  # 128KB
HTTP_DISCONNECT: Final = "http.disconnect"
HTTP_RESPONSE_BODY: Final = "http.response.body"
HTTP_RESPONSE_START: Final = "http.response.start"
ONE_MEGABYTE: Final = 1024 * 1024
OPENAPI_JSON_HANDLER_NAME: Final = f"{uuid4().hex}_litestar_openapi_json"
OPENAPI_NOT_INITIALIZED: Final = "Litestar has not been instantiated with OpenAPIConfig"
REDIRECT_STATUS_CODES: Final = {301, 302, 303, 307, 308}
REDIRECT_ALLOWED_MEDIA_TYPES: Final = {MediaType.TEXT, MediaType.HTML, MediaType.JSON}
RESERVED_KWARGS: Final = {"state", "headers", "cookies", "request", "socket", "data", "query", "scope", "body"}
SKIP_VALIDATION_NAMES: Final = {"request", "socket", "scope", "receive", "send"}
UNDEFINED_SENTINELS: Final = {Signature.empty, Empty, Ellipsis, MISSING, UnsetType}
WEBSOCKET_CLOSE: Final = "websocket.close"
WEBSOCKET_DISCONNECT: Final = "websocket.disconnect"

# deprecated constants
_SCOPE_STATE_CSRF_TOKEN_KEY = "csrf_token"  # noqa: S105  # possible hardcoded password
_SCOPE_STATE_DEPENDENCY_CACHE: Final = "dependency_cache"
_SCOPE_STATE_NAMESPACE: Final = "__litestar__"
_SCOPE_STATE_RESPONSE_COMPRESSED: Final = "response_compressed"
_SCOPE_STATE_DO_CACHE: Final = "do_cache"
_SCOPE_STATE_IS_CACHED: Final = "is_cached"

_deprecated_names = {
    "SCOPE_STATE_CSRF_TOKEN_KEY": _SCOPE_STATE_CSRF_TOKEN_KEY,
    "SCOPE_STATE_DEPENDENCY_CACHE": _SCOPE_STATE_DEPENDENCY_CACHE,
    "SCOPE_STATE_NAMESPACE": _SCOPE_STATE_NAMESPACE,
    "SCOPE_STATE_RESPONSE_COMPRESSED": _SCOPE_STATE_RESPONSE_COMPRESSED,
    "SCOPE_STATE_DO_CACHE": _SCOPE_STATE_DO_CACHE,
    "SCOPE_STATE_IS_CACHED": _SCOPE_STATE_IS_CACHED,
}


def __getattr__(name: str) -> Any:
    if name in _deprecated_names:
        warn_deprecation(
            deprecated_name=f"litestar.constants.{name}",
            version="2.4",
            kind="import",
            removal_in="3.0",
            info=f"'{name}' from 'litestar.constants' is deprecated and will be removed in 3.0. "
            "Direct access to Litestar scope state is not recommended.",
        )

        return globals()["_deprecated_names"][name]
    raise AttributeError(f"module {__name__} has no attribute {name}")  # pragma: no cover
