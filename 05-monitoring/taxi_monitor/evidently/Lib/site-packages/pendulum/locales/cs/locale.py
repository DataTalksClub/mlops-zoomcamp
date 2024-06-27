from __future__ import annotations

from pendulum.locales.cs.custom import translations as custom_translations


"""
cs locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "few"
    if ((n == n and (n >= 2 and n <= 4)) and (0 == 0 and (0 == 0)))
    else "many"
    if (not (0 == 0 and (0 == 0)))
    else "one"
    if ((n == n and (n == 1)) and (0 == 0 and (0 == 0)))
    else "other",
    "ordinal": lambda n: "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "po",
                1: "út",
                2: "st",
                3: "čt",
                4: "pá",
                5: "so",
                6: "ne",
            },
            "narrow": {
                0: "P",
                1: "Ú",
                2: "S",
                3: "Č",
                4: "P",
                5: "S",
                6: "N",
            },
            "short": {
                0: "po",
                1: "út",
                2: "st",
                3: "čt",
                4: "pá",
                5: "so",
                6: "ne",
            },
            "wide": {
                0: "pondělí",
                1: "úterý",
                2: "středa",
                3: "čtvrtek",
                4: "pátek",
                5: "sobota",
                6: "neděle",
            },
        },
        "months": {
            "abbreviated": {
                1: "led",
                2: "úno",
                3: "bře",
                4: "dub",
                5: "kvě",
                6: "čvn",
                7: "čvc",
                8: "srp",
                9: "zář",
                10: "říj",
                11: "lis",
                12: "pro",
            },
            "narrow": {
                1: "1",
                2: "2",
                3: "3",
                4: "4",
                5: "5",
                6: "6",
                7: "7",
                8: "8",
                9: "9",
                10: "10",
                11: "11",
                12: "12",
            },
            "wide": {
                1: "ledna",
                2: "února",
                3: "března",
                4: "dubna",
                5: "května",
                6: "června",
                7: "července",
                8: "srpna",
                9: "září",
                10: "října",
                11: "listopadu",
                12: "prosince",
            },
        },
        "units": {
            "year": {
                "one": "{0} rok",
                "few": "{0} roky",
                "many": "{0} roku",
                "other": "{0} let",
            },
            "month": {
                "one": "{0} měsíc",
                "few": "{0} měsíce",
                "many": "{0} měsíce",
                "other": "{0} měsíců",
            },
            "week": {
                "one": "{0} týden",
                "few": "{0} týdny",
                "many": "{0} týdne",
                "other": "{0} týdnů",
            },
            "day": {
                "one": "{0} den",
                "few": "{0} dny",
                "many": "{0} dne",
                "other": "{0} dní",
            },
            "hour": {
                "one": "{0} hodina",
                "few": "{0} hodiny",
                "many": "{0} hodiny",
                "other": "{0} hodin",
            },
            "minute": {
                "one": "{0} minuta",
                "few": "{0} minuty",
                "many": "{0} minuty",
                "other": "{0} minut",
            },
            "second": {
                "one": "{0} sekunda",
                "few": "{0} sekundy",
                "many": "{0} sekundy",
                "other": "{0} sekund",
            },
            "microsecond": {
                "one": "{0} mikrosekunda",
                "few": "{0} mikrosekundy",
                "many": "{0} mikrosekundy",
                "other": "{0} mikrosekund",
            },
        },
        "relative": {
            "year": {
                "future": {
                    "other": "za {0} let",
                    "one": "za {0} rok",
                    "few": "za {0} roky",
                    "many": "za {0} roku",
                },
                "past": {
                    "other": "před {0} lety",
                    "one": "před {0} rokem",
                    "few": "před {0} lety",
                    "many": "před {0} roku",
                },
            },
            "month": {
                "future": {
                    "other": "za {0} měsíců",
                    "one": "za {0} měsíc",
                    "few": "za {0} měsíce",
                    "many": "za {0} měsíce",
                },
                "past": {
                    "other": "před {0} měsíci",
                    "one": "před {0} měsícem",
                    "few": "před {0} měsíci",
                    "many": "před {0} měsíce",
                },
            },
            "week": {
                "future": {
                    "other": "za {0} týdnů",
                    "one": "za {0} týden",
                    "few": "za {0} týdny",
                    "many": "za {0} týdne",
                },
                "past": {
                    "other": "před {0} týdny",
                    "one": "před {0} týdnem",
                    "few": "před {0} týdny",
                    "many": "před {0} týdne",
                },
            },
            "day": {
                "future": {
                    "other": "za {0} dní",
                    "one": "za {0} den",
                    "few": "za {0} dny",
                    "many": "za {0} dne",
                },
                "past": {
                    "other": "před {0} dny",
                    "one": "před {0} dnem",
                    "few": "před {0} dny",
                    "many": "před {0} dne",
                },
            },
            "hour": {
                "future": {
                    "other": "za {0} hodin",
                    "one": "za {0} hodinu",
                    "few": "za {0} hodiny",
                    "many": "za {0} hodiny",
                },
                "past": {
                    "other": "před {0} hodinami",
                    "one": "před {0} hodinou",
                    "few": "před {0} hodinami",
                    "many": "před {0} hodiny",
                },
            },
            "minute": {
                "future": {
                    "other": "za {0} minut",
                    "one": "za {0} minutu",
                    "few": "za {0} minuty",
                    "many": "za {0} minuty",
                },
                "past": {
                    "other": "před {0} minutami",
                    "one": "před {0} minutou",
                    "few": "před {0} minutami",
                    "many": "před {0} minuty",
                },
            },
            "second": {
                "future": {
                    "other": "za {0} sekund",
                    "one": "za {0} sekundu",
                    "few": "za {0} sekundy",
                    "many": "za {0} sekundy",
                },
                "past": {
                    "other": "před {0} sekundami",
                    "one": "před {0} sekundou",
                    "few": "před {0} sekundami",
                    "many": "před {0} sekundy",
                },
            },
        },
        "day_periods": {
            "midnight": "půlnoc",
            "am": "dop.",
            "noon": "poledne",
            "pm": "odp.",
            "morning1": "ráno",
            "morning2": "dopoledne",
            "afternoon1": "odpoledne",
            "evening1": "večer",
            "night1": "v noci",
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
