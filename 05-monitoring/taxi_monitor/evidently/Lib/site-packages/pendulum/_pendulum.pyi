from __future__ import annotations

from datetime import date
from datetime import datetime
from datetime import time
from typing import NamedTuple

class Duration:
    years: int = 0
    months: int = 0
    weeks: int = 0
    days: int = 0
    remaining_days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    remaining_seconds: int = 0
    microseconds: int = 0

class PreciseDiff(NamedTuple):
    years: int
    months: int
    days: int
    hours: int
    minutes: int
    seconds: int
    microseconds: int
    total_days: int

def parse_iso8601(
    text: str,
) -> datetime | date | time | Duration: ...
def days_in_year(year: int) -> int: ...
def is_leap(year: int) -> bool: ...
def is_long_year(year: int) -> bool: ...
def local_time(
    unix_time: int, utc_offset: int, microseconds: int
) -> tuple[int, int, int, int, int, int, int]: ...
def precise_diff(d1: datetime | date, d2: datetime | date) -> PreciseDiff: ...
def week_day(year: int, month: int, day: int) -> int: ...
