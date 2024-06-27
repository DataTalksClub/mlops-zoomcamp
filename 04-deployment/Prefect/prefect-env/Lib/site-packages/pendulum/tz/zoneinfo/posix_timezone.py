"""
Parsing of a POSIX zone spec as described in the TZ part of section 8.3 in
http://pubs.opengroup.org/onlinepubs/009695399/basedefs/xbd_chap08.html.
"""
import re

from typing import Optional

from pendulum.constants import MONTHS_OFFSETS
from pendulum.constants import SECS_PER_DAY

from .exceptions import InvalidPosixSpec


_spec = re.compile(
    "^"
    r"(?P<std_abbr><.*?>|[^-+,\d]{3,})"
    r"(?P<std_offset>([+-])?(\d{1,2})(:\d{2}(:\d{2})?)?)"
    r"(?P<dst_info>"
    r"    (?P<dst_abbr><.*?>|[^-+,\d]{3,})"
    r"    (?P<dst_offset>([+-])?(\d{1,2})(:\d{2}(:\d{2})?)?)?"
    r")?"
    r"(?:,(?P<rules>"
    r"    (?P<dst_start>"
    r"        (?:J\d+|\d+|M\d{1,2}.\d.[0-6])"
    r"        (?:/(?P<dst_start_offset>([+-])?(\d+)(:\d{2}(:\d{2})?)?))?"
    "    )"
    "    ,"
    r"    (?P<dst_end>"
    r"        (?:J\d+|\d+|M\d{1,2}.\d.[0-6])"
    r"        (?:/(?P<dst_end_offset>([+-])?(\d+)(:\d{2}(:\d{2})?)?))?"
    "    )"
    "))?"
    "$",
    re.VERBOSE,
)


def posix_spec(spec):  # type: (str) -> PosixTimezone
    try:
        return _posix_spec(spec)
    except ValueError:
        raise InvalidPosixSpec(spec)


def _posix_spec(spec):  # type: (str) -> PosixTimezone
    m = _spec.match(spec)
    if not m:
        raise ValueError("Invalid posix spec")

    std_abbr = _parse_abbr(m.group("std_abbr"))
    std_offset = _parse_offset(m.group("std_offset"))

    dst_abbr = None
    dst_offset = None
    if m.group("dst_info"):
        dst_abbr = _parse_abbr(m.group("dst_abbr"))
        if m.group("dst_offset"):
            dst_offset = _parse_offset(m.group("dst_offset"))
        else:
            dst_offset = std_offset + 3600

    dst_start = None
    dst_end = None
    if m.group("rules"):
        dst_start = _parse_rule(m.group("dst_start"))
        dst_end = _parse_rule(m.group("dst_end"))

    return PosixTimezone(std_abbr, std_offset, dst_abbr, dst_offset, dst_start, dst_end)


def _parse_abbr(text):  # type: (str) -> str
    return text.lstrip("<").rstrip(">")


def _parse_offset(text, sign=-1):  # type: (str, int) -> int
    if text.startswith(("+", "-")):
        if text.startswith("-"):
            sign *= -1

        text = text[1:]

    minutes = 0
    seconds = 0

    parts = text.split(":")
    hours = int(parts[0])

    if len(parts) > 1:
        minutes = int(parts[1])

        if len(parts) > 2:
            seconds = int(parts[2])

    return sign * ((((hours * 60) + minutes) * 60) + seconds)


def _parse_rule(rule):  # type: (str) -> PosixTransition
    klass = NPosixTransition
    args = ()

    if rule.startswith("M"):
        rule = rule[1:]
        parts = rule.split(".")
        month = int(parts[0])
        week = int(parts[1])
        day = int(parts[2].split("/")[0])

        args += (month, week, day)
        klass = MPosixTransition
    elif rule.startswith("J"):
        rule = rule[1:]
        args += (int(rule.split("/")[0]),)
        klass = JPosixTransition
    else:
        args += (int(rule.split("/")[0]),)

    # Checking offset
    parts = rule.split("/")
    if len(parts) > 1:
        offset = _parse_offset(parts[-1], sign=1)
    else:
        offset = 7200

    args += (offset,)

    return klass(*args)


class PosixTransition(object):
    def __init__(self, offset):  # type: (int) -> None
        self._offset = offset

    @property
    def offset(self):  # type: () -> int
        return self._offset

    def trans_offset(self, is_leap, jan1_weekday):  # type: (bool, int) -> int
        raise NotImplementedError()


class JPosixTransition(PosixTransition):
    def __init__(self, day, offset):  # type: (int, int) -> None
        self._day = day

        super(JPosixTransition, self).__init__(offset)

    @property
    def day(self):  # type: () -> int
        """
        day of non-leap year [1:365]
        """
        return self._day

    def trans_offset(self, is_leap, jan1_weekday):  # type: (bool, int) -> int
        days = self._day
        if not is_leap or days < MONTHS_OFFSETS[1][3]:
            days -= 1

        return (days * SECS_PER_DAY) + self._offset


class NPosixTransition(PosixTransition):
    def __init__(self, day, offset):  # type: (int, int) -> None
        self._day = day

        super(NPosixTransition, self).__init__(offset)

    @property
    def day(self):  # type: () -> int
        """
        day of year [0:365]
        """
        return self._day

    def trans_offset(self, is_leap, jan1_weekday):  # type: (bool, int) -> int
        days = self._day

        return (days * SECS_PER_DAY) + self._offset


class MPosixTransition(PosixTransition):
    def __init__(self, month, week, weekday, offset):
        # type: (int, int, int, int) -> None
        self._month = month
        self._week = week
        self._weekday = weekday

        super(MPosixTransition, self).__init__(offset)

    @property
    def month(self):  # type: () -> int
        """
        month of year [1:12]
        """
        return self._month

    @property
    def week(self):  # type: () -> int
        """
        week of month [1:5] (5==last)
        """
        return self._week

    @property
    def weekday(self):  # type: () -> int
        """
        0==Sun, ..., 6=Sat
        """
        return self._weekday

    def trans_offset(self, is_leap, jan1_weekday):  # type: (bool, int) -> int
        last_week = self._week == 5
        days = MONTHS_OFFSETS[is_leap][self._month + int(last_week)]
        weekday = (jan1_weekday + days) % 7
        if last_week:
            days -= (weekday + 7 - 1 - self._weekday) % 7 + 1
        else:
            days += (self._weekday + 7 - weekday) % 7
            days += (self._week - 1) * 7

        return (days * SECS_PER_DAY) + self._offset


class PosixTimezone:
    """
    The entirety of a POSIX-string specified time-zone rule.

    The standard abbreviation and offset are always given.
    """

    def __init__(
        self,
        std_abbr,  # type: str
        std_offset,  # type: int
        dst_abbr,  # type: Optional[str]
        dst_offset,  # type: Optional[int]
        dst_start=None,  # type: Optional[PosixTransition]
        dst_end=None,  # type: Optional[PosixTransition]
    ):
        self._std_abbr = std_abbr
        self._std_offset = std_offset
        self._dst_abbr = dst_abbr
        self._dst_offset = dst_offset
        self._dst_start = dst_start
        self._dst_end = dst_end

    @property
    def std_abbr(self):  # type: () -> str
        return self._std_abbr

    @property
    def std_offset(self):  # type: () -> int
        return self._std_offset

    @property
    def dst_abbr(self):  # type: () -> Optional[str]
        return self._dst_abbr

    @property
    def dst_offset(self):  # type: () -> Optional[int]
        return self._dst_offset

    @property
    def dst_start(self):  # type: () -> Optional[PosixTransition]
        return self._dst_start

    @property
    def dst_end(self):  # type: () -> Optional[PosixTransition]
        return self._dst_end
