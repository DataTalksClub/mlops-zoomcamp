"""Main package for humanize."""

from __future__ import annotations

import importlib.metadata

from humanize.filesize import naturalsize
from humanize.i18n import activate, deactivate, decimal_separator, thousands_separator
from humanize.number import (
    apnumber,
    clamp,
    fractional,
    intcomma,
    intword,
    metric,
    ordinal,
    scientific,
)
from humanize.time import (
    naturaldate,
    naturalday,
    naturaldelta,
    naturaltime,
    precisedelta,
)

__version__ = importlib.metadata.version(__name__)


__all__ = [
    "__version__",
    "activate",
    "apnumber",
    "clamp",
    "deactivate",
    "decimal_separator",
    "fractional",
    "intcomma",
    "intword",
    "metric",
    "naturaldate",
    "naturalday",
    "naturaldelta",
    "naturalsize",
    "naturaltime",
    "ordinal",
    "precisedelta",
    "scientific",
    "thousands_separator",
]
