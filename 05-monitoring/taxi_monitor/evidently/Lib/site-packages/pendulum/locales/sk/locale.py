from __future__ import annotations

from pendulum.locales.sk.custom import translations as custom_translations


"""
sk locale file.

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
                1: "ut",
                2: "st",
                3: "št",
                4: "pi",
                5: "so",
                6: "ne",
            },
            "narrow": {
                0: "p",
                1: "u",
                2: "s",
                3: "š",
                4: "p",
                5: "s",
                6: "n",
            },
            "short": {
                0: "po",
                1: "ut",
                2: "st",
                3: "št",
                4: "pi",
                5: "so",
                6: "ne",
            },
            "wide": {
                0: "pondelok",
                1: "utorok",
                2: "streda",
                3: "štvrtok",
                4: "piatok",
                5: "sobota",
                6: "nedeľa",
            },
        },
        "months": {
            "abbreviated": {
                1: "jan",
                2: "feb",
                3: "mar",
                4: "apr",
                5: "máj",
                6: "jún",
                7: "júl",
                8: "aug",
                9: "sep",
                10: "okt",
                11: "nov",
                12: "dec",
            },
            "narrow": {
                1: "j",
                2: "f",
                3: "m",
                4: "a",
                5: "m",
                6: "j",
                7: "j",
                8: "a",
                9: "s",
                10: "o",
                11: "n",
                12: "d",
            },
            "wide": {
                1: "januára",
                2: "februára",
                3: "marca",
                4: "apríla",
                5: "mája",
                6: "júna",
                7: "júla",
                8: "augusta",
                9: "septembra",
                10: "októbra",
                11: "novembra",
                12: "decembra",
            },
        },
        "units": {
            "year": {
                "one": "{0} rok",
                "few": "{0} roky",
                "many": "{0} roka",
                "other": "{0} rokov",
            },
            "month": {
                "one": "{0} mesiac",
                "few": "{0} mesiace",
                "many": "{0} mesiaca",
                "other": "{0} mesiacov",
            },
            "week": {
                "one": "{0} týždeň",
                "few": "{0} týždne",
                "many": "{0} týždňa",
                "other": "{0} týždňov",
            },
            "day": {
                "one": "{0} deň",
                "few": "{0} dni",
                "many": "{0} dňa",
                "other": "{0} dní",
            },
            "hour": {
                "one": "{0} hodina",
                "few": "{0} hodiny",
                "many": "{0} hodiny",
                "other": "{0} hodín",
            },
            "minute": {
                "one": "{0} minúta",
                "few": "{0} minúty",
                "many": "{0} minúty",
                "other": "{0} minút",
            },
            "second": {
                "one": "{0} sekunda",
                "few": "{0} sekundy",
                "many": "{0} sekundy",
                "other": "{0} sekúnd",
            },
            "microsecond": {
                "one": "{0} mikrosekunda",
                "few": "{0} mikrosekundy",
                "many": "{0} mikrosekundy",
                "other": "{0} mikrosekúnd",
            },
        },
        "relative": {
            "year": {
                "future": {
                    "other": "o {0} rokov",
                    "one": "o {0} rok",
                    "few": "o {0} roky",
                    "many": "o {0} roka",
                },
                "past": {
                    "other": "pred {0} rokmi",
                    "one": "pred {0} rokom",
                    "few": "pred {0} rokmi",
                    "many": "pred {0} roka",
                },
            },
            "month": {
                "future": {
                    "other": "o {0} mesiacov",
                    "one": "o {0} mesiac",
                    "few": "o {0} mesiace",
                    "many": "o {0} mesiaca",
                },
                "past": {
                    "other": "pred {0} mesiacmi",
                    "one": "pred {0} mesiacom",
                    "few": "pred {0} mesiacmi",
                    "many": "pred {0} mesiaca",
                },
            },
            "week": {
                "future": {
                    "other": "o {0} týždňov",
                    "one": "o {0} týždeň",
                    "few": "o {0} týždne",
                    "many": "o {0} týždňa",
                },
                "past": {
                    "other": "pred {0} týždňami",
                    "one": "pred {0} týždňom",
                    "few": "pred {0} týždňami",
                    "many": "pred {0} týždňa",
                },
            },
            "day": {
                "future": {
                    "other": "o {0} dní",
                    "one": "o {0} deň",
                    "few": "o {0} dni",
                    "many": "o {0} dňa",
                },
                "past": {
                    "other": "pred {0} dňami",
                    "one": "pred {0} dňom",
                    "few": "pred {0} dňami",
                    "many": "pred {0} dňa",
                },
            },
            "hour": {
                "future": {
                    "other": "o {0} hodín",
                    "one": "o {0} hodinu",
                    "few": "o {0} hodiny",
                    "many": "o {0} hodiny",
                },
                "past": {
                    "other": "pred {0} hodinami",
                    "one": "pred {0} hodinou",
                    "few": "pred {0} hodinami",
                    "many": "pred {0} hodinou",
                },
            },
            "minute": {
                "future": {
                    "other": "o {0} minút",
                    "one": "o {0} minútu",
                    "few": "o {0} minúty",
                    "many": "o {0} minúty",
                },
                "past": {
                    "other": "pred {0} minútami",
                    "one": "pred {0} minútou",
                    "few": "pred {0} minútami",
                    "many": "pred {0} minúty",
                },
            },
            "second": {
                "future": {
                    "other": "o {0} sekúnd",
                    "one": "o {0} sekundu",
                    "few": "o {0} sekundy",
                    "many": "o {0} sekundy",
                },
                "past": {
                    "other": "pred {0} sekundami",
                    "one": "pred {0} sekundou",
                    "few": "pred {0} sekundami",
                    "many": "pred {0} sekundy",
                },
            },
        },
        "day_periods": {
            "midnight": "o polnoci",
            "am": "AM",
            "noon": "napoludnie",
            "pm": "PM",
            "morning1": "ráno",
            "morning2": "dopoludnia",
            "afternoon1": "popoludní",
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
