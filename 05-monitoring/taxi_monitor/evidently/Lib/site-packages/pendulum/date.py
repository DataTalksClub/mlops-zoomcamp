# The following is only needed because of Python 3.7
# mypy: no-warn-unused-ignores
from __future__ import annotations

import calendar
import math

from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import TYPE_CHECKING
from typing import ClassVar
from typing import NoReturn
from typing import cast
from typing import overload

import pendulum

from pendulum.constants import MONTHS_PER_YEAR
from pendulum.constants import YEARS_PER_CENTURY
from pendulum.constants import YEARS_PER_DECADE
from pendulum.day import WeekDay
from pendulum.exceptions import PendulumException
from pendulum.helpers import add_duration
from pendulum.interval import Interval
from pendulum.mixins.default import FormattableMixin


if TYPE_CHECKING:
    from typing_extensions import Self
    from typing_extensions import SupportsIndex


class Date(FormattableMixin, date):
    _MODIFIERS_VALID_UNITS: ClassVar[list[str]] = [
        "day",
        "week",
        "month",
        "year",
        "decade",
        "century",
    ]

    # Getters/Setters

    def set(
        self, year: int | None = None, month: int | None = None, day: int | None = None
    ) -> Self:
        return self.replace(year=year, month=month, day=day)

    @property
    def day_of_week(self) -> WeekDay:
        """
        Returns the day of the week (0-6).
        """
        return WeekDay(self.weekday())

    @property
    def day_of_year(self) -> int:
        """
        Returns the day of the year (1-366).
        """
        k = 1 if self.is_leap_year() else 2

        return (275 * self.month) // 9 - k * ((self.month + 9) // 12) + self.day - 30

    @property
    def week_of_year(self) -> int:
        return self.isocalendar()[1]

    @property
    def days_in_month(self) -> int:
        return calendar.monthrange(self.year, self.month)[1]

    @property
    def week_of_month(self) -> int:
        return math.ceil((self.day + self.first_of("month").isoweekday() - 1) / 7)

    @property
    def age(self) -> int:
        return self.diff(abs=False).in_years()

    @property
    def quarter(self) -> int:
        return math.ceil(self.month / 3)

    # String Formatting

    def to_date_string(self) -> str:
        """
        Format the instance as date.

        :rtype: str
        """
        return self.strftime("%Y-%m-%d")

    def to_formatted_date_string(self) -> str:
        """
        Format the instance as a readable date.

        :rtype: str
        """
        return self.strftime("%b %d, %Y")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.year}, {self.month}, {self.day})"

    # COMPARISONS

    def closest(self, dt1: date, dt2: date) -> Self:
        """
        Get the closest date from the instance.
        """
        dt1 = self.__class__(dt1.year, dt1.month, dt1.day)
        dt2 = self.__class__(dt2.year, dt2.month, dt2.day)

        if self.diff(dt1).in_seconds() < self.diff(dt2).in_seconds():
            return dt1

        return dt2

    def farthest(self, dt1: date, dt2: date) -> Self:
        """
        Get the farthest date from the instance.
        """
        dt1 = self.__class__(dt1.year, dt1.month, dt1.day)
        dt2 = self.__class__(dt2.year, dt2.month, dt2.day)

        if self.diff(dt1).in_seconds() > self.diff(dt2).in_seconds():
            return dt1

        return dt2

    def is_future(self) -> bool:
        """
        Determines if the instance is in the future, ie. greater than now.
        """
        return self > self.today()

    def is_past(self) -> bool:
        """
        Determines if the instance is in the past, ie. less than now.
        """
        return self < self.today()

    def is_leap_year(self) -> bool:
        """
        Determines if the instance is a leap year.
        """
        return calendar.isleap(self.year)

    def is_long_year(self) -> bool:
        """
        Determines if the instance is a long year

        See link `<https://en.wikipedia.org/wiki/ISO_8601#Week_dates>`_
        """
        return Date(self.year, 12, 28).isocalendar()[1] == 53

    def is_same_day(self, dt: date) -> bool:
        """
        Checks if the passed in date is the same day as the instance current day.
        """
        return self == dt

    def is_anniversary(self, dt: date | None = None) -> bool:
        """
        Check if it's the anniversary.

        Compares the date/month values of the two dates.
        """
        if dt is None:
            dt = self.__class__.today()

        instance = self.__class__(dt.year, dt.month, dt.day)

        return (self.month, self.day) == (instance.month, instance.day)

    # the additional method for checking if today is the anniversary day
    # the alias is provided to start using a new name and keep the backward
    # compatibility the old name can be completely replaced with the new in
    # one of the future versions
    is_birthday = is_anniversary

    # ADDITIONS AND SUBTRACTIONS

    def add(
        self, years: int = 0, months: int = 0, weeks: int = 0, days: int = 0
    ) -> Self:
        """
        Add duration to the instance.

        :param years: The number of years
        :param months: The number of months
        :param weeks: The number of weeks
        :param days: The number of days
        """
        dt = add_duration(
            date(self.year, self.month, self.day),
            years=years,
            months=months,
            weeks=weeks,
            days=days,
        )

        return self.__class__(dt.year, dt.month, dt.day)

    def subtract(
        self, years: int = 0, months: int = 0, weeks: int = 0, days: int = 0
    ) -> Self:
        """
        Remove duration from the instance.

        :param years: The number of years
        :param months: The number of months
        :param weeks: The number of weeks
        :param days: The number of days
        """
        return self.add(years=-years, months=-months, weeks=-weeks, days=-days)

    def _add_timedelta(self, delta: timedelta) -> Self:
        """
        Add timedelta duration to the instance.

        :param delta: The timedelta instance
        """
        if isinstance(delta, pendulum.Duration):
            return self.add(
                years=delta.years,
                months=delta.months,
                weeks=delta.weeks,
                days=delta.remaining_days,
            )

        return self.add(days=delta.days)

    def _subtract_timedelta(self, delta: timedelta) -> Self:
        """
        Remove timedelta duration from the instance.

        :param delta: The timedelta instance
        """
        if isinstance(delta, pendulum.Duration):
            return self.subtract(
                years=delta.years,
                months=delta.months,
                weeks=delta.weeks,
                days=delta.remaining_days,
            )

        return self.subtract(days=delta.days)

    def __add__(self, other: timedelta) -> Self:
        if not isinstance(other, timedelta):
            return NotImplemented

        return self._add_timedelta(other)

    @overload  # type: ignore[override]  # this is only needed because of Python 3.7
    def __sub__(self, __delta: timedelta) -> Self:
        ...

    @overload
    def __sub__(self, __dt: datetime) -> NoReturn:
        ...

    @overload
    def __sub__(self, __dt: Self) -> Interval:
        ...

    def __sub__(self, other: timedelta | date) -> Self | Interval:
        if isinstance(other, timedelta):
            return self._subtract_timedelta(other)

        if not isinstance(other, date):
            return NotImplemented

        dt = self.__class__(other.year, other.month, other.day)

        return dt.diff(self, False)

    # DIFFERENCES

    def diff(self, dt: date | None = None, abs: bool = True) -> Interval:
        """
        Returns the difference between two Date objects as an Interval.

        :param dt: The date to compare to (defaults to today)
        :param abs: Whether to return an absolute interval or not
        """
        if dt is None:
            dt = self.today()

        return Interval(self, Date(dt.year, dt.month, dt.day), absolute=abs)

    def diff_for_humans(
        self,
        other: date | None = None,
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

        :param other: The date to compare to (defaults to today)
        :param absolute: removes time difference modifiers ago, after, etc
        :param locale: The locale to use for localization
        """
        is_now = other is None

        if is_now:
            other = self.today()

        diff = self.diff(other)

        return pendulum.format_diff(diff, is_now, absolute, locale)

    # MODIFIERS

    def start_of(self, unit: str) -> Self:
        """
        Returns a copy of the instance with the time reset
        with the following rules:

        * day: time to 00:00:00
        * week: date to first day of the week and time to 00:00:00
        * month: date to first day of the month and time to 00:00:00
        * year: date to first day of the year and time to 00:00:00
        * decade: date to first day of the decade and time to 00:00:00
        * century: date to first day of century and time to 00:00:00

        :param unit: The unit to reset to
        """
        if unit not in self._MODIFIERS_VALID_UNITS:
            raise ValueError(f'Invalid unit "{unit}" for start_of()')

        return cast("Self", getattr(self, f"_start_of_{unit}")())

    def end_of(self, unit: str) -> Self:
        """
        Returns a copy of the instance with the time reset
        with the following rules:

        * week: date to last day of the week
        * month: date to last day of the month
        * year: date to last day of the year
        * decade: date to last day of the decade
        * century: date to last day of century

        :param unit: The unit to reset to
        """
        if unit not in self._MODIFIERS_VALID_UNITS:
            raise ValueError(f'Invalid unit "{unit}" for end_of()')

        return cast("Self", getattr(self, f"_end_of_{unit}")())

    def _start_of_day(self) -> Self:
        """
        Compatibility method.
        """
        return self

    def _end_of_day(self) -> Self:
        """
        Compatibility method
        """
        return self

    def _start_of_month(self) -> Self:
        """
        Reset the date to the first day of the month.
        """
        return self.set(self.year, self.month, 1)

    def _end_of_month(self) -> Self:
        """
        Reset the date to the last day of the month.
        """
        return self.set(self.year, self.month, self.days_in_month)

    def _start_of_year(self) -> Self:
        """
        Reset the date to the first day of the year.
        """
        return self.set(self.year, 1, 1)

    def _end_of_year(self) -> Self:
        """
        Reset the date to the last day of the year.
        """
        return self.set(self.year, 12, 31)

    def _start_of_decade(self) -> Self:
        """
        Reset the date to the first day of the decade.
        """
        year = self.year - self.year % YEARS_PER_DECADE

        return self.set(year, 1, 1)

    def _end_of_decade(self) -> Self:
        """
        Reset the date to the last day of the decade.
        """
        year = self.year - self.year % YEARS_PER_DECADE + YEARS_PER_DECADE - 1

        return self.set(year, 12, 31)

    def _start_of_century(self) -> Self:
        """
        Reset the date to the first day of the century.
        """
        year = self.year - 1 - (self.year - 1) % YEARS_PER_CENTURY + 1

        return self.set(year, 1, 1)

    def _end_of_century(self) -> Self:
        """
        Reset the date to the last day of the century.
        """
        year = self.year - 1 - (self.year - 1) % YEARS_PER_CENTURY + YEARS_PER_CENTURY

        return self.set(year, 12, 31)

    def _start_of_week(self) -> Self:
        """
        Reset the date to the first day of the week.
        """
        dt = self

        if self.day_of_week != pendulum._WEEK_STARTS_AT:
            dt = self.previous(pendulum._WEEK_STARTS_AT)

        return dt.start_of("day")

    def _end_of_week(self) -> Self:
        """
        Reset the date to the last day of the week.
        """
        dt = self

        if self.day_of_week != pendulum._WEEK_ENDS_AT:
            dt = self.next(pendulum._WEEK_ENDS_AT)

        return dt.end_of("day")

    def next(self, day_of_week: WeekDay | None = None) -> Self:
        """
        Modify to the next occurrence of a given day of the week.
        If no day_of_week is provided, modify to the next occurrence
        of the current day of the week.  Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.

        :param day_of_week: The next day of week to reset to.
        """
        if day_of_week is None:
            day_of_week = self.day_of_week

        if day_of_week < WeekDay.MONDAY or day_of_week > WeekDay.SUNDAY:
            raise ValueError("Invalid day of week")

        dt = self.add(days=1)
        while dt.day_of_week != day_of_week:
            dt = dt.add(days=1)

        return dt

    def previous(self, day_of_week: WeekDay | None = None) -> Self:
        """
        Modify to the previous occurrence of a given day of the week.
        If no day_of_week is provided, modify to the previous occurrence
        of the current day of the week.  Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.

        :param day_of_week: The previous day of week to reset to.
        """
        if day_of_week is None:
            day_of_week = self.day_of_week

        if day_of_week < WeekDay.MONDAY or day_of_week > WeekDay.SUNDAY:
            raise ValueError("Invalid day of week")

        dt = self.subtract(days=1)
        while dt.day_of_week != day_of_week:
            dt = dt.subtract(days=1)

        return dt

    def first_of(self, unit: str, day_of_week: WeekDay | None = None) -> Self:
        """
        Returns an instance set to the first occurrence
        of a given day of the week in the current unit.
        If no day_of_week is provided, modify to the first day of the unit.
        Use the supplied consts to indicate the desired day_of_week,
        ex. pendulum.MONDAY.

        Supported units are month, quarter and year.

        :param unit: The unit to use
        :param day_of_week: The day of week to reset to.
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
        ex. pendulum.MONDAY.

        Supported units are month, quarter and year.

        :param unit: The unit to use
        :param day_of_week: The day of week to reset to.
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
        to indicate the desired day_of_week, ex. pendulum.MONDAY.

        Supported units are month, quarter and year.

        :param unit: The unit to use
        :param nth: The occurrence to use
        :param day_of_week: The day of week to set to.
        """
        if unit not in ["month", "quarter", "year"]:
            raise ValueError(f'Invalid unit "{unit}" for first_of()')

        dt = cast("Self", getattr(self, f"_nth_of_{unit}")(nth, day_of_week))
        if not dt:
            raise PendulumException(
                f"Unable to find occurrence {nth}"
                f" of {WeekDay(day_of_week).name.capitalize()} in {unit}"
            )

        return dt

    def _first_of_month(self, day_of_week: WeekDay) -> Self:
        """
        Modify to the first occurrence of a given day of the week
        in the current month. If no day_of_week is provided,
        modify to the first day of the month. Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.

        :param day_of_week: The day of week to set to.
        """
        dt = self

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
        to indicate the desired day_of_week, ex. pendulum.MONDAY.

        :param day_of_week: The day of week to set to.
        """
        dt = self

        if day_of_week is None:
            return dt.set(day=self.days_in_month)

        month = calendar.monthcalendar(dt.year, dt.month)

        calendar_day = day_of_week

        if month[-1][calendar_day] > 0:
            day_of_month = month[-1][calendar_day]
        else:
            day_of_month = month[-2][calendar_day]

        return dt.set(day=day_of_month)

    def _nth_of_month(self, nth: int, day_of_week: WeekDay) -> Self | None:
        """
        Modify to the given occurrence of a given day of the week
        in the current month. If the calculated occurrence is outside,
        the scope of the current month, then return False and no
        modifications are made. Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.
        """
        if nth == 1:
            return self.first_of("month", day_of_week)

        dt = self.first_of("month")
        check = dt.format("YYYY-MM")
        for _ in range(nth - (1 if dt.day_of_week == day_of_week else 0)):
            dt = dt.next(day_of_week)

        if dt.format("YYYY-MM") == check:
            return self.set(day=dt.day)

        return None

    def _first_of_quarter(self, day_of_week: WeekDay | None = None) -> Self:
        """
        Modify to the first occurrence of a given day of the week
        in the current quarter. If no day_of_week is provided,
        modify to the first day of the quarter. Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.
        """
        return self.set(self.year, self.quarter * 3 - 2, 1).first_of(
            "month", day_of_week
        )

    def _last_of_quarter(self, day_of_week: WeekDay | None = None) -> Self:
        """
        Modify to the last occurrence of a given day of the week
        in the current quarter. If no day_of_week is provided,
        modify to the last day of the quarter. Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.
        """
        return self.set(self.year, self.quarter * 3, 1).last_of("month", day_of_week)

    def _nth_of_quarter(self, nth: int, day_of_week: WeekDay) -> Self | None:
        """
        Modify to the given occurrence of a given day of the week
        in the current quarter. If the calculated occurrence is outside,
        the scope of the current quarter, then return False and no
        modifications are made. Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.
        """
        if nth == 1:
            return self.first_of("quarter", day_of_week)

        dt = self.replace(self.year, self.quarter * 3, 1)
        last_month = dt.month
        year = dt.year
        dt = dt.first_of("quarter")
        for _ in range(nth - (1 if dt.day_of_week == day_of_week else 0)):
            dt = dt.next(day_of_week)

        if last_month < dt.month or year != dt.year:
            return None

        return self.set(self.year, dt.month, dt.day)

    def _first_of_year(self, day_of_week: WeekDay | None = None) -> Self:
        """
        Modify to the first occurrence of a given day of the week
        in the current year. If no day_of_week is provided,
        modify to the first day of the year. Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.
        """
        return self.set(month=1).first_of("month", day_of_week)

    def _last_of_year(self, day_of_week: WeekDay | None = None) -> Self:
        """
        Modify to the last occurrence of a given day of the week
        in the current year. If no day_of_week is provided,
        modify to the last day of the year. Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.
        """
        return self.set(month=MONTHS_PER_YEAR).last_of("month", day_of_week)

    def _nth_of_year(self, nth: int, day_of_week: WeekDay) -> Self | None:
        """
        Modify to the given occurrence of a given day of the week
        in the current year. If the calculated occurrence is outside,
        the scope of the current year, then return False and no
        modifications are made. Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.
        """
        if nth == 1:
            return self.first_of("year", day_of_week)

        dt = self.first_of("year")
        year = dt.year
        for _ in range(nth - (1 if dt.day_of_week == day_of_week else 0)):
            dt = dt.next(day_of_week)

        if year != dt.year:
            return None

        return self.set(self.year, dt.month, dt.day)

    def average(self, dt: date | None = None) -> Self:
        """
        Modify the current instance to the average
        of a given instance (default now) and the current instance.
        """
        if dt is None:
            dt = Date.today()

        return self.add(days=int(self.diff(dt, False).in_days() / 2))

    # Native methods override

    @classmethod
    def today(cls) -> Self:
        dt = date.today()

        return cls(dt.year, dt.month, dt.day)

    @classmethod
    def fromtimestamp(cls, t: float) -> Self:
        dt = super().fromtimestamp(t)

        return cls(dt.year, dt.month, dt.day)

    @classmethod
    def fromordinal(cls, n: int) -> Self:
        dt = super().fromordinal(n)

        return cls(dt.year, dt.month, dt.day)

    def replace(
        self,
        year: SupportsIndex | None = None,
        month: SupportsIndex | None = None,
        day: SupportsIndex | None = None,
    ) -> Self:
        year = year if year is not None else self.year
        month = month if month is not None else self.month
        day = day if day is not None else self.day

        return self.__class__(year, month, day)
