from __future__ import annotations

import datetime as dt
import functools
import inspect
import os
import sys
import time as time_module
import uuid
from collections.abc import Generator
from time import gmtime as orig_gmtime
from time import struct_time
from types import TracebackType
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Generator as TypingGenerator
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union
from typing import cast
from typing import overload
from unittest import TestCase
from unittest import mock

import _time_machine
from dateutil.parser import parse as parse_datetime

# time.clock_gettime and time.CLOCK_REALTIME not always available
# e.g. on builds against old macOS = official Python.org installer
try:
    from time import CLOCK_REALTIME
except ImportError:
    # Dummy value that won't compare equal to any value
    CLOCK_REALTIME = sys.maxsize

try:
    from time import tzset

    HAVE_TZSET = True
except ImportError:  # pragma: no cover
    # Windows
    HAVE_TZSET = False

if sys.version_info >= (3, 9):
    from zoneinfo import ZoneInfo

    HAVE_ZONEINFO = True
else:
    try:
        from backports.zoneinfo import ZoneInfo

        HAVE_ZONEINFO = True
    except ImportError:  # pragma: no cover
        HAVE_ZONEINFO = False


try:
    import pytest
except ImportError:  # pragma: no cover
    HAVE_PYTEST = False
else:
    HAVE_PYTEST = True

NANOSECONDS_PER_SECOND = 1_000_000_000

# Windows' time epoch is not unix epoch but in 1601. This constant helps us
# translate to it.
_system_epoch = orig_gmtime(0)
SYSTEM_EPOCH_TIMESTAMP_NS = int(
    dt.datetime(
        _system_epoch.tm_year,
        _system_epoch.tm_mon,
        _system_epoch.tm_mday,
        _system_epoch.tm_hour,
        _system_epoch.tm_min,
        _system_epoch.tm_sec,
        tzinfo=dt.timezone.utc,
    ).timestamp()
    * NANOSECONDS_PER_SECOND
)

DestinationBaseType = Union[
    int,
    float,
    dt.datetime,
    dt.timedelta,
    dt.date,
    str,
]
DestinationType = Union[
    DestinationBaseType,
    Callable[[], DestinationBaseType],
    TypingGenerator[DestinationBaseType, None, None],
]

_F = TypeVar("_F", bound=Callable[..., Any])
_AF = TypeVar("_AF", bound=Callable[..., Awaitable[Any]])
TestCaseType = TypeVar("TestCaseType", bound=Type[TestCase])

# copied from typeshed:
_TimeTuple = Tuple[int, int, int, int, int, int, int, int, int]


def extract_timestamp_tzname(
    destination: DestinationType,
) -> tuple[float, str | None]:
    dest: DestinationBaseType
    if isinstance(destination, Generator):
        dest = next(destination)
    elif callable(destination):
        dest = destination()
    else:
        dest = destination

    timestamp: float
    tzname: str | None = None
    if isinstance(dest, int):
        timestamp = float(dest)
    elif isinstance(dest, float):
        timestamp = dest
    elif isinstance(dest, dt.datetime):
        if HAVE_ZONEINFO and isinstance(dest.tzinfo, ZoneInfo):
            tzname = dest.tzinfo.key
        if dest.tzinfo is None:
            dest = dest.replace(tzinfo=dt.timezone.utc)
        timestamp = dest.timestamp()
    elif isinstance(dest, dt.timedelta):
        timestamp = time_module.time() + dest.total_seconds()
    elif isinstance(dest, dt.date):
        timestamp = dt.datetime.combine(
            dest, dt.time(0, 0), tzinfo=dt.timezone.utc
        ).timestamp()
    elif isinstance(dest, str):
        timestamp = parse_datetime(dest).timestamp()
    else:
        raise TypeError(f"Unsupported destination {dest!r}")

    return timestamp, tzname


class Coordinates:
    def __init__(
        self,
        destination_timestamp: float,
        destination_tzname: str | None,
        tick: bool,
    ) -> None:
        self._destination_timestamp_ns = int(
            destination_timestamp * NANOSECONDS_PER_SECOND
        )
        self._destination_tzname = destination_tzname
        self._tick = tick
        self._requested = False

    def time(self) -> float:
        return self.time_ns() / NANOSECONDS_PER_SECOND

    def time_ns(self) -> int:
        if not self._tick:
            return self._destination_timestamp_ns

        base = SYSTEM_EPOCH_TIMESTAMP_NS + self._destination_timestamp_ns
        now_ns: int = _time_machine.original_time_ns()

        if not self._requested:
            self._requested = True
            self._real_start_timestamp_ns = now_ns
            return base

        return base + (now_ns - self._real_start_timestamp_ns)

    def shift(self, delta: dt.timedelta | int | float) -> None:
        if isinstance(delta, dt.timedelta):
            total_seconds = delta.total_seconds()
        elif isinstance(delta, (int, float)):
            total_seconds = delta
        else:
            raise TypeError(f"Unsupported type for delta argument: {delta!r}")

        self._destination_timestamp_ns += int(total_seconds * NANOSECONDS_PER_SECOND)

    def move_to(
        self,
        destination: DestinationType,
        tick: bool | None = None,
    ) -> None:
        self._stop()
        timestamp, self._destination_tzname = extract_timestamp_tzname(destination)
        self._destination_timestamp_ns = int(timestamp * NANOSECONDS_PER_SECOND)
        self._requested = False
        self._start()
        if tick is not None:
            self._tick = tick

    def _start(self) -> None:
        if HAVE_TZSET and self._destination_tzname is not None:
            self._orig_tz = os.environ.get("TZ")
            os.environ["TZ"] = self._destination_tzname
            tzset()

    def _stop(self) -> None:
        if HAVE_TZSET and self._destination_tzname is not None:
            if self._orig_tz is None:
                del os.environ["TZ"]
            else:
                os.environ["TZ"] = self._orig_tz
            tzset()


coordinates_stack: list[Coordinates] = []

# During time travel, patch the uuid module's time-based generation function to
# None, which makes it use time.time(). Otherwise it makes a system call to
# find the current datetime. The time it finds is stored in generated UUID1
# values.
uuid_generate_time_attr = "_generate_time_safe"
uuid_generate_time_patcher = mock.patch.object(uuid, uuid_generate_time_attr, new=None)
uuid_uuid_create_patcher = mock.patch.object(uuid, "_UuidCreate", new=None)


class travel:
    def __init__(self, destination: DestinationType, *, tick: bool = True) -> None:
        self.destination_timestamp, self.destination_tzname = extract_timestamp_tzname(
            destination
        )
        self.tick = tick

    def start(self) -> Coordinates:
        global coordinates_stack

        _time_machine.patch_if_needed()

        if not coordinates_stack:
            if sys.version_info < (3, 9):
                # We need to cause the functions to be loaded before we patch
                # them out, which is done by this internal function before:
                # https://github.com/python/cpython/pull/19948
                uuid._load_system_functions()
            uuid_generate_time_patcher.start()
            uuid_uuid_create_patcher.start()

        coordinates = Coordinates(
            destination_timestamp=self.destination_timestamp,
            destination_tzname=self.destination_tzname,
            tick=self.tick,
        )
        coordinates_stack.append(coordinates)
        coordinates._start()

        return coordinates

    def stop(self) -> None:
        global coordinates_stack
        coordinates_stack.pop()._stop()

        if not coordinates_stack:
            uuid_generate_time_patcher.stop()
            uuid_uuid_create_patcher.stop()

    def __enter__(self) -> Coordinates:
        return self.start()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.stop()

    @overload
    def __call__(self, wrapped: TestCaseType) -> TestCaseType:  # pragma: no cover
        ...

    @overload
    def __call__(self, wrapped: _AF) -> _AF:  # pragma: no cover
        ...

    @overload
    def __call__(self, wrapped: _F) -> _F:  # pragma: no cover
        ...

    # 'Any' below is workaround for Mypy error:
    # Overloaded function implementation does not accept all possible arguments
    # of signature
    def __call__(
        self, wrapped: TestCaseType | _AF | _F | Any
    ) -> TestCaseType | _AF | _F | Any:
        if isinstance(wrapped, type):
            # Class decorator
            if not issubclass(wrapped, TestCase):
                raise TypeError("Can only decorate unittest.TestCase subclasses.")

            # Modify the setUpClass method
            orig_setUpClass = wrapped.setUpClass.__func__  # type: ignore[attr-defined]

            @functools.wraps(orig_setUpClass)
            def setUpClass(cls: type[TestCase]) -> None:
                self.__enter__()
                try:
                    orig_setUpClass(cls)
                except Exception:
                    self.__exit__(*sys.exc_info())
                    raise

            wrapped.setUpClass = classmethod(setUpClass)  # type: ignore[assignment]

            orig_tearDownClass = (
                wrapped.tearDownClass.__func__  # type: ignore[attr-defined]
            )

            @functools.wraps(orig_tearDownClass)
            def tearDownClass(cls: type[TestCase]) -> None:
                orig_tearDownClass(cls)
                self.__exit__(None, None, None)

            wrapped.tearDownClass = classmethod(  # type: ignore[assignment]
                tearDownClass
            )
            return cast(TestCaseType, wrapped)
        elif inspect.iscoroutinefunction(wrapped):

            @functools.wraps(wrapped)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                with self:
                    return await wrapped(*args, **kwargs)

            return cast(_AF, wrapper)
        else:
            assert callable(wrapped)

            @functools.wraps(wrapped)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                with self:
                    return wrapped(*args, **kwargs)

            return cast(_F, wrapper)


# datetime module


def now(tz: dt.tzinfo | None = None) -> dt.datetime:
    if not coordinates_stack:
        result: dt.datetime = _time_machine.original_now(tz)
        return result
    return dt.datetime.fromtimestamp(time(), tz)


def utcnow() -> dt.datetime:
    if not coordinates_stack:
        result: dt.datetime = _time_machine.original_utcnow()
        return result
    return dt.datetime.fromtimestamp(time(), dt.timezone.utc).replace(tzinfo=None)


# time module


def clock_gettime(clk_id: int) -> float:
    if not coordinates_stack or clk_id != CLOCK_REALTIME:
        result: float = _time_machine.original_clock_gettime(clk_id)
        return result
    return time()


def clock_gettime_ns(clk_id: int) -> int:
    if not coordinates_stack or clk_id != CLOCK_REALTIME:
        result: int = _time_machine.original_clock_gettime_ns(clk_id)
        return result
    return time_ns()


def gmtime(secs: float | None = None) -> struct_time:
    result: struct_time
    if not coordinates_stack or secs is not None:
        result = _time_machine.original_gmtime(secs)
    else:
        result = _time_machine.original_gmtime(coordinates_stack[-1].time())
    return result


def localtime(secs: float | None = None) -> struct_time:
    result: struct_time
    if not coordinates_stack or secs is not None:
        result = _time_machine.original_localtime(secs)
    else:
        result = _time_machine.original_localtime(coordinates_stack[-1].time())
    return result


def strftime(format: str, t: _TimeTuple | struct_time | None = None) -> str:
    result: str
    if t is not None:
        result = _time_machine.original_strftime(format, t)
    elif not coordinates_stack:
        result = _time_machine.original_strftime(format)
    else:
        result = _time_machine.original_strftime(format, localtime())
    return result


def time() -> float:
    if not coordinates_stack:
        result: float = _time_machine.original_time()
        return result
    return coordinates_stack[-1].time()


def time_ns() -> int:
    if not coordinates_stack:
        result: int = _time_machine.original_time_ns()
        return result
    return coordinates_stack[-1].time_ns()


# pytest plugin

if HAVE_PYTEST:  # pragma: no branch

    class TimeMachineFixture:
        traveller: travel | None
        coordinates: Coordinates | None

        def __init__(self) -> None:
            self.traveller = None
            self.coordinates = None

        def move_to(
            self,
            destination: DestinationType,
            tick: bool | None = None,
        ) -> None:
            if self.traveller is None:
                if tick is None:
                    tick = True
                self.traveller = travel(destination, tick=tick)
                self.coordinates = self.traveller.start()
            else:
                assert self.coordinates is not None
                self.coordinates.move_to(destination, tick=tick)

        def shift(self, delta: dt.timedelta | int | float) -> None:
            if self.traveller is None:
                raise RuntimeError(
                    "Initialize time_machine with move_to() before using shift()."
                )
            assert self.coordinates is not None
            self.coordinates.shift(delta=delta)

        def stop(self) -> None:
            if self.traveller is not None:
                self.traveller.stop()

    @pytest.fixture(name="time_machine")
    def time_machine_fixture() -> TypingGenerator[TimeMachineFixture, None, None]:
        fixture = TimeMachineFixture()
        yield fixture
        fixture.stop()


# escape hatch


class _EscapeHatchDatetimeDatetime:
    def now(self, tz: dt.tzinfo | None = None) -> dt.datetime:
        result: dt.datetime = _time_machine.original_now(tz)
        return result

    def utcnow(self) -> dt.datetime:
        result: dt.datetime = _time_machine.original_utcnow()
        return result


class _EscapeHatchDatetime:
    def __init__(self) -> None:
        self.datetime = _EscapeHatchDatetimeDatetime()


class _EscapeHatchTime:
    def clock_gettime(self, clk_id: int) -> float:
        result: float = _time_machine.original_clock_gettime(clk_id)
        return result

    def clock_gettime_ns(self, clk_id: int) -> int:
        result: int = _time_machine.original_clock_gettime_ns(clk_id)
        return result

    def gmtime(self, secs: float | None = None) -> struct_time:
        result: struct_time = _time_machine.original_gmtime(secs)
        return result

    def localtime(self, secs: float | None = None) -> struct_time:
        result: struct_time = _time_machine.original_localtime(secs)
        return result

    def monotonic(self) -> float:
        result: float = _time_machine.original_monotonic()
        return result

    def monotonic_ns(self) -> int:
        result: int = _time_machine.original_monotonic_ns()
        return result

    def strftime(self, format: str, t: _TimeTuple | struct_time | None = None) -> str:
        result: str
        if t is not None:
            result = _time_machine.original_strftime(format, t)
        else:
            result = _time_machine.original_strftime(format)
        return result

    def time(self) -> float:
        result: float = _time_machine.original_time()
        return result

    def time_ns(self) -> int:
        result: int = _time_machine.original_time_ns()
        return result


class _EscapeHatch:
    def __init__(self) -> None:
        self.datetime = _EscapeHatchDatetime()
        self.time = _EscapeHatchTime()

    def is_travelling(self) -> bool:
        return bool(coordinates_stack)


escape_hatch = _EscapeHatch()
