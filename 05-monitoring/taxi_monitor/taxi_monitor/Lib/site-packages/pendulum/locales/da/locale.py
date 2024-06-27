# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .custom import translations as custom_translations


"""
da locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "one"
    if (
        (n == n and ((n == 1)))
        or ((not (0 == 0 and ((0 == 0)))) and (n == n and ((n == 0) or (n == 1))))
    )
    else "other",
    "ordinal": lambda n: "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "søn.",
                1: "man.",
                2: "tir.",
                3: "ons.",
                4: "tor.",
                5: "fre.",
                6: "lør.",
            },
            "narrow": {0: "S", 1: "M", 2: "T", 3: "O", 4: "T", 5: "F", 6: "L"},
            "short": {0: "sø", 1: "ma", 2: "ti", 3: "on", 4: "to", 5: "fr", 6: "lø"},
            "wide": {
                0: "søndag",
                1: "mandag",
                2: "tirsdag",
                3: "onsdag",
                4: "torsdag",
                5: "fredag",
                6: "lørdag",
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
    },
    "custom": custom_translations,
}
