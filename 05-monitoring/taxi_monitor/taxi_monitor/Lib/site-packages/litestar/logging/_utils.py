from __future__ import annotations

from typing import Any

__all__ = ("resolve_handlers",)


def resolve_handlers(handlers: list[Any]) -> list[Any]:
    """Convert list of string of handlers to the object of respective handler.

    Indexing the list performs the evaluation of the object.

    Args:
        handlers: An instance of 'ConvertingList'

    Returns:
        A list of resolved handlers.

    Notes:
        Due to missing typing in 'typeshed' we cannot type this as ConvertingList for now.
    """
    return [handlers[i] for i in range(len(handlers))]
