from __future__ import annotations

import datetime
import re

from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Match
from typing import Sequence
from typing import cast

import pendulum

from pendulum.locales.locale import Locale


if TYPE_CHECKING:
    from pendulum import Timezone

_MATCH_1 = r"\d"
_MATCH_2 = r"\d\d"
_MATCH_3 = r"\d{3}"
_MATCH_4 = r"\d{4}"
_MATCH_6 = r"[+-]?\d{6}"
_MATCH_1_TO_2 = r"\d\d?"
_MATCH_1_TO_2_LEFT_PAD = r"[0-9 ]\d?"
_MATCH_1_TO_3 = r"\d{1,3}"
_MATCH_1_TO_4 = r"\d{1,4}"
_MATCH_1_TO_6 = r"[+-]?\d{1,6}"
_MATCH_3_TO_4 = r"\d{3}\d?"
_MATCH_5_TO_6 = r"\d{5}\d?"
_MATCH_UNSIGNED = r"\d+"
_MATCH_SIGNED = r"[+-]?\d+"
_MATCH_OFFSET = r"[Zz]|[+-]\d\d:?\d\d"
_MATCH_SHORT_OFFSET = r"[Zz]|[+-]\d\d(?::?\d\d)?"
_MATCH_TIMESTAMP = r"[+-]?\d+(\.\d{1,6})?"
_MATCH_WORD = (
    "(?i)[0-9]*"
    "['a-z\u00A0-\u05FF\u0700-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+"
    r"|[\u0600-\u06FF/]+(\s*?[\u0600-\u06FF]+){1,2}"
)
_MATCH_TIMEZONE = "[A-Za-z0-9-+]+(/[A-Za-z0-9-+_]+)?"


class Formatter:
    _TOKENS: str = (
        r"\[([^\[]*)\]|\\(.)|"
        "("
        "Mo|MM?M?M?"
        "|Do|DDDo|DD?D?D?|ddd?d?|do?|eo?"
        "|E{1,4}"
        "|w[o|w]?|W[o|W]?|Qo?"
        "|YYYY|YY|Y"
        "|gg(ggg?)?|GG(GGG?)?"
        "|a|A"
        "|hh?|HH?|kk?"
        "|mm?|ss?|S{1,9}"
        "|x|X"
        "|zz?|ZZ?"
        "|LTS|LT|LL?L?L?"
        ")"
    )

    _FORMAT_RE: re.Pattern[str] = re.compile(_TOKENS)

    _FROM_FORMAT_RE: re.Pattern[str] = re.compile(r"(?<!\\\[)" + _TOKENS + r"(?!\\\])")

    _LOCALIZABLE_TOKENS: ClassVar[
        dict[str, str | Callable[[Locale], Sequence[str]] | None]
    ] = {
        "Qo": None,
        "MMMM": "months.wide",
        "MMM": "months.abbreviated",
        "Mo": None,
        "DDDo": None,
        "Do": lambda locale: tuple(
            rf"\d+{o}" for o in locale.get("custom.ordinal").values()
        ),
        "dddd": "days.wide",
        "ddd": "days.abbreviated",
        "dd": "days.short",
        "do": None,
        "e": None,
        "eo": None,
        "Wo": None,
        "wo": None,
        "A": lambda locale: (
            locale.translation("day_periods.am"),
            locale.translation("day_periods.pm"),
        ),
        "a": lambda locale: (
            locale.translation("day_periods.am").lower(),
            locale.translation("day_periods.pm").lower(),
        ),
    }

    _TOKENS_RULES: ClassVar[dict[str, Callable[[pendulum.DateTime], str]]] = {
        # Year
        "YYYY": lambda dt: f"{dt.year:d}",
        "YY": lambda dt: f"{dt.year:d}"[2:],
        "Y": lambda dt: f"{dt.year:d}",
        # Quarter
        "Q": lambda dt: f"{dt.quarter:d}",
        # Month
        "MM": lambda dt: f"{dt.month:02d}",
        "M": lambda dt: f"{dt.month:d}",
        # Day
        "DD": lambda dt: f"{dt.day:02d}",
        "D": lambda dt: f"{dt.day:d}",
        # Day of Year
        "DDDD": lambda dt: f"{dt.day_of_year:03d}",
        "DDD": lambda dt: f"{dt.day_of_year:d}",
        # Day of Week
        "d": lambda dt: f"{(dt.day_of_week + 1) % 7:d}",
        # Day of ISO Week
        "E": lambda dt: f"{dt.isoweekday():d}",
        # Hour
        "HH": lambda dt: f"{dt.hour:02d}",
        "H": lambda dt: f"{dt.hour:d}",
        "hh": lambda dt: f"{dt.hour % 12 or 12:02d}",
        "h": lambda dt: f"{dt.hour % 12 or 12:d}",
        # Minute
        "mm": lambda dt: f"{dt.minute:02d}",
        "m": lambda dt: f"{dt.minute:d}",
        # Second
        "ss": lambda dt: f"{dt.second:02d}",
        "s": lambda dt: f"{dt.second:d}",
        # Fractional second
        "S": lambda dt: f"{dt.microsecond // 100000:01d}",
        "SS": lambda dt: f"{dt.microsecond // 10000:02d}",
        "SSS": lambda dt: f"{dt.microsecond // 1000:03d}",
        "SSSS": lambda dt: f"{dt.microsecond // 100:04d}",
        "SSSSS": lambda dt: f"{dt.microsecond // 10:05d}",
        "SSSSSS": lambda dt: f"{dt.microsecond:06d}",
        # Timestamp
        "X": lambda dt: f"{dt.int_timestamp:d}",
        "x": lambda dt: f"{dt.int_timestamp * 1000 + dt.microsecond // 1000:d}",
        # Timezone
        "zz": lambda dt: f'{dt.tzname() if dt.tzinfo is not None else ""}',
        "z": lambda dt: f'{dt.timezone_name or ""}',
    }

    _DATE_FORMATS: ClassVar[dict[str, str]] = {
        "LTS": "formats.time.full",
        "LT": "formats.time.short",
        "L": "formats.date.short",
        "LL": "formats.date.long",
        "LLL": "formats.datetime.long",
        "LLLL": "formats.datetime.full",
    }

    _DEFAULT_DATE_FORMATS: ClassVar[dict[str, str]] = {
        "LTS": "h:mm:ss A",
        "LT": "h:mm A",
        "L": "MM/DD/YYYY",
        "LL": "MMMM D, YYYY",
        "LLL": "MMMM D, YYYY h:mm A",
        "LLLL": "dddd, MMMM D, YYYY h:mm A",
    }

    _REGEX_TOKENS: ClassVar[dict[str, str | Sequence[str] | None]] = {
        "Y": _MATCH_SIGNED,
        "YY": (_MATCH_1_TO_2, _MATCH_2),
        "YYYY": (_MATCH_1_TO_4, _MATCH_4),
        "Q": _MATCH_1,
        "Qo": None,
        "M": _MATCH_1_TO_2,
        "MM": (_MATCH_1_TO_2, _MATCH_2),
        "MMM": _MATCH_WORD,
        "MMMM": _MATCH_WORD,
        "D": _MATCH_1_TO_2,
        "DD": (_MATCH_1_TO_2_LEFT_PAD, _MATCH_2),
        "DDD": _MATCH_1_TO_3,
        "DDDD": _MATCH_3,
        "dddd": _MATCH_WORD,
        "ddd": _MATCH_WORD,
        "dd": _MATCH_WORD,
        "d": _MATCH_1,
        "e": _MATCH_1,
        "E": _MATCH_1,
        "Do": None,
        "H": _MATCH_1_TO_2,
        "HH": (_MATCH_1_TO_2, _MATCH_2),
        "h": _MATCH_1_TO_2,
        "hh": (_MATCH_1_TO_2, _MATCH_2),
        "m": _MATCH_1_TO_2,
        "mm": (_MATCH_1_TO_2, _MATCH_2),
        "s": _MATCH_1_TO_2,
        "ss": (_MATCH_1_TO_2, _MATCH_2),
        "S": (_MATCH_1_TO_3, _MATCH_1),
        "SS": (_MATCH_1_TO_3, _MATCH_2),
        "SSS": (_MATCH_1_TO_3, _MATCH_3),
        "SSSS": _MATCH_UNSIGNED,
        "SSSSS": _MATCH_UNSIGNED,
        "SSSSSS": _MATCH_UNSIGNED,
        "x": _MATCH_SIGNED,
        "X": _MATCH_TIMESTAMP,
        "ZZ": _MATCH_SHORT_OFFSET,
        "Z": _MATCH_OFFSET,
        "z": _MATCH_TIMEZONE,
    }

    _PARSE_TOKENS: ClassVar[dict[str, Callable[[str], Any]]] = {
        "YYYY": lambda year: int(year),
        "YY": lambda year: int(year),
        "Q": lambda quarter: int(quarter),
        "MMMM": lambda month: month,
        "MMM": lambda month: month,
        "MM": lambda month: int(month),
        "M": lambda month: int(month),
        "DDDD": lambda day: int(day),
        "DDD": lambda day: int(day),
        "DD": lambda day: int(day),
        "D": lambda day: int(day),
        "dddd": lambda weekday: weekday,
        "ddd": lambda weekday: weekday,
        "dd": lambda weekday: weekday,
        "d": lambda weekday: int(weekday),
        "E": lambda weekday: int(weekday) - 1,
        "HH": lambda hour: int(hour),
        "H": lambda hour: int(hour),
        "hh": lambda hour: int(hour),
        "h": lambda hour: int(hour),
        "mm": lambda minute: int(minute),
        "m": lambda minute: int(minute),
        "ss": lambda second: int(second),
        "s": lambda second: int(second),
        "S": lambda us: int(us) * 100000,
        "SS": lambda us: int(us) * 10000,
        "SSS": lambda us: int(us) * 1000,
        "SSSS": lambda us: int(us) * 100,
        "SSSSS": lambda us: int(us) * 10,
        "SSSSSS": lambda us: int(us),
        "a": lambda meridiem: meridiem,
        "X": lambda ts: float(ts),
        "x": lambda ts: float(ts) / 1e3,
        "ZZ": str,
        "Z": str,
        "z": str,
    }

    def format(
        self, dt: pendulum.DateTime, fmt: str, locale: str | Locale | None = None
    ) -> str:
        """
        Formats a DateTime instance with a given format and locale.

        :param dt: The instance to format
        :param fmt: The format to use
        :param locale: The locale to use
        """
        loaded_locale: Locale = Locale.load(locale or pendulum.get_locale())

        result = self._FORMAT_RE.sub(
            lambda m: m.group(1)
            if m.group(1)
            else m.group(2)
            if m.group(2)
            else self._format_token(dt, m.group(3), loaded_locale),
            fmt,
        )

        return result

    def _format_token(self, dt: pendulum.DateTime, token: str, locale: Locale) -> str:
        """
        Formats a DateTime instance with a given token and locale.

        :param dt: The instance to format
        :param token: The token to use
        :param locale: The locale to use
        """
        if token in self._DATE_FORMATS:
            fmt = locale.get(f"custom.date_formats.{token}")
            if fmt is None:
                fmt = self._DEFAULT_DATE_FORMATS[token]

            return self.format(dt, fmt, locale)

        if token in self._LOCALIZABLE_TOKENS:
            return self._format_localizable_token(dt, token, locale)

        if token in self._TOKENS_RULES:
            return self._TOKENS_RULES[token](dt)

        # Timezone
        if token in ["ZZ", "Z"]:
            if dt.tzinfo is None:
                return ""

            separator = ":" if token == "Z" else ""
            offset = dt.utcoffset() or datetime.timedelta()
            minutes = offset.total_seconds() / 60

            sign = "+" if minutes >= 0 else "-"

            hour, minute = divmod(abs(int(minutes)), 60)

            return f"{sign}{hour:02d}{separator}{minute:02d}"

        return token

    def _format_localizable_token(
        self, dt: pendulum.DateTime, token: str, locale: Locale
    ) -> str:
        """
        Formats a DateTime instance
        with a given localizable token and locale.

        :param dt: The instance to format
        :param token: The token to use
        :param locale: The locale to use
        """
        if token == "MMM":
            return cast(str, locale.get("translations.months.abbreviated")[dt.month])
        elif token == "MMMM":
            return cast(str, locale.get("translations.months.wide")[dt.month])
        elif token == "dd":
            return cast(str, locale.get("translations.days.short")[dt.day_of_week])
        elif token == "ddd":
            return cast(
                str,
                locale.get("translations.days.abbreviated")[dt.day_of_week],
            )
        elif token == "dddd":
            return cast(str, locale.get("translations.days.wide")[dt.day_of_week])
        elif token == "e":
            first_day = cast(int, locale.get("translations.week_data.first_day"))

            return str((dt.day_of_week % 7 - first_day) % 7)
        elif token == "Do":
            return locale.ordinalize(dt.day)
        elif token == "do":
            return locale.ordinalize((dt.day_of_week + 1) % 7)
        elif token == "Mo":
            return locale.ordinalize(dt.month)
        elif token == "Qo":
            return locale.ordinalize(dt.quarter)
        elif token == "wo":
            return locale.ordinalize(dt.week_of_year)
        elif token == "DDDo":
            return locale.ordinalize(dt.day_of_year)
        elif token == "eo":
            first_day = cast(int, locale.get("translations.week_data.first_day"))

            return locale.ordinalize((dt.day_of_week % 7 - first_day) % 7 + 1)
        elif token == "A":
            key = "translations.day_periods"
            if dt.hour >= 12:
                key += ".pm"
            else:
                key += ".am"

            return cast(str, locale.get(key))
        else:
            return token

    def parse(
        self,
        time: str,
        fmt: str,
        now: pendulum.DateTime,
        locale: str | None = None,
    ) -> dict[str, Any]:
        """
        Parses a time string matching a given format as a tuple.

        :param time: The timestring
        :param fmt: The format
        :param now: The datetime to use as "now"
        :param locale: The locale to use

        :return: The parsed elements
        """
        escaped_fmt = re.escape(fmt)

        tokens = self._FROM_FORMAT_RE.findall(escaped_fmt)
        if not tokens:
            raise ValueError("The given time string does not match the given format")

        if not locale:
            locale = pendulum.get_locale()

        loaded_locale: Locale = Locale.load(locale)

        parsed = {
            "year": None,
            "month": None,
            "day": None,
            "hour": None,
            "minute": None,
            "second": None,
            "microsecond": None,
            "tz": None,
            "quarter": None,
            "day_of_week": None,
            "day_of_year": None,
            "meridiem": None,
            "timestamp": None,
        }

        pattern = self._FROM_FORMAT_RE.sub(
            lambda m: self._replace_tokens(m.group(0), loaded_locale), escaped_fmt
        )

        if not re.search("^" + pattern + "$", time):
            raise ValueError(f"String does not match format {fmt}")

        def _get_parsed_values(m: Match[str]) -> Any:
            return self._get_parsed_values(m, parsed, loaded_locale, now)

        re.sub(pattern, _get_parsed_values, time)

        return self._check_parsed(parsed, now)

    def _check_parsed(
        self, parsed: dict[str, Any], now: pendulum.DateTime
    ) -> dict[str, Any]:
        """
        Checks validity of parsed elements.

        :param parsed: The elements to parse.

        :return: The validated elements.
        """
        validated: dict[str, int | Timezone | None] = {
            "year": parsed["year"],
            "month": parsed["month"],
            "day": parsed["day"],
            "hour": parsed["hour"],
            "minute": parsed["minute"],
            "second": parsed["second"],
            "microsecond": parsed["microsecond"],
            "tz": None,
        }

        # If timestamp has been specified
        # we use it and don't go any further
        if parsed["timestamp"] is not None:
            str_us = str(parsed["timestamp"])
            if "." in str_us:
                microseconds = int(f'{str_us.split(".")[1].ljust(6, "0")}')
            else:
                microseconds = 0

            from pendulum.helpers import local_time

            time = local_time(parsed["timestamp"], 0, microseconds)
            validated["year"] = time[0]
            validated["month"] = time[1]
            validated["day"] = time[2]
            validated["hour"] = time[3]
            validated["minute"] = time[4]
            validated["second"] = time[5]
            validated["microsecond"] = time[6]

            return validated

        if parsed["quarter"] is not None:
            if validated["year"] is not None:
                dt = pendulum.datetime(cast(int, validated["year"]), 1, 1)
            else:
                dt = now

            dt = dt.start_of("year")

            while dt.quarter != parsed["quarter"]:
                dt = dt.add(months=3)

            validated["year"] = dt.year
            validated["month"] = dt.month
            validated["day"] = dt.day

        if validated["year"] is None:
            validated["year"] = now.year

        if parsed["day_of_year"] is not None:
            dt = cast(
                pendulum.DateTime,
                pendulum.parse(f'{validated["year"]}-{parsed["day_of_year"]:>03d}'),
            )

            validated["month"] = dt.month
            validated["day"] = dt.day

        if parsed["day_of_week"] is not None:
            dt = pendulum.datetime(
                cast(int, validated["year"]),
                cast(int, validated["month"]) or now.month,
                cast(int, validated["day"]) or now.day,
            )
            dt = dt.start_of("week").subtract(days=1)
            dt = dt.next(parsed["day_of_week"])
            validated["year"] = dt.year
            validated["month"] = dt.month
            validated["day"] = dt.day

        # Meridiem
        if parsed["meridiem"] is not None:
            # If the time is greater than 13:00:00
            # This is not valid
            if validated["hour"] is None:
                raise ValueError("Invalid Date")

            t = (
                validated["hour"],
                validated["minute"],
                validated["second"],
                validated["microsecond"],
            )
            if t >= (13, 0, 0, 0):
                raise ValueError("Invalid date")

            pm = parsed["meridiem"] == "pm"
            validated["hour"] %= 12  # type: ignore[operator]
            if pm:
                validated["hour"] += 12  # type: ignore[operator]

        if validated["month"] is None:
            if parsed["year"] is not None:
                validated["month"] = parsed["month"] or 1
            else:
                validated["month"] = parsed["month"] or now.month

        if validated["day"] is None:
            if parsed["year"] is not None or parsed["month"] is not None:
                validated["day"] = parsed["day"] or 1
            else:
                validated["day"] = parsed["day"] or now.day

        for part in ["hour", "minute", "second", "microsecond"]:
            if validated[part] is None:
                validated[part] = 0

        validated["tz"] = parsed["tz"]

        return validated

    def _get_parsed_values(
        self,
        m: Match[str],
        parsed: dict[str, Any],
        locale: Locale,
        now: pendulum.DateTime,
    ) -> None:
        for token, index in m.re.groupindex.items():
            if token in self._LOCALIZABLE_TOKENS:
                self._get_parsed_locale_value(token, m.group(index), parsed, locale)
            else:
                self._get_parsed_value(token, m.group(index), parsed, now)

    def _get_parsed_value(
        self,
        token: str,
        value: str,
        parsed: dict[str, Any],
        now: pendulum.DateTime,
    ) -> None:
        parsed_token = self._PARSE_TOKENS[token](value)

        if "Y" in token:
            if token == "YY":
                if parsed_token <= 68:
                    parsed_token += 2000
                else:
                    parsed_token += 1900

            parsed["year"] = parsed_token
        elif token == "Q":
            parsed["quarter"] = parsed_token
        elif token in ["MM", "M"]:
            parsed["month"] = parsed_token
        elif token in ["DDDD", "DDD"]:
            parsed["day_of_year"] = parsed_token
        elif "D" in token:
            parsed["day"] = parsed_token
        elif "H" in token:
            parsed["hour"] = parsed_token
        elif token in ["hh", "h"]:
            if parsed_token > 12:
                raise ValueError("Invalid date")

            parsed["hour"] = parsed_token
        elif "m" in token:
            parsed["minute"] = parsed_token
        elif "s" in token:
            parsed["second"] = parsed_token
        elif "S" in token:
            parsed["microsecond"] = parsed_token
        elif token in ["d", "E"]:
            parsed["day_of_week"] = parsed_token
        elif token in ["X", "x"]:
            parsed["timestamp"] = parsed_token
        elif token in ["ZZ", "Z"]:
            negative = bool(value.startswith("-"))
            tz = value[1:]
            if ":" not in tz:
                if len(tz) == 2:
                    tz = f"{tz}00"

                off_hour = tz[0:2]
                off_minute = tz[2:4]
            else:
                off_hour, off_minute = tz.split(":")

            offset = ((int(off_hour) * 60) + int(off_minute)) * 60

            if negative:
                offset = -1 * offset

            parsed["tz"] = pendulum.timezone(offset)
        elif token == "z":
            # Full timezone
            if value not in pendulum.timezones():
                raise ValueError("Invalid date")

            parsed["tz"] = pendulum.timezone(value)

    def _get_parsed_locale_value(
        self, token: str, value: str, parsed: dict[str, Any], locale: Locale
    ) -> None:
        if token == "MMMM":
            unit = "month"
            match = "months.wide"
        elif token == "MMM":
            unit = "month"
            match = "months.abbreviated"
        elif token == "Do":
            parsed["day"] = int(cast(Match[str], re.match(r"(\d+)", value)).group(1))

            return
        elif token == "dddd":
            unit = "day_of_week"
            match = "days.wide"
        elif token == "ddd":
            unit = "day_of_week"
            match = "days.abbreviated"
        elif token == "dd":
            unit = "day_of_week"
            match = "days.short"
        elif token in ["a", "A"]:
            valid_values = [
                locale.translation("day_periods.am"),
                locale.translation("day_periods.pm"),
            ]

            if token == "a":
                value = value.lower()
                valid_values = [x.lower() for x in valid_values]

            if value not in valid_values:
                raise ValueError("Invalid date")

            parsed["meridiem"] = ["am", "pm"][valid_values.index(value)]

            return
        else:
            raise ValueError(f'Invalid token "{token}"')

        parsed[unit] = locale.match_translation(match, value)
        if value is None:
            raise ValueError("Invalid date")

    def _replace_tokens(self, token: str, locale: Locale) -> str:
        if token.startswith("[") and token.endswith("]"):
            return token[1:-1]
        elif token.startswith("\\"):
            if len(token) == 2 and token[1] in {"[", "]"}:
                return ""

            return token
        elif token not in self._REGEX_TOKENS and token not in self._LOCALIZABLE_TOKENS:
            raise ValueError(f"Unsupported token: {token}")

        if token in self._LOCALIZABLE_TOKENS:
            values = self._LOCALIZABLE_TOKENS[token]
            if callable(values):
                candidates = values(locale)
            else:
                candidates = tuple(
                    locale.translation(
                        cast(str, self._LOCALIZABLE_TOKENS[token])
                    ).values()
                )
        else:
            candidates = cast(Sequence[str], self._REGEX_TOKENS[token])

        if not candidates:
            raise ValueError(f"Unsupported token: {token}")

        if not isinstance(candidates, tuple):
            candidates = (cast(str, candidates),)

        pattern = f'(?P<{token}>{"|".join(candidates)})'

        return pattern
