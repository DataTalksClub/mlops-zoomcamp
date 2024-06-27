from __future__ import annotations

import asyncio
from asyncio import CancelledError, Queue, Task, create_task
from contextlib import AbstractAsyncContextManager, asynccontextmanager, suppress
from functools import partial
from typing import TYPE_CHECKING, AsyncGenerator, Awaitable, Callable, Iterable

import msgspec.json

from litestar.di import Provide
from litestar.exceptions import ImproperlyConfiguredException, LitestarException
from litestar.handlers import WebsocketRouteHandler
from litestar.plugins import InitPluginProtocol
from litestar.serialization import default_serializer

from .subscriber import BacklogStrategy, EventCallback, Subscriber

if TYPE_CHECKING:
    from types import TracebackType

    from litestar.channels.backends.base import ChannelsBackend
    from litestar.config.app import AppConfig
    from litestar.connection import WebSocket
    from litestar.types import LitestarEncodableType, TypeEncodersMap
    from litestar.types.asgi_types import WebSocketMode


class ChannelsException(LitestarException):
    pass


class ChannelsPlugin(InitPluginProtocol, AbstractAsyncContextManager):
    def __init__(
        self,
        backend: ChannelsBackend,
        *,
        channels: Iterable[str] | None = None,
        arbitrary_channels_allowed: bool = False,
        create_ws_route_handlers: bool = False,
        ws_handler_send_history: int = 0,
        ws_handler_base_path: str = "/",
        ws_send_mode: WebSocketMode = "text",
        subscriber_max_backlog: int | None = None,
        subscriber_backlog_strategy: BacklogStrategy = "backoff",
        subscriber_class: type[Subscriber] = Subscriber,
        type_encoders: TypeEncodersMap | None = None,
    ) -> None:
        """Plugin to handle broadcasting to WebSockets with support for channels.

        This plugin is available as an injected dependency using the ``channels`` key.

        Args:
            backend: Backend to store data in
            channels: Channels to serve. If ``arbitrary_channels_allowed`` is ``False`` (the default), trying to
                subscribe to a channel not in ``channels`` will raise an exception
            arbitrary_channels_allowed: Allow the creation of channels on the fly
            create_ws_route_handlers: If ``True``, websocket route handlers will be created for all channels defined in
                ``channels``. If ``arbitrary_channels_allowed`` is ``True``, a single handler will be created instead,
                handling all channels. The handlers created will accept WebSocket connections and start sending received
                events for their respective channels.
            ws_handler_send_history: Amount of history entries to send from the generated websocket route handlers after
                a client has connected. A value of ``0`` indicates to not send a history
            ws_handler_base_path: Path prefix used for the generated route handlers
            ws_send_mode: Send mode to use for sending data through a :class:`WebSocket <.connection.WebSocket>`.
                This will be used when sending within generated route handlers or :meth:`Subscriber.run_in_background`
            subscriber_max_backlog: Maximum amount of unsent messages to be held in memory for a given subscriber. If
                that limit is reached, new messages will be treated accordingly to ``backlog_strategy``
            subscriber_backlog_strategy: Define the behaviour if ``max_backlog`` is reached for a subscriber. `
                `backoff`` will result in new messages being dropped until older ones have been processed. ``dropleft``
                will drop older messages in favour of new ones.
            subscriber_class: A :class:`Subscriber` subclass to return from :meth:`subscribe`
            type_encoders: An additional mapping of type encoders used to encode data before sending

        """
        self._backend = backend
        self._pub_queue: Queue[tuple[bytes, list[str]]] | None = None
        self._pub_task: Task | None = None
        self._sub_task: Task | None = None

        if not (channels or arbitrary_channels_allowed):
            raise ImproperlyConfiguredException("Must define either channels or set arbitrary_channels_allowed=True")

        # make the path absolute, so we can simply concatenate it later
        if not ws_handler_base_path.endswith("/"):
            ws_handler_base_path += "/"

        self._arbitrary_channels_allowed = arbitrary_channels_allowed
        self._create_route_handlers = create_ws_route_handlers
        self._handler_root_path = ws_handler_base_path
        self._socket_send_mode: WebSocketMode = ws_send_mode
        self._encode_json = msgspec.json.Encoder(
            enc_hook=partial(default_serializer, type_encoders=type_encoders)
        ).encode
        self._handler_should_send_history = bool(ws_handler_send_history)
        self._history_limit = None if ws_handler_send_history < 0 else ws_handler_send_history
        self._max_backlog = subscriber_max_backlog
        self._backlog_strategy: BacklogStrategy = subscriber_backlog_strategy
        self._subscriber_class = subscriber_class

        self._channels: dict[str, set[Subscriber]] = {channel: set() for channel in channels or []}

    def encode_data(self, data: LitestarEncodableType) -> bytes:
        """Encode data before storing it in the backend"""
        if isinstance(data, bytes):
            return data

        return data.encode() if isinstance(data, str) else self._encode_json(data)

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        """Plugin hook. Set up a ``channels`` dependency, add route handlers and register application hooks"""
        app_config.dependencies["channels"] = Provide(lambda: self, use_cache=True, sync_to_thread=False)
        app_config.lifespan.append(self)
        app_config.signature_namespace.update(ChannelsPlugin=ChannelsPlugin)

        if self._create_route_handlers:
            if self._arbitrary_channels_allowed:
                path = self._handler_root_path + "{channel_name:str}"
                route_handlers = [WebsocketRouteHandler(path)(self._ws_handler_func)]
            else:
                route_handlers = [
                    WebsocketRouteHandler(self._handler_root_path + channel_name)(
                        self._create_ws_handler_func(channel_name)
                    )
                    for channel_name in self._channels
                ]
            app_config.route_handlers.extend(route_handlers)

        return app_config

    def publish(self, data: LitestarEncodableType, channels: str | Iterable[str]) -> None:
        """Schedule ``data`` to be published to ``channels``.

        .. note::
            This is a synchronous method that returns immediately. There are no
            guarantees that when this method returns the data will have been published
            to the backend. For that, use :meth:`wait_published`

        """
        if isinstance(channels, str):
            channels = [channels]
        data = self.encode_data(data)
        try:
            self._pub_queue.put_nowait((data, list(channels)))  # type: ignore[union-attr]
        except AttributeError as e:
            raise RuntimeError("Plugin not yet initialized. Did you forget to call on_startup?") from e

    async def wait_published(self, data: LitestarEncodableType, channels: str | Iterable[str]) -> None:
        """Publish ``data`` to ``channels``"""
        if isinstance(channels, str):
            channels = [channels]
        data = self.encode_data(data)

        await self._backend.publish(data, channels)

    async def subscribe(self, channels: str | Iterable[str], history: int | None = None) -> Subscriber:
        """Create a :class:`Subscriber`, providing a stream of all events in ``channels``.

        The created subscriber will be passive by default and has to be consumed manually,
        either by using :meth:`Subscriber.run_in_background` or iterating over events
        using :meth:`Subscriber.iter_events`.

        Args:
            channels: Channel(s) to subscribe to
            history: If a non-negative integer, add this amount of history entries from
                each channel to the subscriber's event stream. Note that this will wait
                until all history entries are fetched and pushed to the subscriber's
                stream. For more control use :meth:`put_subscriber_history`.

        Returns:
            A :class:`Subscriber`

        Raises:
            ChannelsException: If a channel in ``channels`` has not been declared on this backend and
                ``arbitrary_channels_allowed`` has not been set to ``True``
        """
        if isinstance(channels, str):
            channels = [channels]

        subscriber = self._subscriber_class(
            plugin=self,
            max_backlog=self._max_backlog,
            backlog_strategy=self._backlog_strategy,
        )
        channels_to_subscribe = set()

        for channel in channels:
            if channel not in self._channels:
                if not self._arbitrary_channels_allowed:
                    raise ChannelsException(
                        f"Unknown channel: {channel!r}. Either explicitly defined the channel or set "
                        "arbitrary_channels_allowed=True"
                    )
                self._channels[channel] = set()
            channel_subscribers = self._channels[channel]
            if not channel_subscribers:
                channels_to_subscribe.add(channel)

            channel_subscribers.add(subscriber)

        if channels_to_subscribe:
            await self._backend.subscribe(channels_to_subscribe)

        if history:
            await self.put_subscriber_history(subscriber=subscriber, limit=history, channels=channels)

        return subscriber

    async def unsubscribe(self, subscriber: Subscriber, channels: str | Iterable[str] | None = None) -> None:
        """Unsubscribe a :class:`Subscriber` from ``channels``. If the subscriber has a running sending task, it will
        be stopped.

        Args:
            channels: Channels to unsubscribe from. If ``None``, unsubscribe from all channels
            subscriber: :class:`Subscriber` to unsubscribe
        """
        if channels is None:
            channels = list(self._channels.keys())
        elif isinstance(channels, str):
            channels = [channels]

        channels_to_unsubscribe: set[str] = set()

        for channel in channels:
            channel_subscribers = self._channels[channel]

            try:
                channel_subscribers.remove(subscriber)
            except KeyError:  # subscriber was not subscribed to this channel. This may happen if channels is None
                continue

            if not channel_subscribers:
                channels_to_unsubscribe.add(channel)

        if all(subscriber not in queues for queues in self._channels.values()):
            await subscriber.put(None)  # this will stop any running task or generator by breaking the inner loop
            if subscriber.is_running:
                await subscriber.stop()

        if channels_to_unsubscribe:
            await self._backend.unsubscribe(channels_to_unsubscribe)

    @asynccontextmanager
    async def start_subscription(
        self, channels: str | Iterable[str], history: int | None = None
    ) -> AsyncGenerator[Subscriber, None]:
        """Create a :class:`Subscriber` and tie its subscriptions to a context manager;
        Upon exiting the context, :meth:`unsubscribe` will be called.

        Args:
            channels: Channel(s) to subscribe to
            history: If a non-negative integer, add this amount of history entries from
                each channel to the subscriber's event stream. Note that this will wait
                until all history entries are fetched and pushed to the subscriber's
                stream. For more control use :meth:`put_subscriber_history`.

        Returns:
            A :class:`Subscriber`
        """
        subscriber = await self.subscribe(channels, history=history)

        try:
            yield subscriber
        finally:
            await self.unsubscribe(subscriber, channels)

    async def put_subscriber_history(
        self, subscriber: Subscriber, channels: str | Iterable[str], limit: int | None = None
    ) -> None:
        """Fetch the history of ``channels`` from the backend and put them in the
        subscriber's stream
        """
        if isinstance(channels, str):
            channels = [channels]

        for channel in channels:
            history = await self._backend.get_history(channel, limit)
            for entry in history:
                await subscriber.put(entry)

    async def _ws_handler_func(self, channel_name: str, socket: WebSocket) -> None:
        await socket.accept()

        # the ternary operator triggers a mypy bug: https://github.com/python/mypy/issues/10740
        on_event: EventCallback = socket.send_text if self._socket_send_mode == "text" else socket.send_bytes  # type: ignore[assignment]

        async with self.start_subscription(channel_name) as subscriber:
            if self._handler_should_send_history:
                await self.put_subscriber_history(subscriber, channels=channel_name, limit=self._history_limit)

            # use the background task, so we can block on receive(), breaking the loop when a connection closes
            async with subscriber.run_in_background(on_event):
                while (await socket.receive())["type"] != "websocket.disconnect":
                    continue

    def _create_ws_handler_func(self, channel_name: str) -> Callable[[WebSocket], Awaitable[None]]:
        async def ws_handler_func(socket: WebSocket) -> None:
            await self._ws_handler_func(channel_name=channel_name, socket=socket)

        return ws_handler_func

    async def _pub_worker(self) -> None:
        while self._pub_queue:
            data, channels = await self._pub_queue.get()
            await self._backend.publish(data, channels)
            self._pub_queue.task_done()

    async def _sub_worker(self) -> None:
        async for channel, payload in self._backend.stream_events():
            for subscriber in self._channels.get(channel, []):
                subscriber.put_nowait(payload)

    async def _on_startup(self) -> None:
        await self._backend.on_startup()
        self._pub_queue = Queue()
        self._pub_task = create_task(self._pub_worker())
        self._sub_task = create_task(self._sub_worker())
        if self._channels:
            await self._backend.subscribe(list(self._channels))

    async def _on_shutdown(self) -> None:
        if self._pub_queue:
            await self._pub_queue.join()
            self._pub_queue = None

        await asyncio.gather(
            *[
                subscriber.stop(join=False)
                for subscribers in self._channels.values()
                for subscriber in subscribers
                if subscriber.is_running
            ]
        )

        if self._sub_task:
            self._sub_task.cancel()
            with suppress(CancelledError):
                await self._sub_task
            self._sub_task = None

        if self._pub_task:
            self._pub_task.cancel()
            with suppress(CancelledError):
                await self._pub_task
            self._sub_task = None

        await self._backend.on_shutdown()

    async def __aenter__(self) -> ChannelsPlugin:
        await self._on_startup()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._on_shutdown()
