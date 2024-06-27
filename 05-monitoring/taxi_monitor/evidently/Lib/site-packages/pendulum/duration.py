from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING
from typing import cast
from typing import overload

import pendulum

from pendulum.constants import SECONDS_PER_DAY
from pendulum.constants import SECONDS_PER_HOUR
from pendulum.constants import SECONDS_PER_MINUTE
from pendulum.constants import US_PER_SECOND
from pendulum.utils._compat import PYPY


if TYPE_CHECKING:
    from typing_extensions import Self


def _divide_and_round(a: float, b: float) -> int:
    """divide a by b and round result to the nearest integer

    When the ratio is exactly half-way between two integers,
    the even integer is returned.
    """
    # Based on the reference implementation for divmod_near
    # in Objects/longobject.c.
    q, r = divmod(a, b)

    # The output of divmod() is either a float or an int,
    # but we always want it to be an int.
    q = int(q)

    # round up if either r / b > 0.5, or r / b == 0.5 and q is odd.
    # The expression r / b > 0.5 is equivalent to 2 * r > b if b is
    # positive, 2 * r < b if b negative.
    r *= 2
    greater_than_half = r > b if b > 0 else r < b
    if greater_than_half or r == b and q % 2 == 1:
        q += 1

    return q


class Duration(timedelta):
    """
    Replacement for the standard timedelta class.

    Provides several improvements over the base class.
    """

    _total: float = 0
    _years: int = 0
    _months: int = 0
    _weeks: int = 0
    _days: int = 0
    _remaining_days: int = 0
    _seconds: int = 0
    _microseconds: int = 0

    _y = None
    _m = None
    _w = None
    _d = None
    _h = None
    _i = None
    _s = None
    _invert = None

    def __new__(
        cls,
        days: float = 0,
        seconds: float = 0,
        microseconds: float = 0,
        milliseconds: float = 0,
        minutes: float = 0,
        hours: float = 0,
        weeks: float = 0,
        years: float = 0,
        months: float = 0,
    ) -> Self:
        if not isinstance(years, int) or not isinstance(months, int):
            raise ValueError("Float year and months are not supported")

        self = timedelta.__new__(
            cls,
            days + years * 365 + months * 30,
            seconds,
            microseconds,
            milliseconds,
            minutes,
            hours,
            weeks,
        )

        # Intuitive normalization
        total = self.total_seconds() - (years * 365 + months * 30) * SECONDS_PER_DAY
        self._total = total

        m = 1
        if total < 0:
            m = -1

        self._microseconds = round(total % m * 1e6)
        self._seconds = abs(int(total)) % SECONDS_PER_DAY * m

        _days = abs(int(total)) // SECONDS_PER_DAY * m
        self._days = _days
        self._remaining_days = abs(_days) % 7 * m
        self._weeks = abs(_days) // 7 * m
        self._months = months
        self._years = years

        self._signature = {  # type: ignore[attr-defined]
            "years": years,
            "months": months,
            "weeks": weeks,
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "microseconds": microseconds + milliseconds * 1000,
        }

        return self

    def total_minutes(self) -> float:
        return self.total_seconds() / SECONDS_PER_MINUTE

    def total_hours(self) -> float:
        return self.total_seconds() / SECONDS_PER_HOUR

    def total_days(self) -> float:
        return self.total_seconds() / SECONDS_PER_DAY

    def total_weeks(self) -> float:
        return self.total_days() / 7

    if PYPY:

        def total_seconds(self) -> float:
            days = 0

            if hasattr(self, "_years"):
                days += self._years * 365

            if hasattr(self, "_months"):
                days += self._months * 30

            if hasattr(self, "_remaining_days"):
                days += self._weeks * 7 + self._remaining_days
            else:
                days += self._days

            return (
                (days * SECONDS_PER_DAY + self._seconds) * US_PER_SECOND
                + self._microseconds
            ) / US_PER_SECOND

    @property
    def years(self) -> int:
        return self._years

    @property
    def months(self) -> int:
        return self._months

    @property
    def weeks(self) -> int:
        return self._weeks

    if PYPY:

        @property
        def days(self) -> int:
            return self._years * 365 + self._months * 30 + self._days

    @property
    def remaining_days(self) -> int:
        return self._remaining_days

    @property
    def hours(self) -> int:
        if self._h is None:
            seconds = self._seconds
            self._h = 0
            if abs(seconds) >= 3600:
                self._h = (abs(seconds) // 3600 % 24) * self._sign(seconds)

        return self._h

    @property
    def minutes(self) -> int:
        if self._i is None:
            seconds = self._seconds
            self._i = 0
            if abs(seconds) >= 60:
                self._i = (abs(seconds) // 60 % 60) * self._sign(seconds)

        return self._i

    @property
    def seconds(self) -> int:
        return self._seconds

    @property
    def remaining_seconds(self) -> int:
        if self._s is None:
            self._s = self._seconds
            self._s = abs(self._s) % 60 * self._sign(self._s)

        return self._s

    @property
    def microseconds(self) -> int:
        return self._microseconds

    @property
    def invert(self) -> bool:
        if self._invert is None:
            self._invert = self.total_seconds() < 0

        return self._invert

    def in_weeks(self) -> int:
        return int(self.total_weeks())

    def in_days(self) -> int:
        return int(self.total_days())

    def in_hours(self) -> int:
        return int(self.total_hours())

    def in_minutes(self) -> int:
        return int(self.total_minutes())

    def in_seconds(self) -> int:
        return int(self.total_seconds())

    def in_words(self, locale: str | None = None, separator: str = " ") -> str:
        """
        Get the current interval in words in the current locale.

        Ex: 6 jours 23 heures 58 minutes

        :param locale: The locale to use. Defaults to current locale.
        :param separator: The separator to use between each unit
        """
        intervals = [
            ("year", self.years),
            ("month", self.months),
            ("week", self.weeks),
            ("day", self.remaining_days),
            ("hour", self.hours),
            ("minute", self.minutes),
            ("second", self.remaining_seconds),
        ]

        if locale is None:
            locale = pendulum.get_locale()

        loaded_locale = pendulum.locale(locale)

        parts = []
        for interval in intervals:
            unit, interval_count = interval
            if abs(interval_count) > 0:
                translation = loaded_locale.translation(
                    f"units.{unit}.{loaded_locale.plural(abs(interval_count))}"
                )
                parts.append(translation.format(interval_count))

        if not parts:
            count: int | str = 0
            if abs(self.microseconds) > 0:
                unit = f"units.second.{loaded_locale.plural(1)}"
                count = f"{abs(self.microseconds) / 1e6:.2f}"
            else:
                unit = f"units.microsecond.{loaded_locale.plural(0)}"
            translation = loaded_locale.translation(unit)
            parts.append(translation.format(count))

        return separator.join(parts)

    def _sign(self, value: float) -> int:
        if value < 0:
            return -1

        return 1

    def as_timedelta(self) -> timedelta:
        """
        Return the interval as a native timedelta.
        """
        return timedelta(seconds=self.total_seconds())

    def __str__(self) -> str:
        return self.in_words()

    def __repr__(self) -> str:
        rep = f"{self.__class__.__name__}("

        if self._years:
            rep += f"years={self._years}, "

        if self._months:
            rep += f"months={self._months}, "

        if self._weeks:
            rep += f"weeks={self._weeks}, "

        if self._days:
            rep += f"days={self._remaining_days}, "

        if self.hours:
            rep += f"hours={self.hours}, "

        if self.minutes:
            rep += f"minutes={self.minutes}, "

        if self.remaining_seconds:
            rep += f"seconds={self.remaining_seconds}, "

        if self.microseconds:
            rep += f"microseconds={self.microseconds}, "

        rep += ")"

        return rep.replace(", )", ")")

    def __add__(self, other: timedelta) -> Self:
        if isinstance(other, timedelta):
            return self.__class__(seconds=self.total_seconds() + other.total_seconds())

        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other: timedelta) -> Self:
        if isinstance(other, timedelta):
            return self.__class__(seconds=self.total_seconds() - other.total_seconds())

        return NotImplemented

    def __neg__(self) -> Self:
        return self.__class__(
            years=-self._years,
            months=-self._months,
            weeks=-self._weeks,
            days=-self._remaining_days,
            seconds=-self._seconds,
            microseconds=-self._microseconds,
        )

    def _to_microseconds(self) -> int:
        return (self._days * (24 * 3600) + self._seconds) * 1000000 + self._microseconds

    def __mul__(self, other: int | float) -> Self:
        if isinstance(other, int):
            return self.__class__(
                years=self._years * other,
                months=self._months * other,
                seconds=self._total * other,
            )

        if isinstance(other, float):
            usec = self._to_microseconds()
            a, b = other.as_integer_ratio()

            return self.__class__(0, 0, _divide_and_round(usec * a, b))

        return NotImplemented

    __rmul__ = __mul__

    @overload
    def __floordiv__(self, other: timedelta) -> int:
        ...

    @overload
    def __floordiv__(self, other: int) -> Self:
        ...

    def __floordiv__(self, other: int | timedelta) -> int | Duration:
        if not isinstance(other, (int, timedelta)):
            return NotImplemented

        usec = self._to_microseconds()
        if isinstance(other, timedelta):
            return cast(
                int, usec // other._to_microseconds()  # type: ignore[attr-defined]
            )

        if isinstance(other, int):
            return self.__class__(
                0,
                0,
                usec // other,
                years=self._years // other,
                months=self._months // other,
            )

    @overload
    def __truediv__(self, other: timedelta) -> float:
        ...

    @overload
    def __truediv__(self, other: float) -> Self:
        ...

    def __truediv__(self, other: int | float | timedelta) -> Self | float:
        if not isinstance(other, (int, float, timedelta)):
            return NotImplemented

        usec = self._to_microseconds()
        if isinstance(other, timedelta):
            return cast(
                float, usec / other._to_microseconds()  # type: ignore[attr-defined]
            )

        if isinstance(other, int):
            return self.__class__(
                0,
                0,
                _divide_and_round(usec, other),
                years=_divide_and_round(self._years, other),
                months=_divide_and_round(self._months, other),
            )

        if isinstance(other, float):
            a, b = other.as_integer_ratio()

            return self.__class__(
                0,
                0,
                _divide_and_round(b * usec, a),
                years=_divide_and_round(self._years * b, a),
                months=_divide_and_round(self._months, other),
            )

    __div__ = __floordiv__

    def __mod__(self, other: timedelta) -> Self:
        if isinstance(other, timedelta):
            r = self._to_microseconds() % other._to_microseconds()  # type: ignore[attr-defined] # noqa: E501

            return self.__class__(0, 0, r)

        return NotImplemented

    def __divmod__(self, other: timedelta) -> tuple[int, Duration]:
        if isinstance(other, timedelta):
            q, r = divmod(
                self._to_microseconds(),
                other._to_microseconds(),  # type: ignore[attr-defined]
            )

            return q, self.__class__(0, 0, r)

        return NotImplemented

    def __deepcopy__(self, _: dict[int, Self]) -> Self:
        return self.__class__(
            days=self.remaining_days,
            seconds=self.remaining_seconds,
            microseconds=self.microseconds,
            minutes=self.minutes,
            hours=self.hours,
            years=self.years,
            months=self.months,
        )


Duration.min = Duration(days=-999999999)
Duration.max = Duration(
    days=999999999, hours=23, minutes=59, seconds=59, microseconds=999999
)
Duration.resolution = Duration(microseconds=1)


class AbsoluteDuration(Duration):
    """
    Duration that expresses a time difference in absolute values.
    """

    def __new__(
        cls,
        days: float = 0,
        seconds: float = 0,
        microseconds: float = 0,
        milliseconds: float = 0,
        minutes: float = 0,
        hours: float = 0,
        weeks: float = 0,
        years: float = 0,
        months: float = 0,
    ) -> AbsoluteDuration:
        if not isinstance(years, int) or not isinstance(months, int):
            raise ValueError("Float year and months are not supported")

        self = timedelta.__new__(
            cls, days, seconds, microseconds, milliseconds, minutes, hours, weeks
        )

        # We need to compute the total_seconds() value
        # on a native timedelta object
        delta = timedelta(
            days, seconds, microseconds, milliseconds, minutes, hours, weeks
        )

        # Intuitive normalization
        self._total = delta.total_seconds()
        total = abs(self._total)

        self._microseconds = round(total % 1 * 1e6)
        days, self._seconds = divmod(int(total), SECONDS_PER_DAY)
        self._days = abs(days + years * 365 + months * 30)
        self._weeks, self._remaining_days = divmod(days, 7)
        self._months = abs(months)
        self._years = abs(years)

        return self

    def total_seconds(self) -> float:
        return abs(self._total)

    @property
    def invert(self) -> bool:
        if self._invert is None:
            self._invert = self._total < 0

        return self._invert
