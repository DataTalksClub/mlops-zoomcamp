from __future__ import annotations

from pendulum.locales.en_gb.custom import translations as custom_translations


"""
en-gb locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "one"
    if ((n == n and (n == 1)) and (0 == 0 and (0 == 0)))
    else "other",
    "ordinal": lambda n: "few"
    if (
        ((n % 10) == (n % 10) and ((n % 10) == 3))
        and (not ((n % 100) == (n % 100) and ((n % 100) == 13)))
    )
    else "one"
    if (
        ((n % 10) == (n % 10) and ((n % 10) == 1))
        and (not ((n % 100) == (n % 100) and ((n % 100) == 11)))
    )
    else "two"
    if (
        ((n % 10) == (n % 10) and ((n % 10) == 2))
        and (not ((n % 100) == (n % 100) and ((n % 100) == 12)))
    )
    else "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "Mon",
                1: "Tue",
                2: "Wed",
                3: "Thu",
                4: "Fri",
                5: "Sat",
                6: "Sun",
            },
            "narrow": {
                0: "M",
                1: "T",
                2: "W",
                3: "T",
                4: "F",
                5: "S",
                6: "S",
            },
            "short": {
                0: "Mo",
                1: "Tu",
                2: "We",
                3: "Th",
                4: "Fr",
                5: "Sa",
                6: "Su",
            },
            "wide": {
                0: "Monday",
                1: "Tuesday",
                2: "Wednesday",
                3: "Thursday",
                4: "Friday",
                5: "Saturday",
                6: "Sunday",
            },
        },
        "months": {
            "abbreviated": {
                1: "Jan",
                2: "Feb",
                3: "Mar",
                4: "Apr",
                5: "May",
                6: "Jun",
                7: "Jul",
                8: "Aug",
                9: "Sept",
                10: "Oct",
                11: "Nov",
                12: "Dec",
            },
            "narrow": {
                1: "J",
                2: "F",
                3: "M",
                4: "A",
                5: "M",
                6: "J",
                7: "J",
                8: "A",
                9: "S",
                10: "O",
                11: "N",
                12: "D",
            },
            "wide": {
                1: "January",
                2: "February",
                3: "March",
                4: "April",
                5: "May",
                6: "June",
                7: "July",
                8: "August",
                9: "September",
                10: "October",
                11: "November",
                12: "December",
            },
        },
        "units": {
            "year": {
                "one": "{0} year",
                "other": "{0} years",
            },
            "month": {
                "one": "{0} month",
                "other": "{0} months",
            },
            "week": {
                "one": "{0} week",
                "other": "{0} weeks",
            },
            "day": {
                "one": "{0} day",
                "other": "{0} days",
            },
            "hour": {
                "one": "{0} hour",
                "other": "{0} hours",
            },
            "minute": {
                "one": "{0} minute",
                "other": "{0} minutes",
            },
            "second": {
                "one": "{0} second",
                "other": "{0} seconds",
            },
            "microsecond": {
                "one": "{0} microsecond",
                "other": "{0} microseconds",
            },
        },
        "relative": {
            "year": {
                "future": {
                    "other": "in {0} years",
                    "one": "in {0} year",
                },
                "past": {
                    "other": "{0} years ago",
                    "one": "{0} year ago",
                },
            },
            "month": {
                "future": {
                    "other": "in {0} months",
                    "one": "in {0} month",
                },
                "past": {
                    "other": "{0} months ago",
                    "one": "{0} month ago",
                },
            },
            "week": {
                "future": {
                    "other": "in {0} weeks",
                    "one": "in {0} week",
                },
                "past": {
                    "other": "{0} weeks ago",
                    "one": "{0} week ago",
                },
            },
            "day": {
                "future": {
                    "other": "in {0} days",
                    "one": "in {0} day",
                },
                "past": {
                    "other": "{0} days ago",
                    "one": "{0} day ago",
                },
            },
            "hour": {
                "future": {
                    "other": "in {0} hours",
                    "one": "in {0} hour",
                },
                "past": {
                    "other": "{0} hours ago",
                    "one": "{0} hour ago",
                },
            },
            "minute": {
                "future": {
                    "other": "in {0} minutes",
                    "one": "in {0} minute",
                },
                "past": {
                    "other": "{0} minutes ago",
                    "one": "{0} minute ago",
                },
            },
            "second": {
                "future": {
                    "other": "in {0} seconds",
                    "one": "in {0} second",
                },
                "past": {
                    "other": "{0} seconds ago",
                    "one": "{0} second ago",
                },
            },
        },
        "day_periods": {
            "midnight": "midnight",
            "am": "am",
            "noon": "noon",
            "pm": "pm",
            "morning1": "in the morning",
            "afternoon1": "in the afternoon",
            "evening1": "in the evening",
            "night1": "at night",
        },
        "week_data": {
            "min_days": 4,
            "first_day": 0,
            "weekend_start": 5,
            "weekend_end": 6,
        },
    },
    "custom": custom_translations,
}
