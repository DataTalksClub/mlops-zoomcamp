"""
he custom locale file.
"""
from __future__ import annotations


translations = {
    "units": {"few_second": "כמה שניות"},
    # Relative time
    "ago": "לפני {0}",
    "from_now": "תוך {0}",
    "after": "בעוד {0}",
    "before": "{0} קודם",
    # Ordinals
    "ordinal": {"other": "º"},
    # Date formats
    "date_formats": {
        "LTS": "H:mm:ss",
        "LT": "H:mm",
        "LLLL": "dddd, D [ב] MMMM [ב] YYYY H:mm",
        "LLL": "D [ב] MMMM [ב] YYYY H:mm",
        "LL": "D [ב] MMMM [ב] YYYY",
        "L": "DD/MM/YYYY",
    },
}
