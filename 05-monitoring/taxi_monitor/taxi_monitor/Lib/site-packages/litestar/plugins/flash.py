"""Plugin for creating and retrieving flash messages."""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping

import litestar.exceptions
from litestar import Request
from litestar.exceptions import MissingDependencyException
from litestar.middleware import DefineMiddleware
from litestar.middleware.session import SessionMiddleware
from litestar.plugins import InitPluginProtocol
from litestar.security.session_auth.middleware import MiddlewareWrapper
from litestar.template.base import _get_request_from_context
from litestar.utils.predicates import is_class_and_subclass

if TYPE_CHECKING:
    from collections.abc import Callable

    from litestar.config.app import AppConfig
    from litestar.connection.base import AuthT, StateT, UserT
    from litestar.template import TemplateConfig


@dataclass
class FlashConfig:
    """Configuration for Flash messages."""

    template_config: TemplateConfig


class FlashPlugin(InitPluginProtocol):
    """Flash messages Plugin."""

    def __init__(self, config: FlashConfig):
        """Initialize the plugin.

        Args:
            config: Configuration for flash messages, including the template engine instance.
        """
        self.config = config

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        """Register the message callable on the template engine instance.

        Args:
            app_config: The application configuration.

        Returns:
            The application configuration with the message callable registered.
        """
        for mw in app_config.middleware:
            if isinstance(mw, DefineMiddleware) and is_class_and_subclass(
                mw.middleware, (MiddlewareWrapper, SessionMiddleware)
            ):
                break
        else:
            raise litestar.exceptions.ImproperlyConfiguredException("Flash messages require a session middleware.")
        template_callable: Callable[[Any], Any] = get_flashes
        with suppress(MissingDependencyException):
            from litestar.contrib.minijinja import MiniJinjaTemplateEngine, _transform_state

            if isinstance(self.config.template_config.engine_instance, MiniJinjaTemplateEngine):
                template_callable = _transform_state(get_flashes)

        self.config.template_config.engine_instance.register_template_callable("get_flashes", template_callable)  # pyright: ignore[reportGeneralTypeIssues]
        return app_config


def flash(
    request: Request[UserT, AuthT, StateT],
    message: Any,
    category: str,
) -> None:
    request.session.setdefault("_messages", []).append({"message": message, "category": category})


def get_flashes(context: Mapping[str, Any]) -> Any:
    return _get_request_from_context(context).session.pop("_messages", [])
