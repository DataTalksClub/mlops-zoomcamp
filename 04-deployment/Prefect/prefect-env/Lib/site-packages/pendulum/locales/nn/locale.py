# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .custom import translations as custom_translations


"""
nn locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "one" if (n == n and ((n == 1))) else "other",
    "ordinal": lambda n: "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "søn.",
                1: "mån.",
                2: "tys.",
                3: "ons.",
                4: "tor.",
                5: "fre.",
                6: "lau.",
            },
            "narrow": {0: "S", 1: "M", 2: "T", 3: "O", 4: "T", 5: "F", 6: "L"},
            "short": {
                0: "sø.",
                1: "må.",
                2: "ty.",
                3: "on.",
                4: "to.",
                5: "fr.",
                6: "la.",
            },
            "wide": {
                0: "søndag",
                1: "måndag",
                2: "tysdag",
                3: "onsdag",
                4: "torsdag",
                5: "fredag",
                6: "laurdag",
            },
        },
        "months": {
            "abbreviated": {
                1: "jan.",
                2: "feb.",
                3: "mars",
                4: "apr.",
                5: "mai",
                6: "juni",
                7: "juli",
                8: "aug.",
                9: "sep.",
                10: "okt.",
                11: "nov.",
                12: "des.",
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
                3: "mars",
                4: "april",
                5: "mai",
                6: "juni",
                7: "juli",
                8: "august",
                9: "september",
                10: "oktober",
                11: "november",
                12: "desember",
            },
        },
        "units": {
            "year": {"one": "{0} år", "other": "{0} år"},
            "month": {"one": "{0} månad", "other": "{0} månadar"},
            "week": {"one": "{0} veke", "other": "{0} veker"},
            "day": {"one": "{0} dag", "other": "{0} dagar"},
            "hour": {"one": "{0} time", "other": "{0} timar"},
            "minute": {"one": "{0} minutt", "other": "{0} minutt"},
            "second": {"one": "{0} sekund", "other": "{0} sekund"},
            "microsecond": {"one": "{0} mikrosekund", "other": "{0} mikrosekund"},
        },
        "relative": {
            "year": {
                "future": {"other": "om {0} år", "one": "om {0} år"},
                "past": {"other": "for {0} år sidan", "one": "for {0} år sidan"},
            },
            "month": {
                "future": {"other": "om {0} månadar", "one": "om {0} månad"},
                "past": {
                    "other": "for {0} månadar sidan",
                    "one": "for {0} månad sidan",
                },
            },
            "week": {
                "future": {"other": "om {0} veker", "one": "om {0} veke"},
                "past": {"other": "for {0} veker sidan", "one": "for {0} veke sidan"},
            },
            "day": {
                "future": {"other": "om {0} dagar", "one": "om {0} dag"},
                "past": {"other": "for {0} dagar sidan", "one": "for {0} dag sidan"},
            },
            "hour": {
                "future": {"other": "om {0} timar", "one": "om {0} time"},
                "past": {"other": "for {0} timar sidan", "one": "for {0} time sidan"},
            },
            "minute": {
                "future": {"other": "om {0} minutt", "one": "om {0} minutt"},
                "past": {
                    "other": "for {0} minutt sidan",
                    "one": "for {0} minutt sidan",
                },
            },
            "second": {
                "future": {"other": "om {0} sekund", "one": "om {0} sekund"},
                "past": {
                    "other": "for {0} sekund sidan",
                    "one": "for {0} sekund sidan",
                },
            },
        },
        "day_periods": {"am": "formiddag", "pm": "ettermiddag"},
    },
    "custom": custom_translations,
}
