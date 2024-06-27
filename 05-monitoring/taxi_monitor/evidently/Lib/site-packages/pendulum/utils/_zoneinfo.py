from __future__ import annotations

import sys

from typing import TYPE_CHECKING


if sys.version_info < (3, 9):
    # Works around https://github.com/pganssle/zoneinfo/issues/125
    from backports.zoneinfo import TZPATH
    from backports.zoneinfo import InvalidTZPathWarning
    from backports.zoneinfo import ZoneInfoNotFoundError
    from backports.zoneinfo import available_timezones
    from backports.zoneinfo import reset_tzpath

    if TYPE_CHECKING:
        from collections.abc import Iterable
        from datetime import datetime
        from datetime import timedelta
        from datetime import tzinfo
        from typing import Any
        from typing import Protocol

        from typing_extensions import Self

        class _IOBytes(Protocol):
            def read(self, __size: int) -> bytes:
                ...

            def seek(self, __size: int, __whence: int = ...) -> Any:
                ...

        class ZoneInfo(tzinfo):
            @property
            def key(self) -> str:
                ...

            def __init__(self, key: str) -> None:
                ...

            @classmethod
            def no_cache(cls, key: str) -> Self:
                ...

            @classmethod
            def from_file(cls, __fobj: _IOBytes, key: str | None = ...) -> Self:
                ...

            @classmethod
            def clear_cache(cls, *, only_keys: Iterable[str] | None = ...) -> None:
                ...

            def tzname(self, __dt: datetime | None) -> str | None:
                ...

            def utcoffset(self, __dt: datetime | None) -> timedelta | None:
                ...

            def dst(self, __dt: datetime | None) -> timedelta | None:
                ...

    else:
        from backports.zoneinfo import ZoneInfo

else:
    from zoneinfo import TZPATH
    from zoneinfo import InvalidTZPathWarning
    from zoneinfo import ZoneInfo
    from zoneinfo import ZoneInfoNotFoundError
    from zoneinfo import available_timezones
    from zoneinfo import reset_tzpath

__all__ = [
    "ZoneInfo",
    "reset_tzpath",
    "available_timezones",
    "TZPATH",
    "ZoneInfoNotFoundError",
    "InvalidTZPathWarning",
]
