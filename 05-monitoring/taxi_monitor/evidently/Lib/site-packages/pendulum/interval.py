from __future__ import annotations

import operator

from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import TYPE_CHECKING
from typing import Iterator
from typing import Union
from typing import cast
from typing import overload

import pendulum

from pendulum.constants import MONTHS_PER_YEAR
from pendulum.duration import Duration
from pendulum.helpers import precise_diff


if TYPE_CHECKING:
    from typing_extensions import Self
    from typing_extensions import SupportsIndex

    from pendulum.helpers import PreciseDiff
    from pendulum.locales.locale import Locale


class Interval(Duration):
    """
    An interval of time between two datetimes.
    """

    @overload
    def __new__(
        cls,
        start: pendulum.DateTime | datetime,
        end: pendulum.DateTime | datetime,
        absolute: bool = False,
    ) -> Self:
        ...

    @overload
    def __new__(
        cls,
        start: pendulum.Date | date,
        end: pendulum.Date | date,
        absolute: bool = False,
    ) -> Self:
        ...

    def __new__(
        cls,
        start: pendulum.DateTime | pendulum.Date | datetime | date,
        end: pendulum.DateTime | pendulum.Date | datetime | date,
        absolute: bool = False,
    ) -> Self:
        if (
            isinstance(start, datetime)
            and not isinstance(end, datetime)
            or not isinstance(start, datetime)
            and isinstance(end, datetime)
        ):
            raise ValueError(
                "Both start and end of an Interval must have the same type"
            )

        if (
            isinstance(start, datetime)
            and isinstance(end, datetime)
            and (
                start.tzinfo is None
                and end.tzinfo is not None
                or start.tzinfo is not None
                and end.tzinfo is None
            )
        ):
            raise TypeError("can't compare offset-naive and offset-aware datetimes")

        if absolute and start > end:
            end, start = start, end

        _start = start
        _end = end
        if isinstance(start, pendulum.DateTime):
            _start = datetime(
                start.year,
                start.month,
                start.day,
                start.hour,
                start.minute,
                start.second,
                start.microsecond,
                tzinfo=start.tzinfo,
                fold=start.fold,
            )
        elif isinstance(start, pendulum.Date):
            _start = date(start.year, start.month, start.day)

        if isinstance(end, pendulum.DateTime):
            _end = datetime(
                end.year,
                end.month,
                end.day,
                end.hour,
                end.minute,
                end.second,
                end.microsecond,
                tzinfo=end.tzinfo,
                fold=end.fold,
            )
        elif isinstance(end, pendulum.Date):
            _end = date(end.year, end.month, end.day)

        # Fixing issues with datetime.__sub__()
        # not handling offsets if the tzinfo is the same
        if (
            isinstance(_start, datetime)
            and isinstance(_end, datetime)
            and _start.tzinfo is _end.tzinfo
        ):
            if _start.tzinfo is not None:
                offset = cast(timedelta, cast(datetime, start).utcoffset())
                _start = (_start - offset).replace(tzinfo=None)

            if isinstance(end, datetime) and _end.tzinfo is not None:
                offset = cast(timedelta, end.utcoffset())
                _end = (_end - offset).replace(tzinfo=None)

        delta: timedelta = _end - _start  # type: ignore[operator]

        return super().__new__(cls, seconds=delta.total_seconds())

    def __init__(
        self,
        start: pendulum.DateTime | pendulum.Date | datetime | date,
        end: pendulum.DateTime | pendulum.Date | datetime | date,
        absolute: bool = False,
    ) -> None:
        super().__init__()

        _start: pendulum.DateTime | pendulum.Date | datetime | date
        if not isinstance(start, pendulum.Date):
            if isinstance(start, datetime):
                start = pendulum.instance(start)
            else:
                start = pendulum.date(start.year, start.month, start.day)

            _start = start
        else:
            if isinstance(start, pendulum.DateTime):
                _start = datetime(
                    start.year,
                    start.month,
                    start.day,
                    start.hour,
                    start.minute,
                    start.second,
                    start.microsecond,
                    tzinfo=start.tzinfo,
                )
            else:
                _start = date(start.year, start.month, start.day)

        _end: pendulum.DateTime | pendulum.Date | datetime | date
        if not isinstance(end, pendulum.Date):
            if isinstance(end, datetime):
                end = pendulum.instance(end)
            else:
                end = pendulum.date(end.year, end.month, end.day)

            _end = end
        else:
            if isinstance(end, pendulum.DateTime):
                _end = datetime(
                    end.year,
                    end.month,
                    end.day,
                    end.hour,
                    end.minute,
                    end.second,
                    end.microsecond,
                    tzinfo=end.tzinfo,
                )
            else:
                _end = date(end.year, end.month, end.day)

        self._invert = False
        if start > end:
            self._invert = True

            if absolute:
                end, start = start, end
                _end, _start = _start, _end

        self._absolute = absolute
        self._start: pendulum.DateTime | pendulum.Date = start
        self._end: pendulum.DateTime | pendulum.Date = end
        self._delta: PreciseDiff = precise_diff(_start, _end)

    @property
    def years(self) -> int:
        return self._delta.years

    @property
    def months(self) -> int:
        return self._delta.months

    @property
    def weeks(self) -> int:
        return abs(self._delta.days) // 7 * self._sign(self._delta.days)

    @property
    def days(self) -> int:
        return self._days

    @property
    def remaining_days(self) -> int:
        return abs(self._delta.days) % 7 * self._sign(self._days)

    @property
    def hours(self) -> int:
        return self._delta.hours

    @property
    def minutes(self) -> int:
        return self._delta.minutes

    @property
    def start(self) -> pendulum.DateTime | pendulum.Date | datetime | date:
        return self._start

    @property
    def end(self) -> pendulum.DateTime | pendulum.Date | datetime | date:
        return self._end

    def in_years(self) -> int:
        """
        Gives the duration of the Interval in full years.
        """
        return self.years

    def in_months(self) -> int:
        """
        Gives the duration of the Interval in full months.
        """
        return self.years * MONTHS_PER_YEAR + self.months

    def in_weeks(self) -> int:
        days = self.in_days()
        sign = 1

        if days < 0:
            sign = -1

        return sign * (abs(days) // 7)

    def in_days(self) -> int:
        return self._delta.total_days

    def in_words(self, locale: str | None = None, separator: str = " ") -> str:
        """
        Get the current interval in words in the current locale.

        Ex: 6 jours 23 heures 58 minutes

        :param locale: The locale to use. Defaults to current locale.
        :param separator: The separator to use between each unit
        """
        from pendulum.locales.locale import Locale

        intervals = [
            ("year", self.years),
            ("month", self.months),
            ("week", self.weeks),
            ("day", self.remaining_days),
            ("hour", self.hours),
            ("minute", self.minutes),
            ("second", self.remaining_seconds),
        ]
        loaded_locale: Locale = Locale.load(locale or pendulum.get_locale())
        parts = []
        for interval in intervals:
            unit, interval_count = interval
            if abs(interval_count) > 0:
                translation = loaded_locale.translation(
                    f"units.{unit}.{loaded_locale.plural(abs(interval_count))}"
                )
                parts.append(translation.format(interval_count))

        if not parts:
            count: str | int = 0
            if abs(self.microseconds) > 0:
                unit = f"units.second.{loaded_locale.plural(1)}"
                count = f"{abs(self.microseconds) / 1e6:.2f}"
            else:
                unit = f"units.microsecond.{loaded_locale.plural(0)}"

            translation = loaded_locale.translation(unit)
            parts.append(translation.format(count))

        return separator.join(parts)

    def range(
        self, unit: str, amount: int = 1
    ) -> Iterator[pendulum.DateTime | pendulum.Date]:
        method = "add"
        op = operator.le
        if not self._absolute and self.invert:
            method = "subtract"
            op = operator.ge

        start, end = self.start, self.end

        i = amount
        while op(start, end):
            yield cast(Union[pendulum.DateTime, pendulum.Date], start)

            start = getattr(self.start, method)(**{unit: i})

            i += amount

    def as_duration(self) -> Duration:
        """
        Return the Interval as a Duration.
        """
        return Duration(seconds=self.total_seconds())

    def __iter__(self) -> Iterator[pendulum.DateTime | pendulum.Date]:
        return self.range("days")

    def __contains__(
        self, item: datetime | date | pendulum.DateTime | pendulum.Date
    ) -> bool:
        return self.start <= item <= self.end

    def __add__(self, other: timedelta) -> Duration:  # type: ignore[override]
        return self.as_duration().__add__(other)

    __radd__ = __add__  # type: ignore[assignment]

    def __sub__(self, other: timedelta) -> Duration:  # type: ignore[override]
        return self.as_duration().__sub__(other)

    def __neg__(self) -> Self:
        return self.__class__(self.end, self.start, self._absolute)

    def __mul__(self, other: int | float) -> Duration:  # type: ignore[override]
        return self.as_duration().__mul__(other)

    __rmul__ = __mul__  # type: ignore[assignment]

    @overload  # type: ignore[override]
    def __floordiv__(self, other: timedelta) -> int:
        ...

    @overload
    def __floordiv__(self, other: int) -> Duration:
        ...

    def __floordiv__(self, other: int | timedelta) -> int | Duration:
        return self.as_duration().__floordiv__(other)

    __div__ = __floordiv__  # type: ignore[assignment]

    @overload  # type: ignore[override]
    def __truediv__(self, other: timedelta) -> float:
        ...

    @overload
    def __truediv__(self, other: float) -> Duration:
        ...

    def __truediv__(self, other: float | timedelta) -> Duration | float:
        return self.as_duration().__truediv__(other)

    def __mod__(self, other: timedelta) -> Duration:  # type: ignore[override]
        return self.as_duration().__mod__(other)

    def __divmod__(self, other: timedelta) -> tuple[int, Duration]:
        return self.as_duration().__divmod__(other)

    def __abs__(self) -> Self:
        return self.__class__(self.start, self.end, absolute=True)

    def __repr__(self) -> str:
        return f"<Interval [{self._start} -> {self._end}]>"

    def __str__(self) -> str:
        return self.__repr__()

    def _cmp(self, other: timedelta) -> int:
        # Only needed for PyPy
        assert isinstance(other, timedelta)

        if isinstance(other, Interval):
            other = other.as_timedelta()

        td = self.as_timedelta()

        return 0 if td == other else 1 if td > other else -1

    def _getstate(
        self, protocol: SupportsIndex = 3
    ) -> tuple[
        pendulum.DateTime | pendulum.Date | datetime | date,
        pendulum.DateTime | pendulum.Date | datetime | date,
        bool,
    ]:
        start, end = self.start, self.end

        if self._invert and self._absolute:
            end, start = start, end

        return start, end, self._absolute

    def __reduce__(
        self,
    ) -> tuple[
        type[Self],
        tuple[
            pendulum.DateTime | pendulum.Date | datetime | date,
            pendulum.DateTime | pendulum.Date | datetime | date,
            bool,
        ],
    ]:
        return self.__reduce_ex__(2)

    def __reduce_ex__(
        self, protocol: SupportsIndex
    ) -> tuple[
        type[Self],
        tuple[
            pendulum.DateTime | pendulum.Date | datetime | date,
            pendulum.DateTime | pendulum.Date | datetime | date,
            bool,
        ],
    ]:
        return self.__class__, self._getstate(protocol)

    def __hash__(self) -> int:
        return hash((self.start, self.end, self._absolute))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Interval):
            return (self.start, self.end, self._absolute) == (
                other.start,
                other.end,
                other._absolute,
            )
        else:
            return self.as_duration() == other

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
