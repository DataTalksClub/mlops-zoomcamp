from __future__ import annotations

from pendulum.locales.fr.custom import translations as custom_translations


"""
fr locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "one" if (n == n and ((n == 0) or (n == 1))) else "other",
    "ordinal": lambda n: "one" if (n == n and (n == 1)) else "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "lun.",
                1: "mar.",
                2: "mer.",
                3: "jeu.",
                4: "ven.",
                5: "sam.",
                6: "dim.",
            },
            "narrow": {0: "L", 1: "M", 2: "M", 3: "J", 4: "V", 5: "S", 6: "D"},
            "short": {0: "lu", 1: "ma", 2: "me", 3: "je", 4: "ve", 5: "sa", 6: "di"},
            "wide": {
                0: "lundi",
                1: "mardi",
                2: "mercredi",
                3: "jeudi",
                4: "vendredi",
                5: "samedi",
                6: "dimanche",
            },
        },
        "months": {
            "abbreviated": {
                1: "janv.",
                2: "févr.",
                3: "mars",
                4: "avr.",
                5: "mai",
                6: "juin",
                7: "juil.",
                8: "août",
                9: "sept.",
                10: "oct.",
                11: "nov.",
                12: "déc.",
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
                1: "janvier",
                2: "février",
                3: "mars",
                4: "avril",
                5: "mai",
                6: "juin",
                7: "juillet",
                8: "août",
                9: "septembre",
                10: "octobre",
                11: "novembre",
                12: "décembre",
            },
        },
        "units": {
            "year": {"one": "{0} an", "other": "{0} ans"},
            "month": {"one": "{0} mois", "other": "{0} mois"},
            "week": {"one": "{0} semaine", "other": "{0} semaines"},
            "day": {"one": "{0} jour", "other": "{0} jours"},
            "hour": {"one": "{0} heure", "other": "{0} heures"},
            "minute": {"one": "{0} minute", "other": "{0} minutes"},
            "second": {"one": "{0} seconde", "other": "{0} secondes"},
            "microsecond": {"one": "{0} microseconde", "other": "{0} microsecondes"},
        },
        "relative": {
            "year": {
                "future": {"other": "dans {0} ans", "one": "dans {0} an"},
                "past": {"other": "il y a {0} ans", "one": "il y a {0} an"},
            },
            "month": {
                "future": {"other": "dans {0} mois", "one": "dans {0} mois"},
                "past": {"other": "il y a {0} mois", "one": "il y a {0} mois"},
            },
            "week": {
                "future": {"other": "dans {0} semaines", "one": "dans {0} semaine"},
                "past": {"other": "il y a {0} semaines", "one": "il y a {0} semaine"},
            },
            "day": {
                "future": {"other": "dans {0} jours", "one": "dans {0} jour"},
                "past": {"other": "il y a {0} jours", "one": "il y a {0} jour"},
            },
            "hour": {
                "future": {"other": "dans {0} heures", "one": "dans {0} heure"},
                "past": {"other": "il y a {0} heures", "one": "il y a {0} heure"},
            },
            "minute": {
                "future": {"other": "dans {0} minutes", "one": "dans {0} minute"},
                "past": {"other": "il y a {0} minutes", "one": "il y a {0} minute"},
            },
            "second": {
                "future": {"other": "dans {0} secondes", "one": "dans {0} seconde"},
                "past": {"other": "il y a {0} secondes", "one": "il y a {0} seconde"},
            },
        },
        "day_periods": {
            "midnight": "minuit",
            "am": "AM",
            "noon": "midi",
            "pm": "PM",
            "morning1": "du matin",
            "afternoon1": "de l’après-midi",
            "evening1": "du soir",
            "night1": "de nuit",
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
