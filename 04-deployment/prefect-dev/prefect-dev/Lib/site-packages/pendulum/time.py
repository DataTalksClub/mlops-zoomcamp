from __future__ import absolute_import

from datetime import time
from datetime import timedelta

import pendulum

from .constants import SECS_PER_HOUR
from .constants import SECS_PER_MIN
from .constants import USECS_PER_SEC
from .duration import AbsoluteDuration
from .duration import Duration
from .mixins.default import FormattableMixin


class Time(FormattableMixin, time):
    """
    Represents a time instance as hour, minute, second, microsecond.
    """

    # String formatting
    def __repr__(self):
        us = ""
        if self.microsecond:
            us = ", {}".format(self.microsecond)

        tzinfo = ""
        if self.tzinfo:
            tzinfo = ", tzinfo={}".format(repr(self.tzinfo))

        return "{}({}, {}, {}{}{})".format(
            self.__class__.__name__, self.hour, self.minute, self.second, us, tzinfo
        )

    # Comparisons

    def closest(self, dt1, dt2):
        """
        Get the closest time from the instance.

        :type dt1: Time or time
        :type dt2: Time or time

        :rtype: Time
        """
        dt1 = self.__class__(dt1.hour, dt1.minute, dt1.second, dt1.microsecond)
        dt2 = self.__class__(dt2.hour, dt2.minute, dt2.second, dt2.microsecond)

        if self.diff(dt1).in_seconds() < self.diff(dt2).in_seconds():
            return dt1

        return dt2

    def farthest(self, dt1, dt2):
        """
        Get the farthest time from the instance.

        :type dt1: Time or time
        :type dt2: Time or time

        :rtype: Time
        """
        dt1 = self.__class__(dt1.hour, dt1.minute, dt1.second, dt1.microsecond)
        dt2 = self.__class__(dt2.hour, dt2.minute, dt2.second, dt2.microsecond)

        if self.diff(dt1).in_seconds() > self.diff(dt2).in_seconds():
            return dt1

        return dt2

    # ADDITIONS AND SUBSTRACTIONS

    def add(self, hours=0, minutes=0, seconds=0, microseconds=0):
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
        from .datetime import DateTime

        return (
            DateTime.EPOCH.at(self.hour, self.minute, self.second, self.microsecond)
            .add(
                hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds
            )
            .time()
        )

    def subtract(self, hours=0, minutes=0, seconds=0, microseconds=0):
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
        from .datetime import DateTime

        return (
            DateTime.EPOCH.at(self.hour, self.minute, self.second, self.microsecond)
            .subtract(
                hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds
            )
            .time()
        )

    def add_timedelta(self, delta):
        """
        Add timedelta duration to the instance.

        :param delta: The timedelta instance
        :type delta: datetime.timedelta

        :rtype: Time
        """
        if delta.days:
            raise TypeError("Cannot add timedelta with days to Time.")

        return self.add(seconds=delta.seconds, microseconds=delta.microseconds)

    def subtract_timedelta(self, delta):
        """
        Remove timedelta duration from the instance.

        :param delta: The timedelta instance
        :type delta: datetime.timedelta

        :rtype: Time
        """
        if delta.days:
            raise TypeError("Cannot subtract timedelta with days to Time.")

        return self.subtract(seconds=delta.seconds, microseconds=delta.microseconds)

    def __add__(self, other):
        if not isinstance(other, timedelta):
            return NotImplemented

        return self.add_timedelta(other)

    def __sub__(self, other):
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

    def __rsub__(self, other):
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

    def diff(self, dt=None, abs=True):
        """
        Returns the difference between two Time objects as an Duration.

        :type dt: Time or None

        :param abs: Whether to return an absolute interval or not
        :type abs: bool

        :rtype: Duration
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

    def diff_for_humans(self, other=None, absolute=False, locale=None):
        """
        Get the difference in a human readable format in the current locale.

        :type other: Time or time

        :param absolute: removes time difference modifiers ago, after, etc
        :type absolute: bool

        :param locale: The locale to use for localization
        :type locale: str

        :rtype: str
        """
        is_now = other is None

        if is_now:
            other = pendulum.now().time()

        diff = self.diff(other)

        return pendulum.format_diff(diff, is_now, absolute, locale)

    # Compatibility methods

    def replace(
        self, hour=None, minute=None, second=None, microsecond=None, tzinfo=True
    ):
        if tzinfo is True:
            tzinfo = self.tzinfo

        hour = hour if hour is not None else self.hour
        minute = minute if minute is not None else self.minute
        second = second if second is not None else self.second
        microsecond = microsecond if microsecond is not None else self.microsecond

        t = super(Time, self).replace(hour, minute, second, microsecond, tzinfo=tzinfo)
        return self.__class__(
            t.hour, t.minute, t.second, t.microsecond, tzinfo=t.tzinfo
        )

    def __getnewargs__(self):
        return (self,)

    def _get_state(self, protocol=3):
        tz = self.tzinfo

        return (self.hour, self.minute, self.second, self.microsecond, tz)

    def __reduce__(self):
        return self.__reduce_ex__(2)

    def __reduce_ex__(self, protocol):
        return self.__class__, self._get_state(protocol)


Time.min = Time(0, 0, 0)
Time.max = Time(23, 59, 59, 999999)
Time.resolution = Duration(microseconds=1)
