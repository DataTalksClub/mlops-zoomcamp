# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .custom import translations as custom_translations


"""
es locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "one" if (n == n and ((n == 1))) else "other",
    "ordinal": lambda n: "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "dom.",
                1: "lun.",
                2: "mar.",
                3: "mié.",
                4: "jue.",
                5: "vie.",
                6: "sáb.",
            },
            "narrow": {0: "D", 1: "L", 2: "M", 3: "X", 4: "J", 5: "V", 6: "S"},
            "short": {0: "DO", 1: "LU", 2: "MA", 3: "MI", 4: "JU", 5: "VI", 6: "SA"},
            "wide": {
                0: "domingo",
                1: "lunes",
                2: "martes",
                3: "miércoles",
                4: "jueves",
                5: "viernes",
                6: "sábado",
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
    },
    "custom": custom_translations,
}
