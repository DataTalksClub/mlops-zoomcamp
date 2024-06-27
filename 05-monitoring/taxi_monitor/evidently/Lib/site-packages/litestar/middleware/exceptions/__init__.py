from __future__ import annotations

from typing import Any

from litestar.middleware._internal.exceptions import middleware
from litestar.utils.deprecation import warn_deprecation


def __getattr__(name: str) -> Any:
    if name == "ExceptionHandlerMiddleware":
        warn_deprecation(
            version="2.9",
            deprecated_name=name,
            kind="class",
            removal_in="3.0",
            info="ExceptionHandlerMiddleware has been removed from the public API.",
        )
        return middleware.ExceptionHandlerMiddleware
    raise AttributeError(f"module {__name__} has no attribute {name}")
