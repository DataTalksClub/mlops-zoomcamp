import os

from collections import namedtuple
from struct import unpack
from typing import IO
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import pytzdata

from pytzdata.exceptions import TimezoneNotFound

from pendulum.utils._compat import PY2

from .exceptions import InvalidTimezone
from .exceptions import InvalidZoneinfoFile
from .posix_timezone import PosixTimezone
from .posix_timezone import posix_spec
from .timezone import Timezone
from .transition import Transition
from .transition_type import TransitionType


_offset = namedtuple("offset", "utc_total_offset is_dst abbr_idx")

header = namedtuple(
    "header",
    "version " "utclocals " "stdwalls " "leaps " "transitions " "types " "abbr_size",
)


class Reader:
    """
    Reads compiled zoneinfo TZif (\0, 2 or 3) files.
    """

    def __init__(self, extend=True):  # type: (bool) -> None
        self._extend = extend

    def read_for(self, timezone):  # type: (str) -> Timezone
        """
        Read the zoneinfo structure for a given timezone name.

        :param timezone: The timezone.
        """
        try:
            file_path = pytzdata.tz_path(timezone)
        except TimezoneNotFound:
            raise InvalidTimezone(timezone)

        return self.read(file_path)

    def read(self, file_path):  # type: (str) -> Timezone
        """
        Read a zoneinfo structure from the given path.

        :param file_path: The path of a zoneinfo file.
        """
        if not os.path.exists(file_path):
            raise InvalidZoneinfoFile("The tzinfo file does not exist")

        with open(file_path, "rb") as fd:
            return self._parse(fd)

    def _check_read(self, fd, nbytes):  # type: (...) -> bytes
        """
        Reads the given number of bytes from the given file
        and checks that the correct number of bytes could be read.
        """
        result = fd.read(nbytes)

        if (not result and nbytes > 0) or len(result) != nbytes:
            raise InvalidZoneinfoFile(
                "Expected {} bytes reading {}, "
                "but got {}".format(nbytes, fd.name, len(result) if result else 0)
            )

        if PY2:
            return bytearray(result)

        return result

    def _parse(self, fd):  # type: (...) -> Timezone
        """
        Parse a zoneinfo file.
        """
        hdr = self._parse_header(fd)

        if hdr.version in (2, 3):
            # We're skipping the entire v1 file since
            # at least the same data will be found in TZFile 2.
            fd.seek(
                hdr.transitions * 5
                + hdr.types * 6
                + hdr.abbr_size
                + hdr.leaps * 4
                + hdr.stdwalls
                + hdr.utclocals,
                1,
            )

            # Parse the second header
            hdr = self._parse_header(fd)

            if hdr.version != 2 and hdr.version != 3:
                raise InvalidZoneinfoFile(
                    "Header versions mismatch for file {}".format(fd.name)
                )

            # Parse the v2 data
            trans = self._parse_trans_64(fd, hdr.transitions)
            type_idx = self._parse_type_idx(fd, hdr.transitions)
            types = self._parse_types(fd, hdr.types)
            abbrs = self._parse_abbrs(fd, hdr.abbr_size, types)

            fd.seek(hdr.leaps * 8 + hdr.stdwalls + hdr.utclocals, 1)

            trule = self._parse_posix_tz(fd)
        else:
            # TZFile v1
            trans = self._parse_trans_32(fd, hdr.transitions)
            type_idx = self._parse_type_idx(fd, hdr.transitions)
            types = self._parse_types(fd, hdr.types)
            abbrs = self._parse_abbrs(fd, hdr.abbr_size, types)
            trule = None

        types = [
            TransitionType(off, is_dst, abbrs[abbr]) for off, is_dst, abbr in types
        ]

        transitions = []
        previous = None
        for trans, idx in zip(trans, type_idx):
            transition = Transition(trans, types[idx], previous)
            transitions.append(transition)

            previous = transition

        if not transitions:
            transitions.append(Transition(0, types[0], None))

        return Timezone(transitions, posix_rule=trule, extended=self._extend)

    def _parse_header(self, fd):  # type: (...) -> header
        buff = self._check_read(fd, 44)

        if buff[:4] != b"TZif":
            raise InvalidZoneinfoFile(
                'The file "{}" has an invalid header.'.format(fd.name)
            )

        version = {0x00: 1, 0x32: 2, 0x33: 3}.get(buff[4])

        if version is None:
            raise InvalidZoneinfoFile(
                'The file "{}" has an invalid version.'.format(fd.name)
            )

        hdr = header(version, *unpack(">6l", buff[20:44]))

        return hdr

    def _parse_trans_64(self, fd, n):  # type: (IO[Any], int) -> List[int]
        trans = []
        for _ in range(n):
            buff = self._check_read(fd, 8)
            trans.append(unpack(">q", buff)[0])

        return trans

    def _parse_trans_32(self, fd, n):  # type: (IO[Any], int) -> List[int]
        trans = []
        for _ in range(n):
            buff = self._check_read(fd, 4)
            trans.append(unpack(">i", buff)[0])

        return trans

    def _parse_type_idx(self, fd, n):  # type: (IO[Any], int) -> List[int]
        buff = self._check_read(fd, n)

        return list(unpack("{}B".format(n), buff))

    def _parse_types(
        self, fd, n
    ):  # type: (IO[Any], int) -> List[Tuple[Any, bool, int]]
        types = []

        for _ in range(n):
            buff = self._check_read(fd, 6)
            offset = unpack(">l", buff[:4])[0]
            is_dst = buff[4] == 1
            types.append((offset, is_dst, buff[5]))

        return types

    def _parse_abbrs(
        self, fd, n, types
    ):  # type: (IO[Any], int, List[Tuple[Any, bool, int]]) -> Dict[int, str]
        abbrs = {}
        buff = self._check_read(fd, n)

        for offset, is_dst, idx in types:
            if idx not in abbrs:
                abbr = buff[idx : buff.find(b"\0", idx)].decode("utf-8")
                abbrs[idx] = abbr

        return abbrs

    def _parse_posix_tz(self, fd):  # type: (...) -> Optional[PosixTimezone]
        s = fd.read().decode("utf-8")

        if not s.startswith("\n") or not s.endswith("\n"):
            raise InvalidZoneinfoFile('Invalid posix rule in file "{}"'.format(fd.name))

        s = s.strip()

        if not s:
            return

        return posix_spec(s)
