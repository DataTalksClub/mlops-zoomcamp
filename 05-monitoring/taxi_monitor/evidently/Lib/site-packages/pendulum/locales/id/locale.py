from __future__ import annotations

from pendulum.locales.id.custom import translations as custom_translations


"""
id locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "other",
    "ordinal": lambda n: "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "Sen",
                1: "Sel",
                2: "Rab",
                3: "Kam",
                4: "Jum",
                5: "Sab",
                6: "Min",
            },
            "narrow": {0: "S", 1: "S", 2: "R", 3: "K", 4: "J", 5: "S", 6: "M"},
            "short": {
                0: "Sen",
                1: "Sel",
                2: "Rab",
                3: "Kam",
                4: "Jum",
                5: "Sab",
                6: "Min",
            },
            "wide": {
                0: "Senin",
                1: "Selasa",
                2: "Rabu",
                3: "Kamis",
                4: "Jumat",
                5: "Sabtu",
                6: "Minggu",
            },
        },
        "months": {
            "abbreviated": {
                1: "Jan",
                2: "Feb",
                3: "Mar",
                4: "Apr",
                5: "Mei",
                6: "Jun",
                7: "Jul",
                8: "Agt",
                9: "Sep",
                10: "Okt",
                11: "Nov",
                12: "Des",
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
                1: "Januari",
                2: "Februari",
                3: "Maret",
                4: "April",
                5: "Mei",
                6: "Juni",
                7: "Juli",
                8: "Agustus",
                9: "September",
                10: "Oktober",
                11: "November",
                12: "Desember",
            },
        },
        "units": {
            "year": {"other": "{0} tahun"},
            "month": {"other": "{0} bulan"},
            "week": {"other": "{0} minggu"},
            "day": {"other": "{0} hari"},
            "hour": {"other": "{0} jam"},
            "minute": {"other": "{0} menit"},
            "second": {"other": "{0} detik"},
            "microsecond": {"other": "{0} mikrodetik"},
        },
        "relative": {
            "year": {
                "future": {"other": "dalam {0} tahun"},
                "past": {"other": "{0} tahun yang lalu"},
            },
            "month": {
                "future": {"other": "dalam {0} bulan"},
                "past": {"other": "{0} bulan yang lalu"},
            },
            "week": {
                "future": {"other": "dalam {0} minggu"},
                "past": {"other": "{0} minggu yang lalu"},
            },
            "day": {
                "future": {"other": "dalam {0} hari"},
                "past": {"other": "{0} hari yang lalu"},
            },
            "hour": {
                "future": {"other": "dalam {0} jam"},
                "past": {"other": "{0} jam yang lalu"},
            },
            "minute": {
                "future": {"other": "dalam {0} menit"},
                "past": {"other": "{0} menit yang lalu"},
            },
            "second": {
                "future": {"other": "dalam {0} detik"},
                "past": {"other": "{0} detik yang lalu"},
            },
        },
        "day_periods": {
            "midnight": "tengah malam",
            "am": "AM",
            "noon": "tengah hari",
            "pm": "PM",
            "morning1": "pagi",
            "afternoon1": "siang",
            "evening1": "sore",
            "night1": "malam",
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
