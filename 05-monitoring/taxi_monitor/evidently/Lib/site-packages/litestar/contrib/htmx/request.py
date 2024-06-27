from __future__ import annotations

from contextlib import suppress
from functools import cached_property
from typing import TYPE_CHECKING, Any
from urllib.parse import unquote, urlsplit, urlunsplit

from litestar import Request
from litestar.connection.base import empty_receive, empty_send
from litestar.contrib.htmx._utils import HTMXHeaders
from litestar.exceptions import SerializationException
from litestar.serialization import decode_json

__all__ = ("HTMXDetails", "HTMXRequest")


if TYPE_CHECKING:
    from litestar.types import Receive, Scope, Send


class HTMXDetails:
    """HTMXDetails holds all the values sent by HTMX client in headers and provide convenient properties."""

    def __init__(self, request: Request) -> None:
        """Initialize :class:`HTMXDetails`"""
        self.request = request

    def _get_header_value(self, name: HTMXHeaders) -> str | None:
        """Parse request header

        Check for uri encoded header and unquotes it in readable format.
        """

        if value := self.request.headers.get(name.value.lower()):
            is_uri_encoded = self.request.headers.get(f"{name.value.lower()}-uri-autoencoded") == "true"
            return unquote(value) if is_uri_encoded else value
        return None

    def __bool__(self) -> bool:
        """Check if request is sent by an HTMX client."""
        return self._get_header_value(HTMXHeaders.REQUEST) == "true"

    @cached_property
    def boosted(self) -> bool:
        """Check if request is boosted."""
        return self._get_header_value(HTMXHeaders.BOOSTED) == "true"

    @cached_property
    def current_url(self) -> str | None:
        """Current url value sent by HTMX client."""
        return self._get_header_value(HTMXHeaders.CURRENT_URL)

    @cached_property
    def current_url_abs_path(self) -> str | None:
        """Current url abs path value, to get query and path parameter sent by HTMX client."""
        if self.current_url:
            split = urlsplit(self.current_url)
            if split.scheme == self.request.scope["scheme"] and split.netloc == self.request.headers.get("host"):
                return str(urlunsplit(split._replace(scheme="", netloc="")))
            return None
        return self.current_url

    @cached_property
    def history_restore_request(self) -> bool:
        """If True then, request is for history restoration after a miss in the local history cache."""
        return self._get_header_value(HTMXHeaders.HISTORY_RESTORE_REQUEST) == "true"

    @cached_property
    def prompt(self) -> str | None:
        """User Response to prompt.

        .. code-block:: html

            <button hx-delete="/account" hx-prompt="Enter your account name to confirm deletion">Delete My Account</button>
        """
        return self._get_header_value(HTMXHeaders.PROMPT)

    @cached_property
    def target(self) -> str | None:
        """ID of the target element if provided on the element."""
        return self._get_header_value(HTMXHeaders.TARGET)

    @cached_property
    def trigger(self) -> str | None:
        """ID of the triggered element if provided on the element."""
        return self._get_header_value(HTMXHeaders.TRIGGER_ID)

    @cached_property
    def trigger_name(self) -> str | None:
        """Name of the triggered element if provided on the element."""
        return self._get_header_value(HTMXHeaders.TRIGGER_NAME)

    @cached_property
    def triggering_event(self) -> Any:
        """Name of the triggered event.

        This value is added by ``event-header`` extension of HTMX to the ``Triggering-Event`` header to requests.
        """
        if value := self._get_header_value(HTMXHeaders.TRIGGERING_EVENT):
            with suppress(SerializationException):
                return decode_json(value=value, type_decoders=self.request.route_handler.resolve_type_decoders())
        return None


class HTMXRequest(Request):
    """HTMX Request class to work with HTMX client."""

    __slots__ = ("htmx",)

    def __init__(self, scope: Scope, receive: Receive = empty_receive, send: Send = empty_send) -> None:
        """Initialize :class:`HTMXRequest`"""
        super().__init__(scope=scope, receive=receive, send=send)
        self.htmx = HTMXDetails(self)
