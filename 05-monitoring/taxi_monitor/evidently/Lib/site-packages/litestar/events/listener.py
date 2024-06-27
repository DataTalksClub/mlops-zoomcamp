from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from litestar.exceptions import ImproperlyConfiguredException
from litestar.utils import ensure_async_callable

if TYPE_CHECKING:
    from litestar.types import AnyCallable, AsyncAnyCallable

__all__ = ("EventListener", "listener")

logger = logging.getLogger(__name__)


class EventListener:
    """Decorator for event listeners"""

    __slots__ = ("event_ids", "fn", "listener_id")

    fn: AsyncAnyCallable

    def __init__(self, *event_ids: str) -> None:
        """Create a decorator for event handlers.

        Args:
            *event_ids: The id of the event to listen to or a list of
                event ids to listen to.
        """
        self.event_ids: frozenset[str] = frozenset(event_ids)

    def __call__(self, fn: AnyCallable) -> EventListener:
        """Decorate a callable by wrapping it inside an instance of EventListener.

        Args:
            fn: Callable to decorate.

        Returns:
            An instance of EventListener
        """
        if not callable(fn):
            raise ImproperlyConfiguredException("EventListener instance should be called as a decorator on a callable")

        self.fn = self.wrap_in_error_handler(ensure_async_callable(fn))

        return self

    @staticmethod
    def wrap_in_error_handler(fn: AsyncAnyCallable) -> AsyncAnyCallable:
        """Wrap a listener function to handle errors.

        Listeners are executed concurrently in a TaskGroup, so we need to ensure that exceptions do not propagate
        to the task group which results in any other unfinished listeners to be cancelled, and the receive stream to
        be closed.

        See https://github.com/litestar-org/litestar/issues/2809

        Args:
            fn: The listener function to wrap.
        """

        async def wrapped(*args: Any, **kwargs: Any) -> None:
            """Wrap a listener function to handle errors."""
            try:
                await fn(*args, **kwargs)
            except Exception as exc:
                logger.exception("Error while executing listener %s: %s", fn.__name__, exc)

        return wrapped

    def __hash__(self) -> int:
        return hash(self.event_ids) + hash(self.fn)


listener = EventListener
