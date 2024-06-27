from __future__ import annotations

from contextlib import ExitStack
from typing import TYPE_CHECKING, Any, Generic, Mapping, Sequence, TypeVar

from httpx import USE_CLIENT_DEFAULT, Client

from litestar.testing.client.base import BaseTestClient
from litestar.testing.life_span_handler import LifeSpanHandler
from litestar.testing.transport import ConnectionUpgradeExceptionError, TestClientTransport
from litestar.types import AnyIOBackend, ASGIApp

if TYPE_CHECKING:
    from httpx._client import UseClientDefault
    from httpx._types import (
        AuthTypes,
        CookieTypes,
        HeaderTypes,
        QueryParamTypes,
        TimeoutTypes,
    )
    from typing_extensions import Self

    from litestar.middleware.session.base import BaseBackendConfig
    from litestar.testing.websocket_test_session import WebSocketTestSession


T = TypeVar("T", bound=ASGIApp)


class TestClient(Client, BaseTestClient, Generic[T]):  # type: ignore[misc]
    lifespan_handler: LifeSpanHandler[Any]
    exit_stack: ExitStack

    def __init__(
        self,
        app: T,
        base_url: str = "http://testserver.local",
        raise_server_exceptions: bool = True,
        root_path: str = "",
        backend: AnyIOBackend = "asyncio",
        backend_options: Mapping[str, Any] | None = None,
        session_config: BaseBackendConfig | None = None,
        timeout: float | None = None,
        cookies: CookieTypes | None = None,
    ) -> None:
        """A client implementation providing a context manager for testing applications.

        Args:
            app: The instance of :class:`Litestar <litestar.app.Litestar>` under test.
            base_url: URL scheme and domain for test request paths, e.g. ``http://testserver``.
            raise_server_exceptions: Flag for the underlying test client to raise server exceptions instead of
                wrapping them in an HTTP response.
            root_path: Path prefix for requests.
            backend: The async backend to use, options are "asyncio" or "trio".
            backend_options: ``anyio`` options.
            session_config: Configuration for Session Middleware class to create raw session cookies for request to the
                route handlers.
            timeout: Request timeout
            cookies: Cookies to set on the client.
        """
        BaseTestClient.__init__(
            self,
            app=app,
            base_url=base_url,
            backend=backend,
            backend_options=backend_options,
            session_config=session_config,
            cookies=cookies,
        )

        Client.__init__(
            self,
            base_url=base_url,
            headers={"user-agent": "testclient"},
            follow_redirects=True,
            cookies=cookies,
            transport=TestClientTransport(  # type: ignore[arg-type]
                client=self,
                raise_server_exceptions=raise_server_exceptions,
                root_path=root_path,
            ),
            timeout=timeout,
        )

    def __enter__(self) -> Self:
        with ExitStack() as stack:
            self.blocking_portal = portal = stack.enter_context(self.portal())
            self.lifespan_handler = LifeSpanHandler(client=self)

            @stack.callback
            def reset_portal() -> None:
                delattr(self, "blocking_portal")

            @stack.callback
            def wait_shutdown() -> None:
                portal.call(self.lifespan_handler.wait_shutdown)

            self.exit_stack = stack.pop_all()

        return self

    def __exit__(self, *args: Any) -> None:
        self.exit_stack.close()

    def websocket_connect(
        self,
        url: str,
        subprotocols: Sequence[str] | None = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
        timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        extensions: Mapping[str, Any] | None = None,
    ) -> WebSocketTestSession:
        """Sends a GET request to establish a websocket connection.

        Args:
            url: Request URL.
            subprotocols: Websocket subprotocols.
            params: Query parameters.
            headers: Request headers.
            cookies: Request cookies.
            auth: Auth headers.
            follow_redirects: Whether to follow redirects.
            timeout: Request timeout.
            extensions: Dictionary of ASGI extensions.

        Returns:
            A `WebSocketTestSession <litestar.testing.WebSocketTestSession>` instance.
        """
        try:
            self.send(
                self._prepare_ws_connect_request(
                    url=url,
                    subprotocols=subprotocols,
                    params=params,
                    headers=headers,
                    cookies=cookies,
                    extensions=extensions,
                    timeout=timeout,
                ),
                auth=auth,
                follow_redirects=follow_redirects,
            )
        except ConnectionUpgradeExceptionError as exc:
            return exc.session

        raise RuntimeError("Expected WebSocket upgrade")  # pragma: no cover

    def set_session_data(self, data: dict[str, Any]) -> None:
        """Set session data.

        Args:
            data: Session data

        Returns:
            None

        Examples:
            .. code-block:: python

                from litestar import Litestar, get
                from litestar.middleware.session.memory_backend import MemoryBackendConfig

                session_config = MemoryBackendConfig()


                @get(path="/test")
                def get_session_data(request: Request) -> Dict[str, Any]:
                    return request.session


                app = Litestar(
                    route_handlers=[get_session_data], middleware=[session_config.middleware]
                )

                with TestClient(app=app, session_config=session_config) as client:
                    client.set_session_data({"foo": "bar"})
                    assert client.get("/test").json() == {"foo": "bar"}

        """
        with self.portal() as portal:
            portal.call(self._set_session_data, data)

    def get_session_data(self) -> dict[str, Any]:
        """Get session data.

        Returns:
            A dictionary containing session data.

        Examples:
            .. code-block:: python

                from litestar import Litestar, post
                from litestar.middleware.session.memory_backend import MemoryBackendConfig

                session_config = MemoryBackendConfig()


                @post(path="/test")
                def set_session_data(request: Request) -> None:
                    request.session["foo"] == "bar"


                app = Litestar(
                    route_handlers=[set_session_data], middleware=[session_config.middleware]
                )

                with TestClient(app=app, session_config=session_config) as client:
                    client.post("/test")
                    assert client.get_session_data() == {"foo": "bar"}

        """
        with self.portal() as portal:
            return portal.call(self._get_session_data)
