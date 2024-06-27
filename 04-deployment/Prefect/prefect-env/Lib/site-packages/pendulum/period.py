from __future__ import absolute_import

import operator

from datetime import date
from datetime import datetime
from datetime import timedelta

import pendulum

from pendulum.utils._compat import _HAS_FOLD
from pendulum.utils._compat import decode

from .constants import MONTHS_PER_YEAR
from .duration import Duration
from .helpers import precise_diff


class Period(Duration):
    """
    Duration class that is aware of the datetimes that generated the
    time difference.
    """

    def __new__(cls, start, end, absolute=False):
        if isinstance(start, datetime) and isinstance(end, datetime):
            if (
                start.tzinfo is None
                and end.tzinfo is not None
                or start.tzinfo is not None
                and end.tzinfo is None
            ):
                raise TypeError("can't compare offset-naive and offset-aware datetimes")

        if absolute and start > end:
            end, start = start, end

        _start = start
        _end = end
        if isinstance(start, pendulum.DateTime):
            if _HAS_FOLD:
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
            else:
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
        elif isinstance(start, pendulum.Date):
            _start = date(start.year, start.month, start.day)

        if isinstance(end, pendulum.DateTime):
            if _HAS_FOLD:
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
            else:
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
                _start = (_start - start.utcoffset()).replace(tzinfo=None)

            if isinstance(end, datetime) and _end.tzinfo is not None:
                _end = (_end - end.utcoffset()).replace(tzinfo=None)

        delta = _end - _start

        return super(Period, cls).__new__(cls, seconds=delta.total_seconds())

    def __init__(self, start, end, absolute=False):
        super(Period, self).__init__()

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
        self._start = start
        self._end = end
        self._delta = precise_diff(_start, _end)

    @property
    def years(self):
        return self._delta.years

    @property
    def months(self):
        return self._delta.months

    @property
    def weeks(self):
        return abs(self._delta.days) // 7 * self._sign(self._delta.days)

    @property
    def days(self):
        return self._days

    @property
    def remaining_days(self):
        return abs(self._delta.days) % 7 * self._sign(self._days)

    @property
    def hours(self):
        return self._delta.hours

    @property
    def minutes(self):
        return self._delta.minutes

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    def in_years(self):
        """
        Gives the duration of the Period in full years.

        :rtype: int
        """
        return self.years

    def in_months(self):
        """
        Gives the duration of the Period in full months.

        :rtype: int
        """
        return self.years * MONTHS_PER_YEAR + self.months

    def in_weeks(self):
        days = self.in_days()
        sign = 1

        if days < 0:
            sign = -1

        return sign * (abs(days) // 7)

    def in_days(self):
        return self._delta.total_days

    def in_words(self, locale=None, separator=" "):
        """
        Get the current interval in words in the current locale.

        Ex: 6 jours 23 heures 58 minutes

        :param locale: The locale to use. Defaults to current locale.
        :type locale: str

        :param separator: The separator to use between each unit
        :type separator: str

        :rtype: str
        """
        periods = [
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

        locale = pendulum.locale(locale)
        parts = []
        for period in periods:
            unit, count = period
            if abs(count) > 0:
                translation = locale.translation(
                    "units.{}.{}".format(unit, locale.plural(abs(count)))
                )
                parts.append(translation.format(count))

        if not parts:
            if abs(self.microseconds) > 0:
                unit = "units.second.{}".format(locale.plural(1))
                count = "{:.2f}".format(abs(self.microseconds) / 1e6)
            else:
                unit = "units.microsecond.{}".format(locale.plural(0))
                count = 0
            translation = locale.translation(unit)
            parts.append(translation.format(count))

        return decode(separator.join(parts))

    def range(self, unit, amount=1):
        method = "add"
        op = operator.le
        if not self._absolute and self.invert:
            method = "subtract"
            op = operator.ge

        start, end = self.start, self.end

        i = amount
        while op(start, end):
            yield start

            start = getattr(self.start, method)(**{unit: i})

            i += amount

    def as_interval(self):
        """
        Return the Period as an Duration.

        :rtype: Duration
        """
        return Duration(seconds=self.total_seconds())

    def __iter__(self):
        return self.range("days")

    def __contains__(self, item):
        return self.start <= item <= self.end

    def __add__(self, other):
        return self.as_interval().__add__(other)

    __radd__ = __add__

    def __sub__(self, other):
        return self.as_interval().__sub__(other)

    def __neg__(self):
        return self.__class__(self.end, self.start, self._absolute)

    def __mul__(self, other):
        return self.as_interval().__mul__(other)

    __rmul__ = __mul__

    def __floordiv__(self, other):
        return self.as_interval().__floordiv__(other)

    def __truediv__(self, other):
        return self.as_interval().__truediv__(other)

    __div__ = __floordiv__

    def __mod__(self, other):
        return self.as_interval().__mod__(other)

    def __divmod__(self, other):
        return self.as_interval().__divmod__(other)

    def __abs__(self):
        return self.__class__(self.start, self.end, True)

    def __repr__(self):
        return "<Period [{} -> {}]>".format(self._start, self._end)

    def __str__(self):
        return self.__repr__()

    def _cmp(self, other):
        # Only needed for PyPy
        assert isinstance(other, timedelta)

        if isinstance(other, Period):
            other = other.as_timedelta()

        td = self.as_timedelta()

        return 0 if td == other else 1 if td > other else -1

    def _getstate(self, protocol=3):
        start, end = self.start, self.end

        if self._invert and self._absolute:
            end, start = start, end

        return (start, end, self._absolute)

    def __reduce__(self):
        return self.__reduce_ex__(2)

    def __reduce_ex__(self, protocol):
        return self.__class__, self._getstate(protocol)

    def __hash__(self):
        return hash((self.start, self.end, self._absolute))

    def __eq__(self, other):
        if isinstance(other, Period):
            return (self.start, self.end, self._absolute) == (
                other.start,
                other.end,
                other._absolute,
            )
        else:
            return self.as_interval() == other
