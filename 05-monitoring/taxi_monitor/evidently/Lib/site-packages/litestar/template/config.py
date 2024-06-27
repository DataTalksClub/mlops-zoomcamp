from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from inspect import isclass
from typing import TYPE_CHECKING, Callable, Generic, TypeVar, cast

from litestar.exceptions import ImproperlyConfiguredException
from litestar.template import TemplateEngineProtocol

__all__ = ("TemplateConfig",)

if TYPE_CHECKING:
    from litestar.types import PathType

EngineType = TypeVar("EngineType", bound=TemplateEngineProtocol)


@dataclass
class TemplateConfig(Generic[EngineType]):
    """Configuration for Templating.

    To enable templating, pass an instance of this class to the :class:`Litestar <litestar.app.Litestar>` constructor using the
    'template_config' key.
    """

    engine: type[EngineType] | EngineType | None = field(default=None)
    """A template engine adhering to the :class:`TemplateEngineProtocol <litestar.template.base.TemplateEngineProtocol>`."""
    directory: PathType | list[PathType] | None = field(default=None)
    """A directory or list of directories from which to serve templates."""
    engine_callback: Callable[[EngineType], None] | None = field(default=None)
    """A callback function that allows modifying the instantiated templating protocol."""
    instance: EngineType | None = field(default=None)
    """An instance of the templating protocol."""

    def __post_init__(self) -> None:
        """Ensure that directory is set if engine is a class."""
        if isclass(self.engine) and not self.directory:
            raise ImproperlyConfiguredException("directory is a required kwarg when passing a template engine class")
        """Ensure that directory is not set if instance is."""
        if self.instance is not None and self.directory is not None:
            raise ImproperlyConfiguredException("directory cannot be set if instance is")

    def to_engine(self) -> EngineType:
        """Instantiate the template engine."""
        template_engine = cast(
            "EngineType",
            self.engine(directory=self.directory, engine_instance=None) if isclass(self.engine) else self.engine,
        )
        if callable(self.engine_callback):
            self.engine_callback(template_engine)
        return template_engine

    @cached_property
    def engine_instance(self) -> EngineType:
        """Return the template engine instance."""
        return self.to_engine() if self.instance is None else self.instance
