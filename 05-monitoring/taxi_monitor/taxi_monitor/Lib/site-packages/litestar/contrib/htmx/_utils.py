from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, cast
from urllib.parse import quote

from litestar.exceptions import ImproperlyConfiguredException
from litestar.serialization import encode_json

__all__ = (
    "HTMXHeaders",
    "get_headers",
    "get_location_headers",
    "get_push_url_header",
    "get_redirect_header",
    "get_refresh_header",
    "get_replace_url_header",
    "get_reswap_header",
    "get_retarget_header",
    "get_trigger_event_headers",
)


if TYPE_CHECKING:
    from litestar.contrib.htmx.types import (
        EventAfterType,
        HtmxHeaderType,
        LocationType,
        PushUrlType,
        ReSwapMethod,
        TriggerEventType,
    )

HTMX_STOP_POLLING = 286


class HTMXHeaders(str, Enum):
    """Enum for HTMX Headers"""

    REDIRECT = "HX-Redirect"
    REFRESH = "HX-Refresh"
    PUSH_URL = "HX-Push-Url"
    REPLACE_URL = "HX-Replace-Url"
    RE_SWAP = "HX-Reswap"
    RE_TARGET = "HX-Retarget"
    LOCATION = "HX-Location"

    TRIGGER_EVENT = "HX-Trigger"
    TRIGGER_AFTER_SETTLE = "HX-Trigger-After-Settle"
    TRIGGER_AFTER_SWAP = "HX-Trigger-After-Swap"

    REQUEST = "HX-Request"
    BOOSTED = "HX-Boosted"
    CURRENT_URL = "HX-Current-URL"
    HISTORY_RESTORE_REQUEST = "HX-History-Restore-Request"
    PROMPT = "HX-Prompt"
    TARGET = "HX-Target"
    TRIGGER_ID = "HX-Trigger"  # noqa: PIE796
    TRIGGER_NAME = "HX-Trigger-Name"
    TRIGGERING_EVENT = "Triggering-Event"


def get_trigger_event_headers(trigger_event: TriggerEventType) -> dict[str, Any]:
    """Return headers for trigger event response."""
    after_params: dict[EventAfterType, str] = {
        "receive": HTMXHeaders.TRIGGER_EVENT.value,
        "settle": HTMXHeaders.TRIGGER_AFTER_SETTLE.value,
        "swap": HTMXHeaders.TRIGGER_AFTER_SWAP.value,
    }

    if trigger_header := after_params.get(trigger_event["after"]):
        return {trigger_header: encode_json({trigger_event["name"]: trigger_event["params"] or {}}).decode()}

    raise ImproperlyConfiguredException(
        "invalid value for 'after' param- allowed values are 'receive', 'settle' or 'swap'."
    )


def get_redirect_header(url: str) -> dict[str, Any]:
    """Return headers for redirect response."""
    return {HTMXHeaders.REDIRECT.value: quote(url, safe="/#%[]=:;$&()+,!?*@'~"), "Location": ""}


def get_push_url_header(url: PushUrlType) -> dict[str, Any]:
    """Return headers for push url to browser history response."""
    if isinstance(url, str):
        url = url if url != "False" else "false"
    elif isinstance(url, bool):
        url = "false"

    return {HTMXHeaders.PUSH_URL.value: url}


def get_replace_url_header(url: PushUrlType) -> dict[str, Any]:
    """Return headers for replace url in browser tab response."""
    url = (url if url != "False" else "false") if isinstance(url, str) else "false"
    return {HTMXHeaders.REPLACE_URL: url}


def get_refresh_header(refresh: bool) -> dict[str, Any]:
    """Return headers for client refresh response."""
    return {HTMXHeaders.REFRESH.value: "true" if refresh else ""}


def get_reswap_header(method: ReSwapMethod) -> dict[str, Any]:
    """Return headers for change swap method response."""
    return {HTMXHeaders.RE_SWAP.value: method}


def get_retarget_header(target: str) -> dict[str, Any]:
    """Return headers for change target element response."""
    return {HTMXHeaders.RE_TARGET.value: target}


def get_location_headers(location: LocationType) -> dict[str, Any]:
    """Return headers for redirect without page-reload response."""
    if spec := {key: value for key, value in location.items() if value}:
        return {HTMXHeaders.LOCATION.value: encode_json(spec).decode()}
    raise ValueError("redirect_to is required parameter.")


def get_headers(hx_headers: HtmxHeaderType) -> dict[str, Any]:
    """Return headers for HTMX responses."""
    if not hx_headers:
        raise ValueError("Value for hx_headers cannot be None.")
    htmx_headers_dict: dict[str, Callable] = {
        "redirect": get_redirect_header,
        "refresh": get_refresh_header,
        "push_url": get_push_url_header,
        "replace_url": get_replace_url_header,
        "re_swap": get_reswap_header,
        "re_target": get_retarget_header,
        "trigger_event": get_trigger_event_headers,
        "location": get_location_headers,
    }

    header: dict[str, Any] = {}
    response: dict[str, Any]
    key: str
    value: Any

    for key, value in hx_headers.items():
        if key in ["redirect", "refresh", "location", "replace_url"]:
            return cast("dict[str, Any]", htmx_headers_dict[key](value))
        if value is not None:
            response = htmx_headers_dict[key](value)
            header.update(response)
    return header
