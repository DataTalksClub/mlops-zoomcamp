from __future__ import annotations

from copy import copy
from functools import partial
from typing import TYPE_CHECKING, Any, Callable, Mapping, Sequence, cast

from litestar._signature import SignatureModel
from litestar.di import Provide
from litestar.dto import DTOData
from litestar.exceptions import ImproperlyConfiguredException
from litestar.plugins import DIPlugin, PluginRegistry
from litestar.serialization import default_deserializer, default_serializer
from litestar.types import (
    Dependencies,
    Empty,
    ExceptionHandlersMap,
    Guard,
    Middleware,
    TypeDecodersSequence,
    TypeEncodersMap,
)
from litestar.typing import FieldDefinition
from litestar.utils import ensure_async_callable, get_name, normalize_path
from litestar.utils.helpers import unwrap_partial
from litestar.utils.signature import ParsedSignature, add_types_to_signature_namespace

if TYPE_CHECKING:
    from typing_extensions import Self

    from litestar._kwargs import KwargsModel
    from litestar.app import Litestar
    from litestar.connection import ASGIConnection
    from litestar.controller import Controller
    from litestar.dto import AbstractDTO
    from litestar.params import ParameterKwarg
    from litestar.router import Router
    from litestar.types import AnyCallable, AsyncAnyCallable, ExceptionHandler
    from litestar.types.empty import EmptyType
    from litestar.types.internal_types import PathParameterDefinition

__all__ = ("BaseRouteHandler",)


class BaseRouteHandler:
    """Base route handler.

    Serves as a subclass for all route handlers
    """

    __slots__ = (
        "_fn",
        "_parsed_data_field",
        "_parsed_fn_signature",
        "_parsed_return_field",
        "_resolved_data_dto",
        "_resolved_dependencies",
        "_resolved_guards",
        "_resolved_layered_parameters",
        "_resolved_return_dto",
        "_resolved_signature_namespace",
        "_resolved_type_decoders",
        "_resolved_type_encoders",
        "_signature_model",
        "dependencies",
        "dto",
        "exception_handlers",
        "guards",
        "middleware",
        "name",
        "opt",
        "owner",
        "paths",
        "return_dto",
        "signature_namespace",
        "type_decoders",
        "type_encoders",
    )

    def __init__(
        self,
        path: str | Sequence[str] | None = None,
        *,
        dependencies: Dependencies | None = None,
        dto: type[AbstractDTO] | None | EmptyType = Empty,
        exception_handlers: ExceptionHandlersMap | None = None,
        guards: Sequence[Guard] | None = None,
        middleware: Sequence[Middleware] | None = None,
        name: str | None = None,
        opt: Mapping[str, Any] | None = None,
        return_dto: type[AbstractDTO] | None | EmptyType = Empty,
        signature_namespace: Mapping[str, Any] | None = None,
        signature_types: Sequence[Any] | None = None,
        type_decoders: TypeDecodersSequence | None = None,
        type_encoders: TypeEncodersMap | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize ``HTTPRouteHandler``.

        Args:
            path: A path fragment for the route handler function or a sequence of path fragments. If not given defaults
                to ``/``
            dependencies: A string keyed mapping of dependency :class:`Provider <.di.Provide>` instances.
            dto: :class:`AbstractDTO <.dto.base_dto.AbstractDTO>` to use for (de)serializing and
                validation of request data.
            exception_handlers: A mapping of status codes and/or exception types to handler functions.
            guards: A sequence of :class:`Guard <.types.Guard>` callables.
            middleware: A sequence of :class:`Middleware <.types.Middleware>`.
            name: A string identifying the route handler.
            opt: A string keyed mapping of arbitrary values that can be accessed in :class:`Guards <.types.Guard>` or
                wherever you have access to :class:`Request <.connection.Request>` or
                :class:`ASGI Scope <.types.Scope>`.
            return_dto: :class:`AbstractDTO <.dto.base_dto.AbstractDTO>` to use for serializing
                outbound response data.
            signature_namespace: A mapping of names to types for use in forward reference resolution during signature
                modelling.
            signature_types: A sequence of types for use in forward reference resolution during signature modeling.
                These types will be added to the signature namespace using their ``__name__`` attribute.
            type_decoders: A sequence of tuples, each composed of a predicate testing for type identity and a msgspec hook for deserialization.
            type_encoders: A mapping of types to callables that transform them into types supported for serialization.
            **kwargs: Any additional kwarg - will be set in the opt dictionary.
        """
        self._parsed_fn_signature: ParsedSignature | EmptyType = Empty
        self._parsed_return_field: FieldDefinition | EmptyType = Empty
        self._parsed_data_field: FieldDefinition | None | EmptyType = Empty
        self._resolved_data_dto: type[AbstractDTO] | None | EmptyType = Empty
        self._resolved_dependencies: dict[str, Provide] | EmptyType = Empty
        self._resolved_guards: list[Guard] | EmptyType = Empty
        self._resolved_layered_parameters: dict[str, FieldDefinition] | EmptyType = Empty
        self._resolved_return_dto: type[AbstractDTO] | None | EmptyType = Empty
        self._resolved_signature_namespace: dict[str, Any] | EmptyType = Empty
        self._resolved_type_decoders: TypeDecodersSequence | EmptyType = Empty
        self._resolved_type_encoders: TypeEncodersMap | EmptyType = Empty
        self._signature_model: type[SignatureModel] | EmptyType = Empty

        self.dependencies = dependencies
        self.dto = dto
        self.exception_handlers = exception_handlers
        self.guards = guards
        self.middleware = middleware
        self.name = name
        self.opt = dict(opt or {})
        self.opt.update(**kwargs)
        self.owner: Controller | Router | None = None
        self.return_dto = return_dto
        self.signature_namespace = add_types_to_signature_namespace(
            signature_types or [], dict(signature_namespace or {})
        )
        self.type_decoders = type_decoders
        self.type_encoders = type_encoders

        self.paths = (
            {normalize_path(p) for p in path} if path and isinstance(path, list) else {normalize_path(path or "/")}  # type: ignore[arg-type]
        )

    def __call__(self, fn: AsyncAnyCallable) -> Self:
        """Replace a function with itself."""
        self._fn = fn
        return self

    @property
    def handler_id(self) -> str:
        """A unique identifier used for generation of DTOs."""
        return f"{self!s}::{sum(id(layer) for layer in self.ownership_layers)}"

    @property
    def default_deserializer(self) -> Callable[[Any, Any], Any]:
        """Get a default deserializer for the route handler.

        Returns:
            A default deserializer for the route handler.

        """
        return partial(default_deserializer, type_decoders=self.resolve_type_decoders())

    @property
    def default_serializer(self) -> Callable[[Any], Any]:
        """Get a default serializer for the route handler.

        Returns:
            A default serializer for the route handler.

        """
        return partial(default_serializer, type_encoders=self.resolve_type_encoders())

    @property
    def signature_model(self) -> type[SignatureModel]:
        """Get the signature model for the route handler.

        Returns:
            A signature model for the route handler.

        """
        if self._signature_model is Empty:
            self._signature_model = SignatureModel.create(
                dependency_name_set=self.dependency_name_set,
                fn=cast("AnyCallable", self.fn),
                parsed_signature=self.parsed_fn_signature,
                data_dto=self.resolve_data_dto(),
                type_decoders=self.resolve_type_decoders(),
            )
        return self._signature_model

    @property
    def fn(self) -> AsyncAnyCallable:
        """Get the handler function.

        Raises:
            ImproperlyConfiguredException: if handler fn is not set.

        Returns:
            Handler function
        """
        if not hasattr(self, "_fn"):
            raise ImproperlyConfiguredException("No callable has been registered for this handler")
        return self._fn

    @property
    def parsed_fn_signature(self) -> ParsedSignature:
        """Return the parsed signature of the handler function.

        This method is memoized so the computation occurs only once.

        Returns:
            A ParsedSignature instance
        """
        if self._parsed_fn_signature is Empty:
            self._parsed_fn_signature = ParsedSignature.from_fn(
                unwrap_partial(self.fn), self.resolve_signature_namespace()
            )

        return self._parsed_fn_signature

    @property
    def parsed_return_field(self) -> FieldDefinition:
        if self._parsed_return_field is Empty:
            self._parsed_return_field = self.parsed_fn_signature.return_type
        return self._parsed_return_field

    @property
    def parsed_data_field(self) -> FieldDefinition | None:
        if self._parsed_data_field is Empty:
            self._parsed_data_field = self.parsed_fn_signature.parameters.get("data")
        return self._parsed_data_field

    @property
    def handler_name(self) -> str:
        """Get the name of the handler function.

        Raises:
            ImproperlyConfiguredException: if handler fn is not set.

        Returns:
            Name of the handler function
        """
        return get_name(unwrap_partial(self.fn))

    @property
    def dependency_name_set(self) -> set[str]:
        """Set of all dependency names provided in the handler's ownership layers."""
        layered_dependencies = (layer.dependencies or {} for layer in self.ownership_layers)
        return {name for layer in layered_dependencies for name in layer}  # pyright: ignore

    @property
    def ownership_layers(self) -> list[Self | Controller | Router]:
        """Return the handler layers from the app down to the route handler.

        ``app -> ... -> route handler``
        """
        layers = []

        cur: Any = self
        while cur:
            layers.append(cur)
            cur = cur.owner

        return list(reversed(layers))

    @property
    def app(self) -> Litestar:
        return cast("Litestar", self.ownership_layers[0])

    def resolve_type_encoders(self) -> TypeEncodersMap:
        """Return a merged type_encoders mapping.

        This method is memoized so the computation occurs only once.

        Returns:
            A dict of type encoders
        """
        if self._resolved_type_encoders is Empty:
            self._resolved_type_encoders = {}

            for layer in self.ownership_layers:
                if type_encoders := getattr(layer, "type_encoders", None):
                    self._resolved_type_encoders.update(type_encoders)
        return cast("TypeEncodersMap", self._resolved_type_encoders)

    def resolve_type_decoders(self) -> TypeDecodersSequence:
        """Return a merged type_encoders mapping.

        This method is memoized so the computation occurs only once.

        Returns:
            A dict of type encoders
        """
        if self._resolved_type_decoders is Empty:
            self._resolved_type_decoders = []

            for layer in self.ownership_layers:
                if type_decoders := getattr(layer, "type_decoders", None):
                    self._resolved_type_decoders.extend(list(type_decoders))
        return cast("TypeDecodersSequence", self._resolved_type_decoders)

    def resolve_layered_parameters(self) -> dict[str, FieldDefinition]:
        """Return all parameters declared above the handler."""
        if self._resolved_layered_parameters is Empty:
            parameter_kwargs: dict[str, ParameterKwarg] = {}

            for layer in self.ownership_layers:
                parameter_kwargs.update(getattr(layer, "parameters", {}) or {})

            self._resolved_layered_parameters = {
                key: FieldDefinition.from_kwarg(name=key, annotation=parameter.annotation, kwarg_definition=parameter)
                for key, parameter in parameter_kwargs.items()
            }

        return self._resolved_layered_parameters

    def resolve_guards(self) -> list[Guard]:
        """Return all guards in the handlers scope, starting from highest to current layer."""
        if self._resolved_guards is Empty:
            self._resolved_guards = []

            for layer in self.ownership_layers:
                self._resolved_guards.extend(layer.guards or [])  # pyright: ignore

            self._resolved_guards = cast(
                "list[Guard]", [ensure_async_callable(guard) for guard in self._resolved_guards]
            )

        return self._resolved_guards

    def _get_plugin_registry(self) -> PluginRegistry | None:
        from litestar.app import Litestar

        root_owner = self.ownership_layers[0]
        if isinstance(root_owner, Litestar):
            return root_owner.plugins
        return None

    def resolve_dependencies(self) -> dict[str, Provide]:
        """Return all dependencies correlating to handler function's kwargs that exist in the handler's scope."""
        plugin_registry = self._get_plugin_registry()
        if self._resolved_dependencies is Empty:
            self._resolved_dependencies = {}
            for layer in self.ownership_layers:
                for key, provider in (layer.dependencies or {}).items():
                    self._resolved_dependencies[key] = self._resolve_dependency(
                        key=key, provider=provider, plugin_registry=plugin_registry
                    )

        return self._resolved_dependencies

    def _resolve_dependency(
        self, key: str, provider: Provide | AnyCallable, plugin_registry: PluginRegistry | None
    ) -> Provide:
        if not isinstance(provider, Provide):
            provider = Provide(provider)

        if self._resolved_dependencies is not Empty:  # pragma: no cover
            self._validate_dependency_is_unique(dependencies=self._resolved_dependencies, key=key, provider=provider)

        if not getattr(provider, "parsed_fn_signature", None):
            dependency = unwrap_partial(provider.dependency)
            plugin: DIPlugin | None = None
            if plugin_registry:
                plugin = next(
                    (p for p in plugin_registry.di if isinstance(p, DIPlugin) and p.has_typed_init(dependency)),
                    None,
                )
            if plugin:
                signature, init_type_hints = plugin.get_typed_init(dependency)
                provider.parsed_fn_signature = ParsedSignature.from_signature(signature, init_type_hints)
            else:
                provider.parsed_fn_signature = ParsedSignature.from_fn(dependency, self.resolve_signature_namespace())

        if not getattr(provider, "signature_model", None):
            provider.signature_model = SignatureModel.create(
                dependency_name_set=self.dependency_name_set,
                fn=provider.dependency,
                parsed_signature=provider.parsed_fn_signature,
                data_dto=self.resolve_data_dto(),
                type_decoders=self.resolve_type_decoders(),
            )
        return provider

    def resolve_middleware(self) -> list[Middleware]:
        """Build the middleware stack for the RouteHandler and return it.

        The middlewares are added from top to bottom (``app -> router -> controller -> route handler``) and then
        reversed.
        """
        resolved_middleware: list[Middleware] = []
        for layer in self.ownership_layers:
            resolved_middleware.extend(layer.middleware or [])  # pyright: ignore
        return list(reversed(resolved_middleware))

    def resolve_exception_handlers(self) -> ExceptionHandlersMap:
        """Resolve the exception_handlers by starting from the route handler and moving up.

        This method is memoized so the computation occurs only once.
        """
        resolved_exception_handlers: dict[int | type[Exception], ExceptionHandler] = {}
        for layer in self.ownership_layers:
            resolved_exception_handlers.update(layer.exception_handlers or {})  # pyright: ignore
        return resolved_exception_handlers

    def resolve_opts(self) -> None:
        """Build the route handler opt dictionary by going from top to bottom.

        When merging keys from multiple layers, if the same key is defined by multiple layers, the value from the
        layer closest to the response handler will take precedence.
        """

        opt: dict[str, Any] = {}
        for layer in self.ownership_layers:
            opt.update(layer.opt or {})  # pyright: ignore

        self.opt = opt

    def resolve_signature_namespace(self) -> dict[str, Any]:
        """Build the route handler signature namespace dictionary by going from top to bottom.

        When merging keys from multiple layers, if the same key is defined by multiple layers, the value from the
        layer closest to the response handler will take precedence.
        """
        if self._resolved_layered_parameters is Empty:
            ns: dict[str, Any] = {}
            for layer in self.ownership_layers:
                ns.update(layer.signature_namespace)

            self._resolved_signature_namespace = ns
        return cast("dict[str, Any]", self._resolved_signature_namespace)

    def resolve_data_dto(self) -> type[AbstractDTO] | None:
        """Resolve the data_dto by starting from the route handler and moving up.
        If a handler is found it is returned, otherwise None is set.
        This method is memoized so the computation occurs only once.

        Returns:
            An optional :class:`DTO type <.dto.base_dto.AbstractDTO>`
        """
        if self._resolved_data_dto is Empty:
            if data_dtos := cast(
                "list[type[AbstractDTO] | None]",
                [layer.dto for layer in self.ownership_layers if layer.dto is not Empty],
            ):
                data_dto: type[AbstractDTO] | None = data_dtos[-1]
            elif self.parsed_data_field and (
                plugins_for_data_type := [
                    plugin
                    for plugin in self.app.plugins.serialization
                    if self.parsed_data_field.match_predicate_recursively(plugin.supports_type)
                ]
            ):
                data_dto = plugins_for_data_type[0].create_dto_for_type(self.parsed_data_field)
            else:
                data_dto = None

            if self.parsed_data_field and data_dto:
                data_dto.create_for_field_definition(
                    field_definition=self.parsed_data_field,
                    handler_id=self.handler_id,
                )

            self._resolved_data_dto = data_dto

        return self._resolved_data_dto

    def resolve_return_dto(self) -> type[AbstractDTO] | None:
        """Resolve the return_dto by starting from the route handler and moving up.
        If a handler is found it is returned, otherwise None is set.
        This method is memoized so the computation occurs only once.

        Returns:
            An optional :class:`DTO type <.dto.base_dto.AbstractDTO>`
        """
        if self._resolved_return_dto is Empty:
            if return_dtos := cast(
                "list[type[AbstractDTO] | None]",
                [layer.return_dto for layer in self.ownership_layers if layer.return_dto is not Empty],
            ):
                return_dto: type[AbstractDTO] | None = return_dtos[-1]
            elif plugins_for_return_type := [
                plugin
                for plugin in self.app.plugins.serialization
                if self.parsed_return_field.match_predicate_recursively(plugin.supports_type)
            ]:
                return_dto = plugins_for_return_type[0].create_dto_for_type(self.parsed_return_field)
            else:
                return_dto = self.resolve_data_dto()

            if return_dto and return_dto.is_supported_model_type_field(self.parsed_return_field):
                return_dto.create_for_field_definition(
                    field_definition=self.parsed_return_field,
                    handler_id=self.handler_id,
                )
                self._resolved_return_dto = return_dto
            else:
                self._resolved_return_dto = None

        return self._resolved_return_dto

    async def authorize_connection(self, connection: ASGIConnection) -> None:
        """Ensure the connection is authorized by running all the route guards in scope."""
        for guard in self.resolve_guards():
            await guard(connection, copy(self))  # type: ignore[misc]

    @staticmethod
    def _validate_dependency_is_unique(dependencies: dict[str, Provide], key: str, provider: Provide) -> None:
        """Validate that a given provider has not been already defined under a different key."""
        for dependency_key, value in dependencies.items():
            if provider == value:
                raise ImproperlyConfiguredException(
                    f"Provider for key {key} is already defined under the different key {dependency_key}. "
                    f"If you wish to override a provider, it must have the same key."
                )

    def on_registration(self, app: Litestar) -> None:
        """Called once per handler when the app object is instantiated.

        Args:
            app: The :class:`Litestar<.app.Litestar>` app object.

        Returns:
            None
        """
        self._validate_handler_function()
        self.resolve_dependencies()
        self.resolve_guards()
        self.resolve_middleware()
        self.resolve_opts()
        self.resolve_data_dto()
        self.resolve_return_dto()

    def _validate_handler_function(self) -> None:
        """Validate the route handler function once set by inspecting its return annotations."""
        if (
            self.parsed_data_field is not None
            and self.parsed_data_field.is_subclass_of(DTOData)
            and not self.resolve_data_dto()
        ):
            raise ImproperlyConfiguredException(
                f"Handler function {self.handler_name} has a data parameter that is a subclass of DTOData but no "
                "DTO has been registered for it."
            )

    def __str__(self) -> str:
        """Return a unique identifier for the route handler.

        Returns:
            A string
        """
        target: type[AsyncAnyCallable] | AsyncAnyCallable  # pyright: ignore
        target = unwrap_partial(self.fn)
        if not hasattr(target, "__qualname__"):
            target = type(target)
        return f"{target.__module__}.{target.__qualname__}"

    def create_kwargs_model(
        self,
        path_parameters: dict[str, PathParameterDefinition],
    ) -> KwargsModel:
        """Create a `KwargsModel` for a given route handler."""
        from litestar._kwargs import KwargsModel

        return KwargsModel.create_for_signature_model(
            signature_model=self.signature_model,
            parsed_signature=self.parsed_fn_signature,
            dependencies=self.resolve_dependencies(),
            path_parameters=set(path_parameters.keys()),
            layered_parameters=self.resolve_layered_parameters(),
        )
