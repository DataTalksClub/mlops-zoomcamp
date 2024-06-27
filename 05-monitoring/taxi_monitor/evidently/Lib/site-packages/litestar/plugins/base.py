from __future__ import annotations

import abc
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Iterator, Protocol, TypeVar, Union, cast, runtime_checkable

if TYPE_CHECKING:
    from inspect import Signature

    from click import Group

    from litestar._openapi.schema_generation import SchemaCreator
    from litestar.app import Litestar
    from litestar.config.app import AppConfig
    from litestar.dto import AbstractDTO
    from litestar.openapi.spec import Schema
    from litestar.routes import BaseRoute
    from litestar.typing import FieldDefinition

__all__ = (
    "SerializationPluginProtocol",
    "InitPluginProtocol",
    "OpenAPISchemaPluginProtocol",
    "OpenAPISchemaPlugin",
    "PluginProtocol",
    "CLIPlugin",
    "CLIPluginProtocol",
    "PluginRegistry",
    "DIPlugin",
)


@runtime_checkable
class InitPluginProtocol(Protocol):
    """Protocol used to define plugins that affect the application's init process."""

    __slots__ = ()

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        """Receive the :class:`AppConfig<.config.app.AppConfig>` instance after `on_app_init` hooks have been called.

        Examples:
            .. code-block:: python

                from litestar import Litestar, get
                from litestar.di import Provide
                from litestar.plugins import InitPluginProtocol


                def get_name() -> str:
                    return "world"


                @get("/my-path")
                def my_route_handler(name: str) -> dict[str, str]:
                    return {"hello": name}


                class MyPlugin(InitPluginProtocol):
                    def on_app_init(self, app_config: AppConfig) -> AppConfig:
                        app_config.dependencies["name"] = Provide(get_name)
                        app_config.route_handlers.append(my_route_handler)
                        return app_config


                app = Litestar(plugins=[MyPlugin()])

        Args:
            app_config: The :class:`AppConfig <litestar.config.app.AppConfig>` instance.

        Returns:
            The app config object.
        """
        return app_config  # pragma: no cover


class ReceiveRoutePlugin:
    """Receive routes as they are added to the application."""

    __slots__ = ()

    def receive_route(self, route: BaseRoute) -> None:
        """Receive routes as they are registered on an application."""


@runtime_checkable
class CLIPluginProtocol(Protocol):
    """Plugin protocol to extend the CLI."""

    __slots__ = ()

    def on_cli_init(self, cli: Group) -> None:
        """Called when the CLI is initialized.

        This can be used to extend or override existing commands.

        Args:
            cli: The root :class:`click.Group` of the Litestar CLI

        Examples:
            .. code-block:: python

                from litestar import Litestar
                from litestar.plugins import CLIPluginProtocol
                from click import Group


                class CLIPlugin(CLIPluginProtocol):
                    def on_cli_init(self, cli: Group) -> None:
                        @cli.command()
                        def is_debug_mode(app: Litestar):
                            print(app.debug)


                app = Litestar(plugins=[CLIPlugin()])
        """


class CLIPlugin(CLIPluginProtocol):
    """Plugin protocol to extend the CLI Server Lifespan."""

    __slots__ = ()

    @contextmanager
    def server_lifespan(self, app: Litestar) -> Iterator[None]:
        yield


@runtime_checkable
class SerializationPluginProtocol(Protocol):
    """Protocol used to define a serialization plugin for DTOs."""

    __slots__ = ()

    def supports_type(self, field_definition: FieldDefinition) -> bool:
        """Given a value of indeterminate type, determine if this value is supported by the plugin.

        Args:
            field_definition: A parsed type.

        Returns:
            Whether the type is supported by the plugin.
        """
        raise NotImplementedError()

    def create_dto_for_type(self, field_definition: FieldDefinition) -> type[AbstractDTO]:
        """Given a parsed type, create a DTO class.

        Args:
            field_definition: A parsed type.

        Returns:
            A DTO class.
        """
        raise NotImplementedError()


class DIPlugin(abc.ABC):
    """Extend dependency injection"""

    @abc.abstractmethod
    def has_typed_init(self, type_: Any) -> bool:
        """Return ``True`` if ``type_`` has type information available for its
        :func:`__init__` method that cannot be extracted from this method's type
        annotations (e.g. a Pydantic BaseModel subclass), and
        :meth:`DIPlugin.get_typed_init` supports extraction of these annotations.
        """
        ...

    @abc.abstractmethod
    def get_typed_init(self, type_: Any) -> tuple[Signature, dict[str, Any]]:
        r"""Return signature and type information about the ``type_``\ s :func:`__init__`
        method.
        """
        ...


@runtime_checkable
class OpenAPISchemaPluginProtocol(Protocol):
    """Plugin protocol to extend the support of OpenAPI schema generation for non-library types."""

    __slots__ = ()

    @staticmethod
    def is_plugin_supported_type(value: Any) -> bool:
        """Given a value of indeterminate type, determine if this value is supported by the plugin.

        Args:
            value: An arbitrary value.

        Returns:
            A typeguard dictating whether the value is supported by the plugin.
        """
        raise NotImplementedError()

    def to_openapi_schema(self, field_definition: FieldDefinition, schema_creator: SchemaCreator) -> Schema:
        """Given a type annotation, transform it into an OpenAPI schema class.

        Args:
            field_definition: An :class:`OpenAPI <litestar.openapi.spec.schema.Schema>` instance.
            schema_creator: An instance of the openapi SchemaCreator.

        Returns:
            An :class:`OpenAPI <litestar.openapi.spec.schema.Schema>` instance.
        """
        raise NotImplementedError()


class OpenAPISchemaPlugin(OpenAPISchemaPluginProtocol):
    """Plugin to extend the support of OpenAPI schema generation for non-library types."""

    __slots__ = ()

    @staticmethod
    def is_plugin_supported_type(value: Any) -> bool:
        """Given a value of indeterminate type, determine if this value is supported by the plugin.

        This is called by the default implementation of :meth:`is_plugin_supported_field` for
        backwards compatibility. User's should prefer to override that method instead.

        Args:
            value: An arbitrary value.

        Returns:
            A bool indicating whether the value is supported by the plugin.
        """
        raise NotImplementedError(
            "One of either is_plugin_supported_type or is_plugin_supported_field should be defined. "
            "The default implementation of is_plugin_supported_field calls is_plugin_supported_type "
            "for backwards compatibility. Users should prefer to override is_plugin_supported_field "
            "as it receives a 'FieldDefinition' instance which is more useful than a raw type."
        )

    def is_plugin_supported_field(self, field_definition: FieldDefinition) -> bool:
        """Given a :class:`FieldDefinition <litestar.typing.FieldDefinition>` that represents an indeterminate type,
        determine if this value is supported by the plugin

        Args:
            field_definition: A parsed type.

        Returns:
            Whether the type is supported by the plugin.
        """
        return self.is_plugin_supported_type(field_definition.annotation)

    @staticmethod
    def is_undefined_sentinel(value: Any) -> bool:
        """Return ``True`` if ``value`` should be treated as an undefined field"""
        return False

    @staticmethod
    def is_constrained_field(field_definition: FieldDefinition) -> bool:
        """Return ``True`` if the field should be treated as constrained. If returning
        ``True``, constraints should be defined in the field's extras
        """
        return False


PluginProtocol = Union[
    CLIPlugin,
    CLIPluginProtocol,
    InitPluginProtocol,
    OpenAPISchemaPlugin,
    OpenAPISchemaPluginProtocol,
    ReceiveRoutePlugin,
    SerializationPluginProtocol,
    DIPlugin,
]

PluginT = TypeVar("PluginT", bound=PluginProtocol)


class PluginRegistry:
    __slots__ = {
        "init": "Plugins that implement the InitPluginProtocol",
        "openapi": "Plugins that implement the OpenAPISchemaPluginProtocol",
        "receive_route": "ReceiveRoutePlugin instances",
        "serialization": "Plugins that implement the SerializationPluginProtocol",
        "cli": "Plugins that implement the CLIPluginProtocol",
        "di": "DIPlugin instances",
        "_plugins_by_type": None,
        "_plugins": None,
        "_get_plugins_of_type": None,
    }

    def __init__(self, plugins: list[PluginProtocol]) -> None:
        self._plugins_by_type = {type(p): p for p in plugins}
        self._plugins = frozenset(plugins)
        self.init = tuple(p for p in plugins if isinstance(p, InitPluginProtocol))
        self.openapi = tuple(p for p in plugins if isinstance(p, OpenAPISchemaPluginProtocol))
        self.receive_route = tuple(p for p in plugins if isinstance(p, ReceiveRoutePlugin))
        self.serialization = tuple(p for p in plugins if isinstance(p, SerializationPluginProtocol))
        self.cli = tuple(p for p in plugins if isinstance(p, CLIPluginProtocol))
        self.di = tuple(p for p in plugins if isinstance(p, DIPlugin))

    def get(self, type_: type[PluginT] | str) -> PluginT:
        """Return the registered plugin of ``type_``.

        This should be used with subclasses of the plugin protocols.
        """
        if isinstance(type_, str):
            for plugin in self._plugins:
                _name = plugin.__class__.__name__
                _module = plugin.__class__.__module__
                _qualname = (
                    f"{_module}.{plugin.__class__.__qualname__}"
                    if _module is not None and _module != "__builtin__"
                    else plugin.__class__.__qualname__
                )
                if type_ in {_name, _qualname}:
                    return cast(PluginT, plugin)
            raise KeyError(f"No plugin of type {type_!r} registered")
        try:
            return cast(PluginT, self._plugins_by_type[type_])  # type: ignore[index]
        except KeyError as e:
            raise KeyError(f"No plugin of type {type_.__name__!r} registered") from e

    def __iter__(self) -> Iterator[PluginProtocol]:
        return iter(self._plugins)

    def __contains__(self, item: PluginProtocol) -> bool:
        return item in self._plugins
