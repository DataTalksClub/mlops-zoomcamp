from __future__ import annotations

import re
from typing import TYPE_CHECKING

from litestar.types.internal_types import PathParameterDefinition

if TYPE_CHECKING:
    from litestar.handlers.http_handlers import HTTPRouteHandler
    from litestar.types import Method


__all__ = ("default_operation_id_creator", "SEPARATORS_CLEANUP_PATTERN")

SEPARATORS_CLEANUP_PATTERN = re.compile(r"[!#$%&'*+\-.^_`|~:]+")


def default_operation_id_creator(
    route_handler: HTTPRouteHandler,
    http_method: Method,
    path_components: list[str | PathParameterDefinition],
) -> str:
    """Create a unique 'operationId' for an OpenAPI PathItem entry.

    Args:
        route_handler: The HTTP Route Handler instance.
        http_method: The HTTP method for the given PathItem.
        path_components: A list of path components.

    Returns:
        A camelCased operationId created from the handler function name,
        http method and path components.
    """

    handler_namespace = (
        http_method.title() + route_handler.handler_name.title()
        if len(route_handler.http_methods) > 1
        else route_handler.handler_name.title()
    )

    components_namespace = ""
    for component in (c.name if isinstance(c, PathParameterDefinition) else c for c in path_components):
        if component.title() not in components_namespace:
            components_namespace += component.title()

    return SEPARATORS_CLEANUP_PATTERN.sub("", components_namespace + handler_namespace)
