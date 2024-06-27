from __future__ import annotations

import typing
from abc import abstractmethod
from inspect import getmodule
from typing import TYPE_CHECKING, Collection, Generic, TypeVar

from typing_extensions import NotRequired, TypedDict, get_type_hints

from litestar.dto._backend import DTOBackend
from litestar.dto._codegen_backend import DTOCodegenBackend
from litestar.dto.config import DTOConfig
from litestar.dto.data_structures import DTOData
from litestar.dto.types import RenameStrategy
from litestar.enums import RequestEncodingType
from litestar.exceptions.dto_exceptions import InvalidAnnotationException
from litestar.types.builtin_types import NoneType
from litestar.types.composite_types import TypeEncodersMap
from litestar.typing import FieldDefinition

if TYPE_CHECKING:
    from typing import Any, ClassVar, Generator

    from typing_extensions import Self

    from litestar._openapi.schema_generation import SchemaCreator
    from litestar.connection import ASGIConnection
    from litestar.dto.data_structures import DTOFieldDefinition
    from litestar.openapi.spec import Reference, Schema
    from litestar.types.serialization import LitestarEncodableType

__all__ = ("AbstractDTO",)

T = TypeVar("T")


class _BackendDict(TypedDict):
    data_backend: NotRequired[DTOBackend]
    return_backend: NotRequired[DTOBackend]


class AbstractDTO(Generic[T]):
    """Base class for DTO types."""

    __slots__ = ("asgi_connection",)

    config: ClassVar[DTOConfig]
    """Config objects to define properties of the DTO."""
    model_type: type[T]
    """If ``annotation`` is an iterable, this is the inner type, otherwise will be the same as ``annotation``."""

    _dto_backends: ClassVar[dict[str, _BackendDict]] = {}

    def __init__(self, asgi_connection: ASGIConnection) -> None:
        """Create an AbstractDTOFactory type.

        Args:
            asgi_connection: A :class:`ASGIConnection <litestar.connection.base.ASGIConnection>` instance.
        """
        self.asgi_connection = asgi_connection

    def __class_getitem__(cls, annotation: Any) -> type[Self]:
        field_definition = FieldDefinition.from_annotation(annotation)

        if (field_definition.is_optional and len(field_definition.args) > 2) or (
            field_definition.is_union and not field_definition.is_optional
        ):
            raise InvalidAnnotationException("Unions are currently not supported as type argument to DTOs.")

        if field_definition.is_forward_ref:
            raise InvalidAnnotationException("Forward references are not supported as type argument to DTO")

        # if a configuration is not provided, and the type narrowing is a type var, we don't want to create a subclass
        config = cls.get_dto_config_from_annotated_type(field_definition)

        if not config:
            if field_definition.is_type_var:
                return cls
            config = cls.config if hasattr(cls, "config") else DTOConfig()

        cls_dict: dict[str, Any] = {"config": config, "_type_backend_map": {}, "_handler_backend_map": {}}
        if not field_definition.is_type_var:
            cls_dict.update(model_type=field_definition.annotation)

        return type(f"{cls.__name__}[{annotation}]", (cls,), cls_dict)  # pyright: ignore

    def decode_builtins(self, value: dict[str, Any]) -> Any:
        """Decode a dictionary of Python values into an the DTO's datatype."""

        backend = self._dto_backends[self.asgi_connection.route_handler.handler_id]["data_backend"]  # pyright: ignore
        return backend.populate_data_from_builtins(value, self.asgi_connection)

    def decode_bytes(self, value: bytes) -> Any:
        """Decode a byte string into an the DTO's datatype."""

        backend = self._dto_backends[self.asgi_connection.route_handler.handler_id]["data_backend"]  # pyright: ignore
        return backend.populate_data_from_raw(value, self.asgi_connection)

    def data_to_encodable_type(self, data: T | Collection[T]) -> LitestarEncodableType:
        backend = self._dto_backends[self.asgi_connection.route_handler.handler_id]["return_backend"]  # pyright: ignore
        return backend.encode_data(data)

    @classmethod
    @abstractmethod
    def generate_field_definitions(cls, model_type: type[Any]) -> Generator[DTOFieldDefinition, None, None]:
        """Generate ``FieldDefinition`` instances from ``model_type``.

        Yields:
            ``FieldDefinition`` instances.
        """

    @classmethod
    @abstractmethod
    def detect_nested_field(cls, field_definition: FieldDefinition) -> bool:
        """Return ``True`` if ``field_definition`` represents a nested model field.

        Args:
            field_definition: inspect type to determine if field represents a nested model.

        Returns:
            ``True`` if ``field_definition`` represents a nested model field.
        """

    @classmethod
    def is_supported_model_type_field(cls, field_definition: FieldDefinition) -> bool:
        """Check support for the given type.

        Args:
            field_definition: A :class:`FieldDefinition <litestar.typing.FieldDefinition>` instance.

        Returns:
            Whether the type of the field definition is supported by the DTO.
        """
        return field_definition.is_subclass_of(cls.model_type) or (
            field_definition.origin
            and any(
                cls.resolve_model_type(inner_field).is_subclass_of(cls.model_type)
                for inner_field in field_definition.inner_types
            )
        )

    @classmethod
    def create_for_field_definition(
        cls,
        field_definition: FieldDefinition,
        handler_id: str,
        backend_cls: type[DTOBackend] | None = None,
    ) -> None:
        """Creates a DTO subclass for a field definition.

        Args:
            field_definition: A :class:`FieldDefinition <litestar.typing.FieldDefinition>` instance.
            handler_id: ID of the route handler for which to create a DTO instance.
            backend_cls: Alternative DTO backend class to use

        Returns:
            None
        """

        if handler_id not in cls._dto_backends:
            cls._dto_backends[handler_id] = {}

        backend_context = cls._dto_backends[handler_id]
        key = "data_backend" if field_definition.name == "data" else "return_backend"

        if key not in backend_context:
            model_type_field_definition = cls.resolve_model_type(field_definition=field_definition)
            wrapper_attribute_name: str | None = None

            if not model_type_field_definition.is_subclass_of(cls.model_type):
                if resolved_generic_result := cls.resolve_generic_wrapper_type(
                    field_definition=model_type_field_definition
                ):
                    model_type_field_definition, field_definition, wrapper_attribute_name = resolved_generic_result
                else:
                    raise InvalidAnnotationException(
                        f"DTO narrowed with '{cls.model_type}', handler type is '{field_definition.annotation}'"
                    )

            if backend_cls is None:
                backend_cls = DTOCodegenBackend if cls.config.experimental_codegen_backend is not False else DTOBackend

            backend_context[key] = backend_cls(  # type: ignore[literal-required]
                dto_factory=cls,
                field_definition=field_definition,
                model_type=model_type_field_definition.annotation,
                wrapper_attribute_name=wrapper_attribute_name,
                is_data_field=field_definition.name == "data",
                handler_id=handler_id,
            )

    @classmethod
    def create_openapi_schema(
        cls, field_definition: FieldDefinition, handler_id: str, schema_creator: SchemaCreator
    ) -> Reference | Schema:
        """Create an OpenAPI request body.

        Args:
            field_definition: A parsed type annotation that represents the annotation used on the handler.
            handler_id: ID of the route handler for which to create a DTO instance.
            schema_creator: A factory for creating schemas. Has a ``for_field_definition()`` method that accepts a
                :class:`~litestar.typing.FieldDefinition` instance.

        Returns:
            OpenAPI request body.
        """
        key = "data_backend" if field_definition.name == "data" else "return_backend"
        backend = cls._dto_backends[handler_id][key]  # type: ignore[literal-required]

        if backend.wrapper_attribute_name:
            # The DTO has been built for a handler that has a DTO supported type wrapped in a generic type.
            #
            # The backend doesn't receive the full annotation, only the type of the attribute on the outer type that
            # holds the DTO supported type.
            #
            # This special casing rebuilds the outer generic type annotation with the original model replaced by the DTO
            # generated transfer model type in the type arguments.
            transfer_model = backend.transfer_model_type
            generic_args = tuple(transfer_model if a is cls.model_type else a for a in field_definition.args)
            annotation = field_definition.safe_generic_origin[generic_args]
        else:
            annotation = backend.annotation

        return schema_creator.for_field_definition(
            FieldDefinition.from_annotation(annotation, kwarg_definition=field_definition.kwarg_definition)
        )

    @classmethod
    def resolve_generic_wrapper_type(
        cls, field_definition: FieldDefinition
    ) -> tuple[FieldDefinition, FieldDefinition, str] | None:
        """Handle where DTO supported data is wrapped in a generic container type.

        Args:
            field_definition: A parsed type annotation that represents the annotation used to narrow the DTO type.

        Returns:
            The data model type.
        """
        if field_definition.origin and (
            inner_fields := [
                inner_field
                for inner_field in field_definition.inner_types
                if cls.resolve_model_type(inner_field).is_subclass_of(cls.model_type)
            ]
        ):
            inner_field = inner_fields[0]
            model_field_definition = cls.resolve_model_type(inner_field)

            for attr, attr_type in cls.get_model_type_hints(field_definition.origin).items():
                if isinstance(attr_type.annotation, TypeVar) or any(
                    isinstance(t.annotation, TypeVar) for t in attr_type.inner_types
                ):
                    if attr_type.is_non_string_collection:
                        # the inner type of the collection type is the type var, so we need to specialize the
                        # collection type with the DTO supported type.
                        specialized_annotation = attr_type.safe_generic_origin[model_field_definition.annotation]
                        return model_field_definition, FieldDefinition.from_annotation(specialized_annotation), attr
                    return model_field_definition, inner_field, attr
        return None

    @staticmethod
    def get_model_type_hints(
        model_type: type[Any], namespace: dict[str, Any] | None = None
    ) -> dict[str, FieldDefinition]:
        """Retrieve type annotations for ``model_type``.

        Args:
            model_type: Any type-annotated class.
            namespace: Optional namespace to use for resolving type hints.

        Returns:
            Parsed type hints for ``model_type`` resolved within the scope of its module.
        """
        namespace = namespace or {}
        namespace.update(vars(typing))
        namespace.update(
            {
                "TypeEncodersMap": TypeEncodersMap,
                "DTOConfig": DTOConfig,
                "RenameStrategy": RenameStrategy,
                "RequestEncodingType": RequestEncodingType,
            }
        )

        if model_module := getmodule(model_type):
            namespace.update(vars(model_module))

        return {
            k: FieldDefinition.from_kwarg(annotation=v, name=k)
            for k, v in get_type_hints(model_type, localns=namespace, include_extras=True).items()  # pyright: ignore
        }

    @staticmethod
    def get_dto_config_from_annotated_type(field_definition: FieldDefinition) -> DTOConfig | None:
        """Extract data type and config instances from ``Annotated`` annotation.

        Args:
            field_definition: A parsed type annotation that represents the annotation used to narrow the DTO type.

        Returns:
            The type and config object extracted from the annotation.
        """
        return next((item for item in field_definition.metadata if isinstance(item, DTOConfig)), None)

    @classmethod
    def resolve_model_type(cls, field_definition: FieldDefinition) -> FieldDefinition:
        """Resolve the data model type from a parsed type.

        Args:
            field_definition: A parsed type annotation that represents the annotation used to narrow the DTO type.

        Returns:
            A :class:`FieldDefinition <.typing.FieldDefinition>` that represents the data model type.
        """
        if field_definition.is_optional:
            return cls.resolve_model_type(
                next(t for t in field_definition.inner_types if not t.is_subclass_of(NoneType))
            )

        if field_definition.is_subclass_of(DTOData):
            return cls.resolve_model_type(field_definition.inner_types[0])

        if field_definition.is_collection:
            if field_definition.is_mapping:
                return cls.resolve_model_type(field_definition.inner_types[1])

            if field_definition.is_tuple:
                if any(t is Ellipsis for t in field_definition.args):
                    return cls.resolve_model_type(field_definition.inner_types[0])
            elif field_definition.is_non_string_collection:
                return cls.resolve_model_type(field_definition.inner_types[0])

        return field_definition
