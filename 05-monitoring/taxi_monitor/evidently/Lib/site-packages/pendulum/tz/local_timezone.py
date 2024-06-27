from __future__ import annotations

import contextlib
import os
import re
import sys
import warnings

from contextlib import contextmanager
from typing import Iterator
from typing import cast

from pendulum.tz.exceptions import InvalidTimezone
from pendulum.tz.timezone import UTC
from pendulum.tz.timezone import FixedTimezone
from pendulum.tz.timezone import Timezone


if sys.platform == "win32":
    import winreg

_mock_local_timezone = None
_local_timezone = None


def get_local_timezone() -> Timezone | FixedTimezone:
    global _local_timezone

    if _mock_local_timezone is not None:
        return _mock_local_timezone

    if _local_timezone is None:
        tz = _get_system_timezone()

        _local_timezone = tz

    return _local_timezone


def set_local_timezone(mock: str | Timezone | None = None) -> None:
    global _mock_local_timezone

    _mock_local_timezone = mock


@contextmanager
def test_local_timezone(mock: Timezone) -> Iterator[None]:
    set_local_timezone(mock)

    yield

    set_local_timezone()


def _get_system_timezone() -> Timezone:
    if sys.platform == "win32":
        return _get_windows_timezone()
    elif "darwin" in sys.platform:
        return _get_darwin_timezone()

    return _get_unix_timezone()


if sys.platform == "win32":

    def _get_windows_timezone() -> Timezone:
        from pendulum.tz.data.windows import windows_timezones

        # Windows is special. It has unique time zone names (in several
        # meanings of the word) available, but unfortunately, they can be
        # translated to the language of the operating system, so we need to
        # do a backwards lookup, by going through all time zones and see which
        # one matches.
        handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)

        tz_local_key_name = r"SYSTEM\CurrentControlSet\Control\TimeZoneInformation"
        localtz = winreg.OpenKey(handle, tz_local_key_name)

        timezone_info = {}
        size = winreg.QueryInfoKey(localtz)[1]
        for i in range(size):
            data = winreg.EnumValue(localtz, i)
            timezone_info[data[0]] = data[1]

        localtz.Close()

        if "TimeZoneKeyName" in timezone_info:
            # Windows 7 (and Vista?)

            # For some reason this returns a string with loads of NUL bytes at
            # least on some systems. I don't know if this is a bug somewhere, I
            # just work around it.
            tzkeyname = timezone_info["TimeZoneKeyName"].split("\x00", 1)[0]
        else:
            # Windows 2000 or XP

            # This is the localized name:
            tzwin = timezone_info["StandardName"]

            # Open the list of timezones to look up the real name:
            tz_key_name = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Time Zones"
            tzkey = winreg.OpenKey(handle, tz_key_name)

            # Now, match this value to Time Zone information
            tzkeyname = None
            for i in range(winreg.QueryInfoKey(tzkey)[0]):
                subkey = winreg.EnumKey(tzkey, i)
                sub = winreg.OpenKey(tzkey, subkey)

                info = {}
                size = winreg.QueryInfoKey(sub)[1]
                for i in range(size):
                    data = winreg.EnumValue(sub, i)
                    info[data[0]] = data[1]

                sub.Close()
                with contextlib.suppress(KeyError):
                    # This timezone didn't have proper configuration.
                    # Ignore it.
                    if info["Std"] == tzwin:
                        tzkeyname = subkey
                        break

            tzkey.Close()
            handle.Close()

        if tzkeyname is None:
            raise LookupError("Can not find Windows timezone configuration")

        timezone = windows_timezones.get(tzkeyname)
        if timezone is None:
            # Nope, that didn't work. Try adding "Standard Time",
            # it seems to work a lot of times:
            timezone = windows_timezones.get(tzkeyname + " Standard Time")

        # Return what we have.
        if timezone is None:
            raise LookupError("Unable to find timezone " + tzkeyname)

        return Timezone(timezone)

else:

    def _get_windows_timezone() -> Timezone:
        raise NotImplementedError


def _get_darwin_timezone() -> Timezone:
    # link will be something like /usr/share/zoneinfo/America/Los_Angeles.
    link = os.readlink("/etc/localtime")
    tzname = link[link.rfind("zoneinfo/") + 9 :]

    return Timezone(tzname)


def _get_unix_timezone(_root: str = "/") -> Timezone:
    tzenv = os.environ.get("TZ")
    if tzenv:
        with contextlib.suppress(ValueError):
            return _tz_from_env(tzenv)

    # Now look for distribution specific configuration files
    # that contain the timezone name.
    tzpath = os.path.join(_root, "etc/timezone")
    if os.path.isfile(tzpath):
        with open(tzpath, "rb") as tzfile:
            tzfile_data = tzfile.read()

            # Issue #3 was that /etc/timezone was a zoneinfo file.
            # That's a misconfiguration, but we need to handle it gracefully:
            if tzfile_data[:5] != b"TZif2":
                etctz = tzfile_data.strip().decode()
                # Get rid of host definitions and comments:
                if " " in etctz:
                    etctz, dummy = etctz.split(" ", 1)
                if "#" in etctz:
                    etctz, dummy = etctz.split("#", 1)

                return Timezone(etctz.replace(" ", "_"))

    # CentOS has a ZONE setting in /etc/sysconfig/clock,
    # OpenSUSE has a TIMEZONE setting in /etc/sysconfig/clock and
    # Gentoo has a TIMEZONE setting in /etc/conf.d/clock
    # We look through these files for a timezone:
    zone_re = re.compile(r'\s*ZONE\s*=\s*"')
    timezone_re = re.compile(r'\s*TIMEZONE\s*=\s*"')
    end_re = re.compile('"')

    for filename in ("etc/sysconfig/clock", "etc/conf.d/clock"):
        tzpath = os.path.join(_root, filename)
        if not os.path.isfile(tzpath):
            continue

        with open(tzpath) as tzfile:
            data = tzfile.readlines()

        for line in data:
            # Look for the ZONE= setting.
            match = zone_re.match(line)
            if match is None:
                # No ZONE= setting. Look for the TIMEZONE= setting.
                match = timezone_re.match(line)

            if match is not None:
                # Some setting existed
                line = line[match.end() :]
                etctz = line[
                    : cast(
                        re.Match, end_re.search(line)  # type: ignore[type-arg]
                    ).start()
                ]

                parts = list(reversed(etctz.replace(" ", "_").split(os.path.sep)))
                tzpath_parts: list[str] = []
                while parts:
                    tzpath_parts.insert(0, parts.pop(0))

                    with contextlib.suppress(InvalidTimezone):
                        return Timezone(os.path.join(*tzpath_parts))

    # systemd distributions use symlinks that include the zone name,
    # see manpage of localtime(5) and timedatectl(1)
    tzpath = os.path.join(_root, "etc", "localtime")
    if os.path.isfile(tzpath) and os.path.islink(tzpath):
        parts = list(
            reversed(os.path.realpath(tzpath).replace(" ", "_").split(os.path.sep))
        )
        tzpath_parts: list[str] = []  # type: ignore[no-redef]
        while parts:
            tzpath_parts.insert(0, parts.pop(0))
            with contextlib.suppress(InvalidTimezone):
                return Timezone(os.path.join(*tzpath_parts))

    # No explicit setting existed. Use localtime
    for filename in ("etc/localtime", "usr/local/etc/localtime"):
        tzpath = os.path.join(_root, filename)

        if not os.path.isfile(tzpath):
            continue

        with open(tzpath, "rb") as f:
            return Timezone.from_file(f)

    warnings.warn(
        "Unable not find any timezone configuration, defaulting to UTC.", stacklevel=1
    )

    return UTC


def _tz_from_env(tzenv: str) -> Timezone:
    if tzenv[0] == ":":
        tzenv = tzenv[1:]

    # TZ specifies a file
    if os.path.isfile(tzenv):
        with open(tzenv, "rb") as f:
            return Timezone.from_file(f)

    # TZ specifies a zoneinfo zone.
    try:
        return Timezone(tzenv)
    except ValueError:
        raise
