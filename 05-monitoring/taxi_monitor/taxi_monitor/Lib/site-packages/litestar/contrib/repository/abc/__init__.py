from litestar.utils import warn_deprecation


def __getattr__(attr_name: str) -> object:
    from litestar.repository import abc

    if attr_name in abc.__all__:
        warn_deprecation(
            deprecated_name=f"litestar.contrib.repository.abc.{attr_name}",
            version="2.1",
            kind="import",
            removal_in="3.0",
            info=f"importing {attr_name} from 'litestar.contrib.repository.abc' is deprecated, please"
            f"import it from 'litestar.repository.abc.{attr_name}' instead",
        )

        value = globals()[attr_name] = getattr(abc, attr_name)
        return value

    raise AttributeError(f"module {__name__!r} has no attribute {attr_name!r}")
