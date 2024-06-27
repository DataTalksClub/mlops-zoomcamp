from __future__ import annotations

from copy import copy
from dataclasses import fields
from typing import Any, TypeVar, cast

from litestar._openapi.typescript_converter.schema_parsing import (
    normalize_typescript_namespace,
    parse_schema,
)
from litestar._openapi.typescript_converter.types import (
    TypeScriptInterface,
    TypeScriptNamespace,
    TypeScriptPrimitive,
    TypeScriptProperty,
    TypeScriptType,
    TypeScriptUnion,
)
from litestar.enums import HttpMethod, ParamType
from litestar.openapi.spec import (
    Components,
    OpenAPI,
    Operation,
    Parameter,
    Reference,
    RequestBody,
    Responses,
    Schema,
)

__all__ = (
    "convert_openapi_to_typescript",
    "deref_container",
    "get_openapi_type",
    "parse_params",
    "parse_request_body",
    "parse_responses",
    "resolve_ref",
)

from litestar.openapi.spec.base import BaseSchemaObject

T = TypeVar("T")


def _deref_schema_object(value: BaseSchemaObject, components: Components) -> BaseSchemaObject:
    for field in fields(value):
        if field_value := getattr(value, field.name, None):
            if isinstance(field_value, Reference):
                setattr(
                    value,
                    field.name,
                    deref_container(resolve_ref(field_value, components=components), components=components),
                )
            elif isinstance(field_value, (Schema, dict, list)):
                setattr(value, field.name, deref_container(field_value, components=components))
    return value


def _deref_dict(value: dict[str, Any], components: Components) -> dict[str, Any]:
    for k, v in value.items():
        if isinstance(v, Reference):
            value[k] = deref_container(resolve_ref(v, components=components), components=components)
        elif isinstance(v, (Schema, dict, list)):
            value[k] = deref_container(v, components=components)
    return value


def _deref_list(values: list[Any], components: Components) -> list[Any]:
    for i, value in enumerate(values):
        if isinstance(value, Reference):
            values[i] = deref_container(resolve_ref(value, components=components), components=components)
        elif isinstance(value, (Schema, (dict, list))):
            values[i] = deref_container(value, components=components)
    return values


def deref_container(open_api_container: T, components: Components) -> T:
    """Dereference an object that may contain Reference instances.

    Args:
        open_api_container: Either an OpenAPI content, a dict or a list.
        components: The OpenAPI schema Components section.

    Returns:
        A dereferenced object.
    """
    if isinstance(open_api_container, BaseSchemaObject):
        return cast("T", _deref_schema_object(open_api_container, components))

    if isinstance(open_api_container, dict):
        return cast("T", _deref_dict(copy(open_api_container), components))

    if isinstance(open_api_container, list):
        return cast("T", _deref_list(copy(open_api_container), components))
    raise ValueError(f"unexpected container type {type(open_api_container).__name__}")  # pragma: no cover


def resolve_ref(ref: Reference, components: Components) -> Schema:
    """Resolve a reference object into the actual value it points at.

    Args:
        ref: A Reference instance.
        components: The OpenAPI schema Components section.

    Returns:
        An OpenAPI schema instance.
    """
    current: Any = components
    for path in [p for p in ref.ref.split("/") if p not in {"#", "components"}]:
        current = current[path] if isinstance(current, dict) else getattr(current, path, None)

    if not isinstance(current, Schema):  # pragma: no cover
        raise ValueError(
            f"unexpected value type, expected schema but received {type(current).__name__ if current is not None else 'None'}"
        )

    return current


def get_openapi_type(value: Reference | T, components: Components) -> T:
    """Extract or dereference an OpenAPI container type.

    Args:
        value: Either a reference or a container type.
        components: The OpenAPI schema Components section.

    Returns:
        The extracted container.
    """
    if isinstance(value, Reference):
        resolved_ref = resolve_ref(value, components=components)
        return cast("T", deref_container(open_api_container=resolved_ref, components=components))

    return deref_container(open_api_container=value, components=components)


def parse_params(
    params: list[Parameter],
    components: Components,
) -> tuple[TypeScriptInterface, ...]:
    """Parse request parameters.

    Args:
        params: An OpenAPI Operation parameters.
        components: The OpenAPI schema Components section.

    Returns:
        A tuple of resolved interfaces.
    """
    cookie_params: list[TypeScriptProperty] = []
    header_params: list[TypeScriptProperty] = []
    path_params: list[TypeScriptProperty] = []
    query_params: list[TypeScriptProperty] = []

    for param in params:
        if param.schema:
            schema = get_openapi_type(param.schema, components)
            ts_prop = TypeScriptProperty(
                key=normalize_typescript_namespace(param.name, allow_quoted=True),
                required=param.required,
                value=parse_schema(schema),
            )
            if param.param_in == ParamType.COOKIE:
                cookie_params.append(ts_prop)
            elif param.param_in == ParamType.HEADER:
                header_params.append(ts_prop)
            elif param.param_in == ParamType.PATH:
                path_params.append(ts_prop)
            else:
                query_params.append(ts_prop)

    result: list[TypeScriptInterface] = []

    if cookie_params:
        result.append(TypeScriptInterface("CookieParameters", tuple(cookie_params)))
    if header_params:
        result.append(TypeScriptInterface("HeaderParameters", tuple(header_params)))
    if path_params:
        result.append(TypeScriptInterface("PathParameters", tuple(path_params)))
    if query_params:
        result.append(TypeScriptInterface("QueryParameters", tuple(query_params)))

    return tuple(result)


def parse_request_body(body: RequestBody, components: Components) -> TypeScriptType:
    """Parse the schema request body.

    Args:
        body: An OpenAPI RequestBody instance.
        components: The OpenAPI schema Components section.

    Returns:
        A TypeScript type.
    """
    undefined = TypeScriptPrimitive("undefined")
    if not body.content:
        return TypeScriptType("RequestBody", undefined)

    if content := [get_openapi_type(v.schema, components) for v in body.content.values() if v.schema]:
        schema = content[0]
        return TypeScriptType(
            "RequestBody",
            parse_schema(schema) if body.required else TypeScriptUnion((parse_schema(schema), undefined)),
        )

    return TypeScriptType("RequestBody", undefined)


def parse_responses(responses: Responses, components: Components) -> tuple[TypeScriptNamespace, ...]:
    """Parse a given Operation's Responses object.

    Args:
        responses: An OpenAPI Responses object.
        components: The OpenAPI schema Components section.

    Returns:
        A tuple of namespaces, mapping response codes to data.
    """
    result: list[TypeScriptNamespace] = []
    for http_status, response in [
        (status, get_openapi_type(res, components=components)) for status, res in responses.items()
    ]:
        if response.content and (
            content := [get_openapi_type(v.schema, components) for v in response.content.values() if v.schema]
        ):
            ts_type = parse_schema(content[0])
        else:
            ts_type = TypeScriptPrimitive("undefined")

        containers = [
            TypeScriptType("ResponseBody", ts_type),
            TypeScriptInterface(
                "ResponseHeaders",
                tuple(
                    TypeScriptProperty(
                        required=get_openapi_type(header, components=components).required,
                        key=normalize_typescript_namespace(key, allow_quoted=True),
                        value=TypeScriptPrimitive("string"),
                    )
                    for key, header in response.headers.items()
                ),
            )
            if response.headers
            else None,
        ]

        result.append(TypeScriptNamespace(f"Http{http_status}", tuple(c for c in containers if c)))

    return tuple(result)


def convert_openapi_to_typescript(openapi_schema: OpenAPI, namespace: str = "API") -> TypeScriptNamespace:
    """Convert an OpenAPI Schema instance to a TypeScript namespace. This function is the main entry point for the
    TypeScript converter.

    Args:
        openapi_schema: An OpenAPI Schema instance.
        namespace: The namespace to use.

    Returns:
        A string representing the generated types.
    """
    if not openapi_schema.paths:  # pragma: no cover
        raise ValueError("OpenAPI schema has no paths")
    if not openapi_schema.components:  # pragma: no cover
        raise ValueError("OpenAPI schema has no components")

    operations: list[TypeScriptNamespace] = []

    for path_item in openapi_schema.paths.values():
        shared_params = [
            get_openapi_type(p, components=openapi_schema.components) for p in (path_item.parameters or [])
        ]
        for method in HttpMethod:
            if (
                operation := cast("Operation | None", getattr(path_item, method.lower(), "None"))
            ) and operation.operation_id:
                params = parse_params(
                    [
                        *(
                            get_openapi_type(p, components=openapi_schema.components)
                            for p in (operation.parameters or [])
                        ),
                        *shared_params,
                    ],
                    components=openapi_schema.components,
                )
                request_body = (
                    parse_request_body(
                        get_openapi_type(operation.request_body, components=openapi_schema.components),
                        components=openapi_schema.components,
                    )
                    if operation.request_body
                    else None
                )

                responses = parse_responses(operation.responses or {}, components=openapi_schema.components)

                operations.append(
                    TypeScriptNamespace(
                        normalize_typescript_namespace(operation.operation_id, allow_quoted=False),
                        tuple(container for container in (*params, request_body, *responses) if container),
                    )
                )

    return TypeScriptNamespace(namespace, tuple(operations))
