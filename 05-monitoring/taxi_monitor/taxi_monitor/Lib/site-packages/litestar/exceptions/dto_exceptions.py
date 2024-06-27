from __future__ import annotations

from litestar.exceptions import LitestarException

__all__ = ("DTOFactoryException", "InvalidAnnotationException")


class DTOFactoryException(LitestarException):
    """Base DTO exception type."""


class InvalidAnnotationException(DTOFactoryException):
    """Unexpected DTO type argument."""
