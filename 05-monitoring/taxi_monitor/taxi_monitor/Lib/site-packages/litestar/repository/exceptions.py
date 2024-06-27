try:
    from advanced_alchemy.exceptions import IntegrityError as ConflictError
    from advanced_alchemy.exceptions import NotFoundError, RepositoryError
except ImportError:  # pragma: no cover
    from ._exceptions import ConflictError, NotFoundError, RepositoryError  # type: ignore[assignment]

__all__ = ("ConflictError", "NotFoundError", "RepositoryError")
