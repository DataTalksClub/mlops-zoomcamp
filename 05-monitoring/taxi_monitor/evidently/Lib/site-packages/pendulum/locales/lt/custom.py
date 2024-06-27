"""
lt custom locale file.
"""
from __future__ import annotations


translations = {
    # Relative time
    "units_relative": {
        "year": {
            "future": {
                "other": "{0} metų",
                "one": "{0} metų",
                "few": "{0} metų",
                "many": "{0} metų",
            },
            "past": {
                "other": "{0} metų",
                "one": "{0} metus",
                "few": "{0} metus",
                "many": "{0} metų",
            },
        },
        "month": {
            "future": {
                "other": "{0} mėnesių",
                "one": "{0} mėnesio",
                "few": "{0} mėnesių",
                "many": "{0} mėnesio",
            },
            "past": {
                "other": "{0} mėnesių",
                "one": "{0} mėnesį",
                "few": "{0} mėnesius",
                "many": "{0} mėnesio",
            },
        },
        "week": {
            "future": {
                "other": "{0} savaičių",
                "one": "{0} savaitės",
                "few": "{0} savaičių",
                "many": "{0} savaitės",
            },
            "past": {
                "other": "{0} savaičių",
                "one": "{0} savaitę",
                "few": "{0} savaites",
                "many": "{0} savaitės",
            },
        },
        "day": {
            "future": {
                "other": "{0} dienų",
                "one": "{0} dienos",
                "few": "{0} dienų",
                "many": "{0} dienos",
            },
            "past": {
                "other": "{0} dienų",
                "one": "{0} dieną",
                "few": "{0} dienas",
                "many": "{0} dienos",
            },
        },
        "hour": {
            "future": {
                "other": "{0} valandų",
                "one": "{0} valandos",
                "few": "{0} valandų",
                "many": "{0} valandos",
            },
            "past": {
                "other": "{0} valandų",
                "one": "{0} valandą",
                "few": "{0} valandas",
                "many": "{0} valandos",
            },
        },
        "minute": {
            "future": {
                "other": "{0} minučių",
                "one": "{0} minutės",
                "few": "{0} minučių",
                "many": "{0} minutės",
            },
            "past": {
                "other": "{0} minučių",
                "one": "{0} minutę",
                "few": "{0} minutes",
                "many": "{0} minutės",
            },
        },
        "second": {
            "future": {
                "other": "{0} sekundžių",
                "one": "{0} sekundės",
                "few": "{0} sekundžių",
                "many": "{0} sekundės",
            },
            "past": {
                "other": "{0} sekundžių",
                "one": "{0} sekundę",
                "few": "{0} sekundes",
                "many": "{0} sekundės",
            },
        },
    },
    "after": "po {0}",
    "before": "{0} nuo dabar",
    # Date formats
    "date_formats": {
        "LTS": "HH:mm:ss",
        "LT": "HH:mm",
        "LLLL": "YYYY [m.] MMMM D [d.], dddd, HH:mm [val.]",
        "LLL": "YYYY [m.] MMMM D [d.], HH:mm [val.]",
        "LL": "YYYY [m.] MMMM D [d.]",
        "L": "YYYY-MM-DD",
    },
}
