from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, final
from urllib.parse import urlencode

from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_300_MULTIPLE_CHOICES,
    HTTP_301_MOVED_PERMANENTLY,
    HTTP_308_PERMANENT_REDIRECT,
)

if TYPE_CHECKING:
    from litestar import Litestar
    from litestar.connection import Request
    from litestar.stores.base import Store
    from litestar.types import CacheKeyBuilder, HTTPScope

__all__ = ("ResponseCacheConfig", "default_cache_key_builder", "CACHE_FOREVER")


@final
class CACHE_FOREVER:  # noqa: N801
    """Sentinel value indicating that a cached response should be stored without an expiration, explicitly skipping the
    default expiration
    """


def default_cache_key_builder(request: Request[Any, Any, Any]) -> str:
    """Given a request object, returns a cache key by combining
    the request method and path with the sorted query params.

    Args:
        request: request used to generate cache key.

    Returns:
        A combination of url path and query parameters
    """
    query_params: list[tuple[str, Any]] = list(request.query_params.dict().items())
    query_params.sort(key=lambda x: x[0])
    return request.method + request.url.path + urlencode(query_params, doseq=True)


def default_do_cache_predicate(_: HTTPScope, status_code: int) -> bool:
    """Given a status code, returns a boolean indicating whether the response should be cached.

    Args:
        _: ASGI scope.
        status_code: status code of the response.

    Returns:
        A boolean indicating whether the response should be cached.
    """
    return HTTP_200_OK <= status_code < HTTP_300_MULTIPLE_CHOICES or status_code in (
        HTTP_301_MOVED_PERMANENTLY,
        HTTP_308_PERMANENT_REDIRECT,
    )


@dataclass
class ResponseCacheConfig:
    """Configuration for response caching.

    To enable response caching, pass an instance of this class to :class:`Litestar <.app.Litestar>` using the
    ``response_cache_config`` key.
    """

    default_expiration: int | None = 60
    """Default cache expiration in seconds used when a route handler is configured with ``cache=True``."""
    key_builder: CacheKeyBuilder = field(default=default_cache_key_builder)
    """:class:`CacheKeyBuilder <.types.CacheKeyBuilder>`. Defaults to :func:`default_cache_key_builder`."""
    store: str = "response_cache"
    """Name of the :class:`Store <.stores.base.Store>` to use."""
    cache_response_filter: Callable[[HTTPScope, int], bool] = field(default=default_do_cache_predicate)
    """A callable that receives connection scope and a status code, and returns a boolean indicating whether the
    response should be cached."""

    def get_store_from_app(self, app: Litestar) -> Store:
        """Get the store defined in :attr:`store` from an :class:`Litestar <.app.Litestar>` instance."""
        return app.stores.get(self.store)
