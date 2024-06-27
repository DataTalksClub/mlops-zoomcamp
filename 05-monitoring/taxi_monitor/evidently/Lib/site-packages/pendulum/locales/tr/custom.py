"""
tr custom locale file.
"""
from __future__ import annotations


translations = {
    # Relative time
    "ago": "{} önce",
    "from_now": "{} içinde",
    "after": "{0} sonra",
    "before": "{0} önce",
    # Ordinals
    "ordinal": {"one": ".", "two": ".", "few": ".", "other": "."},
    # Date formats
    "date_formats": {
        "LTS": "h:mm:ss A",
        "LT": "h:mm A",
        "L": "MM/DD/YYYY",
        "LL": "MMMM D, YYYY",
        "LLL": "MMMM D, YYYY h:mm A",
        "LLLL": "dddd, MMMM D, YYYY h:mm A",
    },
}
