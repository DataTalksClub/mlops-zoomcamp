from __future__ import annotations

import sys

from pendulum.utils import _zoneinfo as zoneinfo


PYPY = hasattr(sys, "pypy_version_info")

if sys.version_info < (3, 9):
    import importlib_resources as resources
else:
    from importlib import resources

__all__ = ["resources", "zoneinfo"]
