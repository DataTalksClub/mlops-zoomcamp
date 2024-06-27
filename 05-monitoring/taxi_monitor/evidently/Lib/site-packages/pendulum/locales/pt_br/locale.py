from __future__ import annotations

from pendulum.locales.pt_br.custom import translations as custom_translations


"""
pt_br locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "one"
    if ((n == n and (n >= 0 and n <= 2)) and (not (n == n and (n == 2))))
    else "other",
    "ordinal": lambda n: "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "seg",
                1: "ter",
                2: "qua",
                3: "qui",
                4: "sex",
                5: "sáb",
                6: "dom",
            },
            "narrow": {0: "S", 1: "T", 2: "Q", 3: "Q", 4: "S", 5: "S", 6: "D"},
            "short": {
                0: "seg",
                1: "ter",
                2: "qua",
                3: "qui",
                4: "sex",
                5: "sáb",
                6: "dom",
            },
            "wide": {
                0: "segunda-feira",
                1: "terça-feira",
                2: "quarta-feira",
                3: "quinta-feira",
                4: "sexta-feira",
                5: "sábado",
                6: "domingo",
            },
        },
        "months": {
            "abbreviated": {
                1: "jan",
                2: "fev",
                3: "mar",
                4: "abr",
                5: "mai",
                6: "jun",
                7: "jul",
                8: "ago",
                9: "set",
                10: "out",
                11: "nov",
                12: "dez",
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
                1: "janeiro",
                2: "fevereiro",
                3: "março",
                4: "abril",
                5: "maio",
                6: "junho",
                7: "julho",
                8: "agosto",
                9: "setembro",
                10: "outubro",
                11: "novembro",
                12: "dezembro",
            },
        },
        "units": {
            "year": {"one": "{0} ano", "other": "{0} anos"},
            "month": {"one": "{0} mês", "other": "{0} meses"},
            "week": {"one": "{0} semana", "other": "{0} semanas"},
            "day": {"one": "{0} dia", "other": "{0} dias"},
            "hour": {"one": "{0} hora", "other": "{0} horas"},
            "minute": {"one": "{0} minuto", "other": "{0} minutos"},
            "second": {"one": "{0} segundo", "other": "{0} segundos"},
            "microsecond": {"one": "{0} microssegundo", "other": "{0} microssegundos"},
        },
        "relative": {
            "year": {
                "future": {"other": "em {0} anos", "one": "em {0} ano"},
                "past": {"other": "há {0} anos", "one": "há {0} ano"},
            },
            "month": {
                "future": {"other": "em {0} meses", "one": "em {0} mês"},
                "past": {"other": "há {0} meses", "one": "há {0} mês"},
            },
            "week": {
                "future": {"other": "em {0} semanas", "one": "em {0} semana"},
                "past": {"other": "há {0} semanas", "one": "há {0} semana"},
            },
            "day": {
                "future": {"other": "em {0} dias", "one": "em {0} dia"},
                "past": {"other": "há {0} dias", "one": "há {0} dia"},
            },
            "hour": {
                "future": {"other": "em {0} horas", "one": "em {0} hora"},
                "past": {"other": "há {0} horas", "one": "há {0} hora"},
            },
            "minute": {
                "future": {"other": "em {0} minutos", "one": "em {0} minuto"},
                "past": {"other": "há {0} minutos", "one": "há {0} minuto"},
            },
            "second": {
                "future": {"other": "em {0} segundos", "one": "em {0} segundo"},
                "past": {"other": "há {0} segundos", "one": "há {0} segundo"},
            },
        },
        "day_periods": {
            "midnight": "meia-noite",
            "am": "AM",
            "noon": "meio-dia",
            "pm": "PM",
            "morning1": "da manhã",
            "afternoon1": "da tarde",
            "evening1": "da noite",
            "night1": "da madrugada",
        },
        "week_data": {
            "min_days": 1,
            "first_day": 6,
            "weekend_start": 5,
            "weekend_end": 6,
        },
    },
    "custom": custom_translations,
}
