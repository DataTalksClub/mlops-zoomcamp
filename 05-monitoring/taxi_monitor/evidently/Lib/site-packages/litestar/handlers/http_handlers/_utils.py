from __future__ import annotations

from functools import lru_cache
from inspect import isawaitable
from typing import TYPE_CHECKING, Any, Sequence, cast

from litestar.enums import HttpMethod
from litestar.exceptions import ValidationException
from litestar.response import Response
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from litestar.types.builtin_types import NoneType

if TYPE_CHECKING:
    from litestar.app import Litestar
    from litestar.background_tasks import BackgroundTask, BackgroundTasks
    from litestar.connection import Request
    from litestar.datastructures import Cookie, ResponseHeader
    from litestar.types import AfterRequestHookHandler, ASGIApp, AsyncAnyCallable, Method, TypeEncodersMap
    from litestar.typing import FieldDefinition

__all__ = (
    "create_data_handler",
    "create_generic_asgi_response_handler",
    "create_response_handler",
    "get_default_status_code",
    "is_empty_response_annotation",
    "normalize_headers",
    "normalize_http_method",
)


def create_data_handler(
    after_request: AfterRequestHookHandler | None,
    background: BackgroundTask | BackgroundTasks | None,
    cookies: frozenset[Cookie],
    headers: frozenset[ResponseHeader],
    media_type: str,
    response_class: type[Response],
    status_code: int,
    type_encoders: TypeEncodersMap | None,
) -> AsyncAnyCallable:
    """Create a handler function for arbitrary data.

    Args:
        after_request: An after request handler.
        background: A background task or background tasks.
        cookies: A set of pre-defined cookies.
        headers: A set of response headers.
        media_type: The response media type.
        response_class: The response class to use.
        status_code: The response status code.
        type_encoders: A mapping of types to encoder functions.

    Returns:
        A handler function.

    """

    async def handler(
        data: Any,
        request: Request[Any, Any, Any],
        app: Litestar,
        **kwargs: Any,
    ) -> ASGIApp:
        if isawaitable(data):
            data = await data

        response = response_class(
            background=background,
            content=data,
            media_type=media_type,
            status_code=status_code,
            type_encoders=type_encoders,
        )

        if after_request:
            response = await after_request(response)  # type: ignore[arg-type,misc]

        return response.to_asgi_response(app=None, request=request, headers=normalize_headers(headers), cookies=cookies)  # pyright: ignore

    return handler


def create_generic_asgi_response_handler(after_request: AfterRequestHookHandler | None) -> AsyncAnyCallable:
    """Create a handler function for Responses.

    Args:
        after_request: An after request handler.

    Returns:
        A handler function.
    """

    async def handler(data: ASGIApp, **kwargs: Any) -> ASGIApp:
        return await after_request(data) if after_request else data  # type: ignore[arg-type, misc, no-any-return]

    return handler


@lru_cache(1024)
def normalize_headers(headers: frozenset[ResponseHeader]) -> dict[str, str]:
    """Given a dictionary of ResponseHeader, filter them and return a dictionary of values.

    Args:
        headers: A dictionary of :class:`ResponseHeader <litestar.datastructures.ResponseHeader>` values

    Returns:
        A string keyed dictionary of normalized values
    """
    return {
        header.name: cast("str", header.value)  # we know value to be a string at this point because we validate it
        # that it's not None when initializing a header with documentation_only=True
        for header in headers
        if not header.documentation_only
    }


def create_response_handler(
    after_request: AfterRequestHookHandler | None,
    background: BackgroundTask | BackgroundTasks | None,
    cookies: frozenset[Cookie],
    headers: frozenset[ResponseHeader],
    media_type: str,
    status_code: int,
    type_encoders: TypeEncodersMap | None,
) -> AsyncAnyCallable:
    """Create a handler function for Litestar Responses.

    Args:
        after_request: An after request handler.
        background: A background task or background tasks.
        cookies: A set of pre-defined cookies.
        headers: A set of response headers.
        media_type: The response media type.
        status_code: The response status code.
        type_encoders: A mapping of types to encoder functions.

    Returns:
        A handler function.
    """

    normalized_headers = normalize_headers(headers)
    cookie_list = list(cookies)

    async def handler(
        data: Response,
        app: Litestar,
        request: Request,
        **kwargs: Any,  # kwargs is for return dto
    ) -> ASGIApp:
        response = await after_request(data) if after_request else data  # type:ignore[arg-type,misc]
        return response.to_asgi_response(  # type: ignore[no-any-return]
            app=None,
            background=background,
            cookies=cookie_list,
            headers=normalized_headers,
            media_type=media_type,
            request=request,
            status_code=status_code,
            type_encoders=type_encoders,
        )

    return handler


def normalize_http_method(http_methods: HttpMethod | Method | Sequence[HttpMethod | Method]) -> set[Method]:
    """Normalize HTTP method(s) into a set of upper-case method names.

    Args:
        http_methods: A value for http method.

    Returns:
        A normalized set of http methods.
    """
    output: set[str] = set()

    if isinstance(http_methods, str):
        http_methods = [http_methods]  # pyright: ignore

    for method in http_methods:
        method_name = method.value.upper() if isinstance(method, HttpMethod) else method.upper()
        if method_name not in HTTP_METHOD_NAMES:
            raise ValidationException(f"Invalid HTTP method: {method_name}")
        output.add(method_name)

    return cast("set[Method]", output)


def get_default_status_code(http_methods: set[Method]) -> int:
    """Return the default status code for a given set of HTTP methods.

    Args:
        http_methods: A set of method strings

    Returns:
        A status code
    """
    if HttpMethod.POST in http_methods:
        return HTTP_201_CREATED
    if HttpMethod.DELETE in http_methods:
        return HTTP_204_NO_CONTENT
    return HTTP_200_OK


def is_empty_response_annotation(return_annotation: FieldDefinition) -> bool:
    """Return whether the return annotation is an empty response.

    Args:
        return_annotation: A return annotation.

    Returns:
        Whether the return annotation is an empty response.
    """
    return (
        return_annotation.is_subclass_of(NoneType)
        or return_annotation.is_subclass_of(Response)
        and return_annotation.has_inner_subclass_of(NoneType)
    )


HTTP_METHOD_NAMES = {m.value for m in HttpMethod}
