from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final

from litestar.types import Empty, EmptyType
from litestar.utils.empty import value_or_default

if TYPE_CHECKING:
    from typing_extensions import Self

    from litestar.datastructures import URL, Accept, Headers
    from litestar.types.asgi_types import Scope
    from litestar.types.composite_types import ExceptionHandlersMap

CONNECTION_STATE_KEY: Final = "_ls_connection_state"


@dataclass
class ScopeState:
    """An object for storing connection state.

    This is an internal API, and subject to change without notice.

    All types are a union with `EmptyType` and are seeded with the `Empty` value.
    """

    __slots__ = (
        "accept",
        "base_url",
        "body",
        "content_type",
        "cookies",
        "csrf_token",
        "dependency_cache",
        "do_cache",
        "exception_handlers",
        "flash_messages",
        "form",
        "headers",
        "is_cached",
        "json",
        "log_context",
        "msgpack",
        "parsed_query",
        "response_compressed",
        "response_started",
        "session_id",
        "url",
        "_compat_ns",
    )

    def __init__(self) -> None:
        self.accept = Empty
        self.base_url = Empty
        self.body = Empty
        self.content_type = Empty
        self.cookies = Empty
        self.csrf_token = Empty
        self.dependency_cache = Empty
        self.do_cache = Empty
        self.exception_handlers = Empty
        self.form = Empty
        self.flash_messages = []
        self.headers = Empty
        self.is_cached = Empty
        self.json = Empty
        self.log_context: dict[str, Any] = {}
        self.msgpack = Empty
        self.parsed_query = Empty
        self.response_compressed = Empty
        self.response_started = False
        self.session_id = Empty
        self.url = Empty
        self._compat_ns: dict[str, Any] = {}

    accept: Accept | EmptyType
    base_url: URL | EmptyType
    body: bytes | EmptyType
    content_type: tuple[str, dict[str, str]] | EmptyType
    cookies: dict[str, str] | EmptyType
    csrf_token: str | EmptyType
    dependency_cache: dict[str, Any] | EmptyType
    do_cache: bool | EmptyType
    exception_handlers: ExceptionHandlersMap | EmptyType
    form: dict[str, str | list[str]] | EmptyType
    flash_messages: list[dict[str, str]]
    headers: Headers | EmptyType
    is_cached: bool | EmptyType
    json: Any | EmptyType
    log_context: dict[str, Any]
    msgpack: Any | EmptyType
    parsed_query: tuple[tuple[str, str], ...] | EmptyType
    response_compressed: bool | EmptyType
    response_started: bool
    session_id: str | None | EmptyType
    url: URL | EmptyType
    _compat_ns: dict[str, Any]

    @classmethod
    def from_scope(cls, scope: Scope) -> Self:
        """Create a new `ConnectionState` object from a scope.

        Object is cached in the scope's state under the `SCOPE_STATE_NAMESPACE` key.

        Args:
            scope: The ASGI connection scope.

        Returns:
            A `ConnectionState` object.
        """
        base_scope_state = scope.setdefault("state", {})
        if (state := base_scope_state.get(CONNECTION_STATE_KEY)) is None:
            state = base_scope_state[CONNECTION_STATE_KEY] = cls()
        return state


def get_litestar_scope_state(scope: Scope, key: str, default: Any = None, pop: bool = False) -> Any:
    """Get an internal value from connection scope state.

    Args:
        scope: The connection scope.
        key: Key to get from internal namespace in scope state.
        default: Default value to return.
        pop: Boolean flag dictating whether the value should be deleted from the state.

    Returns:
        Value mapped to ``key`` in internal connection scope namespace.
    """
    scope_state = ScopeState.from_scope(scope)
    try:
        val = value_or_default(getattr(scope_state, key), default)
        if pop:
            setattr(scope_state, key, Empty)
        return val
    except AttributeError:
        if pop:
            return scope_state._compat_ns.pop(key, default)
        return scope_state._compat_ns.get(key, default)


def set_litestar_scope_state(scope: Scope, key: str, value: Any) -> None:
    """Set an internal value in connection scope state.

    Args:
        scope: The connection scope.
        key: Key to set under internal namespace in scope state.
        value: Value for key.
    """
    scope_state = ScopeState.from_scope(scope)
    if hasattr(scope_state, key):
        setattr(scope_state, key, value)
    else:
        scope_state._compat_ns[key] = value


def delete_litestar_scope_state(scope: Scope, key: str) -> None:
    """Delete an internal value from connection scope state.

    Args:
        scope: The connection scope.
        key: Key to set under internal namespace in scope state.
    """
    scope_state = ScopeState.from_scope(scope)
    if hasattr(scope_state, key):
        setattr(scope_state, key, Empty)
    else:
        del scope_state._compat_ns[key]
