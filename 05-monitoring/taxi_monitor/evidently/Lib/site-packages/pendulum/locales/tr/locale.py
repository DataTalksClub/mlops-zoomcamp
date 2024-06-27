from __future__ import annotations

from pendulum.locales.tr.custom import translations as custom_translations


"""
tr locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "one" if (n == n and (n == 1)) else "other",
    "ordinal": lambda n: "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "Pzt",
                1: "Sal",
                2: "Çar",
                3: "Per",
                4: "Cum",
                5: "Cmt",
                6: "Paz",
            },
            "narrow": {
                0: "P",
                1: "S",
                2: "Ç",
                3: "P",
                4: "C",
                5: "C",
                6: "P",
            },
            "short": {
                0: "Pt",
                1: "Sa",
                2: "Ça",
                3: "Pe",
                4: "Cu",
                5: "Ct",
                6: "Pa",
            },
            "wide": {
                0: "Pazartesi",
                1: "Salı",
                2: "Çarşamba",
                3: "Perşembe",
                4: "Cuma",
                5: "Cumartesi",
                6: "Pazar",
            },
        },
        "months": {
            "abbreviated": {
                1: "Oca",
                2: "Şub",
                3: "Mar",
                4: "Nis",
                5: "May",
                6: "Haz",
                7: "Tem",
                8: "Ağu",
                9: "Eyl",
                10: "Eki",
                11: "Kas",
                12: "Ara",
            },
            "narrow": {
                1: "O",
                2: "Ş",
                3: "M",
                4: "N",
                5: "M",
                6: "H",
                7: "T",
                8: "A",
                9: "E",
                10: "E",
                11: "K",
                12: "A",
            },
            "wide": {
                1: "Ocak",
                2: "Şubat",
                3: "Mart",
                4: "Nisan",
                5: "Mayıs",
                6: "Haziran",
                7: "Temmuz",
                8: "Ağustos",
                9: "Eylül",
                10: "Ekim",
                11: "Kasım",
                12: "Aralık",
            },
        },
        "units": {
            "year": {
                "one": "{0} yıl",
                "other": "{0} yıl",
            },
            "month": {
                "one": "{0} ay",
                "other": "{0} ay",
            },
            "week": {
                "one": "{0} hafta",
                "other": "{0} hafta",
            },
            "day": {
                "one": "{0} gün",
                "other": "{0} gün",
            },
            "hour": {
                "one": "{0} saat",
                "other": "{0} saat",
            },
            "minute": {
                "one": "{0} dakika",
                "other": "{0} dakika",
            },
            "second": {
                "one": "{0} saniye",
                "other": "{0} saniye",
            },
            "microsecond": {
                "one": "{0} mikrosaniye",
                "other": "{0} mikrosaniye",
            },
        },
        "relative": {
            "year": {
                "future": {
                    "other": "{0} yıl sonra",
                    "one": "{0} yıl sonra",
                },
                "past": {
                    "other": "{0} yıl önce",
                    "one": "{0} yıl önce",
                },
            },
            "month": {
                "future": {
                    "other": "{0} ay sonra",
                    "one": "{0} ay sonra",
                },
                "past": {
                    "other": "{0} ay önce",
                    "one": "{0} ay önce",
                },
            },
            "week": {
                "future": {
                    "other": "{0} hafta sonra",
                    "one": "{0} hafta sonra",
                },
                "past": {
                    "other": "{0} hafta önce",
                    "one": "{0} hafta önce",
                },
            },
            "day": {
                "future": {
                    "other": "{0} gün sonra",
                    "one": "{0} gün sonra",
                },
                "past": {
                    "other": "{0} gün önce",
                    "one": "{0} gün önce",
                },
            },
            "hour": {
                "future": {
                    "other": "{0} saat sonra",
                    "one": "{0} saat sonra",
                },
                "past": {
                    "other": "{0} saat önce",
                    "one": "{0} saat önce",
                },
            },
            "minute": {
                "future": {
                    "other": "{0} dakika sonra",
                    "one": "{0} dakika sonra",
                },
                "past": {
                    "other": "{0} dakika önce",
                    "one": "{0} dakika önce",
                },
            },
            "second": {
                "future": {
                    "other": "{0} saniye sonra",
                    "one": "{0} saniye sonra",
                },
                "past": {
                    "other": "{0} saniye önce",
                    "one": "{0} saniye önce",
                },
            },
        },
        "day_periods": {
            "midnight": "gece yarısı",
            "am": "ÖÖ",
            "noon": "öğle",
            "pm": "ÖS",
            "morning1": "sabah",
            "morning2": "öğleden önce",
            "afternoon1": "öğleden sonra",
            "afternoon2": "akşamüstü",
            "evening1": "akşam",
            "night1": "gece",
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
