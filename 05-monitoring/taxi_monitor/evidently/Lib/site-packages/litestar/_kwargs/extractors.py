from __future__ import annotations

from collections import defaultdict
from functools import lru_cache, partial
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Mapping, NamedTuple, cast

from litestar._multipart import parse_multipart_form
from litestar._parsers import (
    parse_query_string,
    parse_url_encoded_form_data,
)
from litestar.datastructures import Headers
from litestar.datastructures.upload_file import UploadFile
from litestar.datastructures.url import URL
from litestar.enums import ParamType, RequestEncodingType
from litestar.exceptions import ValidationException
from litestar.params import BodyKwarg
from litestar.types import Empty
from litestar.utils import make_non_optional_union
from litestar.utils.predicates import is_non_string_sequence, is_optional_union
from litestar.utils.scope.state import ScopeState

if TYPE_CHECKING:
    from litestar._kwargs import KwargsModel
    from litestar._kwargs.parameter_definition import ParameterDefinition
    from litestar.connection import ASGIConnection, Request
    from litestar.dto import AbstractDTO
    from litestar.typing import FieldDefinition


__all__ = (
    "body_extractor",
    "cookies_extractor",
    "create_connection_value_extractor",
    "create_data_extractor",
    "create_multipart_extractor",
    "create_query_default_dict",
    "create_url_encoded_data_extractor",
    "headers_extractor",
    "json_extractor",
    "msgpack_extractor",
    "parse_connection_headers",
    "parse_connection_query_params",
    "query_extractor",
    "request_extractor",
    "scope_extractor",
    "socket_extractor",
    "state_extractor",
)


class ParamMappings(NamedTuple):
    alias_and_key_tuples: list[tuple[str, str]]
    alias_defaults: dict[str, Any]
    alias_to_param: dict[str, ParameterDefinition]


def _create_param_mappings(expected_params: set[ParameterDefinition]) -> ParamMappings:
    alias_and_key_tuples = []
    alias_defaults = {}
    alias_to_params: dict[str, ParameterDefinition] = {}
    for param in expected_params:
        alias = param.field_alias
        if param.param_type == ParamType.HEADER:
            alias = alias.lower()

        alias_and_key_tuples.append((alias, param.field_name))

        if not (param.is_required or param.default is Ellipsis):
            alias_defaults[alias] = param.default

        alias_to_params[alias] = param

    return ParamMappings(
        alias_and_key_tuples=alias_and_key_tuples,
        alias_defaults=alias_defaults,
        alias_to_param=alias_to_params,
    )


def create_connection_value_extractor(
    kwargs_model: KwargsModel,
    connection_key: str,
    expected_params: set[ParameterDefinition],
    parser: Callable[[ASGIConnection, KwargsModel], Mapping[str, Any]] | None = None,
) -> Callable[[dict[str, Any], ASGIConnection], None]:
    """Create a kwargs extractor function.

    Args:
        kwargs_model: The KwargsModel instance.
        connection_key: The attribute key to use.
        expected_params: The set of expected params.
        parser: An optional parser function.

    Returns:
        An extractor function.
    """

    alias_and_key_tuples, alias_defaults, alias_to_params = _create_param_mappings(expected_params)

    def extractor(values: dict[str, Any], connection: ASGIConnection) -> None:
        data = parser(connection, kwargs_model) if parser else getattr(connection, connection_key, {})

        try:
            connection_mapping: dict[str, Any] = {
                key: data[alias] if alias in data else alias_defaults[alias] for alias, key in alias_and_key_tuples
            }
            values.update(connection_mapping)
        except KeyError as e:
            param = alias_to_params[e.args[0]]
            path = URL.from_components(
                path=connection.url.path,
                query=connection.url.query,
            )
            raise ValidationException(
                f"Missing required {param.param_type.value} parameter {param.field_alias!r} for path {path}"
            ) from e

    return extractor


@lru_cache(1024)
def create_query_default_dict(
    parsed_query: tuple[tuple[str, str], ...], sequence_query_parameter_names: tuple[str, ...]
) -> defaultdict[str, list[str] | str]:
    """Transform a list of tuples into a default dict. Ensures non-list values are not wrapped in a list.

    Args:
        parsed_query: The parsed query list of tuples.
        sequence_query_parameter_names: A set of query parameters that should be wrapped in list.

    Returns:
        A default dict
    """
    output: defaultdict[str, list[str] | str] = defaultdict(list)

    for k, v in parsed_query:
        if k in sequence_query_parameter_names:
            output[k].append(v)  # type: ignore[union-attr]
        else:
            output[k] = v

    return output


def parse_connection_query_params(connection: ASGIConnection, kwargs_model: KwargsModel) -> dict[str, Any]:
    """Parse query params and cache the result in scope.

    Args:
        connection: The ASGI connection instance.
        kwargs_model: The KwargsModel instance.

    Returns:
        A dictionary of parsed values.
    """
    parsed_query = (
        connection._parsed_query
        if connection._parsed_query is not Empty
        else parse_query_string(connection.scope.get("query_string", b""))
    )
    ScopeState.from_scope(connection.scope).parsed_query = parsed_query
    return create_query_default_dict(
        parsed_query=parsed_query,
        sequence_query_parameter_names=kwargs_model.sequence_query_parameter_names,
    )


def parse_connection_headers(connection: ASGIConnection, _: KwargsModel) -> Headers:
    """Parse header parameters and cache the result in scope.

    Args:
        connection: The ASGI connection instance.
        _: The KwargsModel instance.

    Returns:
        A Headers instance
    """
    return Headers.from_scope(connection.scope)


def state_extractor(values: dict[str, Any], connection: ASGIConnection) -> None:
    """Extract the app state from the connection and insert it to the kwargs injected to the handler.

    Args:
        connection: The ASGI connection instance.
        values: The kwargs that are extracted from the connection and will be injected into the handler.

    Returns:
        None
    """
    values["state"] = connection.app.state._state


def headers_extractor(values: dict[str, Any], connection: ASGIConnection) -> None:
    """Extract the headers from the connection and insert them to the kwargs injected to the handler.

    Args:
        connection: The ASGI connection instance.
        values: The kwargs that are extracted from the connection and will be injected into the handler.

    Returns:
        None
    """
    # TODO: This should be removed in 3.0 and instead Headers should be injected
    # directly. We are only keeping this one around to not break things
    values["headers"] = dict(connection.headers.items())


def cookies_extractor(values: dict[str, Any], connection: ASGIConnection) -> None:
    """Extract the cookies from the connection and insert them to the kwargs injected to the handler.

    Args:
        connection: The ASGI connection instance.
        values: The kwargs that are extracted from the connection and will be injected into the handler.

    Returns:
        None
    """
    values["cookies"] = connection.cookies


def query_extractor(values: dict[str, Any], connection: ASGIConnection) -> None:
    """Extract the query params from the connection and insert them to the kwargs injected to the handler.

    Args:
        connection: The ASGI connection instance.
        values: The kwargs that are extracted from the connection and will be injected into the handler.

    Returns:
        None
    """
    values["query"] = connection.query_params


def scope_extractor(values: dict[str, Any], connection: ASGIConnection) -> None:
    """Extract the scope from the connection and insert it into the kwargs injected to the handler.

    Args:
        connection: The ASGI connection instance.
        values: The kwargs that are extracted from the connection and will be injected into the handler.

    Returns:
        None
    """
    values["scope"] = connection.scope


def request_extractor(values: dict[str, Any], connection: ASGIConnection) -> None:
    """Set the connection instance as the 'request' value in the kwargs injected to the handler.

    Args:
        connection: The ASGI connection instance.
        values: The kwargs that are extracted from the connection and will be injected into the handler.

    Returns:
        None
    """
    values["request"] = connection


def socket_extractor(values: dict[str, Any], connection: ASGIConnection) -> None:
    """Set the connection instance as the 'socket' value in the kwargs injected to the handler.

    Args:
        connection: The ASGI connection instance.
        values: The kwargs that are extracted from the connection and will be injected into the handler.

    Returns:
        None
    """
    values["socket"] = connection


def body_extractor(
    values: dict[str, Any],
    connection: Request[Any, Any, Any],
) -> None:
    """Extract the body from the request instance.

    Notes:
        - this extractor sets a Coroutine as the value in the kwargs. These are resolved at a later stage.

    Args:
        connection: The ASGI connection instance.
        values: The kwargs that are extracted from the connection and will be injected into the handler.

    Returns:
        The Body value.
    """
    values["body"] = connection.body()


async def json_extractor(connection: Request[Any, Any, Any]) -> Any:
    """Extract the data from request and insert it into the kwargs injected to the handler.

    Notes:
        - this extractor sets a Coroutine as the value in the kwargs. These are resolved at a later stage.

    Args:
        connection: The ASGI connection instance.

    Returns:
        The JSON value.
    """
    if not await connection.body():
        return Empty
    return await connection.json()


async def msgpack_extractor(connection: Request[Any, Any, Any]) -> Any:
    """Extract the data from request and insert it into the kwargs injected to the handler.

    Notes:
        - this extractor sets a Coroutine as the value in the kwargs. These are resolved at a later stage.

    Args:
        connection: The ASGI connection instance.

    Returns:
        The MessagePack value.
    """
    if not await connection.body():
        return Empty
    return await connection.msgpack()


async def _extract_multipart(
    connection: Request[Any, Any, Any],
    body_kwarg_multipart_form_part_limit: int | None,
    field_definition: FieldDefinition,
    is_data_optional: bool,
    data_dto: type[AbstractDTO] | None,
) -> Any:
    multipart_form_part_limit = (
        body_kwarg_multipart_form_part_limit
        if body_kwarg_multipart_form_part_limit is not None
        else connection.app.multipart_form_part_limit
    )
    connection.scope["_form"] = form_values = (  # type: ignore[typeddict-unknown-key]
        connection.scope["_form"]  # type: ignore[typeddict-item]
        if "_form" in connection.scope
        else parse_multipart_form(
            body=await connection.body(),
            boundary=connection.content_type[-1].get("boundary", "").encode(),
            multipart_form_part_limit=multipart_form_part_limit,
            type_decoders=connection.route_handler.resolve_type_decoders(),
        )
    )

    if field_definition.is_non_string_sequence:
        values = list(form_values.values())
        if isinstance(values[0], list) and (
            field_definition.has_inner_subclass_of(UploadFile)
            or (field_definition.is_optional and field_definition.inner_types[0].is_non_string_sequence)
        ):
            return values[0]

        return values

    if field_definition.is_simple_type and field_definition.annotation is UploadFile and form_values:
        return next(v for v in form_values.values() if isinstance(v, UploadFile))

    if not form_values and is_data_optional:
        return None

    if data_dto:
        return data_dto(connection).decode_builtins(form_values)

    for name, tp in field_definition.get_type_hints().items():
        value = form_values.get(name)
        if (
            value is not None
            and not isinstance(value, list)
            and (
                is_non_string_sequence(tp)
                or (is_optional_union(tp) and is_non_string_sequence(make_non_optional_union(tp)))
            )
        ):
            form_values[name] = [value]

    return form_values


def create_multipart_extractor(
    field_definition: FieldDefinition, is_data_optional: bool, data_dto: type[AbstractDTO] | None
) -> Callable[[ASGIConnection[Any, Any, Any, Any]], Coroutine[Any, Any, Any]]:
    """Create a multipart form-data extractor.

    Args:
        field_definition: A FieldDefinition instance.
        is_data_optional: Boolean dictating whether the field is optional.
        data_dto: A data DTO type, if configured for handler.

    Returns:
        An extractor function.
    """
    body_kwarg_multipart_form_part_limit: int | None = None
    if field_definition.kwarg_definition and isinstance(field_definition.kwarg_definition, BodyKwarg):
        body_kwarg_multipart_form_part_limit = field_definition.kwarg_definition.multipart_form_part_limit

    extract_multipart = partial(
        _extract_multipart,
        body_kwarg_multipart_form_part_limit=body_kwarg_multipart_form_part_limit,
        is_data_optional=is_data_optional,
        data_dto=data_dto,
        field_definition=field_definition,
    )

    return cast("Callable[[ASGIConnection[Any, Any, Any, Any]], Coroutine[Any, Any, Any]]", extract_multipart)


def create_url_encoded_data_extractor(
    is_data_optional: bool, data_dto: type[AbstractDTO] | None
) -> Callable[[ASGIConnection[Any, Any, Any, Any]], Coroutine[Any, Any, Any]]:
    """Create extractor for url encoded form-data.

    Args:
        is_data_optional: Boolean dictating whether the field is optional.
        data_dto: A data DTO type, if configured for handler.

    Returns:
        An extractor function.
    """

    async def extract_url_encoded_extractor(
        connection: Request[Any, Any, Any],
    ) -> Any:
        connection.scope["_form"] = form_values = (  # type: ignore[typeddict-unknown-key]
            connection.scope["_form"]  # type: ignore[typeddict-item]
            if "_form" in connection.scope
            else parse_url_encoded_form_data(await connection.body())
        )

        if not form_values and is_data_optional:
            return None

        return data_dto(connection).decode_builtins(form_values) if data_dto else form_values

    return cast(
        "Callable[[ASGIConnection[Any, Any, Any, Any]], Coroutine[Any, Any, Any]]", extract_url_encoded_extractor
    )


def create_data_extractor(kwargs_model: KwargsModel) -> Callable[[dict[str, Any], ASGIConnection], None]:
    """Create an extractor for a request's body.

    Args:
        kwargs_model: The KwargsModel instance.

    Returns:
        An extractor for the request's body.
    """

    if kwargs_model.expected_form_data:
        media_type, field_definition = kwargs_model.expected_form_data

        if media_type == RequestEncodingType.MULTI_PART:
            data_extractor = create_multipart_extractor(
                field_definition=field_definition,
                is_data_optional=kwargs_model.is_data_optional,
                data_dto=kwargs_model.expected_data_dto,
            )
        else:
            data_extractor = create_url_encoded_data_extractor(
                is_data_optional=kwargs_model.is_data_optional,
                data_dto=kwargs_model.expected_data_dto,
            )
    elif kwargs_model.expected_msgpack_data:
        data_extractor = cast(
            "Callable[[ASGIConnection[Any, Any, Any, Any]], Coroutine[Any, Any, Any]]", msgpack_extractor
        )
    elif kwargs_model.expected_data_dto:
        data_extractor = create_dto_extractor(data_dto=kwargs_model.expected_data_dto)
    else:
        data_extractor = cast(
            "Callable[[ASGIConnection[Any, Any, Any, Any]], Coroutine[Any, Any, Any]]", json_extractor
        )

    def extractor(
        values: dict[str, Any],
        connection: ASGIConnection[Any, Any, Any, Any],
    ) -> None:
        values["data"] = data_extractor(connection)

    return extractor


def create_dto_extractor(
    data_dto: type[AbstractDTO],
) -> Callable[[ASGIConnection[Any, Any, Any, Any]], Coroutine[Any, Any, Any]]:
    """Create a DTO data extractor.


    Returns:
        An extractor function.
    """

    async def dto_extractor(connection: Request[Any, Any, Any]) -> Any:
        if not (body := await connection.body()):
            return Empty
        return data_dto(connection).decode_bytes(body)

    return dto_extractor  # type:ignore[return-value]
