import datetime
import math
import typing

from collections import namedtuple

from ..constants import DAY_OF_WEEK_TABLE
from ..constants import DAYS_PER_L_YEAR
from ..constants import DAYS_PER_MONTHS
from ..constants import DAYS_PER_N_YEAR
from ..constants import EPOCH_YEAR
from ..constants import MONTHS_OFFSETS
from ..constants import SECS_PER_4_YEARS
from ..constants import SECS_PER_100_YEARS
from ..constants import SECS_PER_400_YEARS
from ..constants import SECS_PER_DAY
from ..constants import SECS_PER_HOUR
from ..constants import SECS_PER_MIN
from ..constants import SECS_PER_YEAR
from ..constants import TM_DECEMBER
from ..constants import TM_JANUARY


class PreciseDiff(
    namedtuple(
        "PreciseDiff",
        "years months days " "hours minutes seconds microseconds " "total_days",
    )
):
    def __repr__(self):
        return (
            "{years} years "
            "{months} months "
            "{days} days "
            "{hours} hours "
            "{minutes} minutes "
            "{seconds} seconds "
            "{microseconds} microseconds"
        ).format(
            years=self.years,
            months=self.months,
            days=self.days,
            hours=self.hours,
            minutes=self.minutes,
            seconds=self.seconds,
            microseconds=self.microseconds,
        )


def is_leap(year):  # type: (int) -> bool
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def is_long_year(year):  # type: (int) -> bool
    def p(y):
        return y + y // 4 - y // 100 + y // 400

    return p(year) % 7 == 4 or p(year - 1) % 7 == 3


def week_day(year, month, day):  # type: (int, int, int) -> int
    if month < 3:
        year -= 1

    w = (
        year
        + year // 4
        - year // 100
        + year // 400
        + DAY_OF_WEEK_TABLE[month - 1]
        + day
    ) % 7

    if not w:
        w = 7

    return w


def days_in_year(year):  # type: (int) -> int
    if is_leap(year):
        return DAYS_PER_L_YEAR

    return DAYS_PER_N_YEAR


def timestamp(dt):  # type: (datetime.datetime) -> int
    year = dt.year

    result = (year - 1970) * 365 + MONTHS_OFFSETS[0][dt.month]
    result += (year - 1968) // 4
    result -= (year - 1900) // 100
    result += (year - 1600) // 400

    if is_leap(year) and dt.month < 3:
        result -= 1

    result += dt.day - 1
    result *= 24
    result += dt.hour
    result *= 60
    result += dt.minute
    result *= 60
    result += dt.second

    return result


def local_time(
    unix_time, utc_offset, microseconds
):  # type: (int, int, int) -> typing.Tuple[int, int, int, int, int, int, int]
    """
    Returns a UNIX time as a broken down time
    for a particular transition type.

    :type unix_time: int
    :type utc_offset: int
    :type microseconds: int

    :rtype: tuple
    """
    year = EPOCH_YEAR
    seconds = int(math.floor(unix_time))

    # Shift to a base year that is 400-year aligned.
    if seconds >= 0:
        seconds -= 10957 * SECS_PER_DAY
        year += 30  # == 2000
    else:
        seconds += (146097 - 10957) * SECS_PER_DAY
        year -= 370  # == 1600

    seconds += utc_offset

    # Handle years in chunks of 400/100/4/1
    year += 400 * (seconds // SECS_PER_400_YEARS)
    seconds %= SECS_PER_400_YEARS
    if seconds < 0:
        seconds += SECS_PER_400_YEARS
        year -= 400

    leap_year = 1  # 4-century aligned

    sec_per_100years = SECS_PER_100_YEARS[leap_year]
    while seconds >= sec_per_100years:
        seconds -= sec_per_100years
        year += 100
        leap_year = 0  # 1-century, non 4-century aligned
        sec_per_100years = SECS_PER_100_YEARS[leap_year]

    sec_per_4years = SECS_PER_4_YEARS[leap_year]
    while seconds >= sec_per_4years:
        seconds -= sec_per_4years
        year += 4
        leap_year = 1  # 4-year, non century aligned
        sec_per_4years = SECS_PER_4_YEARS[leap_year]

    sec_per_year = SECS_PER_YEAR[leap_year]
    while seconds >= sec_per_year:
        seconds -= sec_per_year
        year += 1
        leap_year = 0  # non 4-year aligned
        sec_per_year = SECS_PER_YEAR[leap_year]

    # Handle months and days
    month = TM_DECEMBER + 1
    day = seconds // SECS_PER_DAY + 1
    seconds %= SECS_PER_DAY
    while month != TM_JANUARY + 1:
        month_offset = MONTHS_OFFSETS[leap_year][month]
        if day > month_offset:
            day -= month_offset
            break

        month -= 1

    # Handle hours, minutes, seconds and microseconds
    hour = seconds // SECS_PER_HOUR
    seconds %= SECS_PER_HOUR
    minute = seconds // SECS_PER_MIN
    second = seconds % SECS_PER_MIN

    return (year, month, day, hour, minute, second, microseconds)


def precise_diff(
    d1, d2
):  # type: (typing.Union[datetime.datetime, datetime.date], typing.Union[datetime.datetime, datetime.date]) -> PreciseDiff
    """
    Calculate a precise difference between two datetimes.

    :param d1: The first datetime
    :type d1: datetime.datetime or datetime.date

    :param d2: The second datetime
    :type d2: datetime.datetime or datetime.date

    :rtype: PreciseDiff
    """
    sign = 1

    if d1 == d2:
        return PreciseDiff(0, 0, 0, 0, 0, 0, 0, 0)

    tzinfo1 = d1.tzinfo if isinstance(d1, datetime.datetime) else None
    tzinfo2 = d2.tzinfo if isinstance(d2, datetime.datetime) else None

    if (
        tzinfo1 is None
        and tzinfo2 is not None
        or tzinfo2 is None
        and tzinfo1 is not None
    ):
        raise ValueError(
            "Comparison between naive and aware datetimes is not supported"
        )

    if d1 > d2:
        d1, d2 = d2, d1
        sign = -1

    d_diff = 0
    hour_diff = 0
    min_diff = 0
    sec_diff = 0
    mic_diff = 0
    total_days = _day_number(d2.year, d2.month, d2.day) - _day_number(
        d1.year, d1.month, d1.day
    )
    in_same_tz = False
    tz1 = None
    tz2 = None

    # Trying to figure out the timezone names
    # If we can't find them, we assume different timezones
    if tzinfo1 and tzinfo2:
        if hasattr(tzinfo1, "name"):
            # Pendulum timezone
            tz1 = tzinfo1.name
        elif hasattr(tzinfo1, "zone"):
            # pytz timezone
            tz1 = tzinfo1.zone

        if hasattr(tzinfo2, "name"):
            tz2 = tzinfo2.name
        elif hasattr(tzinfo2, "zone"):
            tz2 = tzinfo2.zone

        in_same_tz = tz1 == tz2 and tz1 is not None

    if isinstance(d2, datetime.datetime):
        if isinstance(d1, datetime.datetime):
            # If we are not in the same timezone
            # we need to adjust
            #
            # We also need to adjust if we do not
            # have variable-length units
            if not in_same_tz or total_days == 0:
                offset1 = d1.utcoffset()
                offset2 = d2.utcoffset()

                if offset1:
                    d1 = d1 - offset1

                if offset2:
                    d2 = d2 - offset2

            hour_diff = d2.hour - d1.hour
            min_diff = d2.minute - d1.minute
            sec_diff = d2.second - d1.second
            mic_diff = d2.microsecond - d1.microsecond
        else:
            hour_diff = d2.hour
            min_diff = d2.minute
            sec_diff = d2.second
            mic_diff = d2.microsecond

        if mic_diff < 0:
            mic_diff += 1000000
            sec_diff -= 1

        if sec_diff < 0:
            sec_diff += 60
            min_diff -= 1

        if min_diff < 0:
            min_diff += 60
            hour_diff -= 1

        if hour_diff < 0:
            hour_diff += 24
            d_diff -= 1

    y_diff = d2.year - d1.year
    m_diff = d2.month - d1.month
    d_diff += d2.day - d1.day

    if d_diff < 0:
        year = d2.year
        month = d2.month

        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1

        leap = int(is_leap(year))

        days_in_last_month = DAYS_PER_MONTHS[leap][month]
        days_in_month = DAYS_PER_MONTHS[int(is_leap(d2.year))][d2.month]

        if d_diff < days_in_month - days_in_last_month:
            # We don't have a full month, we calculate days
            if days_in_last_month < d1.day:
                d_diff += d1.day
            else:
                d_diff += days_in_last_month
        elif d_diff == days_in_month - days_in_last_month:
            # We have exactly a full month
            # We remove the days difference
            # and add one to the months difference
            d_diff = 0
            m_diff += 1
        else:
            # We have a full month
            d_diff += days_in_last_month

        m_diff -= 1

    if m_diff < 0:
        m_diff += 12
        y_diff -= 1

    return PreciseDiff(
        sign * y_diff,
        sign * m_diff,
        sign * d_diff,
        sign * hour_diff,
        sign * min_diff,
        sign * sec_diff,
        sign * mic_diff,
        sign * total_days,
    )


def _day_number(year, month, day):  # type: (int, int, int) -> int
    month = (month + 9) % 12
    year = year - month // 10

    return (
        365 * year
        + year // 4
        - year // 100
        + year // 400
        + (month * 306 + 5) // 10
        + (day - 1)
    )
