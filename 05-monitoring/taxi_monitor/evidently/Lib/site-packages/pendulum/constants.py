# The day constants
from __future__ import annotations


# Number of X in Y.
YEARS_PER_CENTURY = 100
YEARS_PER_DECADE = 10
MONTHS_PER_YEAR = 12
WEEKS_PER_YEAR = 52
DAYS_PER_WEEK = 7
HOURS_PER_DAY = 24
MINUTES_PER_HOUR = 60
SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = MINUTES_PER_HOUR * SECONDS_PER_MINUTE
SECONDS_PER_DAY = HOURS_PER_DAY * SECONDS_PER_HOUR
US_PER_SECOND = 1000000

# Formats
ATOM = "YYYY-MM-DDTHH:mm:ssZ"
COOKIE = "dddd, DD-MMM-YYYY HH:mm:ss zz"
ISO8601 = "YYYY-MM-DDTHH:mm:ssZ"
ISO8601_EXTENDED = "YYYY-MM-DDTHH:mm:ss.SSSSSSZ"
RFC822 = "ddd, DD MMM YY HH:mm:ss ZZ"
RFC850 = "dddd, DD-MMM-YY HH:mm:ss zz"
RFC1036 = "ddd, DD MMM YY HH:mm:ss ZZ"
RFC1123 = "ddd, DD MMM YYYY HH:mm:ss ZZ"
RFC2822 = "ddd, DD MMM YYYY HH:mm:ss ZZ"
RFC3339 = ISO8601
RFC3339_EXTENDED = ISO8601_EXTENDED
RSS = "ddd, DD MMM YYYY HH:mm:ss ZZ"
W3C = ISO8601


EPOCH_YEAR = 1970

DAYS_PER_N_YEAR = 365
DAYS_PER_L_YEAR = 366

USECS_PER_SEC = 1000000

SECS_PER_MIN = 60
SECS_PER_HOUR = 60 * SECS_PER_MIN
SECS_PER_DAY = SECS_PER_HOUR * 24

# 400-year chunks always have 146097 days (20871 weeks).
SECS_PER_400_YEARS = 146097 * SECS_PER_DAY

# The number of seconds in an aligned 100-year chunk, for those that
# do not begin with a leap year and those that do respectively.
SECS_PER_100_YEARS = (
    (76 * DAYS_PER_N_YEAR + 24 * DAYS_PER_L_YEAR) * SECS_PER_DAY,
    (75 * DAYS_PER_N_YEAR + 25 * DAYS_PER_L_YEAR) * SECS_PER_DAY,
)

# The number of seconds in an aligned 4-year chunk, for those that
# do not begin with a leap year and those that do respectively.
SECS_PER_4_YEARS = (
    (4 * DAYS_PER_N_YEAR + 0 * DAYS_PER_L_YEAR) * SECS_PER_DAY,
    (3 * DAYS_PER_N_YEAR + 1 * DAYS_PER_L_YEAR) * SECS_PER_DAY,
)

# The number of seconds in non-leap and leap years respectively.
SECS_PER_YEAR = (DAYS_PER_N_YEAR * SECS_PER_DAY, DAYS_PER_L_YEAR * SECS_PER_DAY)

DAYS_PER_YEAR = (DAYS_PER_N_YEAR, DAYS_PER_L_YEAR)

# The month lengths in non-leap and leap years respectively.
DAYS_PER_MONTHS = (
    (-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    (-1, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
)

# The day offsets of the beginning of each (1-based) month in non-leap
# and leap years respectively.
# For example, in a leap year there are 335 days before December.
MONTHS_OFFSETS = (
    (-1, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365),
    (-1, 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366),
)

DAY_OF_WEEK_TABLE = (0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4)

TM_SUNDAY = 0
TM_MONDAY = 1
TM_TUESDAY = 2
TM_WEDNESDAY = 3
TM_THURSDAY = 4
TM_FRIDAY = 5
TM_SATURDAY = 6

TM_JANUARY = 0
TM_FEBRUARY = 1
TM_MARCH = 2
TM_APRIL = 3
TM_MAY = 4
TM_JUNE = 5
TM_JULY = 6
TM_AUGUST = 7
TM_SEPTEMBER = 8
TM_OCTOBER = 9
TM_NOVEMBER = 10
TM_DECEMBER = 11
