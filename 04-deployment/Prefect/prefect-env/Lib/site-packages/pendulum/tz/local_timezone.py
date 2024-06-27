import os
import re
import sys

from contextlib import contextmanager
from typing import Iterator
from typing import Optional
from typing import Union

from .timezone import Timezone
from .timezone import TimezoneFile
from .zoneinfo.exceptions import InvalidTimezone


try:
    import _winreg as winreg
except ImportError:
    try:
        import winreg
    except ImportError:
        winreg = None


_mock_local_timezone = None
_local_timezone = None


def get_local_timezone():  # type: () -> Timezone
    global _local_timezone

    if _mock_local_timezone is not None:
        return _mock_local_timezone

    if _local_timezone is None:
        tz = _get_system_timezone()

        _local_timezone = tz

    return _local_timezone


def set_local_timezone(mock=None):  # type: (Optional[Union[str, Timezone]]) -> None
    global _mock_local_timezone

    _mock_local_timezone = mock


@contextmanager
def test_local_timezone(mock):  # type: (Timezone) -> Iterator[None]
    set_local_timezone(mock)

    yield

    set_local_timezone()


def _get_system_timezone():  # type: () -> Timezone
    if sys.platform == "win32":
        return _get_windows_timezone()
    elif "darwin" in sys.platform:
        return _get_darwin_timezone()

    return _get_unix_timezone()


def _get_windows_timezone():  # type: () -> Timezone
    from .data.windows import windows_timezones

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
            try:
                if info["Std"] == tzwin:
                    tzkeyname = subkey
                    break
            except KeyError:
                # This timezone didn't have proper configuration.
                # Ignore it.
                pass

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


def _get_darwin_timezone():  # type: () -> Timezone
    # link will be something like /usr/share/zoneinfo/America/Los_Angeles.
    link = os.readlink("/etc/localtime")
    tzname = link[link.rfind("zoneinfo/") + 9 :]

    return Timezone(tzname)


def _get_unix_timezone(_root="/"):  # type: (str) -> Timezone
    tzenv = os.environ.get("TZ")
    if tzenv:
        try:
            return _tz_from_env(tzenv)
        except ValueError:
            pass

    # Now look for distribution specific configuration files
    # that contain the timezone name.
    tzpath = os.path.join(_root, "etc/timezone")
    if os.path.exists(tzpath):
        with open(tzpath, "rb") as tzfile:
            data = tzfile.read()

            # Issue #3 was that /etc/timezone was a zoneinfo file.
            # That's a misconfiguration, but we need to handle it gracefully:
            if data[:5] != "TZif2":
                etctz = data.strip().decode()
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
        if not os.path.exists(tzpath):
            continue

        with open(tzpath, "rt") as tzfile:
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
                etctz = line[: end_re.search(line).start()]

                parts = list(reversed(etctz.replace(" ", "_").split(os.path.sep)))
                tzpath = []
                while parts:
                    tzpath.insert(0, parts.pop(0))

                    try:
                        return Timezone(os.path.join(*tzpath))
                    except InvalidTimezone:
                        pass

    # systemd distributions use symlinks that include the zone name,
    # see manpage of localtime(5) and timedatectl(1)
    tzpath = os.path.join(_root, "etc", "localtime")
    if os.path.exists(tzpath) and os.path.islink(tzpath):
        parts = list(
            reversed(os.path.realpath(tzpath).replace(" ", "_").split(os.path.sep))
        )
        tzpath = []
        while parts:
            tzpath.insert(0, parts.pop(0))
            try:
                return Timezone(os.path.join(*tzpath))
            except InvalidTimezone:
                pass

    # No explicit setting existed. Use localtime
    for filename in ("etc/localtime", "usr/local/etc/localtime"):
        tzpath = os.path.join(_root, filename)

        if not os.path.exists(tzpath):
            continue

        return TimezoneFile(tzpath)

    raise RuntimeError("Unable to find any timezone configuration")


def _tz_from_env(tzenv):  # type: (str) -> Timezone
    if tzenv[0] == ":":
        tzenv = tzenv[1:]

    # TZ specifies a file
    if os.path.exists(tzenv):
        return TimezoneFile(tzenv)

    # TZ specifies a zoneinfo zone.
    try:
        return Timezone(tzenv)
    except ValueError:
        raise
