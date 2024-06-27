import sniffio

from .base import ConcurrencyBackend


def detect_concurrency_backend() -> ConcurrencyBackend:
    library = sniffio.current_async_library()

    if library == "asyncio":
        from .asyncio import AsyncioBackend

        return AsyncioBackend()
    elif library == "trio":
        from .trio import TrioBackend

        return TrioBackend()

    raise NotImplementedError(
        f"Unsupported async library: {library}"
    )  # pragma: no cover
