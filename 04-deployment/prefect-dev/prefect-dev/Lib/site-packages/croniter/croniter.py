#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import traceback as _traceback
import copy
import math
import re
import sys
import inspect
from time import time
import datetime
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc
import calendar
import binascii
import random

# as pytz is optional in thirdparty libs but we need it for good support under
# python2, just test that it's well installed
import pytz  # noqa

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict  # py26 degraded mode, expanders order will not be immutable


M_ALPHAS = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
DOW_ALPHAS = {'sun': 0, 'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6}
ALPHAS = {}
for i in M_ALPHAS, DOW_ALPHAS:
    ALPHAS.update(i)
del i
step_search_re = re.compile(r'^([^-]+)-([^-/]+)(/(\d+))?$')
only_int_re = re.compile(r'^\d+$')

WEEKDAYS = '|'.join(DOW_ALPHAS.keys())
MONTHS = '|'.join(M_ALPHAS.keys())
star_or_int_re = re.compile(r'^(\d+|\*)$')
special_dow_re = re.compile(
    (r'^(?P<pre>((?P<he>(({WEEKDAYS})(-({WEEKDAYS}))?)').format(WEEKDAYS=WEEKDAYS) +
    (r'|(({MONTHS})(-({MONTHS}))?)|\w+)#)|l)(?P<last>\d+)$').format(MONTHS=MONTHS)
)
re_star = re.compile('[*]')
hash_expression_re = re.compile(
    r'^(?P<hash_type>h|r)(\((?P<range_begin>\d+)-(?P<range_end>\d+)\))?(\/(?P<divisor>\d+))?$'
)
VALID_LEN_EXPRESSION = [5, 6]
EXPRESSIONS = {}


def timedelta_to_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) \
        / 10**6


def datetime_to_timestamp(d):
    if d.tzinfo is not None:
        d = d.replace(tzinfo=None) - d.utcoffset()

    return timedelta_to_seconds(d - datetime.datetime(1970, 1, 1))


def _get_caller_globals_and_locals():
    """
    Returns the globals and locals of the calling frame.

    Is there an alternative to frame hacking here?
    """
    caller_frame = inspect.stack()[2]
    myglobals = caller_frame[0].f_globals
    mylocals = caller_frame[0].f_locals
    return myglobals, mylocals


class CroniterError(ValueError):
    """ General top-level Croniter base exception """
    pass


class CroniterBadTypeRangeError(TypeError):
    """."""


class CroniterBadCronError(CroniterError):
    """ Syntax, unknown value, or range error within a cron expression """
    pass


class CroniterUnsupportedSyntaxError(CroniterBadCronError):
    """ Valid cron syntax, but likely to produce inaccurate results """
    # Extending CroniterBadCronError, which may be contridatory, but this allows
    # catching both errors with a single exception.  From a user perspective
    # these will likely be handled the same way.
    pass


class CroniterBadDateError(CroniterError):
    """ Unable to find next/prev timestamp match """
    pass


class CroniterNotAlphaError(CroniterBadCronError):
    """ Cron syntax contains an invalid day or month abbreviation """
    pass


class croniter(object):
    MONTHS_IN_YEAR = 12
    RANGES = (
        (0, 59),
        (0, 23),
        (1, 31),
        (1, 12),
        (0, 7),
        (0, 59)
    )
    DAYS = (
        31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31
    )

    ALPHACONV = (
        {},  # 0: min
        {},  # 1: hour
        {"l": "l"},  # 2: dom
        # 3: mon
        copy.deepcopy(M_ALPHAS),
        # 4: dow
        copy.deepcopy(DOW_ALPHAS),
        # command/user
        {}
    )

    LOWMAP = (
        {},
        {},
        {0: 1},
        {0: 1},
        {7: 0},
        {},
    )

    LEN_MEANS_ALL = (
        60,
        24,
        31,
        12,
        7,
        60
    )

    bad_length = 'Exactly 5 or 6 columns has to be specified for iterator ' \
                 'expression.'

    def __init__(self, expr_format, start_time=None, ret_type=float,
                 day_or=True, max_years_between_matches=None, is_prev=False,
                 hash_id=None, implement_cron_bug=False):
        self._ret_type = ret_type
        self._day_or = day_or
        self._implement_cron_bug = implement_cron_bug

        if hash_id:
            if not isinstance(hash_id, (bytes, str)):
                raise TypeError('hash_id must be bytes or UTF-8 string')
            if not isinstance(hash_id, bytes):
                hash_id = hash_id.encode('UTF-8')

        self._max_years_btw_matches_explicitly_set = (
            max_years_between_matches is not None)
        if not self._max_years_btw_matches_explicitly_set:
            max_years_between_matches = 50
        self._max_years_between_matches = max(int(max_years_between_matches), 1)

        if start_time is None:
            start_time = time()

        self.tzinfo = None

        self.start_time = None
        self.dst_start_time = None
        self.cur = None
        self.set_current(start_time, force=False)

        self.expanded, self.nth_weekday_of_month = self.expand(expr_format, hash_id=hash_id)
        self.expressions = EXPRESSIONS[(expr_format, hash_id)]
        self._is_prev = is_prev

    @classmethod
    def _alphaconv(cls, index, key, expressions):
        try:
            return cls.ALPHACONV[index][key]
        except KeyError:
            raise CroniterNotAlphaError(
                "[{0}] is not acceptable".format(" ".join(expressions)))

    def get_next(self, ret_type=None, start_time=None):
        self.set_current(start_time, force=True)
        return self._get_next(ret_type or self._ret_type, is_prev=False)

    def get_prev(self, ret_type=None):
        return self._get_next(ret_type or self._ret_type, is_prev=True)

    def get_current(self, ret_type=None):
        ret_type = ret_type or self._ret_type
        if issubclass(ret_type, datetime.datetime):
            return self._timestamp_to_datetime(self.cur)
        return self.cur

    def set_current(self, start_time, force=True):
        if (force or (self.cur is None)) and start_time is not None:
            if isinstance(start_time, datetime.datetime):
                self.tzinfo = start_time.tzinfo
                start_time = self._datetime_to_timestamp(start_time)

            self.start_time = start_time
            self.dst_start_time = start_time
            self.cur = start_time
        return self.cur

    @classmethod
    def _datetime_to_timestamp(cls, d):
        """
        Converts a `datetime` object `d` into a UNIX timestamp.
        """
        return datetime_to_timestamp(d)

    def _timestamp_to_datetime(self, timestamp):
        """
        Converts a UNIX timestamp `timestamp` into a `datetime` object.
        """
        result = datetime.datetime.fromtimestamp(timestamp, tz=tzutc()).replace(tzinfo=None)
        if self.tzinfo:
            result = result.replace(tzinfo=tzutc()).astimezone(self.tzinfo)

        return result

    @classmethod
    def _timedelta_to_seconds(cls, td):
        """
        Converts a 'datetime.timedelta' object `td` into seconds contained in
        the duration.
        Note: We cannot use `timedelta.total_seconds()` because this is not
        supported by Python 2.6.
        """
        return timedelta_to_seconds(td)

    def _get_next(self, ret_type=None, start_time=None, is_prev=None):
        self.set_current(start_time, force=True)
        if is_prev is None:
            is_prev = self._is_prev
        self._is_prev = is_prev
        expanded = self.expanded[:]
        nth_weekday_of_month = self.nth_weekday_of_month.copy()

        ret_type = ret_type or self._ret_type

        if not issubclass(ret_type, (float, datetime.datetime)):
            raise TypeError("Invalid ret_type, only 'float' or 'datetime' "
                            "is acceptable.")

        # exception to support day of month and day of week as defined in cron
        dom_dow_exception_processed = False
        if (expanded[2][0] != '*' and expanded[4][0] != '*') and self._day_or:
            # If requested, handle a bug in vixie cron/ISC cron where day_of_month and day_of_week form
            # an intersection (AND) instead of a union (OR) if either field is an asterisk or starts with an asterisk
            # (https://crontab.guru/cron-bug.html)
            if self._implement_cron_bug and (re_star.match(self.expressions[2]) or re_star.match(self.expressions[4])):
                # To produce a schedule identical to the cron bug, we'll bypass the code that
                # makes a union of DOM and DOW, and instead skip to the code that does an intersect instead
                pass
            else:
                bak = expanded[4]
                expanded[4] = ['*']
                t1 = self._calc(self.cur, expanded, nth_weekday_of_month, is_prev)
                expanded[4] = bak
                expanded[2] = ['*']

                t2 = self._calc(self.cur, expanded, nth_weekday_of_month, is_prev)
                if not is_prev:
                    result = t1 if t1 < t2 else t2
                else:
                    result = t1 if t1 > t2 else t2
                dom_dow_exception_processed = True

        if not dom_dow_exception_processed:
            result = self._calc(self.cur, expanded,
                                nth_weekday_of_month, is_prev)

        # DST Handling for cron job spanning across days
        dtstarttime = self._timestamp_to_datetime(self.dst_start_time)
        dtstarttime_utcoffset = (
            dtstarttime.utcoffset() or datetime.timedelta(0))
        dtresult = self._timestamp_to_datetime(result)
        lag = lag_hours = 0
        # do we trigger DST on next crontab (handle backward changes)
        dtresult_utcoffset = dtstarttime_utcoffset
        if dtresult and self.tzinfo:
            dtresult_utcoffset = dtresult.utcoffset()
            lag_hours = (
                self._timedelta_to_seconds(dtresult - dtstarttime) / (60 * 60)
            )
            lag = self._timedelta_to_seconds(
                dtresult_utcoffset - dtstarttime_utcoffset
            )
        hours_before_midnight = 24 - dtstarttime.hour
        if dtresult_utcoffset != dtstarttime_utcoffset:
            if (
                (lag > 0 and abs(lag_hours) >= hours_before_midnight)
                or (lag < 0 and
                    ((3600 * abs(lag_hours) + abs(lag)) >= hours_before_midnight * 3600))
            ):
                dtresult_adjusted = dtresult - datetime.timedelta(seconds=lag)
                result_adjusted = self._datetime_to_timestamp(dtresult_adjusted)
                # Do the actual adjust only if the result time actually exists
                if self._timestamp_to_datetime(result_adjusted).tzinfo == dtresult_adjusted.tzinfo:
                    dtresult = dtresult_adjusted
                    result = result_adjusted
                self.dst_start_time = result
        self.cur = result
        if issubclass(ret_type, datetime.datetime):
            result = dtresult
        return result

    # iterator protocol, to enable direct use of croniter
    # objects in a loop, like "for dt in croniter('5 0 * * *'): ..."
    # or for combining multiple croniters into single
    # dates feed using 'itertools' module
    def all_next(self, ret_type=None):
        '''Generator of all consecutive dates. Can be used instead of
        implicit call to __iter__, whenever non-default
        'ret_type' has to be specified.
        '''
        # In a Python 3.7+ world:  contextlib.suppress and contextlib.nullcontext could be used instead
        try:
            while True:
                self._is_prev = False
                yield self._get_next(ret_type or self._ret_type)
        except CroniterBadDateError:
            if self._max_years_btw_matches_explicitly_set:
                return
            else:
                raise

    def all_prev(self, ret_type=None):
        '''Generator of all previous dates.'''
        try:
            while True:
                self._is_prev = True
                yield self._get_next(ret_type or self._ret_type)
        except CroniterBadDateError:
            if self._max_years_btw_matches_explicitly_set:
                return
            else:
                raise

    def iter(self, *args, **kwargs):
        return (self._is_prev and self.all_prev or self.all_next)

    def __iter__(self):
        return self
    __next__ = next = _get_next

    def _calc(self, now, expanded, nth_weekday_of_month, is_prev):
        if is_prev:
            now = math.ceil(now)
            nearest_diff_method = self._get_prev_nearest_diff
            sign = -1
            offset = (len(expanded) == 6 or now % 60 > 0) and 1 or 60
        else:
            now = math.floor(now)
            nearest_diff_method = self._get_next_nearest_diff
            sign = 1
            offset = (len(expanded) == 6) and 1 or 60

        dst = now = self._timestamp_to_datetime(now + sign * offset)

        month, year = dst.month, dst.year
        current_year = now.year
        DAYS = self.DAYS

        def proc_month(d):
            try:
                expanded[3].index('*')
            except ValueError:
                diff_month = nearest_diff_method(
                    d.month, expanded[3], self.MONTHS_IN_YEAR)
                days = DAYS[month - 1]
                if month == 2 and self.is_leap(year) is True:
                    days += 1

                reset_day = 1

                if diff_month is not None and diff_month != 0:
                    if is_prev:
                        d += relativedelta(months=diff_month)
                        reset_day = DAYS[d.month - 1]
                        if d.month == 2 and self.is_leap(d.year) is True:
                            reset_day += 1
                        d += relativedelta(
                            day=reset_day, hour=23, minute=59, second=59)
                    else:
                        d += relativedelta(months=diff_month, day=reset_day,
                                           hour=0, minute=0, second=0)
                    return True, d
            return False, d

        def proc_day_of_month(d):
            try:
                expanded[2].index('*')
            except ValueError:
                days = DAYS[month - 1]
                if month == 2 and self.is_leap(year) is True:
                    days += 1
                if 'l' in expanded[2] and days == d.day:
                    return False, d

                if is_prev:
                    days_in_prev_month = DAYS[
                        (month - 2) % self.MONTHS_IN_YEAR]
                    diff_day = nearest_diff_method(
                        d.day, expanded[2], days_in_prev_month)
                else:
                    diff_day = nearest_diff_method(d.day, expanded[2], days)

                if diff_day is not None and diff_day != 0:
                    if is_prev:
                        d += relativedelta(
                            days=diff_day, hour=23, minute=59, second=59)
                    else:
                        d += relativedelta(
                            days=diff_day, hour=0, minute=0, second=0)
                    return True, d
            return False, d

        def proc_day_of_week(d):
            try:
                expanded[4].index('*')
            except ValueError:
                diff_day_of_week = nearest_diff_method(
                    d.isoweekday() % 7, expanded[4], 7)
                if diff_day_of_week is not None and diff_day_of_week != 0:
                    if is_prev:
                        d += relativedelta(days=diff_day_of_week,
                                           hour=23, minute=59, second=59)
                    else:
                        d += relativedelta(days=diff_day_of_week,
                                           hour=0, minute=0, second=0)
                    return True, d
            return False, d

        def proc_day_of_week_nth(d):
            if '*' in nth_weekday_of_month:
                s = nth_weekday_of_month['*']
                for i in range(0, 7):
                    if i in nth_weekday_of_month:
                        nth_weekday_of_month[i].update(s)
                    else:
                        nth_weekday_of_month[i] = s
                del nth_weekday_of_month['*']

            candidates = []
            for wday, nth in nth_weekday_of_month.items():
                c = self._get_nth_weekday_of_month(d.year, d.month, wday)
                for n in nth:
                    if n == "l":
                        candidate = c[-1]
                    elif len(c) < n:
                        continue
                    else:
                        candidate = c[n - 1]
                    if (
                        (is_prev and candidate <= d.day) or
                        (not is_prev and d.day <= candidate)
                    ):
                        candidates.append(candidate)

            if not candidates:
                if is_prev:
                    d += relativedelta(days=-d.day,
                                       hour=23, minute=59, second=59)
                else:
                    days = DAYS[month - 1]
                    if month == 2 and self.is_leap(year) is True:
                        days += 1
                    d += relativedelta(days=(days - d.day + 1),
                                       hour=0, minute=0, second=0)
                return True, d

            candidates.sort()
            diff_day = (candidates[-1] if is_prev else candidates[0]) - d.day
            if diff_day != 0:
                if is_prev:
                    d += relativedelta(days=diff_day,
                                       hour=23, minute=59, second=59)
                else:
                    d += relativedelta(days=diff_day,
                                       hour=0, minute=0, second=0)
                return True, d
            return False, d

        def proc_hour(d):
            try:
                expanded[1].index('*')
            except ValueError:
                diff_hour = nearest_diff_method(d.hour, expanded[1], 24)
                if diff_hour is not None and diff_hour != 0:
                    if is_prev:
                        d += relativedelta(
                            hours=diff_hour, minute=59, second=59)
                    else:
                        d += relativedelta(hours=diff_hour, minute=0, second=0)
                    return True, d
            return False, d

        def proc_minute(d):
            try:
                expanded[0].index('*')
            except ValueError:
                diff_min = nearest_diff_method(d.minute, expanded[0], 60)
                if diff_min is not None and diff_min != 0:
                    if is_prev:
                        d += relativedelta(minutes=diff_min, second=59)
                    else:
                        d += relativedelta(minutes=diff_min, second=0)
                    return True, d
            return False, d

        def proc_second(d):
            if len(expanded) == 6:
                try:
                    expanded[5].index('*')
                except ValueError:
                    diff_sec = nearest_diff_method(d.second, expanded[5], 60)
                    if diff_sec is not None and diff_sec != 0:
                        d += relativedelta(seconds=diff_sec)
                        return True, d
            else:
                d += relativedelta(second=0)
            return False, d

        procs = [proc_month,
                 proc_day_of_month,
                 (proc_day_of_week_nth if nth_weekday_of_month
                     else proc_day_of_week),
                 proc_hour,
                 proc_minute,
                 proc_second]

        while abs(year - current_year) <= self._max_years_between_matches:
            next = False
            for proc in procs:
                (changed, dst) = proc(dst)
                if changed:
                    month, year = dst.month, dst.year
                    next = True
                    break
            if next:
                continue
            return self._datetime_to_timestamp(dst.replace(microsecond=0))

        if is_prev:
            raise CroniterBadDateError("failed to find prev date")
        raise CroniterBadDateError("failed to find next date")

    def _get_next_nearest(self, x, to_check):
        small = [item for item in to_check if item < x]
        large = [item for item in to_check if item >= x]
        large.extend(small)
        return large[0]

    def _get_prev_nearest(self, x, to_check):
        small = [item for item in to_check if item <= x]
        large = [item for item in to_check if item > x]
        small.reverse()
        large.reverse()
        small.extend(large)
        return small[0]

    def _get_next_nearest_diff(self, x, to_check, range_val):
        for i, d in enumerate(to_check):
            if d == "l":
                # if 'l' then it is the last day of month
                # => its value of range_val
                d = range_val
            if d >= x:
                return d - x
        return to_check[0] - x + range_val

    def _get_prev_nearest_diff(self, x, to_check, range_val):
        candidates = to_check[:]
        candidates.reverse()
        for d in candidates:
            if d != 'l' and d <= x:
                return d - x
        if 'l' in candidates:
            return -x
        candidate = candidates[0]
        for c in candidates:
            # fixed: c < range_val
            # this code will reject all 31 day of month, 12 month, 59 second,
            # 23 hour and so on.
            # if candidates has just a element, this will not harmful.
            # but candidates have multiple elements, then values equal to
            # range_val will rejected.
            if c <= range_val:
                candidate = c
                break
        if candidate > range_val:
            # fix crontab "0 6 30 3 *" condidates only a element,
            # then get_prev error return 2021-03-02 06:00:00
            return - x
        return (candidate - x - range_val)

    @staticmethod
    def _get_nth_weekday_of_month(year, month, day_of_week):
        """ For a given year/month return a list of days in nth-day-of-month order.
        The last weekday of the month is always [-1].
        """
        w = (day_of_week + 6) % 7
        c = calendar.Calendar(w).monthdayscalendar(year, month)
        if c[0][0] == 0:
            c.pop(0)
        return tuple(i[0] for i in c)

    def is_leap(self, year):
        if year % 400 == 0 or (year % 4 == 0 and year % 100 != 0):
            return True
        else:
            return False

    @classmethod
    def _expand(cls, expr_format, hash_id=None):
        # Split the expression in components, and normalize L -> l, MON -> mon,
        # etc. Keep expr_format untouched so we can use it in the exception
        # messages.
        expr_aliases = {
            '@midnight': ('0 0 * * *', 'h h(0-2) * * * h'),
            '@hourly': ('0 * * * *', 'h * * * * h'),
            '@daily': ('0 0 * * *', 'h h * * * h'),
            '@weekly': ('0 0 * * 0', 'h h * * h h'),
            '@monthly': ('0 0 1 * *', 'h h h * * h'),
            '@yearly': ('0 0 1 1 *', 'h h h h * h'),
            '@annually': ('0 0 1 1 *', 'h h h h * h'),
        }

        efl = expr_format.lower()
        hash_id_expr = hash_id is not None and 1 or 0
        try:
            efl = expr_aliases[efl][hash_id_expr]
        except KeyError:
            pass

        expressions = efl.split()

        if len(expressions) not in VALID_LEN_EXPRESSION:
            raise CroniterBadCronError(cls.bad_length)

        expanded = []
        nth_weekday_of_month = {}

        for i, expr in enumerate(expressions):
            for expanderid, expander in EXPANDERS.items():
                expr = expander(cls).expand(efl, i, expr, hash_id=hash_id)

            e_list = expr.split(',')
            res = []

            while len(e_list) > 0:
                e = e_list.pop()
                nth = None

                if i == 4:
                    # Handle special case in the dow expression: 2#3, l3
                    special_dow_rem = special_dow_re.match(str(e))
                    if special_dow_rem:
                        g = special_dow_rem.groupdict()
                        he, last = g.get('he', ''), g.get('last', '')
                        if he:
                            e = he
                            try:
                                nth = int(last)
                                assert (nth >= 1 and nth <= 5)
                            except (KeyError, ValueError, AssertionError):
                                raise CroniterBadCronError(
                                    "[{0}] is not acceptable.  Invalid day_of_week "
                                    "value: '{1}'".format(expr_format, nth))
                        elif last:
                            e = last
                            nth = g['pre']  # 'l'

                # Before matching step_search_re, normalize "*" to "{min}-{max}".
                # Example: in the minute field, "*/5" normalizes to "0-59/5"
                t = re.sub(r'^\*(\/.+)$', r'%d-%d\1' % (
                    cls.RANGES[i][0],
                    cls.RANGES[i][1]),
                    str(e))
                m = step_search_re.search(t)

                if not m:
                    # Before matching step_search_re,
                    # normalize "{start}/{step}" to "{start}-{max}/{step}".
                    # Example: in the minute field, "10/5" normalizes to "10-59/5"
                    t = re.sub(r'^(.+)\/(.+)$', r'\1-%d/\2' % (
                        cls.RANGES[i][1]),
                        str(e))
                    m = step_search_re.search(t)

                if m:
                    # early abort if low/high are out of bounds

                    (low, high, step) = m.group(1), m.group(2), m.group(4) or 1
                    if i == 2 and high == 'l':
                        high = '31'

                    if not only_int_re.search(low):
                        low = "{0}".format(cls._alphaconv(i, low, expressions))

                    if not only_int_re.search(high):
                        high = "{0}".format(cls._alphaconv(i, high, expressions))

                    if (
                        not low or not high or int(low) > int(high)
                        or not only_int_re.search(str(step))
                    ):
                        if i == 4 and high == '0':
                            # handle -Sun notation -> 7
                            high = '7'
                        else:
                            raise CroniterBadCronError(
                                "[{0}] is not acceptable".format(expr_format))

                    low, high, step = map(int, [low, high, step])
                    if (
                        max(low, high) > max(cls.RANGES[i][0], cls.RANGES[i][1])
                    ):
                        raise CroniterBadCronError(
                            "{0} is out of bands".format(expr_format))
                    try:
                        rng = range(low, high + 1, step)
                    except ValueError as exc:
                        raise CroniterBadCronError(
                            'invalid range: {0}'.format(exc))
                    e_list += (["{0}#{1}".format(item, nth) for item in rng]
                               if i == 4 and nth and nth != "l" else rng)
                else:
                    if t.startswith('-'):
                        raise CroniterBadCronError((
                            "[{0}] is not acceptable,"
                            "negative numbers not allowed"
                        ).format(expr_format))
                    if not star_or_int_re.search(t):
                        t = cls._alphaconv(i, t, expressions)

                    try:
                        t = int(t)
                    except ValueError:
                        pass

                    if t in cls.LOWMAP[i] and not (
                        # do not support 0 as a month either for classical 5 fields cron
                        # or 6fields second repeat form
                        # but still let conversion happen if day field is shifted
                        (i in [2, 3] and len(expressions) == 5) or
                        (i in [3, 4] and len(expressions) == 6)
                    ):
                        t = cls.LOWMAP[i][t]

                    if (
                        t not in ["*", "l"]
                        and (int(t) < cls.RANGES[i][0] or
                             int(t) > cls.RANGES[i][1])
                    ):
                        raise CroniterBadCronError(
                            "[{0}] is not acceptable, out of range".format(
                                expr_format))

                    res.append(t)

                    if i == 4 and nth:
                        if t not in nth_weekday_of_month:
                            nth_weekday_of_month[t] = set()
                        nth_weekday_of_month[t].add(nth)

            res = set(res)
            res = sorted(res, key=lambda i: "{:02}".format(i) if isinstance(i, int) else i)
            if len(res) == cls.LEN_MEANS_ALL[i]:
                # Make sure the wildcard is used in the correct way (avoid over-optimization)
                if (
                    (i == 2 and '*' not in expressions[4]) or
                    (i == 4 and '*' not in expressions[2])
                ):
                    pass
                else:
                    res = ['*']

            expanded.append(['*'] if (len(res) == 1
                                      and res[0] == '*')
                            else res)

        # Check to make sure the dow combo in use is supported
        if nth_weekday_of_month:
            dow_expanded_set = set(expanded[4])
            dow_expanded_set = dow_expanded_set.difference(nth_weekday_of_month.keys())
            dow_expanded_set.discard("*")
            # Skip: if it's all weeks instead of wildcard
            if dow_expanded_set and len(set(expanded[4])) != cls.LEN_MEANS_ALL[4]:
                raise CroniterUnsupportedSyntaxError(
                    "day-of-week field does not support mixing literal values and nth day of week syntax.  "
                    "Cron: '{}'    dow={} vs nth={}".format(expr_format, dow_expanded_set, nth_weekday_of_month))

        EXPRESSIONS[(expr_format, hash_id)] = expressions
        return expanded, nth_weekday_of_month

    @classmethod
    def expand(cls, expr_format, hash_id=None):
        """Shallow non Croniter ValueError inside a nice CroniterBadCronError"""
        try:
            return cls._expand(expr_format, hash_id=hash_id)
        except (ValueError,) as exc:
            error_type, error_instance, traceback = sys.exc_info()
            if isinstance(exc, CroniterError):
                raise
            if int(sys.version[0]) >= 3:
                trace = _traceback.format_exc()
                globs, locs = _get_caller_globals_and_locals()
                raise CroniterBadCronError(trace)
            else:
                raise CroniterBadCronError("{0}".format(exc))

    @classmethod
    def is_valid(cls, expression, hash_id=None, encoding='UTF-8'):
        if hash_id:
            if not isinstance(hash_id, (bytes, str)):
                raise TypeError('hash_id must be bytes or UTF-8 string')
            if not isinstance(hash_id, bytes):
                hash_id = hash_id.encode(encoding)
        try:
            cls.expand(expression, hash_id=hash_id)
        except CroniterError:
            return False
        else:
            return True

    @classmethod
    def match(cls, cron_expression, testdate, day_or=True):
        return cls.match_range(cron_expression, testdate, testdate, day_or)

    @classmethod
    def match_range(cls, cron_expression, from_datetime, to_datetime, day_or=True):
        cron = cls(cron_expression, to_datetime, ret_type=datetime.datetime, day_or=day_or)
        td, ms1 = cron.get_current(datetime.datetime), relativedelta(microseconds=1)
        if not td.microsecond:
            td = td + ms1
        cron.set_current(td, force=True)
        tdp, tdt = cron.get_current(), cron.get_prev()
        precision_in_seconds = 1 if len(cron.expanded) == 6 else 60
        duration_in_second = (to_datetime - from_datetime).total_seconds() + precision_in_seconds
        return (max(tdp, tdt) - min(tdp, tdt)).total_seconds() < duration_in_second


def croniter_range(start, stop, expr_format, ret_type=None, day_or=True, exclude_ends=False,
                   _croniter=None):
    """
    Generator that provides all times from start to stop matching the given cron expression.
    If the cron expression matches either 'start' and/or 'stop', those times will be returned as
    well unless 'exclude_ends=True' is passed.

    You can think of this function as sibling to the builtin range function for datetime objects.
    Like range(start,stop,step), except that here 'step' is a cron expression.
    """
    _croniter = _croniter or croniter
    auto_rt = datetime.datetime
    # type is used in first if branch for perfs reasons
    if (
        type(start) is not type(stop) and not (
            isinstance(start, type(stop)) or
            isinstance(stop, type(start)))
    ):
        raise CroniterBadTypeRangeError(
            "The start and stop must be same type.  {0} != {1}".
            format(type(start), type(stop)))
    if isinstance(start, (float, int)):
        start, stop = (datetime.datetime.fromtimestamp(t, tzutc()).replace(tzinfo=None) for t in (start, stop))
        auto_rt = float
    if ret_type is None:
        ret_type = auto_rt
    if not exclude_ends:
        ms1 = relativedelta(microseconds=1)
        if start < stop:    # Forward (normal) time order
            start -= ms1
            stop += ms1
        else:               # Reverse time order
            start += ms1
            stop -= ms1
    year_span = math.floor(abs(stop.year - start.year)) + 1
    ic = _croniter(expr_format, start, ret_type=datetime.datetime, day_or=day_or,
                   max_years_between_matches=year_span)
    # define a continue (cont) condition function and step function for the main while loop
    if start < stop:        # Forward
        def cont(v):
            return v < stop
        step = ic.get_next
    else:                   # Reverse
        def cont(v):
            return v > stop
        step = ic.get_prev
    try:
        dt = step()
        while cont(dt):
            if ret_type is float:
                yield ic.get_current(float)
            else:
                yield dt
            dt = step()
    except CroniterBadDateError:
        # Stop iteration when this exception is raised; no match found within the given year range
        return


class HashExpander:

    def __init__(self, cronit):
        self.cron = cronit

    def do(self, idx, hash_type="h", hash_id=None, range_end=None, range_begin=None):
        """Return a hashed/random integer given range/hash information"""
        hours_or_minutes = idx in {0, 1}
        if range_end is None:
            range_end = self.cron.RANGES[idx][1]
            if hours_or_minutes:
                range_end += 1
        if range_begin is None:
            range_begin = self.cron.RANGES[idx][0]
        if hash_type == 'r':
            crc = random.randint(0, 0xFFFFFFFF)
        else:
            crc = binascii.crc32(hash_id) & 0xFFFFFFFF
        if not hours_or_minutes:
            return ((crc >> idx) % (range_end - range_begin + 1)) + range_begin
        return ((crc >> idx) % (range_end - range_begin)) + range_begin

    def match(self, efl, idx, expr, hash_id=None, **kw):
        return hash_expression_re.match(expr)

    def expand(self, efl, idx, expr, hash_id=None, match='', **kw):
        """Expand a hashed/random expression to its normal representation"""
        if match == '':
            match = self.match(efl, idx, expr, hash_id, **kw)
        if not match:
            return expr
        m = match.groupdict()

        if m['hash_type'] == 'h' and hash_id is None:
            raise CroniterBadCronError('Hashed definitions must include hash_id')

        if m['range_begin'] and m['range_end']:
            if int(m['range_begin']) >= int(m['range_end']):
                raise CroniterBadCronError('Range end must be greater than range begin')

        if m['range_begin'] and m['range_end'] and m['divisor']:
            # Example: H(30-59)/10 -> 34-59/10 (i.e. 34,44,54)
            if int(m["divisor"]) == 0:
                raise CroniterBadCronError("Bad expression: {0}".format(expr))

            return '{0}-{1}/{2}'.format(
                self.do(
                    idx,
                    hash_type=m['hash_type'],
                    hash_id=hash_id,
                    range_end=int(m['divisor']),
                ) + int(m['range_begin']),
                int(m['range_end']),
                int(m['divisor']),
            )
        elif m['range_begin'] and m['range_end']:
            # Example: H(0-29) -> 12
            return str(
                self.do(
                    idx,
                    hash_type=m['hash_type'],
                    hash_id=hash_id,
                    range_end=int(m['range_end']),
                    range_begin=int(m['range_begin']),
                )
            )
        elif m['divisor']:
            # Example: H/15 -> 7-59/15 (i.e. 7,22,37,52)
            if int(m["divisor"]) == 0:
                raise CroniterBadCronError("Bad expression: {0}".format(expr))

            return '{0}-{1}/{2}'.format(
                self.do(
                    idx,
                    hash_type=m['hash_type'],
                    hash_id=hash_id,
                    range_end=int(m['divisor']),
                ),
                self.cron.RANGES[idx][1],
                int(m['divisor']),
            )
        else:
            # Example: H -> 32
            return str(
                self.do(
                    idx,
                    hash_type=m['hash_type'],
                    hash_id=hash_id,
                )
            )


EXPANDERS = OrderedDict([
    ('hash', HashExpander),
])
