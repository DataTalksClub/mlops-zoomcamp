from __future__ import annotations

import datetime as _datetime

from typing import Union
from typing import cast
from typing import overload

from pendulum.__version__ import __version__
from pendulum.constants import DAYS_PER_WEEK
from pendulum.constants import HOURS_PER_DAY
from pendulum.constants import MINUTES_PER_HOUR
from pendulum.constants import MONTHS_PER_YEAR
from pendulum.constants import SECONDS_PER_DAY
from pendulum.constants import SECONDS_PER_HOUR
from pendulum.constants import SECONDS_PER_MINUTE
from pendulum.constants import WEEKS_PER_YEAR
from pendulum.constants import YEARS_PER_CENTURY
from pendulum.constants import YEARS_PER_DECADE
from pendulum.date import Date
from pendulum.datetime import DateTime
from pendulum.day import WeekDay
from pendulum.duration import Duration
from pendulum.formatting import Formatter
from pendulum.helpers import format_diff
from pendulum.helpers import get_locale
from pendulum.helpers import locale
from pendulum.helpers import set_locale
from pendulum.helpers import week_ends_at
from pendulum.helpers import week_starts_at
from pendulum.interval import Interval
from pendulum.parser import parse
from pendulum.testing.traveller import Traveller
from pendulum.time import Time
from pendulum.tz import UTC
from pendulum.tz import fixed_timezone
from pendulum.tz import local_timezone
from pendulum.tz import set_local_timezone
from pendulum.tz import test_local_timezone
from pendulum.tz import timezones
from pendulum.tz.timezone import FixedTimezone
from pendulum.tz.timezone import Timezone


MONDAY = WeekDay.MONDAY
TUESDAY = WeekDay.TUESDAY
WEDNESDAY = WeekDay.WEDNESDAY
THURSDAY = WeekDay.THURSDAY
FRIDAY = WeekDay.FRIDAY
SATURDAY = WeekDay.SATURDAY
SUNDAY = WeekDay.SUNDAY

_TEST_NOW: DateTime | None = None
_LOCALE = "en"
_WEEK_STARTS_AT: WeekDay = WeekDay.MONDAY
_WEEK_ENDS_AT: WeekDay = WeekDay.SUNDAY

_formatter = Formatter()


@overload
def timezone(name: int) -> FixedTimezone:
    ...


@overload
def timezone(name: str) -> Timezone:
    ...


@overload
def timezone(name: str | int) -> Timezone | FixedTimezone:
    ...


def timezone(name: str | int) -> Timezone | FixedTimezone:
    """
    Return a Timezone instance given its name.
    """
    if isinstance(name, int):
        return fixed_timezone(name)

    if name.lower() == "utc":
        return UTC

    return Timezone(name)


def _safe_timezone(
    obj: str | float | _datetime.tzinfo | Timezone | FixedTimezone | None,
    dt: _datetime.datetime | None = None,
) -> Timezone | FixedTimezone:
    """
    Creates a timezone instance
    from a string, Timezone, TimezoneInfo or integer offset.
    """
    if isinstance(obj, (Timezone, FixedTimezone)):
        return obj

    if obj is None or obj == "local":
        return local_timezone()

    if isinstance(obj, (int, float)):
        obj = int(obj * 60 * 60)
    elif isinstance(obj, _datetime.tzinfo):
        # zoneinfo
        if hasattr(obj, "key"):
            obj = obj.key
        # pytz
        elif hasattr(obj, "localize"):
            obj = obj.zone  # type: ignore[attr-defined]
        elif obj.tzname(None) == "UTC":
            return UTC
        else:
            offset = obj.utcoffset(dt)

            if offset is None:
                offset = _datetime.timedelta(0)

            obj = int(offset.total_seconds())

    obj = cast(Union[str, int], obj)

    return timezone(obj)


# Public API
def datetime(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
    microsecond: int = 0,
    tz: str | float | Timezone | FixedTimezone | _datetime.tzinfo | None = UTC,
    fold: int = 1,
    raise_on_unknown_times: bool = False,
) -> DateTime:
    """
    Creates a new DateTime instance from a specific date and time.
    """
    return DateTime.create(
        year,
        month,
        day,
        hour=hour,
        minute=minute,
        second=second,
        microsecond=microsecond,
        tz=tz,
        fold=fold,
        raise_on_unknown_times=raise_on_unknown_times,
    )


def local(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
    microsecond: int = 0,
) -> DateTime:
    """
    Return a DateTime in the local timezone.
    """
    return datetime(
        year, month, day, hour, minute, second, microsecond, tz=local_timezone()
    )


def naive(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
    microsecond: int = 0,
    fold: int = 1,
) -> DateTime:
    """
    Return a naive DateTime.
    """
    return DateTime(year, month, day, hour, minute, second, microsecond, fold=fold)


def date(year: int, month: int, day: int) -> Date:
    """
    Create a new Date instance.
    """
    return Date(year, month, day)


def time(hour: int, minute: int = 0, second: int = 0, microsecond: int = 0) -> Time:
    """
    Create a new Time instance.
    """
    return Time(hour, minute, second, microsecond)


@overload
def instance(
    obj: _datetime.datetime,
    tz: str | Timezone | FixedTimezone | _datetime.tzinfo | None = UTC,
) -> DateTime:
    ...


@overload
def instance(
    obj: _datetime.date,
    tz: str | Timezone | FixedTimezone | _datetime.tzinfo | None = UTC,
) -> Date:
    ...


@overload
def instance(
    obj: _datetime.time,
    tz: str | Timezone | FixedTimezone | _datetime.tzinfo | None = UTC,
) -> Time:
    ...


def instance(
    obj: _datetime.datetime | _datetime.date | _datetime.time,
    tz: str | Timezone | FixedTimezone | _datetime.tzinfo | None = UTC,
) -> DateTime | Date | Time:
    """
    Create a DateTime/Date/Time instance from a datetime/date/time native one.
    """
    if isinstance(obj, (DateTime, Date, Time)):
        return obj

    if isinstance(obj, _datetime.date) and not isinstance(obj, _datetime.datetime):
        return date(obj.year, obj.month, obj.day)

    if isinstance(obj, _datetime.time):
        return Time.instance(obj, tz=tz)

    return DateTime.instance(obj, tz=tz)


def now(tz: str | Timezone | None = None) -> DateTime:
    """
    Get a DateTime instance for the current date and time.
    """
    return DateTime.now(tz)


def today(tz: str | Timezone = "local") -> DateTime:
    """
    Create a DateTime instance for today.
    """
    return now(tz).start_of("day")


def tomorrow(tz: str | Timezone = "local") -> DateTime:
    """
    Create a DateTime instance for tomorrow.
    """
    return today(tz).add(days=1)


def yesterday(tz: str | Timezone = "local") -> DateTime:
    """
    Create a DateTime instance for yesterday.
    """
    return today(tz).subtract(days=1)


def from_format(
    string: str,
    fmt: str,
    tz: str | Timezone = UTC,
    locale: str | None = None,
) -> DateTime:
    """
    Creates a DateTime instance from a specific format.
    """
    parts = _formatter.parse(string, fmt, now(tz=tz), locale=locale)
    if parts["tz"] is None:
        parts["tz"] = tz

    return datetime(**parts)


def from_timestamp(timestamp: int | float, tz: str | Timezone = UTC) -> DateTime:
    """
    Create a DateTime instance from a timestamp.
    """
    dt = _datetime.datetime.utcfromtimestamp(timestamp)

    dt = datetime(
        dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond
    )

    if tz is not UTC or tz != "UTC":
        dt = dt.in_timezone(tz)

    return dt


def duration(
    days: float = 0,
    seconds: float = 0,
    microseconds: float = 0,
    milliseconds: float = 0,
    minutes: float = 0,
    hours: float = 0,
    weeks: float = 0,
    years: float = 0,
    months: float = 0,
) -> Duration:
    """
    Create a Duration instance.
    """
    return Duration(
        days=days,
        seconds=seconds,
        microseconds=microseconds,
        milliseconds=milliseconds,
        minutes=minutes,
        hours=hours,
        weeks=weeks,
        years=years,
        months=months,
    )


def interval(start: DateTime, end: DateTime, absolute: bool = False) -> Interval:
    """
    Create an Interval instance.
    """
    return Interval(start, end, absolute=absolute)


# Testing

_traveller = Traveller(DateTime)

freeze = _traveller.freeze
travel = _traveller.travel
travel_to = _traveller.travel_to
travel_back = _traveller.travel_back

__all__ = [
    "__version__",
    "DAYS_PER_WEEK",
    "HOURS_PER_DAY",
    "MINUTES_PER_HOUR",
    "MONTHS_PER_YEAR",
    "SECONDS_PER_DAY",
    "SECONDS_PER_HOUR",
    "SECONDS_PER_MINUTE",
    "WEEKS_PER_YEAR",
    "YEARS_PER_CENTURY",
    "YEARS_PER_DECADE",
    "Date",
    "DateTime",
    "Duration",
    "Formatter",
    "WeekDay",
    "date",
    "datetime",
    "duration",
    "format_diff",
    "freeze",
    "from_format",
    "from_timestamp",
    "get_locale",
    "instance",
    "interval",
    "local",
    "locale",
    "naive",
    "now",
    "set_locale",
    "week_ends_at",
    "week_starts_at",
    "parse",
    "Interval",
    "Time",
    "UTC",
    "local_timezone",
    "set_local_timezone",
    "test_local_timezone",
    "time",
    "timezone",
    "timezones",
    "today",
    "tomorrow",
    "travel",
    "travel_back",
    "travel_to",
    "FixedTimezone",
    "Timezone",
    "yesterday",
]
