from __future__ import annotations

import contextlib
import copy
import os
import re
import struct

from datetime import date
from datetime import datetime
from datetime import time
from typing import Any
from typing import Optional
from typing import cast

from dateutil import parser

from pendulum.parsing.exceptions import ParserError


with_extensions = os.getenv("PENDULUM_EXTENSIONS", "1") == "1"

try:
    if not with_extensions or struct.calcsize("P") == 4:
        raise ImportError()

    from pendulum._pendulum import Duration
    from pendulum._pendulum import parse_iso8601
except ImportError:
    from pendulum.duration import Duration  # type: ignore[assignment]
    from pendulum.parsing.iso8601 import parse_iso8601  # type: ignore[assignment]


COMMON = re.compile(
    # Date (optional)  # noqa: ERA001
    "^"
    "(?P<date>"
    "    (?P<classic>"  # Classic date (YYYY-MM-DD)
    r"        (?P<year>\d{4})"  # Year
    "        (?P<monthday>"
    r"            (?P<monthsep>[/:])?(?P<month>\d{2})"  # Month (optional)
    r"            ((?P<daysep>[/:])?(?P<day>\d{2}))"  # Day (optional)
    "        )?"
    "    )"
    ")?"
    # Time (optional)  # noqa: ERA001
    "(?P<time>" r"    (?P<timesep>\ )?"  # Separator (space)
    # HH:mm:ss (optional mm and ss)
    r"    (?P<hour>\d{1,2}):(?P<minute>\d{1,2})?(?::(?P<second>\d{1,2}))?"
    # Subsecond part (optional)
    "    (?P<subsecondsection>"
    "        (?:[.|,])"  # Subsecond separator (optional)
    r"        (?P<subsecond>\d{1,9})"  # Subsecond
    "    )?"
    ")?"
    "$",
    re.VERBOSE,
)

DEFAULT_OPTIONS = {
    "day_first": False,
    "year_first": True,
    "strict": True,
    "exact": False,
    "now": None,
}


def parse(text: str, **options: Any) -> datetime | date | time | _Interval | Duration:
    """
    Parses a string with the given options.

    :param text: The string to parse.
    """
    _options: dict[str, Any] = copy.copy(DEFAULT_OPTIONS)
    _options.update(options)

    return _normalize(_parse(text, **_options), **_options)


def _normalize(
    parsed: datetime | date | time | _Interval | Duration, **options: Any
) -> datetime | date | time | _Interval | Duration:
    """
    Normalizes the parsed element.

    :param parsed: The parsed elements.
    """
    if options.get("exact"):
        return parsed

    if isinstance(parsed, time):
        now = cast(Optional[datetime], options["now"]) or datetime.now()

        return datetime(
            now.year,
            now.month,
            now.day,
            parsed.hour,
            parsed.minute,
            parsed.second,
            parsed.microsecond,
        )
    elif isinstance(parsed, date) and not isinstance(parsed, datetime):
        return datetime(parsed.year, parsed.month, parsed.day)

    return parsed


def _parse(text: str, **options: Any) -> datetime | date | time | _Interval | Duration:
    # Trying to parse ISO8601
    with contextlib.suppress(ValueError):
        return parse_iso8601(text)

    with contextlib.suppress(ValueError):
        return _parse_iso8601_interval(text)

    with contextlib.suppress(ParserError):
        return _parse_common(text, **options)

    # We couldn't parse the string
    # so we fallback on the dateutil parser
    # If not strict
    if options.get("strict", True):
        raise ParserError(f"Unable to parse string [{text}]")

    try:
        dt = parser.parse(
            text, dayfirst=options["day_first"], yearfirst=options["year_first"]
        )
    except ValueError:
        raise ParserError(f"Invalid date string: {text}")

    return dt


def _parse_common(text: str, **options: Any) -> datetime | date | time:
    """
    Tries to parse the string as a common datetime format.

    :param text: The string to parse.
    """
    m = COMMON.match(text)
    has_date = False
    year = 0
    month = 1
    day = 1

    if not m:
        raise ParserError("Invalid datetime string")

    if m.group("date"):
        # A date has been specified
        has_date = True

        year = int(m.group("year"))

        if not m.group("monthday"):
            # No month and day
            month = 1
            day = 1
        else:
            if options["day_first"]:
                month = int(m.group("day"))
                day = int(m.group("month"))
            else:
                month = int(m.group("month"))
                day = int(m.group("day"))

    if not m.group("time"):
        return date(year, month, day)

    # Grabbing hh:mm:ss
    hour = int(m.group("hour"))

    minute = int(m.group("minute"))

    second = int(m.group("second")) if m.group("second") else 0

    # Grabbing subseconds, if any
    microsecond = 0
    if m.group("subsecondsection"):
        # Limiting to 6 chars
        subsecond = m.group("subsecond")[:6]

        microsecond = int(f"{subsecond:0<6}")

    if has_date:
        return datetime(year, month, day, hour, minute, second, microsecond)

    return time(hour, minute, second, microsecond)


class _Interval:
    """
    Special class to handle ISO 8601 intervals
    """

    def __init__(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        duration: Duration | None = None,
    ) -> None:
        self.start = start
        self.end = end
        self.duration = duration


def _parse_iso8601_interval(text: str) -> _Interval:
    if "/" not in text:
        raise ParserError("Invalid interval")

    first, last = text.split("/")
    start = end = duration = None

    if first[0] == "P":
        # duration/end
        duration = parse_iso8601(first)
        end = parse_iso8601(last)
    elif last[0] == "P":
        # start/duration
        start = parse_iso8601(first)
        duration = parse_iso8601(last)
    else:
        # start/end
        start = parse_iso8601(first)
        end = parse_iso8601(last)

    return _Interval(
        cast(datetime, start), cast(datetime, end), cast(Duration, duration)
    )


__all__ = ["parse", "parse_iso8601"]
