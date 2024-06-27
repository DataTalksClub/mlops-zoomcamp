from __future__ import annotations

import os
import struct

from datetime import date
from datetime import datetime
from datetime import timedelta
from math import copysign
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import overload

import pendulum

from pendulum.constants import DAYS_PER_MONTHS
from pendulum.day import WeekDay
from pendulum.formatting.difference_formatter import DifferenceFormatter
from pendulum.locales.locale import Locale


if TYPE_CHECKING:
    # Prevent import cycles
    from pendulum.duration import Duration

with_extensions = os.getenv("PENDULUM_EXTENSIONS", "1") == "1"

_DT = TypeVar("_DT", bound=datetime)
_D = TypeVar("_D", bound=date)

try:
    if not with_extensions or struct.calcsize("P") == 4:
        raise ImportError()

    from pendulum._pendulum import PreciseDiff
    from pendulum._pendulum import days_in_year
    from pendulum._pendulum import is_leap
    from pendulum._pendulum import is_long_year
    from pendulum._pendulum import local_time
    from pendulum._pendulum import precise_diff
    from pendulum._pendulum import week_day
except ImportError:
    from pendulum._helpers import PreciseDiff  # type: ignore[assignment]
    from pendulum._helpers import days_in_year
    from pendulum._helpers import is_leap
    from pendulum._helpers import is_long_year
    from pendulum._helpers import local_time
    from pendulum._helpers import precise_diff  # type: ignore[assignment]
    from pendulum._helpers import week_day

difference_formatter = DifferenceFormatter()


@overload
def add_duration(
    dt: _DT,
    years: int = 0,
    months: int = 0,
    weeks: int = 0,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: float = 0,
    microseconds: int = 0,
) -> _DT:
    ...


@overload
def add_duration(
    dt: _D,
    years: int = 0,
    months: int = 0,
    weeks: int = 0,
    days: int = 0,
) -> _D:
    pass


def add_duration(
    dt: date | datetime,
    years: int = 0,
    months: int = 0,
    weeks: int = 0,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: float = 0,
    microseconds: int = 0,
) -> date | datetime:
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
        div, mod = divmod(seconds * s, 60)  # type: ignore[assignment]
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
    diff: Duration,
    is_now: bool = True,
    absolute: bool = False,
    locale: str | None = None,
) -> str:
    if locale is None:
        locale = get_locale()

    return difference_formatter.format(diff, is_now, absolute, locale)


def _sign(x: float) -> int:
    return int(copysign(1, x))


# Global helpers


def locale(name: str) -> Locale:
    return Locale.load(name)


def set_locale(name: str) -> None:
    locale(name)

    pendulum._LOCALE = name


def get_locale() -> str:
    return pendulum._LOCALE


def week_starts_at(wday: WeekDay) -> None:
    if wday < WeekDay.MONDAY or wday > WeekDay.SUNDAY:
        raise ValueError("Invalid day of week")

    pendulum._WEEK_STARTS_AT = wday


def week_ends_at(wday: WeekDay) -> None:
    if wday < WeekDay.MONDAY or wday > WeekDay.SUNDAY:
        raise ValueError("Invalid day of week")

    pendulum._WEEK_ENDS_AT = wday


__all__ = [
    "PreciseDiff",
    "days_in_year",
    "is_leap",
    "is_long_year",
    "local_time",
    "precise_diff",
    "week_day",
    "add_duration",
    "format_diff",
    "locale",
    "set_locale",
    "get_locale",
    "week_starts_at",
    "week_ends_at",
]
