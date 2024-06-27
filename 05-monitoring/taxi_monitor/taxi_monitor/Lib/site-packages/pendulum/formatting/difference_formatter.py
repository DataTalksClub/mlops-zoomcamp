import typing

import pendulum

from pendulum.utils._compat import decode

from ..locales.locale import Locale


class DifferenceFormatter(object):
    """
    Handles formatting differences in text.
    """

    def __init__(self, locale="en"):
        self._locale = Locale.load(locale)

    def format(
        self, diff, is_now=True, absolute=False, locale=None
    ):  # type: (pendulum.Period, bool, bool, typing.Optional[str]) -> str
        """
        Formats a difference.

        :param diff: The difference to format
        :type diff: pendulum.period.Period

        :param is_now: Whether the difference includes now
        :type is_now: bool

        :param absolute: Whether it's an absolute difference or not
        :type absolute: bool

        :param locale: The locale to use
        :type locale: str or None

        :rtype: str
        """
        if locale is None:
            locale = self._locale
        else:
            locale = Locale.load(locale)

        count = diff.remaining_seconds

        if diff.years > 0:
            unit = "year"
            count = diff.years

            if diff.months > 6:
                count += 1
        elif diff.months == 11 and (diff.weeks * 7 + diff.remaining_days) > 15:
            unit = "year"
            count = 1
        elif diff.months > 0:
            unit = "month"
            count = diff.months

            if (diff.weeks * 7 + diff.remaining_days) >= 27:
                count += 1
        elif diff.weeks > 0:
            unit = "week"
            count = diff.weeks

            if diff.remaining_days > 3:
                count += 1
        elif diff.remaining_days > 0:
            unit = "day"
            count = diff.remaining_days

            if diff.hours >= 22:
                count += 1
        elif diff.hours > 0:
            unit = "hour"
            count = diff.hours
        elif diff.minutes > 0:
            unit = "minute"
            count = diff.minutes
        elif 10 < diff.remaining_seconds <= 59:
            unit = "second"
            count = diff.remaining_seconds
        else:
            # We check if the "a few seconds" unit exists
            time = locale.get("custom.units.few_second")
            if time is not None:
                if absolute:
                    return time

                key = "custom"
                is_future = diff.invert
                if is_now:
                    if is_future:
                        key += ".from_now"
                    else:
                        key += ".ago"
                else:
                    if is_future:
                        key += ".after"
                    else:
                        key += ".before"

                return locale.get(key).format(time)
            else:
                unit = "second"
                count = diff.remaining_seconds

        if count == 0:
            count = 1

        if absolute:
            key = "translations.units.{}".format(unit)
        else:
            is_future = diff.invert

            if is_now:
                # Relative to now, so we can use
                # the CLDR data
                key = "translations.relative.{}".format(unit)

                if is_future:
                    key += ".future"
                else:
                    key += ".past"
            else:
                # Absolute comparison
                # So we have to use the custom locale data

                # Checking for special pluralization rules
                key = "custom.units_relative"
                if is_future:
                    key += ".{}.future".format(unit)
                else:
                    key += ".{}.past".format(unit)

                trans = locale.get(key)
                if not trans:
                    # No special rule
                    time = locale.get(
                        "translations.units.{}.{}".format(unit, locale.plural(count))
                    ).format(count)
                else:
                    time = trans[locale.plural(count)].format(count)

                key = "custom"
                if is_future:
                    key += ".after"
                else:
                    key += ".before"

                return locale.get(key).format(decode(time))

        key += ".{}".format(locale.plural(count))

        return decode(locale.get(key).format(count))
