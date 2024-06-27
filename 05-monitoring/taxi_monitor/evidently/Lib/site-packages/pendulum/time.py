from __future__ import annotations

import datetime

from datetime import time
from datetime import timedelta
from typing import TYPE_CHECKING
from typing import Optional
from typing import cast
from typing import overload

import pendulum

from pendulum.constants import SECS_PER_HOUR
from pendulum.constants import SECS_PER_MIN
from pendulum.constants import USECS_PER_SEC
from pendulum.duration import AbsoluteDuration
from pendulum.duration import Duration
from pendulum.mixins.default import FormattableMixin
from pendulum.tz.timezone import UTC


if TYPE_CHECKING:
    from typing_extensions import Literal
    from typing_extensions import Self
    from typing_extensions import SupportsIndex

    from pendulum.tz.timezone import FixedTimezone
    from pendulum.tz.timezone import Timezone


class Time(FormattableMixin, time):
    """
    Represents a time instance as hour, minute, second, microsecond.
    """

    @classmethod
    def instance(
        cls, t: time, tz: str | Timezone | FixedTimezone | datetime.tzinfo | None = UTC
    ) -> Self:
        tz = t.tzinfo or tz

        if tz is not None:
            tz = pendulum._safe_timezone(tz)

        return cls(t.hour, t.minute, t.second, t.microsecond, tzinfo=tz, fold=t.fold)

    # String formatting
    def __repr__(self) -> str:
        us = ""
        if self.microsecond:
            us = f", {self.microsecond}"

        tzinfo = ""
        if self.tzinfo:
            tzinfo = f", tzinfo={self.tzinfo!r}"

        return (
            f"{self.__class__.__name__}"
            f"({self.hour}, {self.minute}, {self.second}{us}{tzinfo})"
        )

    # Comparisons

    def closest(self, dt1: Time | time, dt2: Time | time) -> Self:
        """
        Get the closest time from the instance.
        """
        dt1 = self.__class__(dt1.hour, dt1.minute, dt1.second, dt1.microsecond)
        dt2 = self.__class__(dt2.hour, dt2.minute, dt2.second, dt2.microsecond)

        if self.diff(dt1).in_seconds() < self.diff(dt2).in_seconds():
            return dt1

        return dt2

    def farthest(self, dt1: Time | time, dt2: Time | time) -> Self:
        """
        Get the farthest time from the instance.
        """
        dt1 = self.__class__(dt1.hour, dt1.minute, dt1.second, dt1.microsecond)
        dt2 = self.__class__(dt2.hour, dt2.minute, dt2.second, dt2.microsecond)

        if self.diff(dt1).in_seconds() > self.diff(dt2).in_seconds():
            return dt1

        return dt2

    # ADDITIONS AND SUBSTRACTIONS

    def add(
        self, hours: int = 0, minutes: int = 0, seconds: int = 0, microseconds: int = 0
    ) -> Time:
        """
        Add duration to the instance.

        :param hours: The number of hours
        :param minutes: The number of minutes
        :param seconds: The number of seconds
        :param microseconds: The number of microseconds
        """
        from pendulum.datetime import DateTime

        return (
            DateTime.EPOCH.at(self.hour, self.minute, self.second, self.microsecond)
            .add(
                hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds
            )
            .time()
        )

    def subtract(
        self, hours: int = 0, minutes: int = 0, seconds: int = 0, microseconds: int = 0
    ) -> Time:
        """
        Add duration to the instance.

        :param hours: The number of hours
        :type hours: int

        :param minutes: The number of minutes
        :type minutes: int

        :param seconds: The number of seconds
        :type seconds: int

        :param microseconds: The number of microseconds
        :type microseconds: int

        :rtype: Time
        """
        from pendulum.datetime import DateTime

        return (
            DateTime.EPOCH.at(self.hour, self.minute, self.second, self.microsecond)
            .subtract(
                hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds
            )
            .time()
        )

    def add_timedelta(self, delta: datetime.timedelta) -> Time:
        """
        Add timedelta duration to the instance.

        :param delta: The timedelta instance
        """
        if delta.days:
            raise TypeError("Cannot add timedelta with days to Time.")

        return self.add(seconds=delta.seconds, microseconds=delta.microseconds)

    def subtract_timedelta(self, delta: datetime.timedelta) -> Time:
        """
        Remove timedelta duration from the instance.

        :param delta: The timedelta instance
        """
        if delta.days:
            raise TypeError("Cannot subtract timedelta with days to Time.")

        return self.subtract(seconds=delta.seconds, microseconds=delta.microseconds)

    def __add__(self, other: datetime.timedelta) -> Time:
        if not isinstance(other, timedelta):
            return NotImplemented

        return self.add_timedelta(other)

    @overload
    def __sub__(self, other: time) -> pendulum.Duration:
        ...

    @overload
    def __sub__(self, other: datetime.timedelta) -> Time:
        ...

    def __sub__(self, other: time | datetime.timedelta) -> pendulum.Duration | Time:
        if not isinstance(other, (Time, time, timedelta)):
            return NotImplemented

        if isinstance(other, timedelta):
            return self.subtract_timedelta(other)

        if isinstance(other, time):
            if other.tzinfo is not None:
                raise TypeError("Cannot subtract aware times to or from Time.")

            other = self.__class__(
                other.hour, other.minute, other.second, other.microsecond
            )

        return other.diff(self, False)

    @overload
    def __rsub__(self, other: time) -> pendulum.Duration:
        ...

    @overload
    def __rsub__(self, other: datetime.timedelta) -> Time:
        ...

    def __rsub__(self, other: time | datetime.timedelta) -> pendulum.Duration | Time:
        if not isinstance(other, (Time, time)):
            return NotImplemented

        if isinstance(other, time):
            if other.tzinfo is not None:
                raise TypeError("Cannot subtract aware times to or from Time.")

            other = self.__class__(
                other.hour, other.minute, other.second, other.microsecond
            )

        return other.__sub__(self)

    # DIFFERENCES

    def diff(self, dt: time | None = None, abs: bool = True) -> Duration:
        """
        Returns the difference between two Time objects as an Duration.

        :param dt: The time to subtract from
        :param abs: Whether to return an absolute duration or not
        """
        if dt is None:
            dt = pendulum.now().time()
        else:
            dt = self.__class__(dt.hour, dt.minute, dt.second, dt.microsecond)

        us1 = (
            self.hour * SECS_PER_HOUR + self.minute * SECS_PER_MIN + self.second
        ) * USECS_PER_SEC

        us2 = (
            dt.hour * SECS_PER_HOUR + dt.minute * SECS_PER_MIN + dt.second
        ) * USECS_PER_SEC

        klass = Duration
        if abs:
            klass = AbsoluteDuration

        return klass(microseconds=us2 - us1)

    def diff_for_humans(
        self,
        other: time | None = None,
        absolute: bool = False,
        locale: str | None = None,
    ) -> str:
        """
        Get the difference in a human readable format in the current locale.

        :param dt: The time to subtract from
        :param absolute: removes time difference modifiers ago, after, etc
        :param locale: The locale to use for localization
        """
        is_now = other is None

        if is_now:
            other = pendulum.now().time()

        diff = self.diff(other)

        return pendulum.format_diff(diff, is_now, absolute, locale)

    # Compatibility methods

    def replace(
        self,
        hour: SupportsIndex | None = None,
        minute: SupportsIndex | None = None,
        second: SupportsIndex | None = None,
        microsecond: SupportsIndex | None = None,
        tzinfo: bool | datetime.tzinfo | Literal[True] | None = True,
        fold: int = 0,
    ) -> Self:
        if tzinfo is True:
            tzinfo = self.tzinfo

        hour = hour if hour is not None else self.hour
        minute = minute if minute is not None else self.minute
        second = second if second is not None else self.second
        microsecond = microsecond if microsecond is not None else self.microsecond

        t = super().replace(
            hour,
            minute,
            second,
            microsecond,
            tzinfo=cast(Optional[datetime.tzinfo], tzinfo),
            fold=fold,
        )
        return self.__class__(
            t.hour, t.minute, t.second, t.microsecond, tzinfo=t.tzinfo
        )

    def __getnewargs__(self) -> tuple[Time]:
        return (self,)

    def _get_state(
        self, protocol: SupportsIndex = 3
    ) -> tuple[int, int, int, int, datetime.tzinfo | None]:
        tz = self.tzinfo

        return self.hour, self.minute, self.second, self.microsecond, tz

    def __reduce__(
        self,
    ) -> tuple[type[Time], tuple[int, int, int, int, datetime.tzinfo | None]]:
        return self.__reduce_ex__(2)

    def __reduce_ex__(
        self, protocol: SupportsIndex
    ) -> tuple[type[Time], tuple[int, int, int, int, datetime.tzinfo | None]]:
        return self.__class__, self._get_state(protocol)


Time.min = Time(0, 0, 0)
Time.max = Time(23, 59, 59, 999999)
Time.resolution = Duration(microseconds=1)
