from __future__ import annotations

import dataclasses
from inspect import cleandoc
from typing import TYPE_CHECKING

from litestar._openapi.parameters import create_parameters_for_handler
from litestar._openapi.request_body import create_request_body
from litestar._openapi.responses import create_responses_for_handler
from litestar._openapi.utils import SEPARATORS_CLEANUP_PATTERN
from litestar.enums import HttpMethod
from litestar.exceptions import ImproperlyConfiguredException
from litestar.openapi.spec import Operation, PathItem
from litestar.utils.helpers import unwrap_partial

if TYPE_CHECKING:
    from litestar._openapi.datastructures import OpenAPIContext
    from litestar.handlers.http_handlers import HTTPRouteHandler
    from litestar.routes import HTTPRoute

__all__ = ("create_path_item_for_route", "merge_path_item_operations")


class PathItemFactory:
    """Factory for creating a PathItem instance for a given route."""

    def __init__(self, openapi_context: OpenAPIContext, route: HTTPRoute) -> None:
        self.context = openapi_context
        self.route = route
        self._path_item = PathItem()

    def create_path_item(self) -> PathItem:
        """Create a PathItem for the given route parsing all http_methods into Operation Models.

        Returns:
            A PathItem instance.
        """
        for http_method, handler_tuple in self.route.route_handler_map.items():
            route_handler, _ = handler_tuple

            if not route_handler.resolve_include_in_schema():
                continue

            operation = self.create_operation_for_handler_method(route_handler, HttpMethod(http_method))

            setattr(self._path_item, http_method.lower(), operation)

        return self._path_item

    def create_operation_for_handler_method(
        self, route_handler: HTTPRouteHandler, http_method: HttpMethod
    ) -> Operation:
        """Create an Operation instance for a given route handler and http method.

        Args:
            route_handler: A route handler instance.
            http_method: An HttpMethod enum value.

        Returns:
            An Operation instance.
        """
        operation_id = self.create_operation_id(route_handler, http_method)
        parameters = create_parameters_for_handler(self.context, route_handler, self.route.path_parameters)
        signature_fields = route_handler.parsed_fn_signature.parameters

        request_body = None
        if data_field := signature_fields.get("data"):
            request_body = create_request_body(
                self.context, route_handler.handler_id, route_handler.resolve_data_dto(), data_field
            )

        raises_validation_error = bool(data_field or self._path_item.parameters or parameters)
        responses = create_responses_for_handler(
            self.context, route_handler, raises_validation_error=raises_validation_error
        )

        return route_handler.operation_class(
            operation_id=operation_id,
            tags=route_handler.resolve_tags() or None,
            summary=route_handler.summary or SEPARATORS_CLEANUP_PATTERN.sub("", route_handler.handler_name.title()),
            description=self.create_description_for_handler(route_handler),
            deprecated=route_handler.deprecated,
            responses=responses,
            request_body=request_body,
            parameters=parameters or None,  # type: ignore[arg-type]
            security=route_handler.resolve_security() or None,
        )

    def create_operation_id(self, route_handler: HTTPRouteHandler, http_method: HttpMethod) -> str:
        """Create an operation id for a given route handler and http method.

        Adds the operation id to the context's operation id set, where it is checked for uniqueness.

        Args:
            route_handler: A route handler instance.
            http_method: An HttpMethod enum value.

        Returns:
            An operation id string.
        """
        if isinstance(route_handler.operation_id, str):
            operation_id = route_handler.operation_id
        elif callable(route_handler.operation_id):
            operation_id = route_handler.operation_id(route_handler, http_method, self.route.path_components)
        else:
            operation_id = self.context.openapi_config.operation_id_creator(
                route_handler, http_method, self.route.path_components
            )
        self.context.add_operation_id(operation_id)
        return operation_id

    def create_description_for_handler(self, route_handler: HTTPRouteHandler) -> str | None:
        """Produce the operation description for a route handler.

        Args:
            route_handler: A route handler instance.

        Returns:
            An optional description string
        """
        handler_description = route_handler.description
        if handler_description is None and self.context.openapi_config.use_handler_docstrings:
            fn = unwrap_partial(route_handler.fn)
            return cleandoc(fn.__doc__) if fn.__doc__ else None
        return handler_description


def create_path_item_for_route(openapi_context: OpenAPIContext, route: HTTPRoute) -> PathItem:
    """Create a PathItem for the given route parsing all http_methods into Operation Models.

    Args:
        openapi_context: The OpenAPIContext instance.
        route: The route to create a PathItem for.

    Returns:
        A PathItem instance.
    """
    path_item_factory = PathItemFactory(openapi_context, route)
    return path_item_factory.create_path_item()


def merge_path_item_operations(source: PathItem, other: PathItem, for_path: str) -> PathItem:
    """Merge operations from path items, creating a new path item that includes
    operations from both.
    """
    attrs_to_merge = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
    fields = {f.name for f in dataclasses.fields(PathItem)} - attrs_to_merge
    if any(getattr(source, attr) and getattr(other, attr) for attr in attrs_to_merge):
        raise ValueError("Cannot merge operation for PathItem if operation is set on both items")

    if differing_values := [
        (value_a, value_b) for attr in fields if (value_a := getattr(source, attr)) != (value_b := getattr(other, attr))
    ]:
        raise ImproperlyConfiguredException(
            f"Conflicting OpenAPI path configuration for {for_path!r}. "
            f"{', '.join(f'{a} != {b}' for a, b in differing_values)}"
        )

    return dataclasses.replace(
        source,
        get=source.get or other.get,
        post=source.post or other.post,
        patch=source.patch or other.patch,
        put=source.put or other.put,
        delete=source.delete or other.delete,
        options=source.options or other.options,
        trace=source.trace or other.trace,
    )
