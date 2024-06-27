# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .custom import translations as custom_translations


"""
pl locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "few"
    if (
        (
            (0 == 0 and ((0 == 0)))
            and ((n % 10) == (n % 10) and (((n % 10) >= 2 and (n % 10) <= 4)))
        )
        and (not ((n % 100) == (n % 100) and (((n % 100) >= 12 and (n % 100) <= 14))))
    )
    else "many"
    if (
        (
            (
                ((0 == 0 and ((0 == 0))) and (not (n == n and ((n == 1)))))
                and ((n % 10) == (n % 10) and (((n % 10) >= 0 and (n % 10) <= 1)))
            )
            or (
                (0 == 0 and ((0 == 0)))
                and ((n % 10) == (n % 10) and (((n % 10) >= 5 and (n % 10) <= 9)))
            )
        )
        or (
            (0 == 0 and ((0 == 0)))
            and ((n % 100) == (n % 100) and (((n % 100) >= 12 and (n % 100) <= 14)))
        )
    )
    else "one"
    if ((n == n and ((n == 1))) and (0 == 0 and ((0 == 0))))
    else "other",
    "ordinal": lambda n: "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "niedz.",
                1: "pon.",
                2: "wt.",
                3: "śr.",
                4: "czw.",
                5: "pt.",
                6: "sob.",
            },
            "narrow": {0: "n", 1: "p", 2: "w", 3: "ś", 4: "c", 5: "p", 6: "s"},
            "short": {
                0: "nie",
                1: "pon",
                2: "wto",
                3: "śro",
                4: "czw",
                5: "pią",
                6: "sob",
            },
            "wide": {
                0: "niedziela",
                1: "poniedziałek",
                2: "wtorek",
                3: "środa",
                4: "czwartek",
                5: "piątek",
                6: "sobota",
            },
        },
        "months": {
            "abbreviated": {
                1: "sty",
                2: "lut",
                3: "mar",
                4: "kwi",
                5: "maj",
                6: "cze",
                7: "lip",
                8: "sie",
                9: "wrz",
                10: "paź",
                11: "lis",
                12: "gru",
            },
            "narrow": {
                1: "s",
                2: "l",
                3: "m",
                4: "k",
                5: "m",
                6: "c",
                7: "l",
                8: "s",
                9: "w",
                10: "p",
                11: "l",
                12: "g",
            },
            "wide": {
                1: "stycznia",
                2: "lutego",
                3: "marca",
                4: "kwietnia",
                5: "maja",
                6: "czerwca",
                7: "lipca",
                8: "sierpnia",
                9: "września",
                10: "października",
                11: "listopada",
                12: "grudnia",
            },
        },
        "units": {
            "year": {
                "one": "{0} rok",
                "few": "{0} lata",
                "many": "{0} lat",
                "other": "{0} roku",
            },
            "month": {
                "one": "{0} miesiąc",
                "few": "{0} miesiące",
                "many": "{0} miesięcy",
                "other": "{0} miesiąca",
            },
            "week": {
                "one": "{0} tydzień",
                "few": "{0} tygodnie",
                "many": "{0} tygodni",
                "other": "{0} tygodnia",
            },
            "day": {
                "one": "{0} dzień",
                "few": "{0} dni",
                "many": "{0} dni",
                "other": "{0} dnia",
            },
            "hour": {
                "one": "{0} godzina",
                "few": "{0} godziny",
                "many": "{0} godzin",
                "other": "{0} godziny",
            },
            "minute": {
                "one": "{0} minuta",
                "few": "{0} minuty",
                "many": "{0} minut",
                "other": "{0} minuty",
            },
            "second": {
                "one": "{0} sekunda",
                "few": "{0} sekundy",
                "many": "{0} sekund",
                "other": "{0} sekundy",
            },
            "microsecond": {
                "one": "{0} mikrosekunda",
                "few": "{0} mikrosekundy",
                "many": "{0} mikrosekund",
                "other": "{0} mikrosekundy",
            },
        },
        "relative": {
            "year": {
                "future": {
                    "other": "za {0} roku",
                    "one": "za {0} rok",
                    "few": "za {0} lata",
                    "many": "za {0} lat",
                },
                "past": {
                    "other": "{0} roku temu",
                    "one": "{0} rok temu",
                    "few": "{0} lata temu",
                    "many": "{0} lat temu",
                },
            },
            "month": {
                "future": {
                    "other": "za {0} miesiąca",
                    "one": "za {0} miesiąc",
                    "few": "za {0} miesiące",
                    "many": "za {0} miesięcy",
                },
                "past": {
                    "other": "{0} miesiąca temu",
                    "one": "{0} miesiąc temu",
                    "few": "{0} miesiące temu",
                    "many": "{0} miesięcy temu",
                },
            },
            "week": {
                "future": {
                    "other": "za {0} tygodnia",
                    "one": "za {0} tydzień",
                    "few": "za {0} tygodnie",
                    "many": "za {0} tygodni",
                },
                "past": {
                    "other": "{0} tygodnia temu",
                    "one": "{0} tydzień temu",
                    "few": "{0} tygodnie temu",
                    "many": "{0} tygodni temu",
                },
            },
            "day": {
                "future": {
                    "other": "za {0} dnia",
                    "one": "za {0} dzień",
                    "few": "za {0} dni",
                    "many": "za {0} dni",
                },
                "past": {
                    "other": "{0} dnia temu",
                    "one": "{0} dzień temu",
                    "few": "{0} dni temu",
                    "many": "{0} dni temu",
                },
            },
            "hour": {
                "future": {
                    "other": "za {0} godziny",
                    "one": "za {0} godzinę",
                    "few": "za {0} godziny",
                    "many": "za {0} godzin",
                },
                "past": {
                    "other": "{0} godziny temu",
                    "one": "{0} godzinę temu",
                    "few": "{0} godziny temu",
                    "many": "{0} godzin temu",
                },
            },
            "minute": {
                "future": {
                    "other": "za {0} minuty",
                    "one": "za {0} minutę",
                    "few": "za {0} minuty",
                    "many": "za {0} minut",
                },
                "past": {
                    "other": "{0} minuty temu",
                    "one": "{0} minutę temu",
                    "few": "{0} minuty temu",
                    "many": "{0} minut temu",
                },
            },
            "second": {
                "future": {
                    "other": "za {0} sekundy",
                    "one": "za {0} sekundę",
                    "few": "za {0} sekundy",
                    "many": "za {0} sekund",
                },
                "past": {
                    "other": "{0} sekundy temu",
                    "one": "{0} sekundę temu",
                    "few": "{0} sekundy temu",
                    "many": "{0} sekund temu",
                },
            },
        },
        "day_periods": {
            "midnight": "o północy",
            "am": "AM",
            "noon": "w południe",
            "pm": "PM",
            "morning1": "rano",
            "morning2": "przed południem",
            "afternoon1": "po południu",
            "evening1": "wieczorem",
            "night1": "w nocy",
        },
    },
    "custom": custom_translations,
}
