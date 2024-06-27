from __future__ import annotations

from io import BytesIO
from types import GeneratorType
from typing import TYPE_CHECKING, Any, Generic, TypedDict, TypeVar, Union, cast
from urllib.parse import unquote

from anyio import Event
from httpx import ByteStream, Response

from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR
from litestar.testing.websocket_test_session import WebSocketTestSession

if TYPE_CHECKING:
    from httpx import Request

    from litestar.testing.client import AsyncTestClient, TestClient
    from litestar.types import (
        HTTPDisconnectEvent,
        HTTPRequestEvent,
        Message,
        Receive,
        ReceiveMessage,
        Send,
        WebSocketScope,
    )


T = TypeVar("T", bound=Union["AsyncTestClient", "TestClient"])


class ConnectionUpgradeExceptionError(Exception):
    def __init__(self, session: WebSocketTestSession) -> None:
        self.session = session


class SendReceiveContext(TypedDict):
    request_complete: bool
    response_complete: Event
    raw_kwargs: dict[str, Any]
    response_started: bool
    template: str | None
    context: Any | None


class TestClientTransport(Generic[T]):
    def __init__(
        self,
        client: T,
        raise_server_exceptions: bool = True,
        root_path: str = "",
    ) -> None:
        self.client = client
        self.raise_server_exceptions = raise_server_exceptions
        self.root_path = root_path

    @staticmethod
    def create_receive(request: Request, context: SendReceiveContext) -> Receive:
        async def receive() -> ReceiveMessage:
            if context["request_complete"]:
                if not context["response_complete"].is_set():
                    await context["response_complete"].wait()
                disconnect_event: HTTPDisconnectEvent = {"type": "http.disconnect"}
                return disconnect_event

            body = cast("Union[bytes, str, GeneratorType]", (request.read() or b""))
            request_event: HTTPRequestEvent = {"type": "http.request", "body": b"", "more_body": False}
            if isinstance(body, GeneratorType):  # pragma: no cover
                try:
                    chunk = body.send(None)
                    request_event["body"] = chunk if isinstance(chunk, bytes) else chunk.encode("utf-8")
                    request_event["more_body"] = True
                except StopIteration:
                    context["request_complete"] = True
            else:
                context["request_complete"] = True
                request_event["body"] = body if isinstance(body, bytes) else body.encode("utf-8")
            return request_event

        return receive

    @staticmethod
    def create_send(request: Request, context: SendReceiveContext) -> Send:
        async def send(message: Message) -> None:
            if message["type"] == "http.response.start":
                assert not context["response_started"], 'Received multiple "http.response.start" messages.'  # noqa: S101
                context["raw_kwargs"]["status_code"] = message["status"]
                context["raw_kwargs"]["headers"] = [
                    (k.decode("utf-8"), v.decode("utf-8")) for k, v in message.get("headers", [])
                ]
                context["response_started"] = True
            elif message["type"] == "http.response.body":
                assert context["response_started"], 'Received "http.response.body" without "http.response.start".'  # noqa: S101
                assert not context[  # noqa: S101
                    "response_complete"
                ].is_set(), 'Received "http.response.body" after response completed.'
                body = message.get("body", b"")
                more_body = message.get("more_body", False)
                if request.method != "HEAD":
                    context["raw_kwargs"]["stream"].write(body)
                if not more_body:
                    context["raw_kwargs"]["stream"].seek(0)
                    context["response_complete"].set()
            elif message["type"] == "http.response.template":  # type: ignore[comparison-overlap] # pragma: no cover
                context["template"] = message["template"]  # type: ignore[unreachable]
                context["context"] = message["context"]

        return send

    def parse_request(self, request: Request) -> dict[str, Any]:
        scheme = request.url.scheme
        netloc = unquote(request.url.netloc.decode(encoding="ascii"))
        path = request.url.path
        raw_path = request.url.raw_path
        query = request.url.query.decode(encoding="ascii")
        default_port = 433 if scheme in {"https", "wss"} else 80

        if ":" in netloc:
            host, port_string = netloc.split(":", 1)
            port = int(port_string)
        else:
            host = netloc
            port = default_port

        host_header = request.headers.pop("host", host if port == default_port else f"{host}:{port}")

        headers = [(k.lower().encode(), v.encode()) for k, v in (("host", host_header), *request.headers.items())]

        return {
            "type": "websocket" if scheme in {"ws", "wss"} else "http",
            "path": unquote(path),
            "raw_path": raw_path,
            "root_path": self.root_path,
            "scheme": scheme,
            "query_string": query.encode(),
            "headers": headers,
            "client": ("testclient", 50000),
            "server": (host, port),
        }

    def handle_request(self, request: Request) -> Response:
        scope = self.parse_request(request=request)
        if scope["type"] == "websocket":
            scope.update(
                subprotocols=[value.strip() for value in request.headers.get("sec-websocket-protocol", "").split(",")]
            )
            session = WebSocketTestSession(client=self.client, scope=cast("WebSocketScope", scope))  # type: ignore[arg-type]
            raise ConnectionUpgradeExceptionError(session)

        scope.update(method=request.method, http_version="1.1", extensions={"http.response.template": {}})

        raw_kwargs: dict[str, Any] = {"stream": BytesIO()}

        try:
            with self.client.portal() as portal:
                response_complete = portal.call(Event)
                context: SendReceiveContext = {
                    "response_complete": response_complete,
                    "request_complete": False,
                    "raw_kwargs": raw_kwargs,
                    "response_started": False,
                    "template": None,
                    "context": None,
                }
                portal.call(
                    self.client.app,
                    scope,
                    self.create_receive(request=request, context=context),
                    self.create_send(request=request, context=context),
                )
        except BaseException as exc:
            if self.raise_server_exceptions:
                raise exc
            return Response(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR, headers=[], stream=ByteStream(b""), request=request
            )
        else:
            if not context["response_started"]:  # pragma: no cover
                if self.raise_server_exceptions:
                    assert context["response_started"], "TestClient did not receive any response."  # noqa: S101
                return Response(
                    status_code=HTTP_500_INTERNAL_SERVER_ERROR, headers=[], stream=ByteStream(b""), request=request
                )

            stream = ByteStream(raw_kwargs.pop("stream", BytesIO()).read())
            response = Response(**raw_kwargs, stream=stream, request=request)
            setattr(response, "template", context["template"])
            setattr(response, "context", context["context"])
            return response

    async def handle_async_request(self, request: Request) -> Response:
        return self.handle_request(request=request)
