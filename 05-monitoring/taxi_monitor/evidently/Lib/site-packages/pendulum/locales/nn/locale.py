from __future__ import annotations

from pendulum.locales.nn.custom import translations as custom_translations


"""
nn locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "one" if (n == n and (n == 1)) else "other",
    "ordinal": lambda n: "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "mån.",
                1: "tys.",
                2: "ons.",
                3: "tor.",
                4: "fre.",
                5: "lau.",
                6: "søn.",
            },
            "narrow": {0: "M", 1: "T", 2: "O", 3: "T", 4: "F", 5: "L", 6: "S"},
            "short": {
                0: "må.",
                1: "ty.",
                2: "on.",
                3: "to.",
                4: "fr.",
                5: "la.",
                6: "sø.",
            },
            "wide": {
                0: "måndag",
                1: "tysdag",
                2: "onsdag",
                3: "torsdag",
                4: "fredag",
                5: "laurdag",
                6: "søndag",
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
        "week_data": {
            "min_days": 1,
            "first_day": 0,
            "weekend_start": 5,
            "weekend_end": 6,
        },
    },
    "custom": custom_translations,
}
