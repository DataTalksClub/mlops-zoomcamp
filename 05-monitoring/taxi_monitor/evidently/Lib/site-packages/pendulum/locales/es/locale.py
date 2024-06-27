from __future__ import annotations

from pendulum.locales.es.custom import translations as custom_translations


"""
es locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "one" if (n == n and (n == 1)) else "other",
    "ordinal": lambda n: "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "lun.",
                1: "mar.",
                2: "mié.",
                3: "jue.",
                4: "vie.",
                5: "sáb.",
                6: "dom.",
            },
            "narrow": {0: "L", 1: "M", 2: "X", 3: "J", 4: "V", 5: "S", 6: "D"},
            "short": {0: "LU", 1: "MA", 2: "MI", 3: "JU", 4: "VI", 5: "SA", 6: "DO"},
            "wide": {
                0: "lunes",
                1: "martes",
                2: "miércoles",
                3: "jueves",
                4: "viernes",
                5: "sábado",
                6: "domingo",
            },
        },
        "months": {
            "abbreviated": {
                1: "ene.",
                2: "feb.",
                3: "mar.",
                4: "abr.",
                5: "may.",
                6: "jun.",
                7: "jul.",
                8: "ago.",
                9: "sept.",
                10: "oct.",
                11: "nov.",
                12: "dic.",
            },
            "narrow": {
                1: "E",
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
                1: "enero",
                2: "febrero",
                3: "marzo",
                4: "abril",
                5: "mayo",
                6: "junio",
                7: "julio",
                8: "agosto",
                9: "septiembre",
                10: "octubre",
                11: "noviembre",
                12: "diciembre",
            },
        },
        "units": {
            "year": {"one": "{0} año", "other": "{0} años"},
            "month": {"one": "{0} mes", "other": "{0} meses"},
            "week": {"one": "{0} semana", "other": "{0} semanas"},
            "day": {"one": "{0} día", "other": "{0} días"},
            "hour": {"one": "{0} hora", "other": "{0} horas"},
            "minute": {"one": "{0} minuto", "other": "{0} minutos"},
            "second": {"one": "{0} segundo", "other": "{0} segundos"},
            "microsecond": {"one": "{0} microsegundo", "other": "{0} microsegundos"},
        },
        "relative": {
            "year": {
                "future": {"other": "dentro de {0} años", "one": "dentro de {0} año"},
                "past": {"other": "hace {0} años", "one": "hace {0} año"},
            },
            "month": {
                "future": {"other": "dentro de {0} meses", "one": "dentro de {0} mes"},
                "past": {"other": "hace {0} meses", "one": "hace {0} mes"},
            },
            "week": {
                "future": {
                    "other": "dentro de {0} semanas",
                    "one": "dentro de {0} semana",
                },
                "past": {"other": "hace {0} semanas", "one": "hace {0} semana"},
            },
            "day": {
                "future": {"other": "dentro de {0} días", "one": "dentro de {0} día"},
                "past": {"other": "hace {0} días", "one": "hace {0} día"},
            },
            "hour": {
                "future": {"other": "dentro de {0} horas", "one": "dentro de {0} hora"},
                "past": {"other": "hace {0} horas", "one": "hace {0} hora"},
            },
            "minute": {
                "future": {
                    "other": "dentro de {0} minutos",
                    "one": "dentro de {0} minuto",
                },
                "past": {"other": "hace {0} minutos", "one": "hace {0} minuto"},
            },
            "second": {
                "future": {
                    "other": "dentro de {0} segundos",
                    "one": "dentro de {0} segundo",
                },
                "past": {"other": "hace {0} segundos", "one": "hace {0} segundo"},
            },
        },
        "day_periods": {
            "am": "a. m.",
            "noon": "del mediodía",
            "pm": "p. m.",
            "morning1": "de la madrugada",
            "morning2": "de la mañana",
            "evening1": "de la tarde",
            "night1": "de la noche",
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
