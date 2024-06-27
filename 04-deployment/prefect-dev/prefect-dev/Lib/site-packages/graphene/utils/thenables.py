"""
This file is used mainly as a bridge for thenable abstractions.
"""

from inspect import isawaitable


def await_and_execute(obj, on_resolve):
    async def build_resolve_async():
        return on_resolve(await obj)

    return build_resolve_async()


def maybe_thenable(obj, on_resolve):
    """
    Execute a on_resolve function once the thenable is resolved,
    returning the same type of object inputed.
    If the object is not thenable, it should return on_resolve(obj)
    """
    if isawaitable(obj):
        return await_and_execute(obj, on_resolve)

    # If it's not awaitable, return the function executed over the object
    return on_resolve(obj)
