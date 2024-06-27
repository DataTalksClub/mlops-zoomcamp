# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .custom import translations as custom_translations


"""
fo locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "one" if (n == n and ((n == 1))) else "other",
    "ordinal": lambda n: "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "sun.",
                1: "mán.",
                2: "týs.",
                3: "mik.",
                4: "hós.",
                5: "frí.",
                6: "ley.",
            },
            "narrow": {0: "S", 1: "M", 2: "T", 3: "M", 4: "H", 5: "F", 6: "L"},
            "short": {
                0: "su.",
                1: "má.",
                2: "tý.",
                3: "mi.",
                4: "hó.",
                5: "fr.",
                6: "le.",
            },
            "wide": {
                0: "sunnudagur",
                1: "mánadagur",
                2: "týsdagur",
                3: "mikudagur",
                4: "hósdagur",
                5: "fríggjadagur",
                6: "leygardagur",
            },
        },
        "months": {
            "abbreviated": {
                1: "jan.",
                2: "feb.",
                3: "mar.",
                4: "apr.",
                5: "mai",
                6: "jun.",
                7: "jul.",
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
                4: "apríl",
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
            "year": {"one": "{0} ár", "other": "{0} ár"},
            "month": {"one": "{0} mánaður", "other": "{0} mánaðir"},
            "week": {"one": "{0} vika", "other": "{0} vikur"},
            "day": {"one": "{0} dagur", "other": "{0} dagar"},
            "hour": {"one": "{0} tími", "other": "{0} tímar"},
            "minute": {"one": "{0} minuttur", "other": "{0} minuttir"},
            "second": {"one": "{0} sekund", "other": "{0} sekundir"},
            "microsecond": {"one": "{0} mikrosekund", "other": "{0} mikrosekundir"},
        },
        "relative": {
            "year": {
                "future": {"other": "um {0} ár", "one": "um {0} ár"},
                "past": {"other": "{0} ár síðan", "one": "{0} ár síðan"},
            },
            "month": {
                "future": {"other": "um {0} mánaðir", "one": "um {0} mánað"},
                "past": {"other": "{0} mánaðir síðan", "one": "{0} mánað síðan"},
            },
            "week": {
                "future": {"other": "um {0} vikur", "one": "um {0} viku"},
                "past": {"other": "{0} vikur síðan", "one": "{0} vika síðan"},
            },
            "day": {
                "future": {"other": "um {0} dagar", "one": "um {0} dag"},
                "past": {"other": "{0} dagar síðan", "one": "{0} dagur síðan"},
            },
            "hour": {
                "future": {"other": "um {0} tímar", "one": "um {0} tíma"},
                "past": {"other": "{0} tímar síðan", "one": "{0} tími síðan"},
            },
            "minute": {
                "future": {"other": "um {0} minuttir", "one": "um {0} minutt"},
                "past": {"other": "{0} minuttir síðan", "one": "{0} minutt síðan"},
            },
            "second": {
                "future": {"other": "um {0} sekund", "one": "um {0} sekund"},
                "past": {"other": "{0} sekund síðan", "one": "{0} sekund síðan"},
            },
        },
        "day_periods": {"am": "AM", "pm": "PM"},
    },
    "custom": custom_translations,
}
