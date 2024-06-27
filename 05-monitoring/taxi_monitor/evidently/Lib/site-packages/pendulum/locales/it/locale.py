from __future__ import annotations

from pendulum.locales.it.custom import translations as custom_translations


"""
it locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "one"
    if ((n == n and (n == 1)) and (0 == 0 and (0 == 0)))
    else "other",
    "ordinal": lambda n: "many"
    if (n == n and ((n == 11) or (n == 8) or (n == 80) or (n == 800)))
    else "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "lun",
                1: "mar",
                2: "mer",
                3: "gio",
                4: "ven",
                5: "sab",
                6: "dom",
            },
            "narrow": {0: "L", 1: "M", 2: "M", 3: "G", 4: "V", 5: "S", 6: "D"},
            "short": {
                0: "lun",
                1: "mar",
                2: "mer",
                3: "gio",
                4: "ven",
                5: "sab",
                6: "dom",
            },
            "wide": {
                0: "lunedì",
                1: "martedì",
                2: "mercoledì",
                3: "giovedì",
                4: "venerdì",
                5: "sabato",
                6: "domenica",
            },
        },
        "months": {
            "abbreviated": {
                1: "gen",
                2: "feb",
                3: "mar",
                4: "apr",
                5: "mag",
                6: "giu",
                7: "lug",
                8: "ago",
                9: "set",
                10: "ott",
                11: "nov",
                12: "dic",
            },
            "narrow": {
                1: "G",
                2: "F",
                3: "M",
                4: "A",
                5: "M",
                6: "G",
                7: "L",
                8: "A",
                9: "S",
                10: "O",
                11: "N",
                12: "D",
            },
            "wide": {
                1: "gennaio",
                2: "febbraio",
                3: "marzo",
                4: "aprile",
                5: "maggio",
                6: "giugno",
                7: "luglio",
                8: "agosto",
                9: "settembre",
                10: "ottobre",
                11: "novembre",
                12: "dicembre",
            },
        },
        "units": {
            "year": {"one": "{0} anno", "other": "{0} anni"},
            "month": {"one": "{0} mese", "other": "{0} mesi"},
            "week": {"one": "{0} settimana", "other": "{0} settimane"},
            "day": {"one": "{0} giorno", "other": "{0} giorni"},
            "hour": {"one": "{0} ora", "other": "{0} ore"},
            "minute": {"one": "{0} minuto", "other": "{0} minuti"},
            "second": {"one": "{0} secondo", "other": "{0} secondi"},
            "microsecond": {"one": "{0} microsecondo", "other": "{0} microsecondi"},
        },
        "relative": {
            "year": {
                "future": {"other": "tra {0} anni", "one": "tra {0} anno"},
                "past": {"other": "{0} anni fa", "one": "{0} anno fa"},
            },
            "month": {
                "future": {"other": "tra {0} mesi", "one": "tra {0} mese"},
                "past": {"other": "{0} mesi fa", "one": "{0} mese fa"},
            },
            "week": {
                "future": {"other": "tra {0} settimane", "one": "tra {0} settimana"},
                "past": {"other": "{0} settimane fa", "one": "{0} settimana fa"},
            },
            "day": {
                "future": {"other": "tra {0} giorni", "one": "tra {0} giorno"},
                "past": {"other": "{0} giorni fa", "one": "{0} giorno fa"},
            },
            "hour": {
                "future": {"other": "tra {0} ore", "one": "tra {0} ora"},
                "past": {"other": "{0} ore fa", "one": "{0} ora fa"},
            },
            "minute": {
                "future": {"other": "tra {0} minuti", "one": "tra {0} minuto"},
                "past": {"other": "{0} minuti fa", "one": "{0} minuto fa"},
            },
            "second": {
                "future": {"other": "tra {0} secondi", "one": "tra {0} secondo"},
                "past": {"other": "{0} secondi fa", "one": "{0} secondo fa"},
            },
        },
        "day_periods": {
            "midnight": "mezzanotte",
            "am": "AM",
            "noon": "mezzogiorno",
            "pm": "PM",
            "morning1": "di mattina",
            "afternoon1": "del pomeriggio",
            "evening1": "di sera",
            "night1": "di notte",
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
