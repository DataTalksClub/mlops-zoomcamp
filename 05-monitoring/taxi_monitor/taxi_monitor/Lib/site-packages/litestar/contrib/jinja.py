from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, TypeVar

from typing_extensions import ParamSpec

from litestar.exceptions import ImproperlyConfiguredException, MissingDependencyException, TemplateNotFoundException
from litestar.template.base import (
    TemplateCallableType,
    TemplateEngineProtocol,
    csrf_token,
    url_for,
    url_for_static_asset,
)

try:
    from jinja2 import Environment, FileSystemLoader, pass_context
    from jinja2 import TemplateNotFound as JinjaTemplateNotFound
except ImportError as e:
    raise MissingDependencyException("jinja2", extra="jinja") from e

if TYPE_CHECKING:
    from pathlib import Path

    from jinja2 import Template as JinjaTemplate

__all__ = ("JinjaTemplateEngine",)

P = ParamSpec("P")
T = TypeVar("T")


class JinjaTemplateEngine(TemplateEngineProtocol["JinjaTemplate", Mapping[str, Any]]):
    """The engine instance."""

    def __init__(
        self,
        directory: Path | list[Path] | None = None,
        engine_instance: Environment | None = None,
    ) -> None:
        """Jinja-based TemplateEngine.

        Args:
            directory: Direct path or list of directory paths from which to serve templates.
            engine_instance: A jinja Environment instance.
        """

        if directory and engine_instance:
            raise ImproperlyConfiguredException("You must provide either a directory or a jinja2 Environment instance.")
        if directory:
            loader = FileSystemLoader(searchpath=directory)
            self.engine = Environment(loader=loader, autoescape=True)
        elif engine_instance:
            self.engine = engine_instance
        self.register_template_callable(key="url_for_static_asset", template_callable=url_for_static_asset)
        self.register_template_callable(key="csrf_token", template_callable=csrf_token)
        self.register_template_callable(key="url_for", template_callable=url_for)

    def get_template(self, template_name: str) -> JinjaTemplate:
        """Retrieve a template by matching its name (dotted path) with files in the directory or directories provided.

        Args:
            template_name: A dotted path

        Returns:
            JinjaTemplate instance

        Raises:
            TemplateNotFoundException: if no template is found.
        """
        try:
            return self.engine.get_template(name=template_name)
        except JinjaTemplateNotFound as exc:
            raise TemplateNotFoundException(template_name=template_name) from exc

    def register_template_callable(
        self, key: str, template_callable: TemplateCallableType[Mapping[str, Any], P, T]
    ) -> None:
        """Register a callable on the template engine.

        Args:
            key: The callable key, i.e. the value to use inside the template to call the callable.
            template_callable: A callable to register.

        Returns:
            None
        """
        self.engine.globals[key] = pass_context(template_callable)

    def render_string(self, template_string: str, context: Mapping[str, Any]) -> str:
        """Render a template from a string with the given context.

        Args:
            template_string: The template string to render.
            context: A dictionary of variables to pass to the template.

        Returns:
            The rendered template as a string.
        """
        template = self.engine.from_string(template_string)
        return template.render(context)

    @classmethod
    def from_environment(cls, jinja_environment: Environment) -> JinjaTemplateEngine:
        """Create a JinjaTemplateEngine from an existing jinja Environment instance.

        Args:
            jinja_environment (jinja2.environment.Environment): A jinja Environment instance.

        Returns:
            JinjaTemplateEngine instance
        """
        return cls(directory=None, engine_instance=jinja_environment)
