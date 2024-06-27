from __future__ import annotations

from pendulum.locales.nl.custom import translations as custom_translations


"""
nl locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "one"
    if ((n == n and (n == 1)) and (0 == 0 and (0 == 0)))
    else "other",
    "ordinal": lambda n: "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "ma",
                1: "di",
                2: "wo",
                3: "do",
                4: "vr",
                5: "za",
                6: "zo",
            },
            "narrow": {0: "M", 1: "D", 2: "W", 3: "D", 4: "V", 5: "Z", 6: "Z"},
            "short": {0: "ma", 1: "di", 2: "wo", 3: "do", 4: "vr", 5: "za", 6: "zo"},
            "wide": {
                0: "maandag",
                1: "dinsdag",
                2: "woensdag",
                3: "donderdag",
                4: "vrijdag",
                5: "zaterdag",
                6: "zondag",
            },
        },
        "months": {
            "abbreviated": {
                1: "jan.",
                2: "feb.",
                3: "mrt.",
                4: "apr.",
                5: "mei",
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
                1: "januari",
                2: "februari",
                3: "maart",
                4: "april",
                5: "mei",
                6: "juni",
                7: "juli",
                8: "augustus",
                9: "september",
                10: "oktober",
                11: "november",
                12: "december",
            },
        },
        "units": {
            "year": {"one": "{0} jaar", "other": "{0} jaar"},
            "month": {"one": "{0} maand", "other": "{0} maanden"},
            "week": {"one": "{0} week", "other": "{0} weken"},
            "day": {"one": "{0} dag", "other": "{0} dagen"},
            "hour": {"one": "{0} uur", "other": "{0} uur"},
            "minute": {"one": "{0} minuut", "other": "{0} minuten"},
            "second": {"one": "{0} seconde", "other": "{0} seconden"},
            "microsecond": {"one": "{0} microseconde", "other": "{0} microseconden"},
        },
        "relative": {
            "year": {
                "future": {"other": "over {0} jaar", "one": "over {0} jaar"},
                "past": {"other": "{0} jaar geleden", "one": "{0} jaar geleden"},
            },
            "month": {
                "future": {"other": "over {0} maanden", "one": "over {0} maand"},
                "past": {"other": "{0} maanden geleden", "one": "{0} maand geleden"},
            },
            "week": {
                "future": {"other": "over {0} weken", "one": "over {0} week"},
                "past": {"other": "{0} weken geleden", "one": "{0} week geleden"},
            },
            "day": {
                "future": {"other": "over {0} dagen", "one": "over {0} dag"},
                "past": {"other": "{0} dagen geleden", "one": "{0} dag geleden"},
            },
            "hour": {
                "future": {"other": "over {0} uur", "one": "over {0} uur"},
                "past": {"other": "{0} uur geleden", "one": "{0} uur geleden"},
            },
            "minute": {
                "future": {"other": "over {0} minuten", "one": "over {0} minuut"},
                "past": {"other": "{0} minuten geleden", "one": "{0} minuut geleden"},
            },
            "second": {
                "future": {"other": "over {0} seconden", "one": "over {0} seconde"},
                "past": {"other": "{0} seconden geleden", "one": "{0} seconde geleden"},
            },
        },
        "day_periods": {
            "midnight": "middernacht",
            "am": "a.m.",
            "pm": "p.m.",
            "morning1": "‘s ochtends",
            "afternoon1": "‘s middags",
            "evening1": "‘s avonds",
            "night1": "‘s nachts",
            "week_data": {
                "min_days": 1,
                "first_day": 0,
                "weekend_start": 5,
                "weekend_end": 6,
            },
        },
    },
    "custom": custom_translations,
}
