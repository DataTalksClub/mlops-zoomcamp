/* ------------------------------------------------------------------------- */

#include <Python.h>
#include <datetime.h>
#include <structmember.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

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
    (uint64_t)(75L * DAYS_PER_N_YEAR + 25L * DAYS_PER_L_YEAR) * SECS_PER_DAY};

// The number of seconds in an aligned 4-year chunk, for those that
// do not begin with a leap year and those that do respectively.
const int32_t SECS_PER_4_YEARS[2] = {
    (4 * DAYS_PER_N_YEAR + 0 * DAYS_PER_L_YEAR) * SECS_PER_DAY,
    (3 * DAYS_PER_N_YEAR + 1 * DAYS_PER_L_YEAR) * SECS_PER_DAY};

// The number of seconds in non-leap and leap years respectively.
const int32_t SECS_PER_YEAR[2] = {
    DAYS_PER_N_YEAR * SECS_PER_DAY,
    DAYS_PER_L_YEAR *SECS_PER_DAY};

#define MONTHS_PER_YEAR 12

// The month lengths in non-leap and leap years respectively.
const int32_t DAYS_PER_MONTHS[2][13] = {
    {-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31},
    {-1, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31}};

// The day offsets of the beginning of each (1-based) month in non-leap
// and leap years respectively.
// For example, in a leap year there are 335 days before December.
const int32_t MONTHS_OFFSETS[2][14] = {
    {-1, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365},
    {-1, 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366}};

const int DAY_OF_WEEK_TABLE[12] = {
    0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4};

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

/* ------------------------------------------------------------------------- */

int _p(int y)
{
    return y + y / 4 - y / 100 + y / 400;
}

int _is_leap(int year)
{
    return year % 4 == 0 && (year % 100 != 0 || year % 400 == 0);
}

int _is_long_year(int year)
{
    return (_p(year) % 7 == 4) || (_p(year - 1) % 7 == 3);
}

int _week_day(int year, int month, int day)
{
    int y;
    int w;

    y = year - (month < 3);

    w = (_p(y) + DAY_OF_WEEK_TABLE[month - 1] + day) % 7;

    if (!w)
    {
        w = 7;
    }

    return w;
}

int _days_in_year(int year)
{
    if (_is_leap(year))
    {
        return DAYS_PER_L_YEAR;
    }

    return DAYS_PER_N_YEAR;
}

int _day_number(int year, int month, int day)
{
    month = (month + 9) % 12;
    year = year - month / 10;

    return (
        365 * year + year / 4 - year / 100 + year / 400 + (month * 306 + 5) / 10 + (day - 1));
}

int _get_offset(PyObject *dt)
{
    PyObject *tzinfo;
    PyObject *offset;

    tzinfo = ((PyDateTime_DateTime *)(dt))->tzinfo;

    if (tzinfo != Py_None)
    {
        offset = PyObject_CallMethod(tzinfo, "utcoffset", "O", dt);

        return PyDateTime_DELTA_GET_DAYS(offset) * SECS_PER_DAY + PyDateTime_DELTA_GET_SECONDS(offset);
    }

    return 0;
}

int _has_tzinfo(PyObject *dt)
{
    return ((_PyDateTime_BaseTZInfo *)(dt))->hastzinfo;
}

char *_get_tz_name(PyObject *dt)
{
    PyObject *tzinfo;
    char *tz = "";

    tzinfo = ((PyDateTime_DateTime *)(dt))->tzinfo;

    if (tzinfo != Py_None)
    {
        if (PyObject_HasAttrString(tzinfo, "name"))
        {
            // Pendulum timezone
            tz = (char *)PyUnicode_AsUTF8(
                PyObject_GetAttrString(tzinfo, "name"));
        }
        else if (PyObject_HasAttrString(tzinfo, "zone"))
        {
            // pytz timezone
            tz = (char *)PyUnicode_AsUTF8(
                PyObject_GetAttrString(tzinfo, "zone"));
        }
    }

    return tz;
}

/* ------------------------ Custom Types ------------------------------- */

/*
 * class Diff():
 */
typedef struct
{
    PyObject_HEAD int years;
    int months;
    int days;
    int hours;
    int minutes;
    int seconds;
    int microseconds;
    int total_days;
} Diff;

/*
 * def __init__(self, years, months, days, hours, minutes, seconds, microseconds, total_days):
 *     self.years = years
 *     # ...
*/
static int Diff_init(Diff *self, PyObject *args, PyObject *kwargs)
{
    int years;
    int months;
    int days;
    int hours;
    int minutes;
    int seconds;
    int microseconds;
    int total_days;

    if (!PyArg_ParseTuple(args, "iiiiiii", &years, &months, &days, &hours, &minutes, &seconds, &microseconds, &total_days))
        return -1;

    self->years = years;
    self->months = months;
    self->days = days;
    self->hours = hours;
    self->minutes = minutes;
    self->seconds = seconds;
    self->microseconds = microseconds;
    self->total_days = total_days;

    return 0;
}

/*
 * def __repr__(self):
 *     return '{} years {} months {} days {} hours {} minutes {} seconds {} microseconds'.format(
 *         self.years, self.months, self.days, self.minutes, self.hours, self.seconds, self.microseconds
 *     )
 */
static PyObject *Diff_repr(Diff *self)
{
    char repr[82] = {0};

    sprintf(
        repr,
        "%d years %d months %d days %d hours %d minutes %d seconds %d microseconds",
        self->years,
        self->months,
        self->days,
        self->hours,
        self->minutes,
        self->seconds,
        self->microseconds);

    return PyUnicode_FromString(repr);
}

/*
 * Instantiate new Diff_type object
 * Skip overhead of calling PyObject_New and PyObject_Init.
 * Directly allocate object.
 */
static PyObject *new_diff_ex(int years, int months, int days, int hours, int minutes, int seconds, int microseconds, int total_days, PyTypeObject *type)
{
    Diff *self = (Diff *)(type->tp_alloc(type, 0));

    if (self != NULL)
    {
        self->years = years;
        self->months = months;
        self->days = days;
        self->hours = hours;
        self->minutes = minutes;
        self->seconds = seconds;
        self->microseconds = microseconds;
        self->total_days = total_days;
    }

    return (PyObject *)self;
}

/*
 * Class member / class attributes
 */
static PyMemberDef Diff_members[] = {
    {"years", T_INT, offsetof(Diff, years), 0, "years in diff"},
    {"months", T_INT, offsetof(Diff, months), 0, "months in diff"},
    {"days", T_INT, offsetof(Diff, days), 0, "days in diff"},
    {"hours", T_INT, offsetof(Diff, hours), 0, "hours in diff"},
    {"minutes", T_INT, offsetof(Diff, minutes), 0, "minutes in diff"},
    {"seconds", T_INT, offsetof(Diff, seconds), 0, "seconds in diff"},
    {"microseconds", T_INT, offsetof(Diff, microseconds), 0, "microseconds in diff"},
    {"total_days", T_INT, offsetof(Diff, total_days), 0, "total days in diff"},
    {NULL}};

static PyTypeObject Diff_type = {
    PyVarObject_HEAD_INIT(NULL, 0) "PreciseDiff",      /* tp_name */
    sizeof(Diff),                                      /* tp_basicsize */
    0,                                                 /* tp_itemsize */
    0,                                                 /* tp_dealloc */
    0,                                                 /* tp_print */
    0,                                                 /* tp_getattr */
    0,                                                 /* tp_setattr */
    0,                                                 /* tp_as_async */
    (reprfunc)Diff_repr,                               /* tp_repr */
    0,                                                 /* tp_as_number */
    0,                                                 /* tp_as_sequence */
    0,                                                 /* tp_as_mapping */
    0,                                                 /* tp_hash  */
    0,                                                 /* tp_call */
    (reprfunc)Diff_repr,                               /* tp_str */
    0,                                                 /* tp_getattro */
    0,                                                 /* tp_setattro */
    0,                                                 /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,          /* tp_flags */
    "Precise difference between two datetime objects", /* tp_doc */
};

#define new_diff(years, months, days, hours, minutes, seconds, microseconds, total_days) new_diff_ex(years, months, days, hours, minutes, seconds, microseconds, total_days, &Diff_type)

/* -------------------------- Functions --------------------------*/

PyObject *is_leap(PyObject *self, PyObject *args)
{
    PyObject *leap;
    int year;

    if (!PyArg_ParseTuple(args, "i", &year))
    {
        PyErr_SetString(
            PyExc_ValueError, "Invalid parameters");
        return NULL;
    }

    leap = PyBool_FromLong(_is_leap(year));

    return leap;
}

PyObject *is_long_year(PyObject *self, PyObject *args)
{
    PyObject *is_long;
    int year;

    if (!PyArg_ParseTuple(args, "i", &year))
    {
        PyErr_SetString(
            PyExc_ValueError, "Invalid parameters");
        return NULL;
    }

    is_long = PyBool_FromLong(_is_long_year(year));

    return is_long;
}

PyObject *week_day(PyObject *self, PyObject *args)
{
    PyObject *wd;
    int year;
    int month;
    int day;

    if (!PyArg_ParseTuple(args, "iii", &year, &month, &day))
    {
        PyErr_SetString(
            PyExc_ValueError, "Invalid parameters");
        return NULL;
    }

    wd = PyLong_FromLong(_week_day(year, month, day));

    return wd;
}

PyObject *days_in_year(PyObject *self, PyObject *args)
{
    PyObject *ndays;
    int year;

    if (!PyArg_ParseTuple(args, "i", &year))
    {
        PyErr_SetString(
            PyExc_ValueError, "Invalid parameters");
        return NULL;
    }

    ndays = PyLong_FromLong(_days_in_year(year));

    return ndays;
}

PyObject *timestamp(PyObject *self, PyObject *args)
{
    int64_t result;
    PyObject *dt;

    if (!PyArg_ParseTuple(args, "O", &dt))
    {
        PyErr_SetString(
            PyExc_ValueError, "Invalid parameters");
        return NULL;
    }

    int year = (double)PyDateTime_GET_YEAR(dt);
    int month = PyDateTime_GET_MONTH(dt);
    int day = PyDateTime_GET_DAY(dt);
    int hour = PyDateTime_DATE_GET_HOUR(dt);
    int minute = PyDateTime_DATE_GET_MINUTE(dt);
    int second = PyDateTime_DATE_GET_SECOND(dt);

    result = (year - 1970) * 365 + MONTHS_OFFSETS[0][month];
    result += (int)floor((double)(year - 1968) / 4);
    result -= (year - 1900) / 100;
    result += (year - 1600) / 400;

    if (_is_leap(year) && month < 3)
    {
        result -= 1;
    }

    result += day - 1;
    result *= 24;
    result += hour;
    result *= 60;
    result += minute;
    result *= 60;
    result += second;

    return PyLong_FromSsize_t(result);
}

PyObject *local_time(PyObject *self, PyObject *args)
{
    double unix_time;
    int32_t utc_offset;
    int32_t year;
    int32_t microsecond;
    int64_t seconds;
    int32_t leap_year;
    int64_t sec_per_100years;
    int64_t sec_per_4years;
    int32_t sec_per_year;
    int32_t month;
    int32_t day;
    int32_t month_offset;
    int32_t hour;
    int32_t minute;
    int32_t second;

    if (!PyArg_ParseTuple(args, "dii", &unix_time, &utc_offset, &microsecond))
    {
        PyErr_SetString(
            PyExc_ValueError, "Invalid parameters");
        return NULL;
    }

    year = EPOCH_YEAR;
    seconds = (int64_t)floor(unix_time);

    // Shift to a base year that is 400-year aligned.
    if (seconds >= 0)
    {
        seconds -= 10957L * SECS_PER_DAY;
        year += 30; // == 2000;
    }
    else
    {
        seconds += (int64_t)(146097L - 10957L) * SECS_PER_DAY;
        year -= 370; // == 1600;
    }

    seconds += utc_offset;

    // Handle years in chunks of 400/100/4/1
    year += 400 * (seconds / SECS_PER_400_YEARS);
    seconds %= SECS_PER_400_YEARS;
    if (seconds < 0)
    {
        seconds += SECS_PER_400_YEARS;
        year -= 400;
    }

    leap_year = 1; // 4-century aligned

    sec_per_100years = SECS_PER_100_YEARS[leap_year];

    while (seconds >= sec_per_100years)
    {
        seconds -= sec_per_100years;
        year += 100;
        leap_year = 0; // 1-century, non 4-century aligned
        sec_per_100years = SECS_PER_100_YEARS[leap_year];
    }

    sec_per_4years = SECS_PER_4_YEARS[leap_year];
    while (seconds >= sec_per_4years)
    {
        seconds -= sec_per_4years;
        year += 4;
        leap_year = 1; // 4-year, non century aligned
        sec_per_4years = SECS_PER_4_YEARS[leap_year];
    }

    sec_per_year = SECS_PER_YEAR[leap_year];
    while (seconds >= sec_per_year)
    {
        seconds -= sec_per_year;
        year += 1;
        leap_year = 0; // non 4-year aligned
        sec_per_year = SECS_PER_YEAR[leap_year];
    }

    // Handle months and days
    month = TM_DECEMBER + 1;
    day = seconds / SECS_PER_DAY + 1;
    seconds %= SECS_PER_DAY;
    while (month != TM_JANUARY + 1)
    {
        month_offset = MONTHS_OFFSETS[leap_year][month];
        if (day > month_offset)
        {
            day -= month_offset;
            break;
        }

        month -= 1;
    }

    // Handle hours, minutes and seconds
    hour = seconds / SECS_PER_HOUR;
    seconds %= SECS_PER_HOUR;
    minute = seconds / SECS_PER_MIN;
    second = seconds % SECS_PER_MIN;

    return Py_BuildValue("NNNNNNN",
                         PyLong_FromLong(year),
                         PyLong_FromLong(month),
                         PyLong_FromLong(day),
                         PyLong_FromLong(hour),
                         PyLong_FromLong(minute),
                         PyLong_FromLong(second),
                         PyLong_FromLong(microsecond));
}

// Calculate a precise difference between two datetimes.
PyObject *precise_diff(PyObject *self, PyObject *args)
{
    PyObject *dt1;
    PyObject *dt2;

    if (!PyArg_ParseTuple(args, "OO", &dt1, &dt2))
    {
        PyErr_SetString(
            PyExc_ValueError, "Invalid parameters");
        return NULL;
    }

    int year_diff = 0;
    int month_diff = 0;
    int day_diff = 0;
    int hour_diff = 0;
    int minute_diff = 0;
    int second_diff = 0;
    int microsecond_diff = 0;
    int sign = 1;
    int year;
    int month;
    int leap;
    int days_in_last_month;
    int days_in_month;
    int dt1_year = PyDateTime_GET_YEAR(dt1);
    int dt2_year = PyDateTime_GET_YEAR(dt2);
    int dt1_month = PyDateTime_GET_MONTH(dt1);
    int dt2_month = PyDateTime_GET_MONTH(dt2);
    int dt1_day = PyDateTime_GET_DAY(dt1);
    int dt2_day = PyDateTime_GET_DAY(dt2);
    int dt1_hour = 0;
    int dt2_hour = 0;
    int dt1_minute = 0;
    int dt2_minute = 0;
    int dt1_second = 0;
    int dt2_second = 0;
    int dt1_microsecond = 0;
    int dt2_microsecond = 0;
    int dt1_total_seconds = 0;
    int dt2_total_seconds = 0;
    int dt1_offset = 0;
    int dt2_offset = 0;
    int dt1_is_datetime = PyDateTime_Check(dt1);
    int dt2_is_datetime = PyDateTime_Check(dt2);
    char *tz1 = "";
    char *tz2 = "";
    int in_same_tz = 0;
    int total_days = (_day_number(dt2_year, dt2_month, dt2_day) - _day_number(dt1_year, dt1_month, dt1_day));

    // If both dates are datetimes, we check
    // If we are in the same timezone
    if (dt1_is_datetime && dt2_is_datetime)
    {
        if (_has_tzinfo(dt1))
        {
            tz1 = _get_tz_name(dt1);
            dt1_offset = _get_offset(dt1);
        }

        if (_has_tzinfo(dt2))
        {
            tz2 = _get_tz_name(dt2);
            dt2_offset = _get_offset(dt2);
        }

        in_same_tz = tz1 == tz2 && strncmp(tz1, "", 1);
    }

    // If we have datetimes (and not only dates)
    // we get the information we need
    if (dt1_is_datetime)
    {
        dt1_hour = PyDateTime_DATE_GET_HOUR(dt1);
        dt1_minute = PyDateTime_DATE_GET_MINUTE(dt1);
        dt1_second = PyDateTime_DATE_GET_SECOND(dt1);
        dt1_microsecond = PyDateTime_DATE_GET_MICROSECOND(dt1);

        if ((!in_same_tz && dt1_offset != 0) || total_days == 0)
        {
            dt1_hour -= dt1_offset / SECS_PER_HOUR;
            dt1_offset %= SECS_PER_HOUR;
            dt1_minute -= dt1_offset / SECS_PER_MIN;
            dt1_offset %= SECS_PER_MIN;
            dt1_second -= dt1_offset;

            if (dt1_second < 0)
            {
                dt1_second += 60;
                dt1_minute -= 1;
            }
            else if (dt1_second > 60)
            {
                dt1_second -= 60;
                dt1_minute += 1;
            }

            if (dt1_minute < 0)
            {
                dt1_minute += 60;
                dt1_hour -= 1;
            }
            else if (dt1_minute > 60)
            {
                dt1_minute -= 60;
                dt1_hour += 1;
            }

            if (dt1_hour < 0)
            {
                dt1_hour += 24;
                dt1_day -= 1;
            }
            else if (dt1_hour > 24)
            {
                dt1_hour -= 24;
                dt1_day += 1;
            }
        }

        dt1_total_seconds = (dt1_hour * SECS_PER_HOUR + dt1_minute * SECS_PER_MIN + dt1_second);
    }

    if (dt2_is_datetime)
    {
        dt2_hour = PyDateTime_DATE_GET_HOUR(dt2);
        dt2_minute = PyDateTime_DATE_GET_MINUTE(dt2);
        dt2_second = PyDateTime_DATE_GET_SECOND(dt2);
        dt2_microsecond = PyDateTime_DATE_GET_MICROSECOND(dt2);

        if ((!in_same_tz && dt2_offset != 0) || total_days == 0)
        {
            dt2_hour -= dt2_offset / SECS_PER_HOUR;
            dt2_offset %= SECS_PER_HOUR;
            dt2_minute -= dt2_offset / SECS_PER_MIN;
            dt2_offset %= SECS_PER_MIN;
            dt2_second -= dt2_offset;

            if (dt2_second < 0)
            {
                dt2_second += 60;
                dt2_minute -= 1;
            }
            else if (dt2_second > 60)
            {
                dt2_second -= 60;
                dt2_minute += 1;
            }

            if (dt2_minute < 0)
            {
                dt2_minute += 60;
                dt2_hour -= 1;
            }
            else if (dt2_minute > 60)
            {
                dt2_minute -= 60;
                dt2_hour += 1;
            }

            if (dt2_hour < 0)
            {
                dt2_hour += 24;
                dt2_day -= 1;
            }
            else if (dt2_hour > 24)
            {
                dt2_hour -= 24;
                dt2_day += 1;
            }
        }

        dt2_total_seconds = (dt2_hour * SECS_PER_HOUR + dt2_minute * SECS_PER_MIN + dt2_second);
    }

    // Direct comparison between two datetimes does not work
    // so we need to check by properties
    int dt1_gt_dt2 = (dt1_year > dt2_year || (dt1_year == dt2_year && dt1_month > dt2_month) || (dt1_year == dt2_year && dt1_month == dt2_month && dt1_day > dt2_day) || (dt1_year == dt2_year && dt1_month == dt2_month && dt1_day == dt2_day && dt1_total_seconds > dt2_total_seconds) || (dt1_year == dt2_year && dt1_month == dt2_month && dt1_day == dt2_day && dt1_total_seconds == dt2_total_seconds && dt1_microsecond > dt2_microsecond));

    if (dt1_gt_dt2)
    {
        PyObject *temp;
        temp = dt1;
        dt1 = dt2;
        dt2 = temp;
        sign = -1;

        // Retrieving properties
        dt1_year = PyDateTime_GET_YEAR(dt1);
        dt2_year = PyDateTime_GET_YEAR(dt2);
        dt1_month = PyDateTime_GET_MONTH(dt1);
        dt2_month = PyDateTime_GET_MONTH(dt2);
        dt1_day = PyDateTime_GET_DAY(dt1);
        dt2_day = PyDateTime_GET_DAY(dt2);

        if (dt2_is_datetime)
        {
            dt1_hour = PyDateTime_DATE_GET_HOUR(dt1);
            dt1_minute = PyDateTime_DATE_GET_MINUTE(dt1);
            dt1_second = PyDateTime_DATE_GET_SECOND(dt1);
            dt1_microsecond = PyDateTime_DATE_GET_MICROSECOND(dt1);
        }

        if (dt1_is_datetime)
        {
            dt2_hour = PyDateTime_DATE_GET_HOUR(dt2);
            dt2_minute = PyDateTime_DATE_GET_MINUTE(dt2);
            dt2_second = PyDateTime_DATE_GET_SECOND(dt2);
            dt2_microsecond = PyDateTime_DATE_GET_MICROSECOND(dt2);
        }

        total_days = (_day_number(dt2_year, dt2_month, dt2_day) - _day_number(dt1_year, dt1_month, dt1_day));
    }

    year_diff = dt2_year - dt1_year;
    month_diff = dt2_month - dt1_month;
    day_diff = dt2_day - dt1_day;
    hour_diff = dt2_hour - dt1_hour;
    minute_diff = dt2_minute - dt1_minute;
    second_diff = dt2_second - dt1_second;
    microsecond_diff = dt2_microsecond - dt1_microsecond;

    if (microsecond_diff < 0)
    {
        microsecond_diff += 1e6;
        second_diff -= 1;
    }

    if (second_diff < 0)
    {
        second_diff += 60;
        minute_diff -= 1;
    }

    if (minute_diff < 0)
    {
        minute_diff += 60;
        hour_diff -= 1;
    }

    if (hour_diff < 0)
    {
        hour_diff += 24;
        day_diff -= 1;
    }

    if (day_diff < 0)
    {
        // If we have a difference in days,
        // we have to check if they represent months
        year = dt2_year;
        month = dt2_month;

        if (month == 1)
        {
            month = 12;
            year -= 1;
        }
        else
        {
            month -= 1;
        }

        leap = _is_leap(year);

        days_in_last_month = DAYS_PER_MONTHS[leap][month];
        days_in_month = DAYS_PER_MONTHS[_is_leap(dt2_year)][dt2_month];

        if (day_diff < days_in_month - days_in_last_month)
        {
            // We don't have a full month, we calculate days
            if (days_in_last_month < dt1_day)
            {
                day_diff += dt1_day;
            }
            else
            {
                day_diff += days_in_last_month;
            }
        }
        else if (day_diff == days_in_month - days_in_last_month)
        {
            // We have exactly a full month
            // We remove the days difference
            // and add one to the months difference
            day_diff = 0;
            month_diff += 1;
        }
        else
        {
            // We have a full month
            day_diff += days_in_last_month;
        }

        month_diff -= 1;
    }

    if (month_diff < 0)
    {
        month_diff += 12;
        year_diff -= 1;
    }

    return new_diff(
        year_diff * sign,
        month_diff * sign,
        day_diff * sign,
        hour_diff * sign,
        minute_diff * sign,
        second_diff * sign,
        microsecond_diff * sign,
        total_days * sign);
}

/* ------------------------------------------------------------------------- */

static PyMethodDef helpers_methods[] = {
    {"is_leap",
     (PyCFunction)is_leap,
     METH_VARARGS,
     PyDoc_STR("Checks if a year is a leap year.")},
    {"is_long_year",
     (PyCFunction)is_long_year,
     METH_VARARGS,
     PyDoc_STR("Checks if a year is a long year.")},
    {"week_day",
     (PyCFunction)week_day,
     METH_VARARGS,
     PyDoc_STR("Returns the weekday number.")},
    {"days_in_year",
     (PyCFunction)days_in_year,
     METH_VARARGS,
     PyDoc_STR("Returns the number of days in the given year.")},
    {"timestamp",
     (PyCFunction)timestamp,
     METH_VARARGS,
     PyDoc_STR("Returns the timestamp of the given datetime.")},
    {"local_time",
     (PyCFunction)local_time,
     METH_VARARGS,
     PyDoc_STR("Returns a UNIX time as a broken down time for a particular transition type.")},
    {"precise_diff",
     (PyCFunction)precise_diff,
     METH_VARARGS,
     PyDoc_STR("Calculate a precise difference between two datetimes.")},
    {NULL}};

/* ------------------------------------------------------------------------- */

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_helpers",
    NULL,
    -1,
    helpers_methods,
    NULL,
    NULL,
    NULL,
    NULL,
};

PyMODINIT_FUNC
PyInit__helpers(void)
{
    PyObject *module;

    PyDateTime_IMPORT;

    module = PyModule_Create(&moduledef);

    if (module == NULL)
        return NULL;

    // Diff declaration
    Diff_type.tp_new = PyType_GenericNew;
    Diff_type.tp_members = Diff_members;
    Diff_type.tp_init = (initproc)Diff_init;

    if (PyType_Ready(&Diff_type) < 0)
        return NULL;

    PyModule_AddObject(module, "PreciseDiff", (PyObject *)&Diff_type);

    return module;
}
