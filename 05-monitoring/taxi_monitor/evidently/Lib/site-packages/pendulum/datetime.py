from __future__ import annotations

import calendar
import datetime
import traceback

from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Optional
from typing import cast
from typing import overload

import pendulum

from pendulum.constants import ATOM
from pendulum.constants import COOKIE
from pendulum.constants import MINUTES_PER_HOUR
from pendulum.constants import MONTHS_PER_YEAR
from pendulum.constants import RFC822
from pendulum.constants import RFC850
from pendulum.constants import RFC1036
from pendulum.constants import RFC1123
from pendulum.constants import RFC2822
from pendulum.constants import RSS
from pendulum.constants import SECONDS_PER_DAY
from pendulum.constants import SECONDS_PER_MINUTE
from pendulum.constants import W3C
from pendulum.constants import YEARS_PER_CENTURY
from pendulum.constants import YEARS_PER_DECADE
from pendulum.date import Date
from pendulum.day import WeekDay
from pendulum.exceptions import PendulumException
from pendulum.helpers import add_duration
from pendulum.interval import Interval
from pendulum.time import Time
from pendulum.tz import UTC
from pendulum.tz import local_timezone
from pendulum.tz.timezone import FixedTimezone
from pendulum.tz.timezone import Timezone


if TYPE_CHECKING:
    from typing_extensions import Literal
    from typing_extensions import Self
    from typing_extensions import SupportsIndex


class DateTime(datetime.datetime, Date):
    EPOCH: ClassVar[DateTime]
    min: ClassVar[DateTime]
    max: ClassVar[DateTime]

    # Formats

    _FORMATS: ClassVar[dict[str, str | Callable[[datetime.datetime], str]]] = {
        "atom": ATOM,
        "cookie": COOKIE,
        "iso8601": lambda dt: dt.isoformat("T"),
        "rfc822": RFC822,
        "rfc850": RFC850,
        "rfc1036": RFC1036,
        "rfc1123": RFC1123,
        "rfc2822": RFC2822,
        "rfc3339": lambda dt: dt.isoformat("T"),
        "rss": RSS,
        "w3c": W3C,
    }

    _MODIFIERS_VALID_UNITS: ClassVar[list[str]] = [
        "second",
        "minute",
        "hour",
        "day",
        "week",
        "month",
        "year",
        "decade",
        "century",
    ]

    _EPOCH: datetime.datetime = datetime.datetime(1970, 1, 1, tzinfo=UTC)

    @classmethod
    def create(
        cls,
        year: SupportsIndex,
        month: SupportsIndex,
        day: SupportsIndex,
        hour: SupportsIndex = 0,
        minute: SupportsIndex = 0,
        second: SupportsIndex = 0,
        microsecond: SupportsIndex = 0,
        tz: str | float | Timezone | FixedTimezone | None | datetime.tzinfo = UTC,
        fold: int = 1,
        raise_on_unknown_times: bool = False,
    ) -> Self:
        """
        Creates a new DateTime instance from a specific date and time.
        """
        if tz is not None:
            tz = pendulum._safe_timezone(tz)

        dt = datetime.datetime(
            year, month, day, hour, minute, second, microsecond, fold=fold
        )

        if tz is not None:
            dt = tz.convert(dt, raise_on_unknown_times=raise_on_unknown_times)

        return cls(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            tzinfo=dt.tzinfo,
            fold=dt.fold,
        )

    @classmethod
    def instance(
        cls,
        dt: datetime.datetime,
        tz: str | Timezone | FixedTimezone | datetime.tzinfo | None = UTC,
    ) -> Self:
        tz = dt.tzinfo or tz

        if tz is not None:
            tz = pendulum._safe_timezone(tz, dt=dt)

        return cls.create(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            tz=tz,
            fold=dt.fold,
        )

    @overload
    @classmethod
    def now(cls, tz: datetime.tzinfo | None = None) -> Self:
        ...

    @overload
    @classmethod
    def now(cls, tz: str | Timezone | FixedTimezone | None = None) -> Self:
        ...

    @classmethod
    def now(
        cls, tz: str | Timezone | FixedTimezone | datetime.tzinfo | None = None
    ) -> Self:
        """
        Get a DateTime instance for the current date and time.
        """
        if tz is None or tz == "local":
            dt = datetime.datetime.now(local_timezone())
        elif tz is UTC or tz == "UTC":
            dt = datetime.datetime.now(UTC)
        else:
            dt = datetime.datetime.now(UTC)
            tz = pendulum._safe_timezone(tz)
            dt = dt.astimezone(tz)

        return cls(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            tzinfo=dt.tzinfo,
            fold=dt.fold,
        )

    @classmethod
    def utcnow(cls) -> Self:
        """
        Get a DateTime instance for the current date and time in UTC.
        """
        return cls.now(UTC)

    @classmethod
    def today(cls) -> Self:
        return cls.now()

    @classmethod
    def strptime(cls, time: str, fmt: str) -> Self:
        return cls.instance(datetime.datetime.strptime(time, fmt))

    # Getters/Setters

    def set(
        self,
        year: int | None = None,
        month: int | None = None,
        day: int | None = None,
        hour: int | None = None,
        minute: int | None = None,
        second: int | None = None,
        microsecond: int | None = None,
        tz: str | float | Timezone | FixedTimezone | datetime.tzinfo | None = None,
    ) -> Self:
        if year is None:
            year = self.year
        if month is None:
            month = self.month
        if day is None:
            day = self.day
        if hour is None:
            hour = self.hour
        if minute is None:
            minute = self.minute
        if second is None:
            second = self.second
        if microsecond is None:
            microsecond = self.microsecond
        if tz is None:
            tz = self.tz

        return self.__class__.create(
            year, month, day, hour, minute, second, microsecond, tz=tz, fold=self.fold
        )

    @property
    def float_timestamp(self) -> float:
        return self.timestamp()

    @property
    def int_timestamp(self) -> int:
        # Workaround needed to avoid inaccuracy
        # for far into the future datetimes
        dt = datetime.datetime(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
            tzinfo=self.tzinfo,
            fold=self.fold,
        )

        delta = dt - self._EPOCH

        return delta.days * SECONDS_PER_DAY + delta.seconds

    @property
    def offset(self) -> int | None:
        return self.get_offset()

    @property
    def offset_hours(self) -> float | None:
        offset = self.get_offset()

        if offset is None:
            return None

        return offset / SECONDS_PER_MINUTE / MINUTES_PER_HOUR

    @property
    def timezone(self) -> Timezone | FixedTimezone | None:
        if not isinstance(self.tzinfo, (Timezone, FixedTimezone)):
            return None

        return self.tzinfo

    @property
    def tz(self) -> Timezone | FixedTimezone | None:
        return self.timezone

    @property
    def timezone_name(self) -> str | None:
        tz = self.timezone

        if tz is None:
            return None

        return tz.name

    @property
    def age(self) -> int:
        return self.date().diff(self.now(self.tz).date(), abs=False).in_years()

    def is_local(self) -> bool:
        return self.offset == self.in_timezone(pendulum.local_timezone()).offset

    def is_utc(self) -> bool:
        return self.offset == 0

    def is_dst(self) -> bool:
        return self.dst() != datetime.timedelta()

    def get_offset(self) -> int | None:
        utcoffset = self.utcoffset()
        if utcoffset is None:
            return None

        return int(utcoffset.total_seconds())

    def date(self) -> Date:
        return Date(self.year, self.month, self.day)

    def time(self) -> Time:
        return Time(self.hour, self.minute, self.second, self.microsecond)

    def naive(self) -> Self:
        """
        Return the DateTime without timezone information.
        """
        return self.__class__(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
        )

    def on(self, year: int, month: int, day: int) -> Self:
        """
        Returns a new instance with the current date set to a different date.
        """
        return self.set(year=int(year), month=int(month), day=int(day))

    def at(
        self, hour: int, minute: int = 0, second: int = 0, microsecond: int = 0
    ) -> Self:
        """
        Returns a new instance with the current time to a different time.
        """
        return self.set(
            hour=hour, minute=minute, second=second, microsecond=microsecond
        )

    def in_timezone(self, tz: str | Timezone | FixedTimezone) -> Self:
        """
        Set the instance's timezone from a string or object.
        """
        tz = pendulum._safe_timezone(tz)

        dt = self
        if not self.timezone:
            dt = dt.replace(fold=1)

        return tz.convert(dt)

    def in_tz(self, tz: str | Timezone | FixedTimezone) -> Self:
        """
        Set the instance's timezone from a string or object.
        """
        return self.in_timezone(tz)

    # STRING FORMATTING

    def to_time_string(self) -> str:
        """
        Format the instance as time.
        """
        return self.format("HH:mm:ss")

    def to_datetime_string(self) -> str:
        """
        Format the instance as date and time.
        """
        return self.format("YYYY-MM-DD HH:mm:ss")

    def to_day_datetime_string(self) -> str:
        """
        Format the instance as day, date and time (in english).
        """
        return self.format("ddd, MMM D, YYYY h:mm A", locale="en")

    def to_atom_string(self) -> str:
        """
        Format the instance as ATOM.
        """
        return self._to_string("atom")

    def to_cookie_string(self) -> str:
        """
        Format the instance as COOKIE.
        """
        return self._to_string("cookie", locale="en")

    def to_iso8601_string(self) -> str:
        """
        Format the instance as ISO 8601.
        """
        string = self._to_string("iso8601")

        if self.tz and self.tz.name == "UTC":
            string = string.replace("+00:00", "Z")

        return string

    def to_rfc822_string(self) -> str:
        """
        Format the instance as RFC 822.
        """
        return self._to_string("rfc822")

    def to_rfc850_string(self) -> str:
        """
        Format the instance as RFC 850.
        """
        return self._to_string("rfc850")

    def to_rfc1036_string(self) -> str:
        """
        Format the instance as RFC 1036.
        """
        return self._to_string("rfc1036")

    def to_rfc1123_string(self) -> str:
        """
        Format the instance as RFC 1123.
        """
        return self._to_string("rfc1123")

    def to_rfc2822_string(self) -> str:
        """
        Format the instance as RFC 2822.
        """
        return self._to_string("rfc2822")

    def to_rfc3339_string(self) -> str:
        """
        Format the instance as RFC 3339.
        """
        return self._to_string("rfc3339")

    def to_rss_string(self) -> str:
        """
        Format the instance as RSS.
        """
        return self._to_string("rss")

    def to_w3c_string(self) -> str:
        """
        Format the instance as W3C.
        """
        return self._to_string("w3c")

    def _to_string(self, fmt: str, locale: str | None = None) -> str:
        """
        Format the instance to a common string format.
        """
        if fmt not in self._FORMATS:
            raise ValueError(f"Format [{fmt}] is not supported")

        fmt_value = self._FORMATS[fmt]
        if callable(fmt_value):
            return fmt_value(self)

        return self.format(fmt_value, locale=locale)

    def __str__(self) -> str:
        return self.isoformat(" ")

    def __repr__(self) -> str:
        us = ""
        if self.microsecond:
            us = f", {self.microsecond}"

        repr_ = "{klass}(" "{year}, {month}, {day}, " "{hour}, {minute}, {second}{us}"

        if self.tzinfo is not None:
            repr_ += ", tzinfo={tzinfo}"

        repr_ += ")"

        return repr_.format(
            klass=self.__class__.__name__,
            year=self.year,
            month=self.month,
            day=self.day,
            hour=self.hour,
            minute=self.minute,
            second=self.second,
            us=us,
            tzinfo=repr(self.tzinfo),
        )

    # Comparisons
    def closest(self, *dts: datetime.datetime) -> Self:  # type: ignore[override]
        """
        Get the closest date to the instance.
        """
        pdts = [self.instance(x) for x in dts]

        return min((abs(self - dt), dt) for dt in pdts)[1]

    def farthest(self, *dts: datetime.datetime) -> Self:  # type: ignore[override]
        """
        Get the farthest date from the instance.
        """
        pdts = [self.instance(x) for x in dts]

        return max((abs(self - dt), dt) for dt in pdts)[1]

    def is_future(self) -> bool:
        """
        Determines if the instance is in the future, ie. greater than now.
        """
        return self > self.now(self.timezone)

    def is_past(self) -> bool:
        """
        Determines if the instance is in the past, ie. less than now.
        """
        return self < self.now(self.timezone)

    def is_long_year(self) -> bool:
        """
        Determines if the instance is a long year

        See link `https://en.wikipedia.org/wiki/ISO_8601#Week_dates`_
        """
        return (
            DateTime.create(self.year, 12, 28, 0, 0, 0, tz=self.tz).isocalendar()[1]
            == 53
        )

    def is_same_day(self, dt: datetime.datetime) -> bool:  # type: ignore[override]
        """
        Checks if the passed in date is the same day
        as the instance current day.
        """
        dt = self.instance(dt)

        return self.to_date_string() == dt.to_date_string()

    def is_anniversary(  # type: ignore[override]
        self, dt: datetime.datetime | None = None
    ) -> bool:
        """
        Check if its the anniversary.
        Compares the date/month values of the two dates.
        """
        if dt is None:
            dt = self.now(self.tz)

        instance = self.instance(dt)

        return (self.month, self.day) == (instance.month, instance.day)

    # ADDITIONS AND SUBSTRACTIONS

    def add(
        self,
        years: int = 0,
        months: int = 0,
        weeks: int = 0,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: float = 0,
        microseconds: int = 0,
    ) -> Self:
        """
        Add a duration to the instance.

        If we're adding units of variable length (i.e., years, months),
        move forward from current time, otherwise move forward from utc, for accuracy
        when moving across DST boundaries.
        """
        units_of_variable_length = any([years, months, weeks, days])

        current_dt = datetime.datetime(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
        )
        if not units_of_variable_length:
            offset = self.utcoffset()
            if offset:
                current_dt = current_dt - offset

        dt = add_duration(
            current_dt,
            years=years,
            months=months,
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            microseconds=microseconds,
        )

        if units_of_variable_length or self.tz is None:
            return self.__class__.create(
                dt.year,
                dt.month,
                dt.day,
                dt.hour,
                dt.minute,
                dt.second,
                dt.microsecond,
                tz=self.tz,
            )

        dt = datetime.datetime(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            tzinfo=UTC,
        )

        dt = self.tz.convert(dt)

        return self.__class__(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            tzinfo=self.tz,
            fold=dt.fold,
        )

    def subtract(
        self,
        years: int = 0,
        months: int = 0,
        weeks: int = 0,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: float = 0,
        microseconds: int = 0,
    ) -> Self:
        """
        Remove duration from the instance.
        """
        return self.add(
            years=-years,
            months=-months,
            weeks=-weeks,
            days=-days,
            hours=-hours,
            minutes=-minutes,
            seconds=-seconds,
            microseconds=-microseconds,
        )

    # Adding a final underscore to the method name
    # to avoid errors for PyPy which already defines
    # a _add_timedelta method
    def _add_timedelta_(self, delta: datetime.timedelta) -> Self:
        """
        Add timedelta duration to the instance.
        """
        if isinstance(delta, pendulum.Interval):
            return self.add(
                years=delta.years,
                months=delta.months,
                weeks=delta.weeks,
                days=delta.remaining_days,
                hours=delta.hours,
                minutes=delta.minutes,
                seconds=delta.remaining_seconds,
                microseconds=delta.microseconds,
            )
        elif isinstance(delta, pendulum.Duration):
            return self.add(**delta._signature)  # type: ignore[attr-defined]

        return self.add(seconds=delta.total_seconds())

    def _subtract_timedelta(self, delta: datetime.timedelta) -> Self:
        """
        Remove timedelta duration from the instance.
        """
        if isinstance(delta, pendulum.Duration):
            return self.subtract(
                years=delta.years, months=delta.months, seconds=delta._total
            )

        return self.subtract(seconds=delta.total_seconds())

    # DIFFERENCES

    def diff(  # type: ignore[override]
        self, dt: datetime.datetime | None = None, abs: bool = True
    ) -> Interval:
        """
        Returns the difference between two DateTime objects represented as an Interval.
        """
        if dt is None:
            dt = self.now(self.tz)

        return Interval(self, dt, absolute=abs)

    def diff_for_humans(  # type: ignore[override]
        self,
        other: DateTime | None = None,
        absolute: bool = False,
        locale: str | None = None,
    ) -> str:
        """
        Get the difference in a human readable format in the current locale.

        When comparing a value in the past to default now:
        1 day ago
        5 months ago

        When comparing a value in the future to default now:
        1 day from now
        5 months from now

        When comparing a value in the past to another value:
        1 day before
        5 months before

        When comparing a value in the future to another value:
        1 day after
        5 months after
        """
        is_now = other is None

        if is_now:
            other = self.now()

        diff = self.diff(other)

        return pendulum.format_diff(diff, is_now, absolute, locale)

    # Modifiers
    def start_of(self, unit: str) -> Self:
        """
        Returns a copy of the instance with the time reset
        with the following rules:

        * second: microsecond set to 0
        * minute: second and microsecond set to 0
        * hour: minute, second and microsecond set to 0
        * day: time to 00:00:00
        * week: date to first day of the week and time to 00:00:00
        * month: date to first day of the month and time to 00:00:00
        * year: date to first day of the year and time to 00:00:00
        * decade: date to first day of the decade and time to 00:00:00
        * century: date to first day of century and time to 00:00:00
        """
        if unit not in self._MODIFIERS_VALID_UNITS:
            raise ValueError(f'Invalid unit "{unit}" for start_of()')

        return cast("Self", getattr(self, f"_start_of_{unit}")())

    def end_of(self, unit: str) -> Self:
        """
        Returns a copy of the instance with the time reset
        with the following rules:

        * second: microsecond set to 999999
        * minute: second set to 59 and microsecond set to 999999
        * hour: minute and second set to 59 and microsecond set to 999999
        * day: time to 23:59:59.999999
        * week: date to last day of the week and time to 23:59:59.999999
        * month: date to last day of the month and time to 23:59:59.999999
        * year: date to last day of the year and time to 23:59:59.999999
        * decade: date to last day of the decade and time to 23:59:59.999999
        * century: date to last day of century and time to 23:59:59.999999
        """
        if unit not in self._MODIFIERS_VALID_UNITS:
            raise ValueError(f'Invalid unit "{unit}" for end_of()')

        return cast("Self", getattr(self, f"_end_of_{unit}")())

    def _start_of_second(self) -> Self:
        """
        Reset microseconds to 0.
        """
        return self.set(microsecond=0)

    def _end_of_second(self) -> Self:
        """
        Set microseconds to 999999.
        """
        return self.set(microsecond=999999)

    def _start_of_minute(self) -> Self:
        """
        Reset seconds and microseconds to 0.
        """
        return self.set(second=0, microsecond=0)

    def _end_of_minute(self) -> Self:
        """
        Set seconds to 59 and microseconds to 999999.
        """
        return self.set(second=59, microsecond=999999)

    def _start_of_hour(self) -> Self:
        """
        Reset minutes, seconds and microseconds to 0.
        """
        return self.set(minute=0, second=0, microsecond=0)

    def _end_of_hour(self) -> Self:
        """
        Set minutes and seconds to 59 and microseconds to 999999.
        """
        return self.set(minute=59, second=59, microsecond=999999)

    def _start_of_day(self) -> Self:
        """
        Reset the time to 00:00:00.
        """
        return self.at(0, 0, 0, 0)

    def _end_of_day(self) -> Self:
        """
        Reset the time to 23:59:59.999999.
        """
        return self.at(23, 59, 59, 999999)

    def _start_of_month(self) -> Self:
        """
        Reset the date to the first day of the month and the time to 00:00:00.
        """
        return self.set(self.year, self.month, 1, 0, 0, 0, 0)

    def _end_of_month(self) -> Self:
        """
        Reset the date to the last day of the month
        and the time to 23:59:59.999999.
        """
        return self.set(self.year, self.month, self.days_in_month, 23, 59, 59, 999999)

    def _start_of_year(self) -> Self:
        """
        Reset the date to the first day of the year and the time to 00:00:00.
        """
        return self.set(self.year, 1, 1, 0, 0, 0, 0)

    def _end_of_year(self) -> Self:
        """
        Reset the date to the last day of the year
        and the time to 23:59:59.999999.
        """
        return self.set(self.year, 12, 31, 23, 59, 59, 999999)

    def _start_of_decade(self) -> Self:
        """
        Reset the date to the first day of the decade
        and the time to 00:00:00.
        """
        year = self.year - self.year % YEARS_PER_DECADE
        return self.set(year, 1, 1, 0, 0, 0, 0)

    def _end_of_decade(self) -> Self:
        """
        Reset the date to the last day of the decade
        and the time to 23:59:59.999999.
        """
        year = self.year - self.year % YEARS_PER_DECADE + YEARS_PER_DECADE - 1

        return self.set(year, 12, 31, 23, 59, 59, 999999)

    def _start_of_century(self) -> Self:
        """
        Reset the date to the first day of the century
        and the time to 00:00:00.
        """
        year = self.year - 1 - (self.year - 1) % YEARS_PER_CENTURY + 1

        return self.set(year, 1, 1, 0, 0, 0, 0)

    def _end_of_century(self) -> Self:
        """
        Reset the date to the last day of the century
        and the time to 23:59:59.999999.
        """
        year = self.year - 1 - (self.year - 1) % YEARS_PER_CENTURY + YEARS_PER_CENTURY

        return self.set(year, 12, 31, 23, 59, 59, 999999)

    def _start_of_week(self) -> Self:
        """
        Reset the date to the first day of the week
        and the time to 00:00:00.
        """
        dt = self

        if self.day_of_week != pendulum._WEEK_STARTS_AT:
            dt = self.previous(pendulum._WEEK_STARTS_AT)

        return dt.start_of("day")

    def _end_of_week(self) -> Self:
        """
        Reset the date to the last day of the week
        and the time to 23:59:59.
        """
        dt = self

        if self.day_of_week != pendulum._WEEK_ENDS_AT:
            dt = self.next(pendulum._WEEK_ENDS_AT)

        return dt.end_of("day")

    def next(self, day_of_week: WeekDay | None = None, keep_time: bool = False) -> Self:
        """
        Modify to the next occurrence of a given day of the week.
        If no day_of_week is provided, modify to the next occurrence
        of the current day of the week.  Use the supplied consts
        to indicate the desired day_of_week, ex. DateTime.MONDAY.
        """
        if day_of_week is None:
            day_of_week = self.day_of_week

        if day_of_week < WeekDay.MONDAY or day_of_week > WeekDay.SUNDAY:
            raise ValueError("Invalid day of week")

        dt = self if keep_time else self.start_of("day")

        dt = dt.add(days=1)
        while dt.day_of_week != day_of_week:
            dt = dt.add(days=1)

        return dt

    def previous(
        self, day_of_week: WeekDay | None = None, keep_time: bool = False
    ) -> Self:
        """
        Modify to the previous occurrence of a given day of the week.
        If no day_of_week is provided, modify to the previous occurrence
        of the current day of the week.  Use the supplied consts
        to indicate the desired day_of_week, ex. DateTime.MONDAY.
        """
        if day_of_week is None:
            day_of_week = self.day_of_week

        if day_of_week < WeekDay.MONDAY or day_of_week > WeekDay.SUNDAY:
            raise ValueError("Invalid day of week")

        dt = self if keep_time else self.start_of("day")

        dt = dt.subtract(days=1)
        while dt.day_of_week != day_of_week:
            dt = dt.subtract(days=1)

        return dt

    def first_of(self, unit: str, day_of_week: WeekDay | None = None) -> Self:
        """
        Returns an instance set to the first occurrence
        of a given day of the week in the current unit.
        If no day_of_week is provided, modify to the first day of the unit.
        Use the supplied consts to indicate the desired day_of_week,
        ex. DateTime.MONDAY.

        Supported units are month, quarter and year.
        """
        if unit not in ["month", "quarter", "year"]:
            raise ValueError(f'Invalid unit "{unit}" for first_of()')

        return cast("Self", getattr(self, f"_first_of_{unit}")(day_of_week))

    def last_of(self, unit: str, day_of_week: WeekDay | None = None) -> Self:
        """
        Returns an instance set to the last occurrence
        of a given day of the week in the current unit.
        If no day_of_week is provided, modify to the last day of the unit.
        Use the supplied consts to indicate the desired day_of_week,
        ex. DateTime.MONDAY.

        Supported units are month, quarter and year.
        """
        if unit not in ["month", "quarter", "year"]:
            raise ValueError(f'Invalid unit "{unit}" for first_of()')

        return cast("Self", getattr(self, f"_last_of_{unit}")(day_of_week))

    def nth_of(self, unit: str, nth: int, day_of_week: WeekDay) -> Self:
        """
        Returns a new instance set to the given occurrence
        of a given day of the week in the current unit.
        If the calculated occurrence is outside the scope of the current unit,
        then raise an error. Use the supplied consts
        to indicate the desired day_of_week, ex. DateTime.MONDAY.

        Supported units are month, quarter and year.
        """
        if unit not in ["month", "quarter", "year"]:
            raise ValueError(f'Invalid unit "{unit}" for first_of()')

        dt = cast(Optional["Self"], getattr(self, f"_nth_of_{unit}")(nth, day_of_week))
        if not dt:
            raise PendulumException(
                f"Unable to find occurrence {nth}"
                f" of {WeekDay(day_of_week).name.capitalize()} in {unit}"
            )

        return dt

    def _first_of_month(self, day_of_week: WeekDay | None = None) -> Self:
        """
        Modify to the first occurrence of a given day of the week
        in the current month. If no day_of_week is provided,
        modify to the first day of the month. Use the supplied consts
        to indicate the desired day_of_week, ex. DateTime.MONDAY.
        """
        dt = self.start_of("day")

        if day_of_week is None:
            return dt.set(day=1)

        month = calendar.monthcalendar(dt.year, dt.month)

        calendar_day = day_of_week

        if month[0][calendar_day] > 0:
            day_of_month = month[0][calendar_day]
        else:
            day_of_month = month[1][calendar_day]

        return dt.set(day=day_of_month)

    def _last_of_month(self, day_of_week: WeekDay | None = None) -> Self:
        """
        Modify to the last occurrence of a given day of the week
        in the current month. If no day_of_week is provided,
        modify to the last day of the month. Use the supplied consts
        to indicate the desired day_of_week, ex. DateTime.MONDAY.
        """
        dt = self.start_of("day")

        if day_of_week is None:
            return dt.set(day=self.days_in_month)

        month = calendar.monthcalendar(dt.year, dt.month)

        calendar_day = day_of_week

        if month[-1][calendar_day] > 0:
            day_of_month = month[-1][calendar_day]
        else:
            day_of_month = month[-2][calendar_day]

        return dt.set(day=day_of_month)

    def _nth_of_month(
        self, nth: int, day_of_week: WeekDay | None = None
    ) -> Self | None:
        """
        Modify to the given occurrence of a given day of the week
        in the current month. If the calculated occurrence is outside,
        the scope of the current month, then return False and no
        modifications are made. Use the supplied consts
        to indicate the desired day_of_week, ex. DateTime.MONDAY.
        """
        if nth == 1:
            return self.first_of("month", day_of_week)

        dt = self.first_of("month")
        check = dt.format("%Y-%M")
        for _ in range(nth - (1 if dt.day_of_week == day_of_week else 0)):
            dt = dt.next(day_of_week)

        if dt.format("%Y-%M") == check:
            return self.set(day=dt.day).start_of("day")

        return None

    def _first_of_quarter(self, day_of_week: WeekDay | None = None) -> Self:
        """
        Modify to the first occurrence of a given day of the week
        in the current quarter. If no day_of_week is provided,
        modify to the first day of the quarter. Use the supplied consts
        to indicate the desired day_of_week, ex. DateTime.MONDAY.
        """
        return self.on(self.year, self.quarter * 3 - 2, 1).first_of(
            "month", day_of_week
        )

    def _last_of_quarter(self, day_of_week: WeekDay | None = None) -> Self:
        """
        Modify to the last occurrence of a given day of the week
        in the current quarter. If no day_of_week is provided,
        modify to the last day of the quarter. Use the supplied consts
        to indicate the desired day_of_week, ex. DateTime.MONDAY.
        """
        return self.on(self.year, self.quarter * 3, 1).last_of("month", day_of_week)

    def _nth_of_quarter(
        self, nth: int, day_of_week: WeekDay | None = None
    ) -> Self | None:
        """
        Modify to the given occurrence of a given day of the week
        in the current quarter. If the calculated occurrence is outside,
        the scope of the current quarter, then return False and no
        modifications are made. Use the supplied consts
        to indicate the desired day_of_week, ex. DateTime.MONDAY.
        """
        if nth == 1:
            return self.first_of("quarter", day_of_week)

        dt = self.set(day=1, month=self.quarter * 3)
        last_month = dt.month
        year = dt.year
        dt = dt.first_of("quarter")
        for _ in range(nth - (1 if dt.day_of_week == day_of_week else 0)):
            dt = dt.next(day_of_week)

        if last_month < dt.month or year != dt.year:
            return None

        return self.on(self.year, dt.month, dt.day).start_of("day")

    def _first_of_year(self, day_of_week: WeekDay | None = None) -> Self:
        """
        Modify to the first occurrence of a given day of the week
        in the current year. If no day_of_week is provided,
        modify to the first day of the year. Use the supplied consts
        to indicate the desired day_of_week, ex. DateTime.MONDAY.
        """
        return self.set(month=1).first_of("month", day_of_week)

    def _last_of_year(self, day_of_week: WeekDay | None = None) -> Self:
        """
        Modify to the last occurrence of a given day of the week
        in the current year. If no day_of_week is provided,
        modify to the last day of the year. Use the supplied consts
        to indicate the desired day_of_week, ex. DateTime.MONDAY.
        """
        return self.set(month=MONTHS_PER_YEAR).last_of("month", day_of_week)

    def _nth_of_year(self, nth: int, day_of_week: WeekDay | None = None) -> Self | None:
        """
        Modify to the given occurrence of a given day of the week
        in the current year. If the calculated occurrence is outside,
        the scope of the current year, then return False and no
        modifications are made. Use the supplied consts
        to indicate the desired day_of_week, ex. DateTime.MONDAY.
        """
        if nth == 1:
            return self.first_of("year", day_of_week)

        dt = self.first_of("year")
        year = dt.year
        for _ in range(nth - (1 if dt.day_of_week == day_of_week else 0)):
            dt = dt.next(day_of_week)

        if year != dt.year:
            return None

        return self.on(self.year, dt.month, dt.day).start_of("day")

    def average(  # type: ignore[override]
        self, dt: datetime.datetime | None = None
    ) -> Self:
        """
        Modify the current instance to the average
        of a given instance (default now) and the current instance.
        """
        if dt is None:
            dt = self.now(self.tz)

        diff = self.diff(dt, False)
        return self.add(
            microseconds=(diff.in_seconds() * 1000000 + diff.microseconds) // 2
        )

    @overload  # type: ignore[override]
    def __sub__(self, other: datetime.timedelta) -> Self:
        ...

    @overload
    def __sub__(self, other: DateTime) -> Interval:
        ...

    def __sub__(self, other: datetime.datetime | datetime.timedelta) -> Self | Interval:
        if isinstance(other, datetime.timedelta):
            return self._subtract_timedelta(other)

        if not isinstance(other, datetime.datetime):
            return NotImplemented

        if not isinstance(other, self.__class__):
            if other.tzinfo is None:
                other = pendulum.naive(
                    other.year,
                    other.month,
                    other.day,
                    other.hour,
                    other.minute,
                    other.second,
                    other.microsecond,
                )
            else:
                other = self.instance(other)

        return other.diff(self, False)

    def __rsub__(self, other: datetime.datetime) -> Interval:
        if not isinstance(other, datetime.datetime):
            return NotImplemented

        if not isinstance(other, self.__class__):
            if other.tzinfo is None:
                other = pendulum.naive(
                    other.year,
                    other.month,
                    other.day,
                    other.hour,
                    other.minute,
                    other.second,
                    other.microsecond,
                )
            else:
                other = self.instance(other)

        return self.diff(other, False)

    def __add__(self, other: datetime.timedelta) -> Self:
        if not isinstance(other, datetime.timedelta):
            return NotImplemented

        caller = traceback.extract_stack(limit=2)[0].name
        if caller == "astimezone":
            return super().__add__(other)

        return self._add_timedelta_(other)

    def __radd__(self, other: datetime.timedelta) -> Self:
        return self.__add__(other)

    # Native methods override

    @classmethod
    def fromtimestamp(cls, t: float, tz: datetime.tzinfo | None = None) -> Self:
        tzinfo = pendulum._safe_timezone(tz)

        return cls.instance(datetime.datetime.fromtimestamp(t, tz=tzinfo), tz=tzinfo)

    @classmethod
    def utcfromtimestamp(cls, t: float) -> Self:
        return cls.instance(datetime.datetime.utcfromtimestamp(t), tz=None)

    @classmethod
    def fromordinal(cls, n: int) -> Self:
        return cls.instance(datetime.datetime.fromordinal(n), tz=None)

    @classmethod
    def combine(
        cls,
        date: datetime.date,
        time: datetime.time,
        tzinfo: datetime.tzinfo | None = None,
    ) -> Self:
        return cls.instance(datetime.datetime.combine(date, time), tz=tzinfo)

    def astimezone(self, tz: datetime.tzinfo | None = None) -> Self:
        dt = super().astimezone(tz)

        return self.__class__(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            fold=dt.fold,
            tzinfo=dt.tzinfo,
        )

    def replace(
        self,
        year: SupportsIndex | None = None,
        month: SupportsIndex | None = None,
        day: SupportsIndex | None = None,
        hour: SupportsIndex | None = None,
        minute: SupportsIndex | None = None,
        second: SupportsIndex | None = None,
        microsecond: SupportsIndex | None = None,
        tzinfo: bool | datetime.tzinfo | Literal[True] | None = True,
        fold: int | None = None,
    ) -> Self:
        if year is None:
            year = self.year
        if month is None:
            month = self.month
        if day is None:
            day = self.day
        if hour is None:
            hour = self.hour
        if minute is None:
            minute = self.minute
        if second is None:
            second = self.second
        if microsecond is None:
            microsecond = self.microsecond
        if tzinfo is True:
            tzinfo = self.tzinfo
        if fold is None:
            fold = self.fold

        if tzinfo is not None:
            tzinfo = pendulum._safe_timezone(tzinfo)

        return self.__class__.create(
            year,
            month,
            day,
            hour,
            minute,
            second,
            microsecond,
            tz=tzinfo,
            fold=fold,
        )

    def __getnewargs__(self) -> tuple[Self]:
        return (self,)

    def _getstate(
        self, protocol: SupportsIndex = 3
    ) -> tuple[int, int, int, int, int, int, int, datetime.tzinfo | None]:
        return (
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
            self.tzinfo,
        )

    def __reduce__(
        self,
    ) -> tuple[
        type[Self],
        tuple[int, int, int, int, int, int, int, datetime.tzinfo | None],
    ]:
        return self.__reduce_ex__(2)

    def __reduce_ex__(
        self, protocol: SupportsIndex
    ) -> tuple[
        type[Self],
        tuple[int, int, int, int, int, int, int, datetime.tzinfo | None],
    ]:
        return self.__class__, self._getstate(protocol)

    def __deepcopy__(self, _: dict[int, Self]) -> Self:
        return self.__class__(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
            tzinfo=self.tz,
            fold=self.fold,
        )

    def _cmp(self, other: datetime.datetime, **kwargs: Any) -> int:
        # Fix for pypy which compares using this method
        # which would lead to infinite recursion if we didn't override
        dt = datetime.datetime(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
            tzinfo=self.tz,
            fold=self.fold,
        )

        return 0 if dt == other else 1 if dt > other else -1


DateTime.min = DateTime(1, 1, 1, 0, 0, tzinfo=UTC)
DateTime.max = DateTime(9999, 12, 31, 23, 59, 59, 999999, tzinfo=UTC)
DateTime.EPOCH = DateTime(1970, 1, 1, tzinfo=UTC)
