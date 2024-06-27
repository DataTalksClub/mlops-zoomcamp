from litestar.utils import warn_deprecation


def __getattr__(attr_name: str) -> object:
    from litestar.repository import filters

    if attr_name in filters.__all__:
        warn_deprecation(
            deprecated_name=f"litestar.repository.contrib.filters.{attr_name}",
            version="2.1",
            kind="import",
            removal_in="3.0",
            info=f"importing {attr_name} from 'litestar.contrib.repository.filters' is deprecated, please"
            f"import it from 'litestar.repository.filters.{attr_name}' instead",
        )

        value = globals()[attr_name] = getattr(filters, attr_name)
        return value

    raise AttributeError(f"module {__name__!r} has no attribute {attr_name!r}")
