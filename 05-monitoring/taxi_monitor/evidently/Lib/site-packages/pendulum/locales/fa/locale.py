from __future__ import annotations

from pendulum.locales.fa.custom import translations as custom_translations


"""
fa locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "one"
    if ((n == n and (n == 0)) or (n == n and (n == 1)))
    else "other",
    "ordinal": lambda n: "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "دوشنبه",
                1: "سه\u200cشنبه",
                2: "چهارشنبه",
                3: "پنجشنبه",
                4: "جمعه",
                5: "شنبه",
                6: "یکشنبه",
            },
            "narrow": {0: "د", 1: "س", 2: "چ", 3: "پ", 4: "ج", 5: "ش", 6: "ی"},
            "short": {0: "۲ش", 1: "۳ش", 2: "۴ش", 3: "۵ش", 4: "ج", 5: "ش", 6: "۱ش"},
            "wide": {
                0: "دوشنبه",
                1: "سه\u200cشنبه",
                2: "چهارشنبه",
                3: "پنجشنبه",
                4: "جمعه",
                5: "شنبه",
                6: "یکشنبه",
            },
        },
        "months": {
            "abbreviated": {
                1: "ژانویهٔ",
                2: "فوریهٔ",
                3: "مارس",
                4: "آوریل",
                5: "مهٔ",
                6: "ژوئن",
                7: "ژوئیهٔ",
                8: "اوت",
                9: "سپتامبر",
                10: "اکتبر",
                11: "نوامبر",
                12: "دسامبر",
            },
            "narrow": {
                1: "ژ",
                2: "ف",
                3: "م",
                4: "آ",
                5: "م",
                6: "ژ",
                7: "ژ",
                8: "ا",
                9: "س",
                10: "ا",
                11: "ن",
                12: "د",
            },
            "wide": {
                1: "ژانویهٔ",
                2: "فوریهٔ",
                3: "مارس",
                4: "آوریل",
                5: "مهٔ",
                6: "ژوئن",
                7: "ژوئیهٔ",
                8: "اوت",
                9: "سپتامبر",
                10: "اکتبر",
                11: "نوامبر",
                12: "دسامبر",
            },
        },
        "units": {
            "year": {"one": "{0} سال", "other": "{0} سال"},
            "month": {"one": "{0} ماه", "other": "{0} ماه"},
            "week": {"one": "{0} هفته", "other": "{0} هفته"},
            "day": {"one": "{0} روز", "other": "{0} روز"},
            "hour": {"one": "{0} ساعت", "other": "{0} ساعت"},
            "minute": {"one": "{0} دقیقه", "other": "{0} دقیقه"},
            "second": {"one": "{0} ثانیه", "other": "{0} ثانیه"},
            "microsecond": {"one": "{0} میکروثانیه", "other": "{0} میکروثانیه"},
        },
        "relative": {
            "year": {
                "future": {"other": "{0} سال بعد", "one": "{0} سال بعد"},
                "past": {"other": "{0} سال پیش", "one": "{0} سال پیش"},
            },
            "month": {
                "future": {"other": "{0} ماه بعد", "one": "{0} ماه بعد"},
                "past": {"other": "{0} ماه پیش", "one": "{0} ماه پیش"},
            },
            "week": {
                "future": {"other": "{0} هفته بعد", "one": "{0} هفته بعد"},
                "past": {"other": "{0} هفته پیش", "one": "{0} هفته پیش"},
            },
            "day": {
                "future": {"other": "{0} روز بعد", "one": "{0} روز بعد"},
                "past": {"other": "{0} روز پیش", "one": "{0} روز پیش"},
            },
            "hour": {
                "future": {"other": "{0} ساعت بعد", "one": "{0} ساعت بعد"},
                "past": {"other": "{0} ساعت پیش", "one": "{0} ساعت پیش"},
            },
            "minute": {
                "future": {"other": "{0} دقیقه بعد", "one": "{0} دقیقه بعد"},
                "past": {"other": "{0} دقیقه پیش", "one": "{0} دقیقه پیش"},
            },
            "second": {
                "future": {"other": "{0} ثانیه بعد", "one": "{0} ثانیه بعد"},
                "past": {"other": "{0} ثانیه پیش", "one": "{0} ثانیه پیش"},
            },
        },
        "day_periods": {
            "midnight": "نیمه\u200cشب",
            "am": "قبل\u200cازظهر",
            "noon": "ظهر",
            "pm": "بعدازظهر",
            "morning1": "صبح",
            "afternoon1": "عصر",
            "evening1": "عصر",
            "night1": "شب",
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
