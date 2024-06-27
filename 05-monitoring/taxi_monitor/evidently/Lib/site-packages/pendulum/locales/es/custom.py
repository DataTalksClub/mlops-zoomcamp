"""
es custom locale file.
"""
from __future__ import annotations


translations = {
    "units": {"few_second": "unos segundos"},
    # Relative time
    "ago": "hace {0}",
    "from_now": "dentro de {0}",
    "after": "{0} después",
    "before": "{0} antes",
    # Ordinals
    "ordinal": {"other": "º"},
    # Date formats
    "date_formats": {
        "LTS": "H:mm:ss",
        "LT": "H:mm",
        "LLLL": "dddd, D [de] MMMM [de] YYYY H:mm",
        "LLL": "D [de] MMMM [de] YYYY H:mm",
        "LL": "D [de] MMMM [de] YYYY",
        "L": "DD/MM/YYYY",
    },
}
