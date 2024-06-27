from __future__ import annotations
from datetime import date,datetime,time,timedelta,timezone,tzinfo
from functools import lru_cache
import re
from typing import Any
from._types import ParseFloat
_TIME_RE_STR='([01][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])(?:\\.([0-9]{1,6})[0-9]*)?'
RE_NUMBER=re.compile('\n0\n(?:\n    x[0-9A-Fa-f](?:_?[0-9A-Fa-f])*   # hex\n    |\n    b[01](?:_?[01])*                 # bin\n    |\n    o[0-7](?:_?[0-7])*               # oct\n)\n|\n[+-]?(?:0|[1-9](?:_?[0-9])*)         # dec, integer part\n(?P<floatpart>\n    (?:\\.[0-9](?:_?[0-9])*)?         # optional fractional part\n    (?:[eE][+-]?[0-9](?:_?[0-9])*)?  # optional exponent part\n)\n',flags=re.VERBOSE)
RE_LOCALTIME=re.compile(_TIME_RE_STR)
RE_DATETIME=re.compile(f"""
([0-9]{{4}})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])  # date, e.g. 1988-10-27
(?:
    [Tt ]
    {_TIME_RE_STR}
    (?:([Zz])|([+-])([01][0-9]|2[0-3]):([0-5][0-9]))?  # optional time offset
)?
""",flags=re.VERBOSE)
def match_to_datetime(match):
	H,I,J,B,K,L,C,M,D,N,O=match.groups();E,F,G=int(H),int(I),int(J)
	if B is None:return date(E,F,G)
	P,Q,R=int(B),int(K),int(L);S=int(C.ljust(6,'0'))if C else 0
	if D:A=cached_tz(N,O,D)
	elif M:A=timezone.utc
	else:A=None
	return datetime(E,F,G,P,Q,R,S,tzinfo=A)
@lru_cache(maxsize=None)
def cached_tz(hour_str,minute_str,sign_str):A=1 if sign_str=='+'else-1;return timezone(timedelta(hours=A*int(hour_str),minutes=A*int(minute_str)))
def match_to_localtime(match):B,C,D,A=match.groups();E=int(A.ljust(6,'0'))if A else 0;return time(int(B),int(C),int(D),E)
def match_to_number(match,parse_float):
	A=match
	if A.group('floatpart'):return parse_float(A.group())
	return int(A.group(),0)