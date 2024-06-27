from __future__ import annotations

from pendulum.locales.zh.custom import translations as custom_translations


"""
zh locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "other",
    "ordinal": lambda n: "other",
    "translations": {
        "days": {
            "abbreviated": {
                0: "周一",
                1: "周二",
                2: "周三",
                3: "周四",
                4: "周五",
                5: "周六",
                6: "周日",
            },
            "narrow": {0: "一", 1: "二", 2: "三", 3: "四", 4: "五", 5: "六", 6: "日"},
            "short": {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"},
            "wide": {
                0: "星期一",
                1: "星期二",
                2: "星期三",
                3: "星期四",
                4: "星期五",
                5: "星期六",
                6: "星期日",
            },
        },
        "months": {
            "abbreviated": {
                1: "1月",
                2: "2月",
                3: "3月",
                4: "4月",
                5: "5月",
                6: "6月",
                7: "7月",
                8: "8月",
                9: "9月",
                10: "10月",
                11: "11月",
                12: "12月",
            },
            "narrow": {
                1: "1",
                2: "2",
                3: "3",
                4: "4",
                5: "5",
                6: "6",
                7: "7",
                8: "8",
                9: "9",
                10: "10",
                11: "11",
                12: "12",
            },
            "wide": {
                1: "一月",
                2: "二月",
                3: "三月",
                4: "四月",
                5: "五月",
                6: "六月",
                7: "七月",
                8: "八月",
                9: "九月",
                10: "十月",
                11: "十一月",
                12: "十二月",
            },
        },
        "units": {
            "year": {"other": "{0}年"},
            "month": {"other": "{0}个月"},
            "week": {"other": "{0}周"},
            "day": {"other": "{0}天"},
            "hour": {"other": "{0}小时"},
            "minute": {"other": "{0}分钟"},
            "second": {"other": "{0}秒钟"},
            "microsecond": {"other": "{0}微秒"},
        },
        "relative": {
            "year": {"future": {"other": "{0}年后"}, "past": {"other": "{0}年前"}},
            "month": {"future": {"other": "{0}个月后"}, "past": {"other": "{0}个月前"}},
            "week": {"future": {"other": "{0}周后"}, "past": {"other": "{0}周前"}},
            "day": {"future": {"other": "{0}天后"}, "past": {"other": "{0}天前"}},
            "hour": {"future": {"other": "{0}小时后"}, "past": {"other": "{0}小时前"}},
            "minute": {"future": {"other": "{0}分钟后"}, "past": {"other": "{0}分钟前"}},
            "second": {"future": {"other": "{0}秒钟后"}, "past": {"other": "{0}秒钟前"}},
        },
        "day_periods": {
            "midnight": "午夜",
            "am": "上午",
            "pm": "下午",
            "morning1": "清晨",
            "morning2": "上午",
            "afternoon1": "下午",
            "afternoon2": "下午",
            "evening1": "晚上",
            "night1": "凌晨",
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
