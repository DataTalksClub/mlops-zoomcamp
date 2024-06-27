from __future__ import annotations

import re
import sys
from typing import Literal, NamedTuple

__all__ = ("Version", "get_version", "parse_version")


if sys.version_info >= (3, 10):
    import importlib.metadata as importlib_metadata
else:
    import importlib_metadata


_ReleaseLevel = Literal["alpha", "beta", "rc", "final"]
_PRE_RELEASE_TAGS = {"alpha", "a", "beta", "b", "rc"}
_PRE_RELEASE_TAGS_CONVERSIONS: dict[str, _ReleaseLevel] = {"a": "alpha", "b": "beta"}

_VERSION_PARTS_RE = re.compile(r"(\d+|[a-z]+|\.)")


class Version(NamedTuple):
    """Litestar version information"""

    major: int
    minor: int
    patch: int
    release_level: _ReleaseLevel
    serial: int

    def formatted(self, short: bool = False) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if not short:
            version += f"{self.release_level}{self.serial}"
        return version


def parse_version(raw_version: str) -> Version:
    """Parse a version string into a :class:`Version`"""
    parts = [p for p in _VERSION_PARTS_RE.split(raw_version) if p and p != "."]
    release_level: _ReleaseLevel = "final"
    serial = "0"

    if len(parts) == 3:
        major, minor, patch = parts
    elif len(parts) == 5:
        major, minor, patch, release_level, serial = parts  # type: ignore[assignment]
        if release_level not in _PRE_RELEASE_TAGS:
            raise ValueError(f"Invalid release level: {release_level}")
        release_level = _PRE_RELEASE_TAGS_CONVERSIONS.get(release_level, release_level)
    else:
        raise ValueError(f"Invalid version: {raw_version}")

    return Version(
        major=int(major), minor=int(minor), patch=int(patch), release_level=release_level, serial=int(serial)
    )


def get_version() -> Version:
    """Get the version of the installed litestar package"""
    return parse_version(importlib_metadata.version("litestar"))
