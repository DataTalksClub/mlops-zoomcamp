# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .custom import translations as custom_translations


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
                0: "Min",
                1: "Sen",
                2: "Sel",
                3: "Rab",
                4: "Kam",
                5: "Jum",
                6: "Sab",
            },
            "narrow": {0: "M", 1: "S", 2: "S", 3: "R", 4: "K", 5: "J", 6: "S"},
            "short": {
                0: "Min",
                1: "Sen",
                2: "Sel",
                3: "Rab",
                4: "Kam",
                5: "Jum",
                6: "Sab",
            },
            "wide": {
                0: "Minggu",
                1: "Senin",
                2: "Selasa",
                3: "Rabu",
                4: "Kamis",
                5: "Jumat",
                6: "Sabtu",
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
    },
    "custom": custom_translations,
}
