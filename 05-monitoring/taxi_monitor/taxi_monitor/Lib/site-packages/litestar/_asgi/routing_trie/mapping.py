from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from litestar._asgi.routing_trie.types import (
    ASGIHandlerTuple,
    PathParameterSentinel,
    create_node,
)
from litestar._asgi.utils import wrap_in_exception_handler
from litestar.types.internal_types import PathParameterDefinition

__all__ = ("add_mount_route", "add_route_to_trie", "build_route_middleware_stack", "configure_node")


if TYPE_CHECKING:
    from litestar._asgi.routing_trie.types import RouteTrieNode
    from litestar.app import Litestar
    from litestar.routes import ASGIRoute, HTTPRoute, WebSocketRoute
    from litestar.types import ASGIApp, RouteHandlerType


def add_mount_route(
    current_node: RouteTrieNode,
    mount_routes: dict[str, RouteTrieNode],
    root_node: RouteTrieNode,
    route: ASGIRoute,
) -> RouteTrieNode:
    """Add a node for a mount route.

    Args:
        current_node: The current trie node that is being mapped.
        mount_routes: A dictionary mapping static routes to trie nodes.
        root_node: The root trie node.
        route: The route that is being added.

    Returns:
        A trie node.
    """

    # we need to ensure that we can traverse the map both through the full path key, e.g. "/my-route/sub-path" and
    # via the components keys ["my-route, "sub-path"]
    if route.path not in current_node.children:
        root_node = current_node
        for component in route.path_components:
            if component not in current_node.children:
                current_node.children[component] = create_node()  # type: ignore[index]
            current_node = current_node.children[component]  # type: ignore[index]

    current_node.is_mount = True
    current_node.is_static = route.route_handler.is_static

    if route.path != "/":
        mount_routes[route.path] = root_node.children[route.path] = current_node
    else:
        mount_routes[route.path] = current_node

    return current_node


def add_route_to_trie(
    app: Litestar,
    mount_routes: dict[str, RouteTrieNode],
    plain_routes: set[str],
    root_node: RouteTrieNode,
    route: HTTPRoute | WebSocketRoute | ASGIRoute,
) -> RouteTrieNode:
    """Add a new route path (e.g. '/foo/bar/{param:int}') into the route_map tree.

    Inserts non-parameter paths ('plain routes') off the tree's root
    node. For paths containing parameters, splits the path on '/' and
    nests each path segment under the previous segment's node (see
    prefix tree / trie).

    Args:
        app: The Litestar app instance.
        mount_routes: A dictionary mapping static routes to trie nodes.
        plain_routes: A set of routes that do not have path parameters.
        root_node: The root trie node.
        route: The route that is being added.

    Returns:
        A RouteTrieNode instance.
    """
    current_node = root_node

    has_path_parameters = bool(route.path_parameters)

    if (route_handler := getattr(route, "route_handler", None)) and getattr(route_handler, "is_mount", False):
        current_node = add_mount_route(
            current_node=current_node,
            mount_routes=mount_routes,
            root_node=root_node,
            route=cast("ASGIRoute", route),
        )

    elif not has_path_parameters:
        plain_routes.add(route.path)
        if route.path not in root_node.children:
            current_node.children[route.path] = create_node()
        current_node = root_node.children[route.path]

    else:
        for component in route.path_components:
            if isinstance(component, PathParameterDefinition):
                current_node.is_path_param_node = True
                next_node_key: type[PathParameterSentinel] | str = PathParameterSentinel

            else:
                next_node_key = component

            if next_node_key not in current_node.children:
                current_node.children[next_node_key] = create_node()

            current_node.child_keys = set(current_node.children.keys())
            current_node = current_node.children[next_node_key]

            if isinstance(component, PathParameterDefinition) and component.type is Path:
                current_node.is_path_type = True

    configure_node(route=route, app=app, node=current_node)
    return current_node


def configure_node(
    app: Litestar,
    route: HTTPRoute | WebSocketRoute | ASGIRoute,
    node: RouteTrieNode,
) -> None:
    """Set required attributes and route handlers on route_map tree node.

    Args:
        app: The Litestar app instance.
        route: The route that is being added.
        node: The trie node being configured.

    Returns:
        None
    """
    from litestar.routes import HTTPRoute, WebSocketRoute

    if not node.path_parameters:
        node.path_parameters = {}

    if isinstance(route, HTTPRoute):
        for method, handler_mapping in route.route_handler_map.items():
            handler, _ = handler_mapping
            node.asgi_handlers[method] = ASGIHandlerTuple(
                asgi_app=build_route_middleware_stack(app=app, route=route, route_handler=handler),
                handler=handler,
            )
            node.path_parameters[method] = tuple(route.path_parameters.values())

    elif isinstance(route, WebSocketRoute):
        node.asgi_handlers["websocket"] = ASGIHandlerTuple(
            asgi_app=build_route_middleware_stack(app=app, route=route, route_handler=route.route_handler),
            handler=route.route_handler,
        )
        node.path_parameters["websocket"] = tuple(route.path_parameters.values())

    else:
        node.asgi_handlers["asgi"] = ASGIHandlerTuple(
            asgi_app=build_route_middleware_stack(app=app, route=route, route_handler=route.route_handler),
            handler=route.route_handler,
        )
        node.path_parameters["asgi"] = tuple(route.path_parameters.values())
        node.is_asgi = True


def build_route_middleware_stack(
    app: Litestar,
    route: HTTPRoute | WebSocketRoute | ASGIRoute,
    route_handler: RouteHandlerType,
) -> ASGIApp:
    """Construct a middleware stack that serves as the point of entry for each route.

    Args:
        app: The Litestar app instance.
        route: The route that is being added.
        route_handler: The route handler that is being wrapped.

    Returns:
        An ASGIApp that is composed of a "stack" of middlewares.
    """
    from litestar.middleware.allowed_hosts import AllowedHostsMiddleware
    from litestar.middleware.compression import CompressionMiddleware
    from litestar.middleware.csrf import CSRFMiddleware
    from litestar.middleware.response_cache import ResponseCacheMiddleware
    from litestar.routes import HTTPRoute

    asgi_handler: ASGIApp = route.handle  # type: ignore[assignment]
    handler_middleware = route_handler.resolve_middleware()
    has_cached_route = isinstance(route, HTTPRoute) and any(r.cache for r in route.route_handlers)
    has_middleware = (
        app.csrf_config or app.compression_config or has_cached_route or app.allowed_hosts or handler_middleware
    )

    if has_middleware:
        # If there is an exception raised from the handler, the first ExceptionHandlerMiddleware that catches the
        # exception will create the response and call send(). As middleware may wrap the send() callable, we need there
        # to be an instance of ExceptionHandlerMiddleware in between the handler and the middleware so that any send
        # wrappers instated by middleware are called. If there is no middleware, we can skip this step.
        asgi_handler = wrap_in_exception_handler(app=asgi_handler)

        if app.csrf_config:
            asgi_handler = CSRFMiddleware(app=asgi_handler, config=app.csrf_config)

        if app.compression_config:
            asgi_handler = CompressionMiddleware(app=asgi_handler, config=app.compression_config)

        if has_cached_route:
            asgi_handler = ResponseCacheMiddleware(app=asgi_handler, config=app.response_cache_config)

        if app.allowed_hosts:
            asgi_handler = AllowedHostsMiddleware(app=asgi_handler, config=app.allowed_hosts)

        for middleware in handler_middleware:
            if hasattr(middleware, "__iter__"):
                handler, kwargs = cast("tuple[Any, dict[str, Any]]", middleware)
                asgi_handler = handler(app=asgi_handler, **kwargs)
            else:
                asgi_handler = middleware(app=asgi_handler)  # type: ignore[call-arg]
    return asgi_handler
