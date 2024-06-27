from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Mapping, Protocol, TypedDict, TypeVar, cast, runtime_checkable

from typing_extensions import Concatenate, ParamSpec, TypeAlias

from litestar.utils.deprecation import warn_deprecation
from litestar.utils.empty import value_or_default
from litestar.utils.scope.state import ScopeState

if TYPE_CHECKING:
    from pathlib import Path

    from litestar.connection import Request

__all__ = (
    "TemplateCallableType",
    "TemplateEngineProtocol",
    "TemplateProtocol",
    "csrf_token",
    "url_for",
    "url_for_static_asset",
)


def _get_request_from_context(context: Mapping[str, Any]) -> Request:
    """Get the request from the template context.

    Args:
        context: The template context.

    Returns:
        The request object.
    """
    return cast("Request", context["request"])


def url_for(context: Mapping[str, Any], /, route_name: str, **path_parameters: Any) -> str:
    """Wrap :func:`route_reverse <litestar.app.route_reverse>` to be used in templates.

    Args:
        context: The template context.
        route_name: The name of the route handler.
        **path_parameters: Actual values for path parameters in the route.

    Raises:
        NoRouteMatchFoundException: If ``route_name`` does not exist, path parameters are missing in **path_parameters
        or have wrong type.

    Returns:
        A fully formatted url path.
    """
    return _get_request_from_context(context).app.route_reverse(route_name, **path_parameters)


def csrf_token(context: Mapping[str, Any], /) -> str:
    """Set a CSRF token on the template.

    Notes:
        - to use this function make sure to pass an instance of :ref:`CSRFConfig <litestar.config.csrf_config.CSRFConfig>` to
        the :class:`Litestar <litestar.app.Litestar>` constructor.

    Args:
        context: The template context.

    Returns:
        A CSRF token if the app level ``csrf_config`` is set, otherwise an empty string.
    """
    scope = _get_request_from_context(context).scope
    return value_or_default(ScopeState.from_scope(scope).csrf_token, "")


def url_for_static_asset(context: Mapping[str, Any], /, name: str, file_path: str) -> str:
    """Wrap :meth:`url_for_static_asset <litestar.app.url_for_static_asset>` to be used in templates.

    Args:
        context: The template context object.
        name: A static handler unique name.
        file_path: a string containing path to an asset.

    Raises:
        NoRouteMatchFoundException: If static files handler with ``name`` does not exist.

    Returns:
        A url path to the asset.
    """
    return _get_request_from_context(context).app.url_for_static_asset(name, file_path)


class TemplateProtocol(Protocol):
    """Protocol Defining a ``Template``.

    Template is a class that has a render method which renders the template into a string.
    """

    def render(self, *args: Any, **kwargs: Any) -> str:
        """Return the rendered template as a string.

        Args:
            *args: Positional arguments passed to the TemplateEngine
            **kwargs: A string keyed mapping of values passed to the TemplateEngine

        Returns:
            The rendered template string
        """
        raise NotImplementedError


P = ParamSpec("P")
R = TypeVar("R")
ContextType = TypeVar("ContextType")
ContextType_co = TypeVar("ContextType_co", covariant=True)
TemplateType_co = TypeVar("TemplateType_co", bound=TemplateProtocol, covariant=True)
TemplateCallableType: TypeAlias = Callable[Concatenate[ContextType, P], R]


@runtime_checkable
class TemplateEngineProtocol(Protocol[TemplateType_co, ContextType_co]):
    """Protocol for template engines."""

    def __init__(self, directory: Path | list[Path] | None, engine_instance: Any | None) -> None:
        """Initialize the template engine with a directory.

        Args:
            directory: Direct path or list of directory paths from which to serve templates, if provided the
                implementation has to create the engine instance.
            engine_instance: A template engine object, if provided the implementation has to use it.
        """

    def get_template(self, template_name: str) -> TemplateType_co:
        """Retrieve a template by matching its name (dotted path) with files in the directory or directories provided.

        Args:
            template_name: A dotted path

        Returns:
            Template instance

        Raises:
            TemplateNotFoundException: if no template is found.
        """
        raise NotImplementedError

    def render_string(self, template_string: str, context: Mapping[str, Any]) -> str:
        """Render a template from a string with the given context.

        Args:
            template_string: The template string to render.
            context: A dictionary of variables to pass to the template.

        Returns:
            The rendered template as a string.
        """
        raise NotImplementedError

    def register_template_callable(
        self, key: str, template_callable: TemplateCallableType[ContextType_co, P, R]
    ) -> None:
        """Register a callable on the template engine.

        Args:
            key: The callable key, i.e. the value to use inside the template to call the callable.
            template_callable: A callable to register.

        Returns:
            None
        """


class _TemplateContext(TypedDict):
    """Dictionary representing a template context."""

    request: Request[Any, Any, Any]
    csrf_input: str


def __getattr__(name: str) -> Any:
    if name == "TemplateContext":
        warn_deprecation(
            "2.3.0",
            "TemplateContext",
            "import",
            removal_in="3.0.0",
            alternative="Mapping",
        )
        return _TemplateContext
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
