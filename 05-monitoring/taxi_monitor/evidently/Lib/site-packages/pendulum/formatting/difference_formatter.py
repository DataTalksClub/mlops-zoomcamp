from __future__ import annotations

import typing as t

from pendulum.locales.locale import Locale


if t.TYPE_CHECKING:
    from pendulum import Duration


class DifferenceFormatter:
    """
    Handles formatting differences in text.
    """

    def __init__(self, locale: str = "en") -> None:
        self._locale = Locale.load(locale)

    def format(
        self,
        diff: Duration,
        is_now: bool = True,
        absolute: bool = False,
        locale: str | Locale | None = None,
    ) -> str:
        """
        Formats a difference.

        :param diff: The difference to format
        :param is_now: Whether the difference includes now
        :param absolute: Whether it's an absolute difference or not
        :param locale: The locale to use
        """
        locale = self._locale if locale is None else Locale.load(locale)

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
                    return t.cast(str, time)

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

                return t.cast(str, locale.get(key).format(time))
            else:
                unit = "second"
                count = diff.remaining_seconds

        if count == 0:
            count = 1

        if absolute:
            key = f"translations.units.{unit}"
        else:
            is_future = diff.invert

            if is_now:
                # Relative to now, so we can use
                # the CLDR data
                key = f"translations.relative.{unit}"

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
                    key += f".{unit}.future"
                else:
                    key += f".{unit}.past"

                trans = locale.get(key)
                if not trans:
                    # No special rule
                    key = f"translations.units.{unit}.{locale.plural(count)}"
                    time = locale.get(key).format(count)
                else:
                    time = trans[locale.plural(count)].format(count)

                key = "custom"
                if is_future:
                    key += ".after"
                else:
                    key += ".before"

                return t.cast(str, locale.get(key).format(time))

        key += f".{locale.plural(count)}"

        return t.cast(str, locale.get(key).format(count))
