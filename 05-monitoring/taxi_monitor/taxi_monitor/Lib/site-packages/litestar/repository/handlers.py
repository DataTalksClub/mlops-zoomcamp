from typing import TYPE_CHECKING

from litestar.repository.filters import (
    BeforeAfter,
    CollectionFilter,
    FilterTypes,
    LimitOffset,
    NotInCollectionFilter,
    NotInSearchFilter,
    OnBeforeAfter,
    OrderBy,
    SearchFilter,
)

if TYPE_CHECKING:
    from litestar.config.app import AppConfig

__all__ = ("signature_namespace_values", "on_app_init")

signature_namespace_values = {
    "BeforeAfter": BeforeAfter,
    "OnBeforeAfter": OnBeforeAfter,
    "CollectionFilter": CollectionFilter,
    "LimitOffset": LimitOffset,
    "OrderBy": OrderBy,
    "SearchFilter": SearchFilter,
    "NotInCollectionFilter": NotInCollectionFilter,
    "NotInSearchFilter": NotInSearchFilter,
    "FilterTypes": FilterTypes,
}


def on_app_init(app_config: "AppConfig") -> "AppConfig":
    """Add custom filters for the application during signature modelling."""

    app_config.signature_namespace.update(signature_namespace_values)
    return app_config
