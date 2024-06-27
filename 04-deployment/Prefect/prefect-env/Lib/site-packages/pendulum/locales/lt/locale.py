# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .custom import translations as custom_translations


"""
lt locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "few"
    if (
        ((n % 10) == (n % 10) and (((n % 10) >= 2 and (n % 10) <= 9)))
        and (not ((n % 100) == (n % 100) and (((n % 100) >= 11 and (n % 100) <= 19))))
    )
    else "many"
    if (not (0 == 0 and ((0 == 0))))
    else "one"
    if (
        ((n % 10) == (n % 10) and (((n % 10) == 1)))
        and (not ((n % 100) == (n % 100) and (((n % 100) >= 11 and (n % 100) <= 19))))
    )
    else "other",
    "ordinal": lambda n: "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "sk",
                1: "pr",
                2: "an",
                3: "tr",
                4: "kt",
                5: "pn",
                6: "št",
            },
            "narrow": {0: "S", 1: "P", 2: "A", 3: "T", 4: "K", 5: "P", 6: "Š"},
            "short": {0: "Sk", 1: "Pr", 2: "An", 3: "Tr", 4: "Kt", 5: "Pn", 6: "Št"},
            "wide": {
                0: "sekmadienis",
                1: "pirmadienis",
                2: "antradienis",
                3: "trečiadienis",
                4: "ketvirtadienis",
                5: "penktadienis",
                6: "šeštadienis",
            },
        },
        "months": {
            "abbreviated": {
                1: "saus.",
                2: "vas.",
                3: "kov.",
                4: "bal.",
                5: "geg.",
                6: "birž.",
                7: "liep.",
                8: "rugp.",
                9: "rugs.",
                10: "spal.",
                11: "lapkr.",
                12: "gruod.",
            },
            "narrow": {
                1: "S",
                2: "V",
                3: "K",
                4: "B",
                5: "G",
                6: "B",
                7: "L",
                8: "R",
                9: "R",
                10: "S",
                11: "L",
                12: "G",
            },
            "wide": {
                1: "sausio",
                2: "vasario",
                3: "kovo",
                4: "balandžio",
                5: "gegužės",
                6: "birželio",
                7: "liepos",
                8: "rugpjūčio",
                9: "rugsėjo",
                10: "spalio",
                11: "lapkričio",
                12: "gruodžio",
            },
        },
        "units": {
            "year": {
                "one": "{0} metai",
                "few": "{0} metai",
                "many": "{0} metų",
                "other": "{0} metų",
            },
            "month": {
                "one": "{0} mėnuo",
                "few": "{0} mėnesiai",
                "many": "{0} mėnesio",
                "other": "{0} mėnesių",
            },
            "week": {
                "one": "{0} savaitė",
                "few": "{0} savaitės",
                "many": "{0} savaitės",
                "other": "{0} savaičių",
            },
            "day": {
                "one": "{0} diena",
                "few": "{0} dienos",
                "many": "{0} dienos",
                "other": "{0} dienų",
            },
            "hour": {
                "one": "{0} valanda",
                "few": "{0} valandos",
                "many": "{0} valandos",
                "other": "{0} valandų",
            },
            "minute": {
                "one": "{0} minutė",
                "few": "{0} minutės",
                "many": "{0} minutės",
                "other": "{0} minučių",
            },
            "second": {
                "one": "{0} sekundė",
                "few": "{0} sekundės",
                "many": "{0} sekundės",
                "other": "{0} sekundžių",
            },
            "microsecond": {
                "one": "{0} mikrosekundė",
                "few": "{0} mikrosekundės",
                "many": "{0} mikrosekundės",
                "other": "{0} mikrosekundžių",
            },
        },
        "relative": {
            "year": {
                "future": {
                    "other": "po {0} metų",
                    "one": "po {0} metų",
                    "few": "po {0} metų",
                    "many": "po {0} metų",
                },
                "past": {
                    "other": "prieš {0} metų",
                    "one": "prieš {0} metus",
                    "few": "prieš {0} metus",
                    "many": "prieš {0} metų",
                },
            },
            "month": {
                "future": {
                    "other": "po {0} mėnesių",
                    "one": "po {0} mėnesio",
                    "few": "po {0} mėnesių",
                    "many": "po {0} mėnesio",
                },
                "past": {
                    "other": "prieš {0} mėnesių",
                    "one": "prieš {0} mėnesį",
                    "few": "prieš {0} mėnesius",
                    "many": "prieš {0} mėnesio",
                },
            },
            "week": {
                "future": {
                    "other": "po {0} savaičių",
                    "one": "po {0} savaitės",
                    "few": "po {0} savaičių",
                    "many": "po {0} savaitės",
                },
                "past": {
                    "other": "prieš {0} savaičių",
                    "one": "prieš {0} savaitę",
                    "few": "prieš {0} savaites",
                    "many": "prieš {0} savaitės",
                },
            },
            "day": {
                "future": {
                    "other": "po {0} dienų",
                    "one": "po {0} dienos",
                    "few": "po {0} dienų",
                    "many": "po {0} dienos",
                },
                "past": {
                    "other": "prieš {0} dienų",
                    "one": "prieš {0} dieną",
                    "few": "prieš {0} dienas",
                    "many": "prieš {0} dienos",
                },
            },
            "hour": {
                "future": {
                    "other": "po {0} valandų",
                    "one": "po {0} valandos",
                    "few": "po {0} valandų",
                    "many": "po {0} valandos",
                },
                "past": {
                    "other": "prieš {0} valandų",
                    "one": "prieš {0} valandą",
                    "few": "prieš {0} valandas",
                    "many": "prieš {0} valandos",
                },
            },
            "minute": {
                "future": {
                    "other": "po {0} minučių",
                    "one": "po {0} minutės",
                    "few": "po {0} minučių",
                    "many": "po {0} minutės",
                },
                "past": {
                    "other": "prieš {0} minučių",
                    "one": "prieš {0} minutę",
                    "few": "prieš {0} minutes",
                    "many": "prieš {0} minutės",
                },
            },
            "second": {
                "future": {
                    "other": "po {0} sekundžių",
                    "one": "po {0} sekundės",
                    "few": "po {0} sekundžių",
                    "many": "po {0} sekundės",
                },
                "past": {
                    "other": "prieš {0} sekundžių",
                    "one": "prieš {0} sekundę",
                    "few": "prieš {0} sekundes",
                    "many": "prieš {0} sekundės",
                },
            },
        },
        "day_periods": {
            "midnight": "vidurnaktis",
            "am": "priešpiet",
            "noon": "perpiet",
            "pm": "popiet",
            "morning1": "rytas",
            "afternoon1": "popietė",
            "evening1": "vakaras",
            "night1": "naktis",
        },
    },
    "custom": custom_translations,
}
