from litestar.utils import warn_deprecation


def __getattr__(attr_name: str) -> object:
    from litestar.repository import handlers

    if attr_name in handlers.__all__:
        warn_deprecation(
            deprecated_name=f"litestar.repository.contrib.handlers.{attr_name}",
            version="2.1",
            kind="import",
            removal_in="3.0",
            info=f"importing {attr_name} from 'litestar.contrib.repository.handlers' is deprecated, please"
            f"import it from 'litestar.repository.handlers.{attr_name}' instead",
        )

        value = globals()[attr_name] = getattr(handlers, attr_name)
        return value

    raise AttributeError(f"module {__name__!r} has no attribute {attr_name!r}")
