from litestar.utils import warn_deprecation


def __getattr__(attr_name: str) -> object:
    from advanced_alchemy.extensions import litestar as aa  # pyright: ignore[reportMissingImports]

    if attr_name in {
        "AuditColumns",
        "BigIntAuditBase",
        "BigIntBase",
        "BigIntPrimaryKey",
        "CommonTableAttributes",
        "UUIDAuditBase",
        "UUIDBase",
        "UUIDPrimaryKey",
        "orm_registry",
    }:
        warn_deprecation(
            deprecated_name=f"litestar.plugins.sqlalchemy.{attr_name}",
            version="2.9.0",
            kind="import",
            removal_in="3.0",
            info=f"importing {attr_name} from 'litestar.plugins.sqlalchemy' is deprecated, please"
            f"import it from 'litestar.plugins.sqlalchemy.base.{attr_name}' instead",
        )
        value = globals()[attr_name] = getattr(aa.base, attr_name)
        return value
    if attr_name in aa.__all__:
        value = globals()[attr_name] = getattr(aa, attr_name)
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {attr_name!r}")
