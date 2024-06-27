from __future__ import annotations

from typing import Any

from litestar.utils.deprecation import warn_deprecation

from . import minijinja as _minijinja


def __getattr__(name: str) -> Any:
    warn_deprecation(
        "2.3.0",
        "contrib.minijnja",
        "import",
        removal_in="3.0.0",
        alternative="contrib.minijinja",
    )
    return getattr(_minijinja, name)
