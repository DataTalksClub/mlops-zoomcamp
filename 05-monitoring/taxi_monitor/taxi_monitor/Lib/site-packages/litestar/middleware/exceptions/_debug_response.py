from __future__ import annotations

from typing import Any

from litestar.exceptions import responses
from litestar.utils.deprecation import warn_deprecation


def __getattr__(name: str) -> Any:
    if name == "create_debug_response":
        warn_deprecation(
            version="2.9",
            deprecated_name=name,
            kind="function",
            removal_in="3.0",
            alternative="litestar.exceptions.responses.create_debug_response",
        )
        return responses.create_debug_response

    raise AttributeError(f"module {__name__} has no attribute {name}")
