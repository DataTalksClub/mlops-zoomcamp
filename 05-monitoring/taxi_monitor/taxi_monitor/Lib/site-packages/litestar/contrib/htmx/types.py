from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, TypedDict, Union

__all__ = (
    "HtmxHeaderType",
    "LocationType",
    "TriggerEventType",
)

if TYPE_CHECKING:
    from typing_extensions import Required


EventAfterType = Literal["receive", "settle", "swap", None]

PushUrlType = Union[str, bool]

ReSwapMethod = Literal[
    "innerHTML", "outerHTML", "beforebegin", "afterbegin", "beforeend", "afterend", "delete", "none", None
]


class LocationType(TypedDict):
    """Type for HX-Location header."""

    path: Required[str]
    source: str | None
    event: str | None
    target: str | None
    swap: ReSwapMethod | None
    values: dict[str, str] | None
    hx_headers: dict[str, Any] | None


class TriggerEventType(TypedDict):
    """Type for HX-Trigger header."""

    name: Required[str]
    params: dict[str, Any] | None
    after: EventAfterType | None


class HtmxHeaderType(TypedDict, total=False):
    """Type for hx_headers parameter in get_headers()."""

    location: LocationType | None
    redirect: str | None
    refresh: bool
    push_url: PushUrlType | None
    replace_url: PushUrlType | None
    re_swap: ReSwapMethod | None
    re_target: str | None
    trigger_event: TriggerEventType | None
