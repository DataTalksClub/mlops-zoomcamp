from __future__ import absolute_import

import os
import struct

from contextlib import contextmanager
from datetime import date
from datetime import datetime
from datetime import timedelta
from math import copysign
from typing import TYPE_CHECKING
from typing import Iterator
from typing import Optional
from typing import TypeVar
from typing import overload

import pendulum

from .constants import DAYS_PER_MONTHS
from .formatting.difference_formatter import DifferenceFormatter
from .locales.locale import Locale


if TYPE_CHECKING:
    # Prevent import cycles
    from .period import Period

with_extensions = os.getenv("PENDULUM_EXTENSIONS", "1") == "1"

_DT = TypeVar("_DT", bound=datetime)
_D = TypeVar("_D", bound=date)

try:
    if not with_extensions or struct.calcsize("P") == 4:
        raise ImportError()

    from ._extensions._helpers import local_time
    from ._extensions._helpers import precise_diff
    from ._extensions._helpers import is_leap
    from ._extensions._helpers import is_long_year
    from ._extensions._helpers import week_day
    from ._extensions._helpers import days_in_year
    from ._extensions._helpers import timestamp
except ImportError:
    from ._extensions.helpers import local_time  # noqa
    from ._extensions.helpers import precise_diff  # noqa
    from ._extensions.helpers import is_leap  # noqa
    from ._extensions.helpers import is_long_year  # noqa
    from ._extensions.helpers import week_day  # noqa
    from ._extensions.helpers import days_in_year  # noqa
    from ._extensions.helpers import timestamp  # noqa


difference_formatter = DifferenceFormatter()


@overload
def add_duration(
    dt,  # type: _DT
    years=0,  # type: int
    months=0,  # type: int
    weeks=0,  # type: int
    days=0,  # type: int
    hours=0,  # type: int
    minutes=0,  # type: int
    seconds=0,  # type: int
    microseconds=0,  # type: int
):  # type: (...) -> _DT
    pass


@overload
def add_duration(
    dt,  # type: _D
    years=0,  # type: int
    months=0,  # type: int
    weeks=0,  # type: int
    days=0,  # type: int
):  # type: (...) -> _D
    pass


def add_duration(
    dt,
    years=0,
    months=0,
    weeks=0,
    days=0,
    hours=0,
    minutes=0,
    seconds=0,
    microseconds=0,
):
    """
    Adds a duration to a date/datetime instance.
    """
    days += weeks * 7

    if (
        isinstance(dt, date)
        and not isinstance(dt, datetime)
        and any([hours, minutes, seconds, microseconds])
    ):
        raise RuntimeError("Time elements cannot be added to a date instance.")

    # Normalizing
    if abs(microseconds) > 999999:
        s = _sign(microseconds)
        div, mod = divmod(microseconds * s, 1000000)
        microseconds = mod * s
        seconds += div * s

    if abs(seconds) > 59:
        s = _sign(seconds)
        div, mod = divmod(seconds * s, 60)
        seconds = mod * s
        minutes += div * s

    if abs(minutes) > 59:
        s = _sign(minutes)
        div, mod = divmod(minutes * s, 60)
        minutes = mod * s
        hours += div * s

    if abs(hours) > 23:
        s = _sign(hours)
        div, mod = divmod(hours * s, 24)
        hours = mod * s
        days += div * s

    if abs(months) > 11:
        s = _sign(months)
        div, mod = divmod(months * s, 12)
        months = mod * s
        years += div * s

    year = dt.year + years
    month = dt.month

    if months:
        month += months
        if month > 12:
            year += 1
            month -= 12
        elif month < 1:
            year -= 1
            month += 12

    day = min(DAYS_PER_MONTHS[int(is_leap(year))][month], dt.day)

    dt = dt.replace(year=year, month=month, day=day)

    return dt + timedelta(
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        microseconds=microseconds,
    )


def format_diff(
    diff, is_now=True, absolute=False, locale=None
):  # type: (Period, bool, bool, Optional[str]) -> str
    if locale is None:
        locale = get_locale()

    return difference_formatter.format(diff, is_now, absolute, locale)


def _sign(x):
    return int(copysign(1, x))


# Global helpers


@contextmanager
def test(mock):  # type: (pendulum.DateTime) -> Iterator[None]
    set_test_now(mock)
    try:
        yield
    finally:
        set_test_now()


def set_test_now(test_now=None):  # type: (Optional[pendulum.DateTime]) -> None
    pendulum._TEST_NOW = test_now


def get_test_now():  # type: () -> Optional[pendulum.DateTime]
    return pendulum._TEST_NOW


def has_test_now():  # type: () -> bool
    return pendulum._TEST_NOW is not None


def locale(name):  # type: (str) -> Locale
    return Locale.load(name)


def set_locale(name):  # type: (str) -> None
    locale(name)

    pendulum._LOCALE = name


def get_locale():  # type: () -> str
    return pendulum._LOCALE


def week_starts_at(wday):  # type: (int) -> None
    if wday < pendulum.SUNDAY or wday > pendulum.SATURDAY:
        raise ValueError("Invalid week day as start of week.")

    pendulum._WEEK_STARTS_AT = wday


def week_ends_at(wday):  # type: (int) -> None
    if wday < pendulum.SUNDAY or wday > pendulum.SATURDAY:
        raise ValueError("Invalid week day as start of week.")

    pendulum._WEEK_ENDS_AT = wday
