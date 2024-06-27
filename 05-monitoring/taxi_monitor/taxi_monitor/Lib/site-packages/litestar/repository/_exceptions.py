from __future__ import annotations  # pragma: no cover

__all__ = ("ConflictError", "NotFoundError", "RepositoryError")  # pragma: no cover


class RepositoryError(Exception):  # pragma: no cover
    """Base repository exception type."""


class ConflictError(RepositoryError):  # pragma: no cover
    """Data integrity error."""


class NotFoundError(RepositoryError):  # pragma: no cover
    """An identity does not exist."""
