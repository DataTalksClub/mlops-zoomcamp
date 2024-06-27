/* ------------------------------------------------------------------------- */

#include <Python.h>
#include <datetime.h>
#include <structmember.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#ifndef PyVarObject_HEAD_INIT
#define PyVarObject_HEAD_INIT(type, size) PyObject_HEAD_INIT(type) size,
#endif


/* ------------------------------------------------------------------------- */

#define EPOCH_YEAR 1970

#define DAYS_PER_N_YEAR 365
#define DAYS_PER_L_YEAR 366

#define USECS_PER_SEC 1000000

#define SECS_PER_MIN 60
#define SECS_PER_HOUR (60 * SECS_PER_MIN)
#define SECS_PER_DAY (SECS_PER_HOUR * 24)

// 400-year chunks always have 146097 days (20871 weeks).
#define DAYS_PER_400_YEARS 146097L
#define SECS_PER_400_YEARS ((int64_t)DAYS_PER_400_YEARS * (int64_t)SECS_PER_DAY)

// The number of seconds in an aligned 100-year chunk, for those that
// do not begin with a leap year and those that do respectively.
const int64_t SECS_PER_100_YEARS[2] = {
    (uint64_t)(76L * DAYS_PER_N_YEAR + 24L * DAYS_PER_L_YEAR) * SECS_PER_DAY,
    (uint64_t)(75L * DAYS_PER_N_YEAR + 25L * DAYS_PER_L_YEAR) * SECS_PER_DAY
};

// The number of seconds in an aligned 4-year chunk, for those that
// do not begin with a leap year and those that do respectively.
const int32_t SECS_PER_4_YEARS[2] = {
    (4 * DAYS_PER_N_YEAR + 0 * DAYS_PER_L_YEAR) * SECS_PER_DAY,
    (3 * DAYS_PER_N_YEAR + 1 * DAYS_PER_L_YEAR) * SECS_PER_DAY
};

// The number of seconds in non-leap and leap years respectively.
const int32_t SECS_PER_YEAR[2] = {
    DAYS_PER_N_YEAR * SECS_PER_DAY,
    DAYS_PER_L_YEAR * SECS_PER_DAY
};

#define MONTHS_PER_YEAR 12

// The month lengths in non-leap and leap years respectively.
const int32_t DAYS_PER_MONTHS[2][13] = {
    {-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31},
    {-1, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31}
};

// The day offsets of the beginning of each (1-based) month in non-leap
// and leap years respectively.
// For example, in a leap year there are 335 days before December.
const int32_t MONTHS_OFFSETS[2][14] = {
    {-1, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365},
    {-1, 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366}
};

const int DAY_OF_WEEK_TABLE[12] = {
    0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4
};

#define TM_SUNDAY 0
#define TM_MONDAY 1
#define TM_TUESDAY 2
#define TM_WEDNESDAY 3
#define TM_THURSDAY 4
#define TM_FRIDAY 5
#define TM_SATURDAY 6

#define TM_JANUARY 0
#define TM_FEBRUARY 1
#define TM_MARCH 2
#define TM_APRIL 3
#define TM_MAY 4
#define TM_JUNE 5
#define TM_JULY 6
#define TM_AUGUST 7
#define TM_SEPTEMBER 8
#define TM_OCTOBER 9
#define TM_NOVEMBER 10
#define TM_DECEMBER 11

// Parsing errors
const int PARSER_INVALID_ISO8601 = 0;
const int PARSER_INVALID_DATE = 1;
const int PARSER_INVALID_TIME = 2;
const int PARSER_INVALID_WEEK_DATE = 3;
const int PARSER_INVALID_WEEK_NUMBER = 4;
const int PARSER_INVALID_WEEKDAY_NUMBER = 5;
const int PARSER_INVALID_ORDINAL_DAY_FOR_YEAR = 6;
const int PARSER_INVALID_MONTH_OR_DAY = 7;
const int PARSER_INVALID_MONTH = 8;
const int PARSER_INVALID_DAY_FOR_MONTH = 9;
const int PARSER_INVALID_HOUR = 10;
const int PARSER_INVALID_MINUTE = 11;
const int PARSER_INVALID_SECOND = 12;
const int PARSER_INVALID_SUBSECOND = 13;
const int PARSER_INVALID_TZ_OFFSET = 14;
const int PARSER_INVALID_DURATION = 15;
const int PARSER_INVALID_DURATION_FLOAT_YEAR_MONTH_NOT_SUPPORTED = 16;

const char PARSER_ERRORS[17][80] = {
    "Invalid ISO 8601 string",
    "Invalid date",
    "Invalid time",
    "Invalid week date",
    "Invalid week number",
    "Invalid weekday number",
    "Invalid ordinal day for year",
    "Invalid month and/or day",
    "Invalid month",
    "Invalid day for month",
    "Invalid hour",
    "Invalid minute",
    "Invalid second",
    "Invalid subsecond",
    "Invalid timezone offset",
    "Invalid duration",
    "Float years and months are not supported"
};

/* ------------------------------------------------------------------------- */


int p(int y) {
    return y + y/4 - y/100 + y/400;
}

int is_leap(int year) {
    return year % 4 == 0 && (year % 100 != 0 || year % 400 == 0);
}

int week_day(int year, int month, int day) {
    int y;
    int w;

    y = year - (month < 3);

    w = (p(y) + DAY_OF_WEEK_TABLE[month - 1] + day) % 7;

    if (!w) {
        w = 7;
    }

    return w;
}

int days_in_year(int year) {
    if (is_leap(year)) {
        return DAYS_PER_L_YEAR;
    }

    return DAYS_PER_N_YEAR;
}

int is_long_year(int year) {
    return (p(year) % 7 == 4) || (p(year - 1) % 7 == 3);
}


/* ------------------------ Custom Types ------------------------------- */


/*
 * class FixedOffset(tzinfo):
 */
typedef struct {
    PyObject_HEAD
    int offset;
    char *tzname;
} FixedOffset;

/*
 * def __init__(self, offset):
 *     self.offset = offset
*/
static int FixedOffset_init(FixedOffset *self, PyObject *args, PyObject *kwargs) {
    int offset;
    char *tzname = NULL;

    static char *kwlist[] = {"offset", "tzname", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "i|s", kwlist, &offset, &tzname))
        return -1;

    self->offset = offset;
    self->tzname = tzname;

    return 0;
}

/*
 * def utcoffset(self, dt):
 *     return timedelta(seconds=self.offset * 60)
 */
static PyObject *FixedOffset_utcoffset(FixedOffset *self, PyObject *args) {
    return PyDelta_FromDSU(0, self->offset, 0);
}

/*
 * def dst(self, dt):
 *     return timedelta(seconds=self.offset * 60)
 */
static PyObject *FixedOffset_dst(FixedOffset *self, PyObject *args) {
    return PyDelta_FromDSU(0, self->offset, 0);
}

/*
 * def tzname(self, dt):
 *     sign = '+'
 *     if self.offset < 0:
 *         sign = '-'
 *     return "%s%d:%d" % (sign, self.offset / 60, self.offset % 60)
 */
static PyObject *FixedOffset_tzname(FixedOffset *self, PyObject *args) {
    if (self->tzname != NULL) {
        return PyUnicode_FromString(self->tzname);
    }

    char tzname_[7] = {0};
    char sign = '+';
    int offset = self->offset;

    if (offset < 0) {
        sign = '-';
        offset *= -1;
    }

    sprintf(
        tzname_,
        "%c%02d:%02d",
        sign,
        offset / SECS_PER_HOUR,
        offset / SECS_PER_MIN % SECS_PER_MIN
    );

    return PyUnicode_FromString(tzname_);
}

/*
 * def __repr__(self):
 *     return self.tzname()
 */
static PyObject *FixedOffset_repr(FixedOffset *self) {
    return FixedOffset_tzname(self, NULL);
}

/*
 * Class member / class attributes
 */
static PyMemberDef FixedOffset_members[] = {
    {"offset", T_INT, offsetof(FixedOffset, offset), 0, "UTC offset"},
    {NULL}
};

/*
 * Class methods
 */
static PyMethodDef FixedOffset_methods[] = {
    {"utcoffset", (PyCFunction)FixedOffset_utcoffset, METH_VARARGS, ""},
    {"dst",       (PyCFunction)FixedOffset_dst,       METH_VARARGS, ""},
    {"tzname",    (PyCFunction)FixedOffset_tzname,    METH_VARARGS, ""},
    {NULL}
};

static PyTypeObject FixedOffset_type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "FixedOffset_type",             /* tp_name */
    sizeof(FixedOffset),                    /* tp_basicsize */
    0,                                      /* tp_itemsize */
    0,                                      /* tp_dealloc */
    0,                                      /* tp_print */
    0,                                      /* tp_getattr */
    0,                                      /* tp_setattr */
    0,                                      /* tp_as_async */
    (reprfunc)FixedOffset_repr,             /* tp_repr */
    0,                                      /* tp_as_number */
    0,                                      /* tp_as_sequence */
    0,                                      /* tp_as_mapping */
    0,                                      /* tp_hash  */
    0,                                      /* tp_call */
    (reprfunc)FixedOffset_repr,             /* tp_str */
    0,                                      /* tp_getattro */
    0,                                      /* tp_setattro */
    0,                                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE, /* tp_flags */
    "TZInfo with fixed offset",             /* tp_doc */
};

/*
 * Instantiate new FixedOffset_type object
 * Skip overhead of calling PyObject_New and PyObject_Init.
 * Directly allocate object.
 */
static PyObject *new_fixed_offset_ex(int offset, char *name, PyTypeObject *type) {
    FixedOffset *self = (FixedOffset *) (type->tp_alloc(type, 0));

    if (self != NULL)
        self->offset = offset;
        self->tzname = name;

    return (PyObject *) self;
}

#define new_fixed_offset(offset, name) new_fixed_offset_ex(offset, name, &FixedOffset_type)


/*
 * class Duration():
 */
typedef struct {
    PyObject_HEAD
    int years;
    int months;
    int weeks;
    int days;
    int hours;
    int minutes;
    int seconds;
    int microseconds;
} Duration;

/*
 * def __init__(self, years, months, days, hours, minutes, seconds, microseconds):
 *     self.years = years
 *     # ...
*/
static int Duration_init(Duration *self, PyObject *args, PyObject *kwargs) {
    int years;
    int months;
    int weeks;
    int days;
    int hours;
    int minutes;
    int seconds;
    int microseconds;

    if (!PyArg_ParseTuple(args, "iiiiiiii", &years, &months, &weeks, &days, &hours, &minutes, &seconds, &microseconds))
        return -1;

    self->years = years;
    self->months = months;
    self->weeks = weeks;
    self->days = days;
    self->hours = hours;
    self->minutes = minutes;
    self->seconds = seconds;
    self->microseconds = microseconds;

    return 0;
}

/*
 * def __repr__(self):
 *     return '{} years {} months {} days {} hours {} minutes {} seconds {} microseconds'.format(
 *         self.years, self.months, self.days, self.minutes, self.hours, self.seconds, self.microseconds
 *     )
 */
static PyObject *Duration_repr(Duration *self) {
    char repr[82] = {0};

    sprintf(
        repr,
        "%d years %d months %d weeks %d days %d hours %d minutes %d seconds %d microseconds",
        self->years,
        self->months,
        self->weeks,
        self->days,
        self->hours,
        self->minutes,
        self->seconds,
        self->microseconds
    );

    return PyUnicode_FromString(repr);
}

/*
 * Instantiate new Duration_type object
 * Skip overhead of calling PyObject_New and PyObject_Init.
 * Directly allocate object.
 */
static PyObject *new_duration_ex(int years, int months, int weeks, int days, int hours, int minutes, int seconds, int microseconds, PyTypeObject *type) {
    Duration *self = (Duration *) (type->tp_alloc(type, 0));

    if (self != NULL) {
        self->years = years;
        self->months = months;
        self->weeks = weeks;
        self->days = days;
        self->hours = hours;
        self->minutes = minutes;
        self->seconds = seconds;
        self->microseconds = microseconds;
    }

    return (PyObject *) self;
}

/*
 * Class member / class attributes
 */
static PyMemberDef Duration_members[] = {
    {"years", T_INT, offsetof(Duration, years), 0, "years in duration"},
    {"months", T_INT, offsetof(Duration, months), 0, "months in duration"},
    {"weeks", T_INT, offsetof(Duration, weeks), 0, "weeks in duration"},
    {"days", T_INT, offsetof(Duration, days), 0, "days in duration"},
    {"remaining_days", T_INT, offsetof(Duration, days), 0, "days in duration"},
    {"hours", T_INT, offsetof(Duration, hours), 0, "hours in duration"},
    {"minutes", T_INT, offsetof(Duration, minutes), 0, "minutes in duration"},
    {"seconds", T_INT, offsetof(Duration, seconds), 0, "seconds in duration"},
    {"remaining_seconds", T_INT, offsetof(Duration, seconds), 0, "seconds in duration"},
    {"microseconds", T_INT, offsetof(Duration, microseconds), 0, "microseconds in duration"},
    {NULL}
};

static PyTypeObject Duration_type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "Duration",                             /* tp_name */
    sizeof(Duration),                       /* tp_basicsize */
    0,                                      /* tp_itemsize */
    0,                                      /* tp_dealloc */
    0,                                      /* tp_print */
    0,                                      /* tp_getattr */
    0,                                      /* tp_setattr */
    0,                                      /* tp_as_async */
    (reprfunc)Duration_repr,                /* tp_repr */
    0,                                      /* tp_as_number */
    0,                                      /* tp_as_sequence */
    0,                                      /* tp_as_mapping */
    0,                                      /* tp_hash  */
    0,                                      /* tp_call */
    (reprfunc)Duration_repr,                /* tp_str */
    0,                                      /* tp_getattro */
    0,                                      /* tp_setattro */
    0,                                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE, /* tp_flags */
    "Duration",                             /* tp_doc */
};

#define new_duration(years, months, weeks, days, hours, minutes, seconds, microseconds) new_duration_ex(years, months, weeks, days, hours, minutes, seconds, microseconds, &Duration_type)

typedef struct {
    int is_date;
    int is_time;
    int is_datetime;
    int is_duration;
    int is_period;
    int ambiguous;
    int year;
    int month;
    int day;
    int hour;
    int minute;
    int second;
    int microsecond;
    int offset;
    int has_offset;
    char *tzname;
    int years;
    int months;
    int weeks;
    int days;
    int hours;
    int minutes;
    int seconds;
    int microseconds;
    int error;
} Parsed;


Parsed* new_parsed() {
    Parsed *parsed;

    if((parsed = malloc(sizeof *parsed)) != NULL) {
        parsed->is_date = 0;
        parsed->is_time = 0;
        parsed->is_datetime = 0;
        parsed->is_duration = 0;
        parsed->is_period = 0;

        parsed->ambiguous = 0;
        parsed->year = 0;
        parsed->month = 1;
        parsed->day = 1;
        parsed->hour = 0;
        parsed->minute = 0;
        parsed->second = 0;
        parsed->microsecond = 0;
        parsed->offset = 0;
        parsed->has_offset = 0;
        parsed->tzname = NULL;

        parsed->years = 0;
        parsed->months = 0;
        parsed->weeks = 0;
        parsed->days = 0;
        parsed->hours = 0;
        parsed->minutes = 0;
        parsed->seconds = 0;
        parsed->microseconds = 0;

        parsed->error = -1;
    }

    return parsed;
}


/* -------------------------- Functions --------------------------*/

Parsed* _parse_iso8601_datetime(char *str, Parsed *parsed) {
    char* c;
    int monthday = 0;
    int week = 0;
    int weekday = 1;
    int ordinal;
    int tz_sign = 0;
    int leap = 0;
    int separators = 0;
    int time = 0;
    int has_hour = 0;
    int i;
    int j;

    // Assuming date only for now
    parsed->is_date = 1;

    c = str;

    for (i = 0; i < 4; i++) {
        if (*c >= '0' && *c <= '9') {
            parsed->year = 10 * parsed->year + *c++ - '0';
        } else {
            parsed->error = PARSER_INVALID_ISO8601;

            return NULL;
        }
    }

    leap = is_leap(parsed->year);

    // Optional separator
    if (*c == '-') {
        separators++;
        c++;
    }

    // Checking for week dates
    if (*c == 'W') {
        c++;

        i = 0;
        while (*c != '\0' && *c != ' ' && *c != 'T') {
            if (*c == '-') {
                separators++;
                c++;
                continue;
            }

            week = 10 * week + *c++ - '0';

            i++;
        }

        switch (i) {
            case 2:
                // Only week number
                break;
            case 3:
                // Week with weekday
                if (!(separators == 0 || separators == 2)) {
                    // We should have 2 or no separator
                    parsed->error = PARSER_INVALID_WEEK_DATE;

                    return NULL;
                }

                weekday = week % 10;
                week /= 10;

                break;
            default:
                // Any other case is wrong
                parsed->error = PARSER_INVALID_WEEK_DATE;

                return NULL;
        }

        // Checks
        if (week > 53 || (week > 52 && !is_long_year(parsed->year))) {
            parsed->error = PARSER_INVALID_WEEK_NUMBER;

            return NULL;
        }

        if (weekday > 7) {
            parsed->error = PARSER_INVALID_WEEKDAY_NUMBER;

            return NULL;
        }

        // Calculating ordinal day
        ordinal = week * 7 + weekday - (week_day(parsed->year, 1, 4) + 3);

        if (ordinal < 1) {
            // Previous year
            ordinal += days_in_year(parsed->year - 1);
            parsed->year -= 1;
            leap = is_leap(parsed->year);
        }

        if (ordinal > days_in_year(parsed->year)) {
            // Next year
            ordinal -= days_in_year(parsed->year);
            parsed->year += 1;
            leap = is_leap(parsed->year);
        }

        for (j = 1; j < 14; j++) {
            if (ordinal <= MONTHS_OFFSETS[leap][j]) {
                parsed->day = ordinal - MONTHS_OFFSETS[leap][j - 1];
                parsed->month = j - 1;

                break;
            }
        }
    } else {
        // At this point we need to check the number
        // of characters until the end of the date part
        // (or the end of the string).
        //
        // If two, we have only a month if there is a separator, it may be a time otherwise.
        // If three, we have an ordinal date.
        // If four, we have a complete date
        i = 0;
        while (*c != '\0' && *c != ' ' && *c != 'T') {
            if (*c == '-') {
                separators++;
                c++;
                continue;
            }

            if (!(*c >= '0' && *c <='9')) {
                parsed->error = PARSER_INVALID_DATE;

                return NULL;
            }

            monthday = 10 * monthday + *c++ - '0';

            i++;
        }

        switch (i) {
            case 0:
                // No month/day specified (only a year)
                break;
            case 2:
                if (!separators) {
                    // The date looks like 201207
                    // which is invalid for a date
                    // But it might be a time in the form hhmmss
                    parsed->ambiguous = 1;
                } else if (separators > 1) {
                    parsed->error = PARSER_INVALID_DATE;

                    return NULL;
                }

                parsed->month = monthday;
                break;
            case 3:
                // Ordinal day
                if (separators > 1) {
                    parsed->error = PARSER_INVALID_DATE;

                    return NULL;
                }

                if (monthday < 1 || monthday > MONTHS_OFFSETS[leap][13]) {
                    parsed->error = PARSER_INVALID_ORDINAL_DAY_FOR_YEAR;

                    return NULL;
                }

                for (j = 1; j < 14; j++) {
                    if (monthday <= MONTHS_OFFSETS[leap][j]) {
                        parsed->day = monthday - MONTHS_OFFSETS[leap][j - 1];
                        parsed->month = j - 1;

                        break;
                    }
                }

                break;
            case 4:
                // Month and day
                parsed->month = monthday / 100;
                parsed->day = monthday % 100;

                break;
            default:
                parsed->error = PARSER_INVALID_MONTH_OR_DAY;

                return NULL;
        }
    }

    // Checks
    if (separators && !monthday && !week) {
        parsed->error = PARSER_INVALID_DATE;

        return NULL;
    }

    if (parsed->month > 12) {
        parsed->error = PARSER_INVALID_MONTH;

        return NULL;
    }

    if (parsed->day > DAYS_PER_MONTHS[leap][parsed->month]) {
        parsed->error = PARSER_INVALID_DAY_FOR_MONTH;

        return NULL;
    }

    separators = 0;
    if (*c == 'T' || *c == ' ') {
        if (parsed->ambiguous) {
            parsed->error = PARSER_INVALID_DATE;

            return NULL;
        }

        // We have time so we have a datetime
        parsed->is_datetime = 1;
        parsed->is_date = 0;

        c++;

        // Grabbing time information
        i = 0;
        while (*c != '\0' && *c != '.' && *c != ',' && *c != 'Z' && *c != '+' && *c != '-') {
            if (*c == ':') {
                separators++;
                c++;
                continue;
            }

            if (!(*c >= '0' && *c <='9')) {
                parsed->error = PARSER_INVALID_TIME;

                return NULL;
            }

            time = 10 * time + *c++ - '0';
            i++;
        }

        switch (i) {
            case 2:
                // Hours only
                if (separators > 0) {
                    // Extraneous separators
                    parsed->error = PARSER_INVALID_TIME;

                    return NULL;
                }

                parsed->hour = time;
                has_hour = 1;
                break;
            case 4:
                // Hours and minutes
                if (separators > 1) {
                    // Extraneous separators
                    parsed->error = PARSER_INVALID_TIME;

                    return NULL;
                }

                parsed->hour = time / 100;
                parsed->minute = time % 100;
                has_hour = 1;
                break;
            case 6:
                // Hours, minutes and seconds
                if (!(separators == 0 || separators == 2)) {
                    // We should have either two separators or none
                    parsed->error = PARSER_INVALID_TIME;

                    return NULL;
                }

                parsed->hour = time / 10000;
                parsed->minute = time / 100 % 100;
                parsed->second = time % 100;
                has_hour = 1;
                break;
            default:
                // Any other case is wrong
                parsed->error = PARSER_INVALID_TIME;

                return NULL;
        }

        // Checks
        if (parsed->hour > 23) {
            parsed->error = PARSER_INVALID_HOUR;

            return NULL;
        }

        if (parsed->minute > 59) {
            parsed->error = PARSER_INVALID_MINUTE;

            return NULL;
        }

        if (parsed->second > 59) {
            parsed->error = PARSER_INVALID_SECOND;

            return NULL;
        }

        // Subsecond
        if (*c == '.' || *c == ',') {
            c++;

            time = 0;
            i = 0;
            while (*c != '\0' && *c != 'Z' && *c != '+' && *c != '-') {
                if (!(*c >= '0' && *c <='9')) {
                    parsed->error = PARSER_INVALID_SUBSECOND;

                    return NULL;
                }

                time = 10 * time + *c++ - '0';
                i++;
            }

            // adjust to microseconds
            if (i > 6) {
                parsed->microsecond = time / pow(10, i - 6);
            } else if (i <= 6) {
                parsed->microsecond = time * pow(10, 6 - i);
            }
        }

        // Timezone
        if (*c == 'Z') {
            parsed->has_offset = 1;
            parsed->tzname = "UTC";
            c++;
        } else if (*c == '+' || *c == '-') {
            tz_sign = 1;
            if (*c == '-') {
                tz_sign = -1;
            }

            parsed->has_offset = 1;
            c++;

            i = 0;
            time = 0;
            separators = 0;
            while (*c != '\0') {
                if (*c == ':') {
                    separators++;
                    c++;
                    continue;
                }

                if (!(*c >= '0' && *c <= '9')) {
                    parsed->error = PARSER_INVALID_TZ_OFFSET;

                    return NULL;
                }

                time = 10 * time + *c++ - '0';
                i++;
            }

            switch (i) {
                case 2:
                    // hh Format
                    if (separators) {
                        // Extraneous separators
                        parsed->error = PARSER_INVALID_TZ_OFFSET;

                        return NULL;
                    }

                    parsed->offset = tz_sign * (time * 3600);
                    break;
                case 4:
                    // hhmm Format
                    if (separators > 1) {
                        // Extraneous separators
                        parsed->error = PARSER_INVALID_TZ_OFFSET;

                        return NULL;
                    }

                    parsed->offset = tz_sign * ((time / 100 * 3600) + (time % 100 * 60));
                    break;
                default:
                    // Wrong format
                    parsed->error = PARSER_INVALID_TZ_OFFSET;

                    return NULL;
            }
        }
    }

    // At this point we should be at the end of the string
    // If not, the string is invalid
    if (*c != '\0') {
        parsed->error = PARSER_INVALID_ISO8601;

        return NULL;
    }

    return parsed;
}


Parsed* _parse_iso8601_duration(char *str, Parsed *parsed) {
    char* c;
    int value = 0;
    int grabbed = 0;
    int in_time = 0;
    int in_fraction = 0;
    int fraction_length = 0;
    int has_fractional = 0;
    int fraction = 0;
    int has_ymd = 0;
    int has_week = 0;
    int has_year = 0;
    int has_month = 0;
    int has_day = 0;
    int has_hour = 0;
    int has_minute = 0;
    int has_second = 0;

    c = str;

    // Removing P operator
    c++;

    parsed->is_duration = 1;

    for (; *c != '\0'; c++) {
        switch (*c) {
            case 'Y':
                if (!grabbed || in_time || has_week || has_ymd) {
                    // No value grabbed
                    parsed->error = PARSER_INVALID_DURATION;

                    return NULL;
                }

                if (fraction) {
                    parsed->error = PARSER_INVALID_DURATION_FLOAT_YEAR_MONTH_NOT_SUPPORTED;

                    return NULL;
                }

                parsed->years = value;

                grabbed = 0;
                value = 0;
                fraction = 0;
                in_fraction = 0;
                has_ymd = 1;
                has_year = 1;

                break;
            case 'M':
                if (!grabbed || has_week) {
                    // No value grabbed
                    parsed->error = PARSER_INVALID_DURATION;

                    return NULL;
                }

                if (in_time) {
                    if (has_second) {
                        parsed->error = PARSER_INVALID_DURATION;

                        return NULL;
                    }

                    if (has_fractional) {
                        parsed->error = PARSER_INVALID_DURATION;

                        return NULL;
                    }

                    parsed->minutes = value;
                    if (fraction) {
                        parsed->seconds = fraction * 6;
                        has_fractional = 1;
                    }

                    has_minute = 1;
                } else {
                    if (fraction) {
                        parsed->error = PARSER_INVALID_DURATION_FLOAT_YEAR_MONTH_NOT_SUPPORTED;

                        return NULL;
                    }

                    if (has_month || has_day) {
                        parsed->error = PARSER_INVALID_DURATION;

                        return NULL;
                    }

                    parsed->months = value;
                    has_ymd = 1;
                    has_month = 1;
                }

                grabbed = 0;
                value = 0;
                fraction = 0;
                in_fraction = 0;

                break;
            case 'D':
                if (!grabbed || in_time || has_week) {
                    // No value grabbed
                    parsed->error = PARSER_INVALID_DURATION;

                    return NULL;
                }

                if (has_day) {
                    parsed->error = PARSER_INVALID_DURATION;

                    return NULL;
                }

                parsed->days = value;
                if (fraction) {
                    parsed->hours = fraction * 2.4;
                    has_fractional = 1;
                }

                grabbed = 0;
                value = 0;
                fraction = 0;
                in_fraction = 0;
                has_ymd = 1;
                has_day = 1;

                break;
            case 'T':
                if (grabbed) {
                    parsed->error = PARSER_INVALID_DURATION;

                    return NULL;
                }

                in_time = 1;

                break;
            case 'H':
                if (!grabbed || !in_time || has_week) {
                    // No value grabbed
                    parsed->error = PARSER_INVALID_DURATION;

                    return NULL;
                }

                if (has_hour || has_second || has_minute) {
                    parsed->error = PARSER_INVALID_DURATION;

                    return NULL;
                }

                if (has_fractional) {
                    parsed->error = PARSER_INVALID_DURATION;

                    return NULL;
                }

                parsed->hours = value;
                if (fraction) {
                    parsed->minutes = fraction * 6;
                    has_fractional = 1;
                }

                grabbed = 0;
                value = 0;
                fraction = 0;
                in_fraction = 0;
                has_hour = 1;

                break;
            case 'S':
                if (!grabbed || !in_time || has_week) {
                    // No value grabbed
                    parsed->error = PARSER_INVALID_DURATION;

                    return NULL;
                }

                if (has_second) {
                    parsed->error = PARSER_INVALID_DURATION;

                    return NULL;
                }

                if (has_fractional) {
                    parsed->error = PARSER_INVALID_DURATION;

                    return NULL;
                }

                if (fraction) {
                    parsed->seconds = value;
                    if (fraction_length > 6) {
                        parsed->microseconds = fraction / pow(10, fraction_length - 6);
                    } else {
                        parsed->microseconds = fraction * pow(10, 6 - fraction_length);
                    }
                    has_fractional = 1;
                } else {
                    parsed->seconds = value;
                }

                grabbed = 0;
                value = 0;
                fraction = 0;
                in_fraction = 0;
                has_second = 1;

                break;
            case 'W':
                if (!grabbed || in_time || has_ymd) {
                    // No value grabbed
                    parsed->error = PARSER_INVALID_DURATION;

                    return NULL;
                }

                parsed->weeks = value;
                if (fraction) {
                    float days;
                    days = fraction * 0.7;
                    parsed->hours = (int) ((days - (int) days) * 24);
                    parsed->days = (int) days;
                }

                grabbed = 0;
                value = 0;
                fraction = 0;
                in_fraction = 0;
                has_week = 1;

                break;
            case '.':
                if (!grabbed || has_fractional) {
                    // No value grabbed
                    parsed->error = PARSER_INVALID_DURATION;

                    return NULL;
                }

                in_fraction = 1;

                break;
            case ',':
                if (!grabbed || has_fractional) {
                    // No value grabbed
                    parsed->error = PARSER_INVALID_DURATION;

                    return NULL;
                }

                in_fraction = 1;

                break;
            default:
                if (*c >= '0' && *c <='9') {
                    if (in_fraction) {
                        fraction = 10 * fraction + *c - '0';
                        fraction_length++;
                    } else {
                        value = 10 * value + *c - '0';
                        grabbed = 1;
                    }
                    break;
                }

                parsed->error = PARSER_INVALID_DURATION;

                return NULL;
        }
    }

    return parsed;
}


PyObject* parse_iso8601(PyObject *self, PyObject *args) {
    char* str;
    PyObject *obj;
    PyObject *tzinfo;
    Parsed *parsed = new_parsed();

    if (!PyArg_ParseTuple(args, "s", &str)) {
        PyErr_SetString(
            PyExc_ValueError, "Invalid parameters"
        );
        return NULL;
    }

    if (*str == 'P') {
        // Duration (or interval)
        if (_parse_iso8601_duration(str, parsed) == NULL) {
            PyErr_SetString(
                PyExc_ValueError, PARSER_ERRORS[parsed->error]
            );

            return NULL;
        }
    } else if (_parse_iso8601_datetime(str, parsed) == NULL) {
        PyErr_SetString(
            PyExc_ValueError, PARSER_ERRORS[parsed->error]
        );

        return NULL;
    }

    if (parsed->is_date) {
        // Date only
        if (parsed->ambiguous) {
            // We can "safely" assume that the ambiguous
            // date was actually a time in the form hhmmss
            parsed->hour = parsed->year / 100;
            parsed->minute = parsed->year % 100;
            parsed->second = parsed->month;

            obj = PyDateTimeAPI->Time_FromTime(
                parsed->hour, parsed->minute, parsed->second, parsed->microsecond,
                Py_BuildValue(""),
                PyDateTimeAPI->TimeType
            );
        } else {
            obj = PyDateTimeAPI->Date_FromDate(
                parsed->year, parsed->month, parsed->day,
                PyDateTimeAPI->DateType
            );
        }
    } else if (parsed->is_datetime) {
        if (!parsed->has_offset) {
            tzinfo = Py_BuildValue("");
        } else {
            tzinfo = new_fixed_offset(parsed->offset, parsed->tzname);
        }

        obj = PyDateTimeAPI->DateTime_FromDateAndTime(
            parsed->year,
            parsed->month,
            parsed->day,
            parsed->hour,
            parsed->minute,
            parsed->second,
            parsed->microsecond,
            tzinfo,
            PyDateTimeAPI->DateTimeType
        );

        Py_DECREF(tzinfo);
    } else if (parsed->is_duration) {
        obj = new_duration(
            parsed->years, parsed->months, parsed->weeks, parsed->days,
            parsed->hours, parsed->minutes, parsed->seconds, parsed->microseconds
        );
    } else {
        return NULL;
    }

    free(parsed);

    return obj;
}


/* ------------------------------------------------------------------------- */

static PyMethodDef helpers_methods[] = {
    {
        "parse_iso8601",
        (PyCFunction) parse_iso8601,
        METH_VARARGS,
        PyDoc_STR("Parses a ISO8601 string into a tuple.")
    },
    {NULL}
};


/* ------------------------------------------------------------------------- */

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_iso8601",
    NULL,
    -1,
    helpers_methods,
    NULL,
    NULL,
    NULL,
    NULL,
};

PyMODINIT_FUNC
PyInit__iso8601(void)
{
    PyObject *module;

    PyDateTime_IMPORT;

    module = PyModule_Create(&moduledef);

    if (module == NULL)
        return NULL;

    // FixedOffset declaration
    FixedOffset_type.tp_new = PyType_GenericNew;
    FixedOffset_type.tp_base = PyDateTimeAPI->TZInfoType;
    FixedOffset_type.tp_methods = FixedOffset_methods;
    FixedOffset_type.tp_members = FixedOffset_members;
    FixedOffset_type.tp_init = (initproc)FixedOffset_init;

    if (PyType_Ready(&FixedOffset_type) < 0)
        return NULL;

    // Duration declaration
    Duration_type.tp_new = PyType_GenericNew;
    Duration_type.tp_members = Duration_members;
    Duration_type.tp_init = (initproc)Duration_init;

    if (PyType_Ready(&Duration_type) < 0)
        return NULL;

    Py_INCREF(&FixedOffset_type);
    Py_INCREF(&Duration_type);

    PyModule_AddObject(module, "TZFixedOffset", (PyObject *)&FixedOffset_type);
    PyModule_AddObject(module, "Duration", (PyObject *)&Duration_type);

    return module;
}
