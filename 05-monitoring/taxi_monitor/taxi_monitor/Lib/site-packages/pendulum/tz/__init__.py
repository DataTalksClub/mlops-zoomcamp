from typing import Tuple
from typing import Union

import pytzdata

from .local_timezone import get_local_timezone
from .local_timezone import set_local_timezone
from .local_timezone import test_local_timezone
from .timezone import UTC
from .timezone import FixedTimezone as _FixedTimezone
from .timezone import Timezone as _Timezone


PRE_TRANSITION = "pre"
POST_TRANSITION = "post"
TRANSITION_ERROR = "error"

timezones = pytzdata.timezones  # type: Tuple[str, ...]


_tz_cache = {}


def timezone(name, extended=True):  # type: (Union[str, int], bool) -> _Timezone
    """
    Return a Timezone instance given its name.
    """
    if isinstance(name, int):
        return fixed_timezone(name)

    if name.lower() == "utc":
        return UTC

    if name in _tz_cache:
        return _tz_cache[name]

    tz = _Timezone(name, extended=extended)
    _tz_cache[name] = tz

    return tz


def fixed_timezone(offset):  # type: (int) -> _FixedTimezone
    """
    Return a Timezone instance given its offset in seconds.
    """
    if offset in _tz_cache:
        return _tz_cache[offset]  # type: ignore

    tz = _FixedTimezone(offset)
    _tz_cache[offset] = tz

    return tz


def local_timezone():  # type: () -> _Timezone
    """
    Return the local timezone.
    """
    return get_local_timezone()
