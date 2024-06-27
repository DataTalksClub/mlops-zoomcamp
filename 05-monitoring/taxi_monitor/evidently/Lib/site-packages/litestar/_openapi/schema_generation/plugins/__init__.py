from .dataclass import DataclassSchemaPlugin
from .pagination import PaginationSchemaPlugin
from .struct import StructSchemaPlugin
from .typed_dict import TypedDictSchemaPlugin

__all__ = ("openapi_schema_plugins",)

# NOTE: The Pagination type plugin has to come before the Dataclass plugin since the Pagination
# classes are dataclasses, but we want to handle them differently from how dataclasses are normally
# handled.
openapi_schema_plugins = [
    PaginationSchemaPlugin(),
    StructSchemaPlugin(),
    DataclassSchemaPlugin(),
    TypedDictSchemaPlugin(),
]
