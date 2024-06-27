from __future__ import annotations

from pendulum.locales.ko.custom import translations as custom_translations


"""
ko locale file.

It has been generated automatically and must not be modified directly.
"""


locale = {
    "plural": lambda n: "other",
    "ordinal": lambda n: "other",
    "translations": {
        "days": {
            "abbreviated": {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"},
            "narrow": {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"},
            "short": {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"},
            "wide": {
                0: "월요일",
                1: "화요일",
                2: "수요일",
                3: "목요일",
                4: "금요일",
                5: "토요일",
                6: "일요일",
            },
        },
        "months": {
            "abbreviated": {
                1: "1월",
                2: "2월",
                3: "3월",
                4: "4월",
                5: "5월",
                6: "6월",
                7: "7월",
                8: "8월",
                9: "9월",
                10: "10월",
                11: "11월",
                12: "12월",
            },
            "narrow": {
                1: "1월",
                2: "2월",
                3: "3월",
                4: "4월",
                5: "5월",
                6: "6월",
                7: "7월",
                8: "8월",
                9: "9월",
                10: "10월",
                11: "11월",
                12: "12월",
            },
            "wide": {
                1: "1월",
                2: "2월",
                3: "3월",
                4: "4월",
                5: "5월",
                6: "6월",
                7: "7월",
                8: "8월",
                9: "9월",
                10: "10월",
                11: "11월",
                12: "12월",
            },
        },
        "units": {
            "year": {"other": "{0}년"},
            "month": {"other": "{0}개월"},
            "week": {"other": "{0}주"},
            "day": {"other": "{0}일"},
            "hour": {"other": "{0}시간"},
            "minute": {"other": "{0}분"},
            "second": {"other": "{0}초"},
            "microsecond": {"other": "{0}마이크로초"},
        },
        "relative": {
            "year": {"future": {"other": "{0}년 후"}, "past": {"other": "{0}년 전"}},
            "month": {"future": {"other": "{0}개월 후"}, "past": {"other": "{0}개월 전"}},
            "week": {"future": {"other": "{0}주 후"}, "past": {"other": "{0}주 전"}},
            "day": {"future": {"other": "{0}일 후"}, "past": {"other": "{0}일 전"}},
            "hour": {"future": {"other": "{0}시간 후"}, "past": {"other": "{0}시간 전"}},
            "minute": {"future": {"other": "{0}분 후"}, "past": {"other": "{0}분 전"}},
            "second": {"future": {"other": "{0}초 후"}, "past": {"other": "{0}초 전"}},
        },
        "day_periods": {
            "midnight": "자정",
            "am": "오전",
            "noon": "정오",
            "pm": "오후",
            "morning1": "새벽",
            "morning2": "오전",
            "afternoon1": "오후",
            "evening1": "저녁",
            "night1": "밤",
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
