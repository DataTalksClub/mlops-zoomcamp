from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING, Final, Literal, Sequence

from litestar._openapi.utils import default_operation_id_creator
from litestar.openapi.plugins import (
    JsonRenderPlugin,
    RapidocRenderPlugin,
    RedocRenderPlugin,
    StoplightRenderPlugin,
    SwaggerRenderPlugin,
    YamlRenderPlugin,
)
from litestar.openapi.spec import (
    Components,
    Contact,
    ExternalDocumentation,
    Info,
    License,
    OpenAPI,
    PathItem,
    Reference,
    SecurityRequirement,
    Server,
    Tag,
)
from litestar.utils.deprecation import warn_deprecation
from litestar.utils.path import normalize_path

if TYPE_CHECKING:
    from litestar.openapi.controller import OpenAPIController
    from litestar.openapi.plugins import OpenAPIRenderPlugin
    from litestar.router import Router
    from litestar.types.callable_types import OperationIDCreator

__all__ = ("OpenAPIConfig",)

_enabled_plugin_map = {
    "elements": StoplightRenderPlugin,
    "openapi.json": JsonRenderPlugin,
    "openapi.yaml": YamlRenderPlugin,
    "openapi.yml": YamlRenderPlugin,
    "rapidoc": RapidocRenderPlugin,
    "redoc": RedocRenderPlugin,
    "swagger": SwaggerRenderPlugin,
    "oauth2-redirect.html": None,
}

_DEFAULT_SCHEMA_SITE: Final = "redoc"


@dataclass
class OpenAPIConfig:
    """Configuration for OpenAPI.

    To enable OpenAPI schema generation and serving, pass an instance of this class to the
    :class:`Litestar <.app.Litestar>` constructor using the ``openapi_config`` kwargs.
    """

    title: str
    """Title of API documentation."""
    version: str
    """API version, e.g. '1.0.0'."""

    create_examples: bool = field(default=False)
    """Generate examples using the polyfactory library."""
    random_seed: int = 10
    """The random seed used when creating the examples to ensure deterministic generation of examples."""
    contact: Contact | None = field(default=None)
    """API contact information, should be an :class:`Contact <litestar.openapi.spec.contact.Contact>` instance."""
    description: str | None = field(default=None)
    """API description."""
    external_docs: ExternalDocumentation | None = field(default=None)
    """Links to external documentation.

    Should be an instance of :class:`ExternalDocumentation <litestar.openapi.spec.external_documentation.ExternalDocumentation>`.
    """
    license: License | None = field(default=None)
    """API Licensing information.

    Should be an instance of :class:`License <litestar.openapi.spec.license.License>`.
    """
    security: list[SecurityRequirement] | None = field(default=None)
    """API Security requirements information.

    Should be an instance of
        :data:`SecurityRequirement <.openapi.spec.SecurityRequirement>`.
    """
    components: Components | list[Components] = field(default_factory=Components)
    """API Components information.

    Should be an instance of :class:`Components <litestar.openapi.spec.components.Components>` or a list thereof.
    """
    servers: list[Server] = field(default_factory=lambda: [Server(url="/")])
    """A list of :class:`Server <litestar.openapi.spec.server.Server>` instances."""
    summary: str | None = field(default=None)
    """A summary text."""
    tags: list[Tag] | None = field(default=None)
    """A list of :class:`Tag <litestar.openapi.spec.tag.Tag>` instances."""
    terms_of_service: str | None = field(default=None)
    """URL to page that contains terms of service."""
    use_handler_docstrings: bool = field(default=False)
    """Draw operation description from route handler docstring if not otherwise provided."""
    webhooks: dict[str, PathItem | Reference] | None = field(default=None)
    """A mapping of key to either :class:`PathItem <litestar.openapi.spec.path_item.PathItem>` or.

    :class:`Reference <litestar.openapi.spec.reference.Reference>` objects.
    """
    operation_id_creator: OperationIDCreator = default_operation_id_creator
    """A callable that generates unique operation ids"""
    path: str | None = field(default=None)
    """Base path for the OpenAPI documentation endpoints.

    If no path is provided the default is ``/schema``.

    Ignored if :attr:`openapi_router` is provided.
    """
    render_plugins: Sequence[OpenAPIRenderPlugin] = field(default=())
    """Plugins for rendering OpenAPI documentation UIs."""
    openapi_router: Router | None = None
    """An optional router for serving OpenAPI documentation and schema files.

    If provided, ``path`` is ignored.

    This parameter is also ignored if the deprecated :attr:`openapi_router <.openapi.OpenAPIConfig.openapi_controller>`
    kwarg is provided.

    :attr:`openapi_router` is not required, but it can be passed to customize the configuration of the router used to
    serve the documentation endpoints. For example, you can add middleware or guards to the router.

    Handlers to serve the OpenAPI schema and documentation sites are added to this router according to
    :attr:`render_plugins`, so routes shouldn't be added that conflict with these.
    """
    openapi_controller: type[OpenAPIController] | None = None
    """Controller for generating OpenAPI routes.

    Must be subclass of :class:`OpenAPIController <litestar.openapi.controller.OpenAPIController>`.

    .. deprecated:: v2.8.0
    """
    root_schema_site: Literal["redoc", "swagger", "elements", "rapidoc"] | None = None
    """The static schema generator to use for the "root" path of ``/schema/``.

    .. deprecated:: v2.8.0
    """
    enabled_endpoints: set[str] | None = None
    """A set of the enabled documentation sites and schema download endpoints.

    .. deprecated:: v2.8.0
    """

    def __post_init__(self) -> None:
        self._issue_deprecations()

        self.root_schema_site = self.root_schema_site or _DEFAULT_SCHEMA_SITE

        self.enabled_endpoints = (
            set(_enabled_plugin_map.keys()) if self.enabled_endpoints is None else self.enabled_endpoints
        )

        if self.path:
            self.path = normalize_path(self.path)

        if self.path and self.openapi_controller is not None:
            self.openapi_controller = type("OpenAPIController", (self.openapi_controller,), {"path": self.path})

        self.default_plugin: OpenAPIRenderPlugin | None = None
        if self.openapi_controller is None:
            if not self.render_plugins:
                self._plugin_backward_compatibility()
            else:
                # user is implicitly opted into the future plugin-based OpenAPI implementation
                # behavior by explicitly providing a list of render plugins
                for plugin in self.render_plugins:
                    if plugin.has_path("/"):
                        self.default_plugin = plugin
                        break
                else:
                    self.default_plugin = self.render_plugins[0]

    def _issue_deprecations(self) -> None:
        """Handle deprecated config options."""
        deprecated_in = "v2.8.0"
        removed_in = "v3.0.0"
        if self.openapi_controller is not None:
            warn_deprecation(
                deprecated_in,
                "openapi_controller",
                "attribute",
                removal_in=removed_in,
                alternative="render_plugins",
            )

        if self.root_schema_site is not None:
            warn_deprecation(
                deprecated_in,
                "root_schema_site",
                "attribute",
                removal_in=removed_in,
                alternative="render_plugins",
                info="Any 'render_plugin' with path '/' or first 'render_plugin' in list will be served at the OpenAPI root.",
            )

        if self.enabled_endpoints is not None:
            warn_deprecation(
                deprecated_in,
                "enabled_endpoints",
                "attribute",
                removal_in=removed_in,
                alternative="render_plugins",
                info="Configure a 'render_plugin' to enable an endpoint.",
            )

    def _plugin_backward_compatibility(self) -> None:
        """Backward compatibility for the plugin-based OpenAPI implementation.

        This preserves backward compatibility with the Controller-based OpenAPI implementation.

        We add a plugin for each enabled endpoint and set the default plugin to the plugin
        that has a path ending in the value of ``root_schema_site``.
        """

        def is_default_plugin(plugin_: OpenAPIRenderPlugin) -> bool:
            """Return True if the plugin is the default plugin."""
            root_schema_site = self.root_schema_site or _DEFAULT_SCHEMA_SITE
            return any(path.endswith(root_schema_site) for path in plugin_.paths)

        self.render_plugins = rps = []
        for key in self.enabled_endpoints or ():
            if plugin_type := _enabled_plugin_map[key]:
                plugin = plugin_type()
                rps.append(plugin)
                if is_default_plugin(plugin):
                    self.default_plugin = plugin

    def to_openapi_schema(self) -> OpenAPI:
        """Return an ``OpenAPI`` instance from the values stored in ``self``.

        Returns:
            An instance of :class:`OpenAPI <litestar.openapi.spec.open_api.OpenAPI>`.
        """

        if isinstance(self.components, list):
            merged_components = Components()
            for components in self.components:
                for key in (f.name for f in fields(components)):
                    if value := getattr(components, key, None):
                        merged_value_dict = getattr(merged_components, key, {}) or {}
                        merged_value_dict.update(value)
                        setattr(merged_components, key, merged_value_dict)

            self.components = merged_components

        return OpenAPI(
            external_docs=self.external_docs,
            security=self.security,
            components=deepcopy(self.components),  # deepcopy prevents mutation of the config's components
            servers=self.servers,
            tags=self.tags,
            webhooks=self.webhooks,
            info=Info(
                title=self.title,
                version=self.version,
                description=self.description,
                contact=self.contact,
                license=self.license,
                summary=self.summary,
                terms_of_service=self.terms_of_service,
            ),
            paths={},
        )
