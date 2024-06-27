from __future__ import absolute_import

import datetime
import typing

import pendulum

from .date import Date
from .datetime import DateTime
from .parsing import _Interval
from .parsing import parse as base_parse
from .time import Duration
from .time import Time
from .tz import UTC


try:
    from .parsing._iso8601 import Duration as CDuration
except ImportError:
    CDuration = None


def parse(
    text, **options
):  # type: (str, **typing.Any) -> typing.Union[Date, Time, DateTime, Duration]
    # Use the mock now value if it exists
    options["now"] = options.get("now", pendulum.get_test_now())

    return _parse(text, **options)


def _parse(text, **options):
    """
    Parses a string with the given options.

    :param text: The string to parse.
    :type text: str

    :rtype: mixed
    """
    # Handling special cases
    if text == "now":
        return pendulum.now()

    parsed = base_parse(text, **options)

    if isinstance(parsed, datetime.datetime):
        return pendulum.datetime(
            parsed.year,
            parsed.month,
            parsed.day,
            parsed.hour,
            parsed.minute,
            parsed.second,
            parsed.microsecond,
            tz=parsed.tzinfo or options.get("tz", UTC),
        )

    if isinstance(parsed, datetime.date):
        return pendulum.date(parsed.year, parsed.month, parsed.day)

    if isinstance(parsed, datetime.time):
        return pendulum.time(
            parsed.hour, parsed.minute, parsed.second, parsed.microsecond
        )

    if isinstance(parsed, _Interval):
        if parsed.duration is not None:
            duration = parsed.duration

            if parsed.start is not None:
                dt = pendulum.instance(parsed.start, tz=options.get("tz", UTC))

                return pendulum.period(
                    dt,
                    dt.add(
                        years=duration.years,
                        months=duration.months,
                        weeks=duration.weeks,
                        days=duration.remaining_days,
                        hours=duration.hours,
                        minutes=duration.minutes,
                        seconds=duration.remaining_seconds,
                        microseconds=duration.microseconds,
                    ),
                )

            dt = pendulum.instance(parsed.end, tz=options.get("tz", UTC))

            return pendulum.period(
                dt.subtract(
                    years=duration.years,
                    months=duration.months,
                    weeks=duration.weeks,
                    days=duration.remaining_days,
                    hours=duration.hours,
                    minutes=duration.minutes,
                    seconds=duration.remaining_seconds,
                    microseconds=duration.microseconds,
                ),
                dt,
            )

        return pendulum.period(
            pendulum.instance(parsed.start, tz=options.get("tz", UTC)),
            pendulum.instance(parsed.end, tz=options.get("tz", UTC)),
        )

    if CDuration and isinstance(parsed, CDuration):
        return pendulum.duration(
            years=parsed.years,
            months=parsed.months,
            weeks=parsed.weeks,
            days=parsed.days,
            hours=parsed.hours,
            minutes=parsed.minutes,
            seconds=parsed.seconds,
            microseconds=parsed.microseconds,
        )

    return parsed
