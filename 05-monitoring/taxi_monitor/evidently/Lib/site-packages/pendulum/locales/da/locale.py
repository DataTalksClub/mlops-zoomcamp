from __future__ import annotations

from pendulum.locales.da.custom import translations as custom_translations


"""
da locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "one"
    if (
        (n == n and (n == 1))
        or ((not (0 == 0 and (0 == 0))) and (n == n and ((n == 0) or (n == 1))))
    )
    else "other",
    "ordinal": lambda n: "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "man.",
                1: "tir.",
                2: "ons.",
                3: "tor.",
                4: "fre.",
                5: "lør.",
                6: "søn.",
            },
            "narrow": {0: "M", 1: "T", 2: "O", 3: "T", 4: "F", 5: "L", 6: "S"},
            "short": {0: "ma", 1: "ti", 2: "on", 3: "to", 4: "fr", 5: "lø", 6: "sø"},
            "wide": {
                0: "mandag",
                1: "tirsdag",
                2: "onsdag",
                3: "torsdag",
                4: "fredag",
                5: "lørdag",
                6: "søndag",
            },
        },
        "months": {
            "abbreviated": {
                1: "jan.",
                2: "feb.",
                3: "mar.",
                4: "apr.",
                5: "maj",
                6: "jun.",
                7: "jul.",
                8: "aug.",
                9: "sep.",
                10: "okt.",
                11: "nov.",
                12: "dec.",
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
                1: "januar",
                2: "februar",
                3: "marts",
                4: "april",
                5: "maj",
                6: "juni",
                7: "juli",
                8: "august",
                9: "september",
                10: "oktober",
                11: "november",
                12: "december",
            },
        },
        "units": {
            "year": {"one": "{0} år", "other": "{0} år"},
            "month": {"one": "{0} måned", "other": "{0} måneder"},
            "week": {"one": "{0} uge", "other": "{0} uger"},
            "day": {"one": "{0} dag", "other": "{0} dage"},
            "hour": {"one": "{0} time", "other": "{0} timer"},
            "minute": {"one": "{0} minut", "other": "{0} minutter"},
            "second": {"one": "{0} sekund", "other": "{0} sekunder"},
            "microsecond": {"one": "{0} mikrosekund", "other": "{0} mikrosekunder"},
        },
        "relative": {
            "year": {
                "future": {"other": "om {0} år", "one": "om {0} år"},
                "past": {"other": "for {0} år siden", "one": "for {0} år siden"},
            },
            "month": {
                "future": {"other": "om {0} måneder", "one": "om {0} måned"},
                "past": {
                    "other": "for {0} måneder siden",
                    "one": "for {0} måned siden",
                },
            },
            "week": {
                "future": {"other": "om {0} uger", "one": "om {0} uge"},
                "past": {"other": "for {0} uger siden", "one": "for {0} uge siden"},
            },
            "day": {
                "future": {"other": "om {0} dage", "one": "om {0} dag"},
                "past": {"other": "for {0} dage siden", "one": "for {0} dag siden"},
            },
            "hour": {
                "future": {"other": "om {0} timer", "one": "om {0} time"},
                "past": {"other": "for {0} timer siden", "one": "for {0} time siden"},
            },
            "minute": {
                "future": {"other": "om {0} minutter", "one": "om {0} minut"},
                "past": {
                    "other": "for {0} minutter siden",
                    "one": "for {0} minut siden",
                },
            },
            "second": {
                "future": {"other": "om {0} sekunder", "one": "om {0} sekund"},
                "past": {
                    "other": "for {0} sekunder siden",
                    "one": "for {0} sekund siden",
                },
            },
        },
        "day_periods": {
            "midnight": "midnat",
            "am": "AM",
            "pm": "PM",
            "morning1": "om morgenen",
            "morning2": "om formiddagen",
            "afternoon1": "om eftermiddagen",
            "evening1": "om aftenen",
            "night1": "om natten",
        },
        "week_data": {
            "min_days": 1,
            "first_day": 0,
            "weekend_start": 5,
            "weekend_end": 6,
        },
    },
    "custom": custom_translations,
}
