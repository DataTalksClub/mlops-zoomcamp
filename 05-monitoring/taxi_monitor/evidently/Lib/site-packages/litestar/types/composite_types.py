from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterator,
    Literal,
    Mapping,
    MutableMapping,
    Sequence,
    Tuple,
    Type,
    Union,
)

__all__ = (
    "Dependencies",
    "ExceptionHandlersMap",
    "Middleware",
    "ParametersMap",
    "PathType",
    "ResponseCookies",
    "ResponseHeaders",
    "Scopes",
    "TypeEncodersMap",
)


if TYPE_CHECKING:
    from os import PathLike
    from pathlib import Path

    from typing_extensions import TypeAlias

    from litestar.datastructures.cookie import Cookie
    from litestar.datastructures.response_header import ResponseHeader
    from litestar.di import Provide
    from litestar.enums import ScopeType
    from litestar.middleware.base import DefineMiddleware, MiddlewareProtocol
    from litestar.params import ParameterKwarg

    from .asgi_types import ASGIApp
    from .callable_types import AnyCallable, ExceptionHandler

Dependencies: TypeAlias = "Mapping[str, Union[Provide, AnyCallable]]"
ExceptionHandlersMap: TypeAlias = "MutableMapping[Union[int, Type[Exception]], ExceptionHandler]"
Middleware: TypeAlias = "Union[Callable[..., ASGIApp], DefineMiddleware, Iterator[Tuple[ASGIApp, Dict[str, Any]]], Type[MiddlewareProtocol]]"
ParametersMap: TypeAlias = "Mapping[str, ParameterKwarg]"
PathType: TypeAlias = "Union[Path, PathLike, str]"
ResponseCookies: TypeAlias = "Union[Sequence[Cookie], Mapping[str, str]]"
ResponseHeaders: TypeAlias = "Union[Sequence[ResponseHeader], Mapping[str, str]]"
Scopes: TypeAlias = "set[Literal[ScopeType.HTTP, ScopeType.WEBSOCKET]]"
TypeDecodersSequence: TypeAlias = "Sequence[tuple[Callable[[Any], bool], Callable[[Any, Any], Any]]]"
TypeEncodersMap: TypeAlias = "Mapping[Any, Callable[[Any], Any]]"
