from __future__ import annotations

from pendulum.parsing.exceptions import ParserError


class PendulumException(Exception):
    pass


__all__ = [
    "ParserError",
    "PendulumException",
]
