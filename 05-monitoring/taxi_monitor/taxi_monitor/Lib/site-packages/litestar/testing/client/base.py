from __future__ import annotations

from contextlib import contextmanager
from http.cookiejar import CookieJar
from typing import TYPE_CHECKING, Any, Generator, Generic, Mapping, Sequence, TypeVar, cast
from warnings import warn

import httpx
from anyio.from_thread import BlockingPortal, start_blocking_portal
from httpx import Cookies, Request, Response
from httpx._client import USE_CLIENT_DEFAULT, BaseClient, UseClientDefault

from litestar import Litestar
from litestar.connection import ASGIConnection
from litestar.datastructures import MutableScopeHeaders
from litestar.enums import ScopeType
from litestar.exceptions import (
    ImproperlyConfiguredException,
)
from litestar.types import AnyIOBackend, ASGIApp, HTTPResponseStartEvent
from litestar.utils.scope.state import ScopeState

if TYPE_CHECKING:
    from httpx._types import (
        CookieTypes,
        HeaderTypes,
        QueryParamTypes,
        TimeoutTypes,
    )

    from litestar.middleware.session.base import BaseBackendConfig, BaseSessionBackend
    from litestar.types.asgi_types import HTTPScope, Receive, Scope, Send

T = TypeVar("T", bound=ASGIApp)


def fake_http_send_message(headers: MutableScopeHeaders) -> HTTPResponseStartEvent:
    headers.setdefault("content-type", "application/text")
    return HTTPResponseStartEvent(type="http.response.start", status=200, headers=headers.headers)


def fake_asgi_connection(app: ASGIApp, cookies: dict[str, str]) -> ASGIConnection[Any, Any, Any, Any]:
    scope: HTTPScope = {
        "type": ScopeType.HTTP,
        "path": "/",
        "raw_path": b"/",
        "root_path": "",
        "scheme": "http",
        "query_string": b"",
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
        "headers": [],
        "method": "GET",
        "http_version": "1.1",
        "extensions": {"http.response.template": {}},
        "app": app,  # type: ignore[typeddict-item]
        "state": {},
        "path_params": {},
        "route_handler": None,  # type: ignore[typeddict-item]
        "asgi": {"version": "3.0", "spec_version": "2.1"},
        "auth": None,
        "session": None,
        "user": None,
    }
    ScopeState.from_scope(scope).cookies = cookies
    return ASGIConnection[Any, Any, Any, Any](scope=scope)


def _wrap_app_to_add_state(app: ASGIApp) -> ASGIApp:
    """Wrap an ASGI app to add state to the scope.

    Litestar depends on `state` being present in the ASGI connection scope. Scope state is optional in the ASGI spec,
    however, the Litestar app always ensures it is present so that it can be depended on internally.

    When the ASGI app that is passed to the test client is _not_ a Litestar app, we need to add
    state to the scope, because httpx does not do this for us.

    This assists us in testing Litestar components that rely on state being present in the scope, without having
    to create a Litestar app for every test case.

    Args:
        app: The ASGI app to wrap.

    Returns:
        The wrapped ASGI app.
    """

    async def wrapped(scope: Scope, receive: Receive, send: Send) -> None:
        scope["state"] = {}
        await app(scope, receive, send)

    return wrapped


class BaseTestClient(Generic[T]):
    __test__ = False
    blocking_portal: BlockingPortal

    __slots__ = (
        "app",
        "base_url",
        "backend",
        "backend_options",
        "session_config",
        "_session_backend",
        "cookies",
    )

    def __init__(
        self,
        app: T,
        base_url: str = "http://testserver.local",
        backend: AnyIOBackend = "asyncio",
        backend_options: Mapping[str, Any] | None = None,
        session_config: BaseBackendConfig | None = None,
        cookies: CookieTypes | None = None,
    ) -> None:
        if "." not in base_url:
            warn(
                f"The base_url {base_url!r} might cause issues. Try adding a domain name such as .local: "
                f"'{base_url}.local'",
                UserWarning,
                stacklevel=1,
            )

        self._session_backend: BaseSessionBackend | None = None
        if session_config:
            self._session_backend = session_config._backend_class(config=session_config)

        if not isinstance(app, Litestar):
            app = _wrap_app_to_add_state(app)  # type: ignore[assignment]

        self.app = cast("T", app)  # type: ignore[redundant-cast]  # pyright needs this

        self.base_url = base_url
        self.backend = backend
        self.backend_options = backend_options
        self.cookies = cookies

    @property
    def session_backend(self) -> BaseSessionBackend[Any]:
        if not self._session_backend:
            raise ImproperlyConfiguredException(
                "Session has not been initialized for this TestClient instance. You can"
                "do so by passing a configuration object to TestClient: TestClient(app=app, session_config=...)"
            )
        return self._session_backend

    @contextmanager
    def portal(self) -> Generator[BlockingPortal, None, None]:
        """Get a BlockingPortal.

        Returns:
            A contextmanager for a BlockingPortal.
        """
        if hasattr(self, "blocking_portal"):
            yield self.blocking_portal
        else:
            with start_blocking_portal(
                backend=self.backend, backend_options=dict(self.backend_options or {})
            ) as portal:
                yield portal

    async def _set_session_data(self, data: dict[str, Any]) -> None:
        mutable_headers = MutableScopeHeaders()
        connection = fake_asgi_connection(
            app=self.app,
            cookies=dict(self.cookies),  # type: ignore[arg-type]
        )
        session_id = self.session_backend.get_session_id(connection)
        connection._connection_state.session_id = session_id  # pyright: ignore [reportGeneralTypeIssues]
        await self.session_backend.store_in_message(
            scope_session=data, message=fake_http_send_message(mutable_headers), connection=connection
        )
        response = Response(200, request=Request("GET", self.base_url), headers=mutable_headers.headers)

        cookies = Cookies(CookieJar())
        cookies.extract_cookies(response)
        self.cookies.update(cookies)  # type: ignore[union-attr]

    async def _get_session_data(self) -> dict[str, Any]:
        return await self.session_backend.load_from_connection(
            connection=fake_asgi_connection(
                app=self.app,
                cookies=dict(self.cookies),  # type: ignore[arg-type]
            ),
        )

    def _prepare_ws_connect_request(  # type: ignore[misc]
        self: BaseClient,  # pyright: ignore
        url: str,
        subprotocols: Sequence[str] | None = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        extensions: Mapping[str, Any] | None = None,
    ) -> httpx.Request:
        default_headers: dict[str, str] = {}
        default_headers.setdefault("connection", "upgrade")
        default_headers.setdefault("sec-websocket-key", "testserver==")
        default_headers.setdefault("sec-websocket-version", "13")
        if subprotocols is not None:
            default_headers.setdefault("sec-websocket-protocol", ", ".join(subprotocols))
        return self.build_request(
            "GET",
            self.base_url.copy_with(scheme="ws").join(url),
            headers={**dict(headers or {}), **default_headers},  # type: ignore[misc]
            params=params,
            cookies=cookies,
            extensions=None if extensions is None else dict(extensions),
            timeout=timeout,
        )
