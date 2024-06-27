"""
en-gb custom locale file.
"""
from __future__ import annotations


translations = {
    "units": {"few_second": "a few seconds"},
    # Relative time
    "ago": "{} ago",
    "from_now": "in {}",
    "after": "{0} after",
    "before": "{0} before",
    # Ordinals
    "ordinal": {"one": "st", "two": "nd", "few": "rd", "other": "th"},
    # Date formats
    "date_formats": {
        "LTS": "HH:mm:ss",
        "LT": "HH:mm",
        "L": "DD/MM/YYYY",
        "LL": "D MMMM YYYY",
        "LLL": "D MMMM YYYY HH:mm",
        "LLLL": "dddd, D MMMM YYYY HH:mm",
    },
}
