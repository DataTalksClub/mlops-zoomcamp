"""
en-us custom locale file.
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
        "LTS": "h:mm:ss A",
        "LT": "h:mm A",
        "L": "MM/DD/YYYY",
        "LL": "MMMM D, YYYY",
        "LLL": "MMMM D, YYYY h:mm A",
        "LLLL": "dddd, MMMM D, YYYY h:mm A",
    },
}
