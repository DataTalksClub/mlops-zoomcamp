# mypy: no-warn-redundant-casts
from __future__ import annotations

import datetime as _datetime

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import cast

from pendulum.tz.exceptions import AmbiguousTime
from pendulum.tz.exceptions import InvalidTimezone
from pendulum.tz.exceptions import NonExistingTime
from pendulum.utils._compat import zoneinfo


if TYPE_CHECKING:
    from typing_extensions import Self

POST_TRANSITION = "post"
PRE_TRANSITION = "pre"
TRANSITION_ERROR = "error"


_DT = TypeVar("_DT", bound=_datetime.datetime)


class PendulumTimezone(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def convert(self, dt: _DT, raise_on_unknown_times: bool = False) -> _DT:
        raise NotImplementedError

    @abstractmethod
    def datetime(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        microsecond: int = 0,
    ) -> _datetime.datetime:
        raise NotImplementedError


class Timezone(zoneinfo.ZoneInfo, PendulumTimezone):
    """
    Represents a named timezone.

    The accepted names are those provided by the IANA time zone database.

    >>> from pendulum.tz.timezone import Timezone
    >>> tz = Timezone('Europe/Paris')
    """

    def __new__(cls, key: str) -> Self:
        try:
            return super().__new__(cls, key)  # type: ignore[call-arg]
        except zoneinfo.ZoneInfoNotFoundError:
            raise InvalidTimezone(key)

    @property
    def name(self) -> str:
        return self.key

    def convert(self, dt: _DT, raise_on_unknown_times: bool = False) -> _DT:
        """
        Converts a datetime in the current timezone.

        If the datetime is naive, it will be normalized.

        >>> from datetime import datetime
        >>> from pendulum import timezone
        >>> paris = timezone('Europe/Paris')
        >>> dt = datetime(2013, 3, 31, 2, 30, fold=1)
        >>> in_paris = paris.convert(dt)
        >>> in_paris.isoformat()
        '2013-03-31T03:30:00+02:00'

        If the datetime is aware, it will be properly converted.

        >>> new_york = timezone('America/New_York')
        >>> in_new_york = new_york.convert(in_paris)
        >>> in_new_york.isoformat()
        '2013-03-30T21:30:00-04:00'
        """

        if dt.tzinfo is None:
            # Technically, utcoffset() can return None, but none of the zone information
            # in tzdata sets _tti_before to None. This can be checked with the following
            # code:
            #
            # >>> import zoneinfo
            # >>> from zoneinfo._zoneinfo import ZoneInfo
            #
            # >>> for tzname in zoneinfo.available_timezones():
            # >>>     if ZoneInfo(tzname)._tti_before is None:
            # >>>         print(tzname)

            offset_before = cast(
                _datetime.timedelta,
                (self.utcoffset(dt.replace(fold=0)) if dt.fold else self.utcoffset(dt)),
            )
            offset_after = cast(
                _datetime.timedelta,
                (self.utcoffset(dt) if dt.fold else self.utcoffset(dt.replace(fold=1))),
            )

            if offset_after > offset_before:
                # Skipped time
                if raise_on_unknown_times:
                    raise NonExistingTime(dt)

                dt = cast(
                    _DT,
                    dt
                    + (
                        (offset_after - offset_before)
                        if dt.fold
                        else (offset_before - offset_after)
                    ),
                )
            elif offset_before > offset_after and raise_on_unknown_times:
                # Repeated time
                raise AmbiguousTime(dt)

            return dt.replace(tzinfo=self)

        return cast(_DT, dt.astimezone(self))

    def datetime(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        microsecond: int = 0,
    ) -> _datetime.datetime:
        """
        Return a normalized datetime for the current timezone.
        """
        return self.convert(
            _datetime.datetime(
                year, month, day, hour, minute, second, microsecond, fold=1
            )
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"


class FixedTimezone(_datetime.tzinfo, PendulumTimezone):
    def __init__(self, offset: int, name: str | None = None) -> None:
        sign = "-" if offset < 0 else "+"

        minutes = offset / 60
        hour, minute = divmod(abs(int(minutes)), 60)

        if not name:
            name = f"{sign}{hour:02d}:{minute:02d}"

        self._name = name
        self._offset = offset
        self._utcoffset = _datetime.timedelta(seconds=offset)

    @property
    def name(self) -> str:
        return self._name

    def convert(self, dt: _DT, raise_on_unknown_times: bool = False) -> _DT:
        if dt.tzinfo is None:
            return dt.__class__(
                dt.year,
                dt.month,
                dt.day,
                dt.hour,
                dt.minute,
                dt.second,
                dt.microsecond,
                tzinfo=self,
                fold=0,
            )

        return cast(_DT, dt.astimezone(self))

    def datetime(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        microsecond: int = 0,
    ) -> _datetime.datetime:
        return self.convert(
            _datetime.datetime(
                year, month, day, hour, minute, second, microsecond, fold=1
            )
        )

    @property
    def offset(self) -> int:
        return self._offset

    def utcoffset(self, dt: _datetime.datetime | None) -> _datetime.timedelta:
        return self._utcoffset

    def dst(self, dt: _datetime.datetime | None) -> _datetime.timedelta:
        return _datetime.timedelta()

    def fromutc(self, dt: _datetime.datetime) -> _datetime.datetime:
        # Use the stdlib datetime's add method to avoid infinite recursion
        return (_datetime.datetime.__add__(dt, self._utcoffset)).replace(tzinfo=self)

    def tzname(self, dt: _datetime.datetime | None) -> str | None:
        return self._name

    def __getinitargs__(self) -> tuple[int, str]:
        return self._offset, self._name

    def __repr__(self) -> str:
        name = ""
        if self._name:
            name = f', name="{self._name}"'

        return f"{self.__class__.__name__}({self._offset}{name})"


UTC = Timezone("UTC")
