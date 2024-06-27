"""
de custom locale file.
"""
from __future__ import annotations


translations = {
    # Relative time
    "after": "{0} später",
    "before": "{0} zuvor",
    "units_relative": {
        "year": {
            "future": {"one": "{0} Jahr", "other": "{0} Jahren"},
            "past": {"one": "{0} Jahr", "other": "{0} Jahren"},
        },
        "month": {
            "future": {"one": "{0} Monat", "other": "{0} Monaten"},
            "past": {"one": "{0} Monat", "other": "{0} Monaten"},
        },
        "week": {
            "future": {"one": "{0} Woche", "other": "{0} Wochen"},
            "past": {"one": "{0} Woche", "other": "{0} Wochen"},
        },
        "day": {
            "future": {"one": "{0} Tag", "other": "{0} Tagen"},
            "past": {"one": "{0} Tag", "other": "{0} Tagen"},
        },
    },
    # Date formats
    "date_formats": {
        "LTS": "HH:mm:ss",
        "LT": "HH:mm",
        "LLLL": "dddd, D. MMMM YYYY HH:mm",
        "LLL": "D. MMMM YYYY HH:mm",
        "LL": "D. MMMM YYYY",
        "L": "DD.MM.YYYY",
    },
}
