from __future__ import division

import datetime
import re

from ..constants import HOURS_PER_DAY
from ..constants import MINUTES_PER_HOUR
from ..constants import MONTHS_OFFSETS
from ..constants import SECONDS_PER_MINUTE
from ..duration import Duration
from ..helpers import days_in_year
from ..helpers import is_leap
from ..helpers import is_long_year
from ..helpers import week_day
from ..tz.timezone import UTC
from ..tz.timezone import FixedTimezone
from .exceptions import ParserError


ISO8601_DT = re.compile(
    # Date (optional)
    "^"
    "(?P<date>"
    "    (?P<classic>"  # Classic date (YYYY-MM-DD) or ordinal (YYYY-DDD)
    r"        (?P<year>\d{4})"  # Year
    "        (?P<monthday>"
    r"            (?P<monthsep>-)?(?P<month>\d{2})"  # Month (optional)
    r"            ((?P<daysep>-)?(?P<day>\d{1,2}))?"  # Day (optional)
    "        )?"
    "    )"
    "    |"
    "    (?P<isocalendar>"  # Calendar date (2016-W05 or 2016-W05-5)
    r"        (?P<isoyear>\d{4})"  # Year
    "        (?P<weeksep>-)?"  # Separator (optional)
    "        W"  # W separator
    r"        (?P<isoweek>\d{2})"  # Week number
    "        (?P<weekdaysep>-)?"  # Separator (optional)
    r"        (?P<isoweekday>\d)?"  # Weekday (optional)
    "    )"
    ")?"
    # Time (optional)
    "(?P<time>"
    r"    (?P<timesep>[T\ ])?"  # Separator (T or space)
    r"    (?P<hour>\d{1,2})(?P<minsep>:)?(?P<minute>\d{1,2})?(?P<secsep>:)?(?P<second>\d{1,2})?"  # HH:mm:ss (optional mm and ss)
    # Subsecond part (optional)
    "    (?P<subsecondsection>"
    "        (?:[.,])"  # Subsecond separator (optional)
    r"        (?P<subsecond>\d{1,9})"  # Subsecond
    "    )?"
    # Timezone offset
    "    (?P<tz>"
    r"        (?:[-+])\d{2}:?(?:\d{2})?|Z"  # Offset (+HH:mm or +HHmm or +HH or Z)
    "    )?"
    ")?"
    "$",
    re.VERBOSE,
)


ISO8601_DURATION = re.compile(
    "^P"  # Duration P indicator
    # Years, months and days (optional)
    "(?P<w>"
    r"    (?P<weeks>\d+(?:[.,]\d+)?W)"
    ")?"
    "(?P<ymd>"
    r"    (?P<years>\d+(?:[.,]\d+)?Y)?"
    r"    (?P<months>\d+(?:[.,]\d+)?M)?"
    r"    (?P<days>\d+(?:[.,]\d+)?D)?"
    ")?"
    "(?P<hms>"
    "    (?P<timesep>T)"  # Separator (T)
    r"    (?P<hours>\d+(?:[.,]\d+)?H)?"
    r"    (?P<minutes>\d+(?:[.,]\d+)?M)?"
    r"    (?P<seconds>\d+(?:[.,]\d+)?S)?"
    ")?"
    "$",
    re.VERBOSE,
)


def parse_iso8601(text):
    """
    ISO 8601 compliant parser.

    :param text: The string to parse
    :type text: str

    :rtype: datetime.datetime or datetime.time or datetime.date
    """
    parsed = _parse_iso8601_duration(text)
    if parsed is not None:
        return parsed

    m = ISO8601_DT.match(text)
    if not m:
        raise ParserError("Invalid ISO 8601 string")

    ambiguous_date = False
    is_date = False
    is_time = False
    year = 0
    month = 1
    day = 1
    minute = 0
    second = 0
    microsecond = 0
    tzinfo = None

    if m:
        if m.group("date"):
            # A date has been specified
            is_date = True

            if m.group("isocalendar"):
                # We have a ISO 8601 string defined
                # by week number
                if (
                    m.group("weeksep")
                    and not m.group("weekdaysep")
                    and m.group("isoweekday")
                ):
                    raise ParserError("Invalid date string: {}".format(text))

                if not m.group("weeksep") and m.group("weekdaysep"):
                    raise ParserError("Invalid date string: {}".format(text))

                try:
                    date = _get_iso_8601_week(
                        m.group("isoyear"), m.group("isoweek"), m.group("isoweekday")
                    )
                except ParserError:
                    raise
                except ValueError:
                    raise ParserError("Invalid date string: {}".format(text))

                year = date["year"]
                month = date["month"]
                day = date["day"]
            else:
                # We have a classic date representation
                year = int(m.group("year"))

                if not m.group("monthday"):
                    # No month and day
                    month = 1
                    day = 1
                else:
                    if m.group("month") and m.group("day"):
                        # Month and day
                        if not m.group("daysep") and len(m.group("day")) == 1:
                            # Ordinal day
                            ordinal = int(m.group("month") + m.group("day"))
                            leap = is_leap(year)
                            months_offsets = MONTHS_OFFSETS[leap]

                            if ordinal > months_offsets[13]:
                                raise ParserError("Ordinal day is out of range")

                            for i in range(1, 14):
                                if ordinal <= months_offsets[i]:
                                    day = ordinal - months_offsets[i - 1]
                                    month = i - 1

                                    break
                        else:
                            month = int(m.group("month"))
                            day = int(m.group("day"))
                    else:
                        # Only month
                        if not m.group("monthsep"):
                            # The date looks like 201207
                            # which is invalid for a date
                            # But it might be a time in the form hhmmss
                            ambiguous_date = True

                        month = int(m.group("month"))
                        day = 1

        if not m.group("time"):
            # No time has been specified
            if ambiguous_date:
                # We can "safely" assume that the ambiguous date
                # was actually a time in the form hhmmss
                hhmmss = "{}{:0>2}".format(str(year), str(month))

                return datetime.time(int(hhmmss[:2]), int(hhmmss[2:4]), int(hhmmss[4:]))

            return datetime.date(year, month, day)

        if ambiguous_date:
            raise ParserError("Invalid date string: {}".format(text))

        if is_date and not m.group("timesep"):
            raise ParserError("Invalid date string: {}".format(text))

        if not is_date:
            is_time = True

        # Grabbing hh:mm:ss
        hour = int(m.group("hour"))
        minsep = m.group("minsep")

        if m.group("minute"):
            minute = int(m.group("minute"))
        elif minsep:
            raise ParserError("Invalid ISO 8601 time part")

        secsep = m.group("secsep")
        if secsep and not minsep and m.group("minute"):
            # minute/second separator but no hour/minute separator
            raise ParserError("Invalid ISO 8601 time part")

        if m.group("second"):
            if not secsep and minsep:
                # No minute/second separator but hour/minute separator
                raise ParserError("Invalid ISO 8601 time part")

            second = int(m.group("second"))
        elif secsep:
            raise ParserError("Invalid ISO 8601 time part")

        # Grabbing subseconds, if any
        if m.group("subsecondsection"):
            # Limiting to 6 chars
            subsecond = m.group("subsecond")[:6]

            microsecond = int("{:0<6}".format(subsecond))

        # Grabbing timezone, if any
        tz = m.group("tz")
        if tz:
            if tz == "Z":
                tzinfo = UTC
            else:
                negative = True if tz.startswith("-") else False
                tz = tz[1:]
                if ":" not in tz:
                    if len(tz) == 2:
                        tz = "{}00".format(tz)

                    off_hour = tz[0:2]
                    off_minute = tz[2:4]
                else:
                    off_hour, off_minute = tz.split(":")

                offset = ((int(off_hour) * 60) + int(off_minute)) * 60

                if negative:
                    offset = -1 * offset

                tzinfo = FixedTimezone(offset)

        if is_time:
            return datetime.time(hour, minute, second, microsecond)

        return datetime.datetime(
            year, month, day, hour, minute, second, microsecond, tzinfo=tzinfo
        )


def _parse_iso8601_duration(text, **options):
    m = ISO8601_DURATION.match(text)
    if not m:
        return

    years = 0
    months = 0
    weeks = 0
    days = 0
    hours = 0
    minutes = 0
    seconds = 0
    microseconds = 0
    fractional = False

    if m.group("w"):
        # Weeks
        if m.group("ymd") or m.group("hms"):
            # Specifying anything more than weeks is not supported
            raise ParserError("Invalid duration string")

        _weeks = m.group("weeks")
        if not _weeks:
            raise ParserError("Invalid duration string")

        _weeks = _weeks.replace(",", ".").replace("W", "")
        if "." in _weeks:
            _weeks, portion = _weeks.split(".")
            weeks = int(_weeks)
            _days = int(portion) / 10 * 7
            days, hours = int(_days // 1), _days % 1 * HOURS_PER_DAY
        else:
            weeks = int(_weeks)

    if m.group("ymd"):
        # Years, months and/or days
        _years = m.group("years")
        _months = m.group("months")
        _days = m.group("days")

        # Checking order
        years_start = m.start("years") if _years else -3
        months_start = m.start("months") if _months else years_start + 1
        days_start = m.start("days") if _days else months_start + 1

        # Check correct order
        if not (years_start < months_start < days_start):
            raise ParserError("Invalid duration")

        if _years:
            _years = _years.replace(",", ".").replace("Y", "")
            if "." in _years:
                raise ParserError("Float years in duration are not supported")
            else:
                years = int(_years)

        if _months:
            if fractional:
                raise ParserError("Invalid duration")

            _months = _months.replace(",", ".").replace("M", "")
            if "." in _months:
                raise ParserError("Float months in duration are not supported")
            else:
                months = int(_months)

        if _days:
            if fractional:
                raise ParserError("Invalid duration")

            _days = _days.replace(",", ".").replace("D", "")

            if "." in _days:
                fractional = True

                _days, _hours = _days.split(".")
                days = int(_days)
                hours = int(_hours) / 10 * HOURS_PER_DAY
            else:
                days = int(_days)

    if m.group("hms"):
        # Hours, minutes and/or seconds
        _hours = m.group("hours") or 0
        _minutes = m.group("minutes") or 0
        _seconds = m.group("seconds") or 0

        # Checking order
        hours_start = m.start("hours") if _hours else -3
        minutes_start = m.start("minutes") if _minutes else hours_start + 1
        seconds_start = m.start("seconds") if _seconds else minutes_start + 1

        # Check correct order
        if not (hours_start < minutes_start < seconds_start):
            raise ParserError("Invalid duration")

        if _hours:
            if fractional:
                raise ParserError("Invalid duration")

            _hours = _hours.replace(",", ".").replace("H", "")

            if "." in _hours:
                fractional = True

                _hours, _mins = _hours.split(".")
                hours += int(_hours)
                minutes += int(_mins) / 10 * MINUTES_PER_HOUR
            else:
                hours += int(_hours)

        if _minutes:
            if fractional:
                raise ParserError("Invalid duration")

            _minutes = _minutes.replace(",", ".").replace("M", "")

            if "." in _minutes:
                fractional = True

                _minutes, _secs = _minutes.split(".")
                minutes += int(_minutes)
                seconds += int(_secs) / 10 * SECONDS_PER_MINUTE
            else:
                minutes += int(_minutes)

        if _seconds:
            if fractional:
                raise ParserError("Invalid duration")

            _seconds = _seconds.replace(",", ".").replace("S", "")

            if "." in _seconds:
                _seconds, _microseconds = _seconds.split(".")
                seconds += int(_seconds)
                microseconds += int("{:0<6}".format(_microseconds[:6]))
            else:
                seconds += int(_seconds)

    return Duration(
        years=years,
        months=months,
        weeks=weeks,
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        microseconds=microseconds,
    )


def _get_iso_8601_week(year, week, weekday):
    if not weekday:
        weekday = 1
    else:
        weekday = int(weekday)

    year = int(year)
    week = int(week)

    if week > 53 or week > 52 and not is_long_year(year):
        raise ParserError("Invalid week for week date")

    if weekday > 7:
        raise ParserError("Invalid weekday for week date")

    # We can't rely on strptime directly here since
    # it does not support ISO week date
    ordinal = week * 7 + weekday - (week_day(year, 1, 4) + 3)

    if ordinal < 1:
        # Previous year
        ordinal += days_in_year(year - 1)
        year -= 1

    if ordinal > days_in_year(year):
        # Next year
        ordinal -= days_in_year(year)
        year += 1

    fmt = "%Y-%j"
    string = "{}-{}".format(year, ordinal)

    dt = datetime.datetime.strptime(string, fmt)

    return {"year": dt.year, "month": dt.month, "day": dt.day}
