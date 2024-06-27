from __future__ import annotations

from pendulum.locales.de.custom import translations as custom_translations


"""
de locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "one"
    if ((n == n and (n == 1)) and (0 == 0 and (0 == 0)))
    else "other",
    "ordinal": lambda n: "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "Mo.",
                1: "Di.",
                2: "Mi.",
                3: "Do.",
                4: "Fr.",
                5: "Sa.",
                6: "So.",
            },
            "narrow": {0: "M", 1: "D", 2: "M", 3: "D", 4: "F", 5: "S", 6: "S"},
            "short": {
                0: "Mo.",
                1: "Di.",
                2: "Mi.",
                3: "Do.",
                4: "Fr.",
                5: "Sa.",
                6: "So.",
            },
            "wide": {
                0: "Montag",
                1: "Dienstag",
                2: "Mittwoch",
                3: "Donnerstag",
                4: "Freitag",
                5: "Samstag",
                6: "Sonntag",
            },
        },
        "months": {
            "abbreviated": {
                1: "Jan.",
                2: "Feb.",
                3: "März",
                4: "Apr.",
                5: "Mai",
                6: "Juni",
                7: "Juli",
                8: "Aug.",
                9: "Sep.",
                10: "Okt.",
                11: "Nov.",
                12: "Dez.",
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
                1: "Januar",
                2: "Februar",
                3: "März",
                4: "April",
                5: "Mai",
                6: "Juni",
                7: "Juli",
                8: "August",
                9: "September",
                10: "Oktober",
                11: "November",
                12: "Dezember",
            },
        },
        "units": {
            "year": {"one": "{0} Jahr", "other": "{0} Jahre"},
            "month": {"one": "{0} Monat", "other": "{0} Monate"},
            "week": {"one": "{0} Woche", "other": "{0} Wochen"},
            "day": {"one": "{0} Tag", "other": "{0} Tage"},
            "hour": {"one": "{0} Stunde", "other": "{0} Stunden"},
            "minute": {"one": "{0} Minute", "other": "{0} Minuten"},
            "second": {"one": "{0} Sekunde", "other": "{0} Sekunden"},
            "microsecond": {"one": "{0} Mikrosekunde", "other": "{0} Mikrosekunden"},
        },
        "relative": {
            "year": {
                "future": {"other": "in {0} Jahren", "one": "in {0} Jahr"},
                "past": {"other": "vor {0} Jahren", "one": "vor {0} Jahr"},
            },
            "month": {
                "future": {"other": "in {0} Monaten", "one": "in {0} Monat"},
                "past": {"other": "vor {0} Monaten", "one": "vor {0} Monat"},
            },
            "week": {
                "future": {"other": "in {0} Wochen", "one": "in {0} Woche"},
                "past": {"other": "vor {0} Wochen", "one": "vor {0} Woche"},
            },
            "day": {
                "future": {"other": "in {0} Tagen", "one": "in {0} Tag"},
                "past": {"other": "vor {0} Tagen", "one": "vor {0} Tag"},
            },
            "hour": {
                "future": {"other": "in {0} Stunden", "one": "in {0} Stunde"},
                "past": {"other": "vor {0} Stunden", "one": "vor {0} Stunde"},
            },
            "minute": {
                "future": {"other": "in {0} Minuten", "one": "in {0} Minute"},
                "past": {"other": "vor {0} Minuten", "one": "vor {0} Minute"},
            },
            "second": {
                "future": {"other": "in {0} Sekunden", "one": "in {0} Sekunde"},
                "past": {"other": "vor {0} Sekunden", "one": "vor {0} Sekunde"},
            },
        },
        "day_periods": {
            "midnight": "Mitternacht",
            "am": "vorm.",
            "pm": "nachm.",
            "morning1": "morgens",
            "morning2": "vormittags",
            "afternoon1": "mittags",
            "afternoon2": "nachmittags",
            "evening1": "abends",
            "night1": "nachts",
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
