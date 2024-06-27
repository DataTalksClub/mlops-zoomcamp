"""DTO backends do the heavy lifting of decoding and validating raw bytes into domain models, and
back again, to bytes.
"""

from __future__ import annotations

from dataclasses import replace
from typing import (
    TYPE_CHECKING,
    AbstractSet,
    Any,
    ClassVar,
    Collection,
    Final,
    Mapping,
    Protocol,
    Union,
    cast,
)

import msgspec
from msgspec import UNSET, Struct, UnsetType, convert, defstruct, field
from typing_extensions import Annotated

from litestar.dto._types import (
    CollectionType,
    CompositeType,
    MappingType,
    NestedFieldInfo,
    SimpleType,
    TransferDTOFieldDefinition,
    TransferType,
    TupleType,
    UnionType,
)
from litestar.dto.data_structures import DTOData, DTOFieldDefinition
from litestar.dto.field import Mark
from litestar.enums import RequestEncodingType
from litestar.params import KwargDefinition
from litestar.serialization import decode_json, decode_msgpack
from litestar.types import Empty
from litestar.typing import FieldDefinition
from litestar.utils import unique_name_for_scope

if TYPE_CHECKING:
    from litestar.connection import ASGIConnection
    from litestar.dto import AbstractDTO, RenameStrategy
    from litestar.types.serialization import LitestarEncodableType

__all__ = ("DTOBackend",)


class CompositeTypeHandler(Protocol):
    def __call__(
        self,
        field_definition: FieldDefinition,
        exclude: AbstractSet[str],
        include: AbstractSet[str],
        rename_fields: dict[str, str],
        unique_name: str,
        nested_depth: int,
    ) -> CompositeType: ...


class DTOBackend:
    __slots__ = (
        "annotation",
        "dto_data_type",
        "dto_factory",
        "field_definition",
        "handler_id",
        "is_data_field",
        "model_type",
        "parsed_field_definitions",
        "reverse_name_map",
        "transfer_model_type",
        "wrapper_attribute_name",
    )

    _seen_model_names: ClassVar[set[str]] = set()

    def __init__(
        self,
        dto_factory: type[AbstractDTO],
        field_definition: FieldDefinition,
        handler_id: str,
        is_data_field: bool,
        model_type: type[Any],
        wrapper_attribute_name: str | None,
    ) -> None:
        """Create dto backend instance.

        Args:
            dto_factory: The DTO factory class calling this backend.
            field_definition: Parsed type.
            handler_id: The name of the handler that this backend is for.
            is_data_field: Whether the field is a subclass of DTOData.
            model_type: Model type.
            wrapper_attribute_name: If the data that DTO should operate upon is wrapped in a generic datastructure, this is the name of the attribute that the data is stored in.
        """
        self.dto_factory: Final[type[AbstractDTO]] = dto_factory
        self.field_definition: Final[FieldDefinition] = field_definition
        self.is_data_field: Final[bool] = is_data_field
        self.handler_id: Final[str] = handler_id
        self.model_type: Final[type[Any]] = model_type
        self.wrapper_attribute_name: Final[str | None] = wrapper_attribute_name

        self.parsed_field_definitions = self.parse_model(
            model_type=model_type,
            exclude=self.dto_factory.config.exclude,
            include=self.dto_factory.config.include,
            rename_fields=self.dto_factory.config.rename_fields,
        )
        self.transfer_model_type = self.create_transfer_model_type(
            model_name=model_type.__name__, field_definitions=self.parsed_field_definitions
        )
        self.dto_data_type: type[DTOData] | None = None

        if field_definition.is_subclass_of(DTOData):
            self.dto_data_type = field_definition.annotation
            field_definition = self.field_definition.inner_types[0]

        self.annotation = build_annotation_for_backend(model_type, field_definition, self.transfer_model_type)

    def parse_model(
        self,
        model_type: Any,
        exclude: AbstractSet[str],
        include: AbstractSet[str],
        rename_fields: dict[str, str],
        nested_depth: int = 0,
    ) -> tuple[TransferDTOFieldDefinition, ...]:
        """Reduce :attr:`model_type` to a tuple :class:`TransferDTOFieldDefinition` instances.

        Returns:
        Fields for data transfer.
        """
        defined_fields = []
        generic_field_definitons = list(FieldDefinition.from_annotation(model_type).generic_types or ())
        for field_definition in self.dto_factory.generate_field_definitions(model_type):
            if field_definition.is_type_var:
                base_arg_field = generic_field_definitons.pop()
                field_definition = replace(
                    field_definition, annotation=base_arg_field.annotation, raw=base_arg_field.raw
                )

            if _should_mark_private(field_definition, self.dto_factory.config.underscore_fields_private):
                field_definition.dto_field.mark = Mark.PRIVATE

            try:
                transfer_type = self._create_transfer_type(
                    field_definition=field_definition,
                    exclude=exclude,
                    include=include,
                    rename_fields=rename_fields,
                    field_name=field_definition.name,
                    unique_name=field_definition.model_name,
                    nested_depth=nested_depth,
                )
            except RecursionError:
                continue

            transfer_field_definition = TransferDTOFieldDefinition.from_dto_field_definition(
                field_definition=field_definition,
                serialization_name=rename_fields.get(field_definition.name),
                transfer_type=transfer_type,
                is_partial=self.dto_factory.config.partial,
                is_excluded=_should_exclude_field(
                    field_definition=field_definition,
                    exclude=exclude,
                    include=include,
                    is_data_field=self.is_data_field,
                ),
            )
            defined_fields.append(transfer_field_definition)
        return tuple(defined_fields)

    def _create_transfer_model_name(self, model_name: str) -> str:
        long_name_prefix = self.handler_id.split("::")[0]
        short_name_prefix = _camelize(long_name_prefix.split(".")[-1], True)

        name_suffix = "RequestBody" if self.is_data_field else "ResponseBody"

        if (short_name := f"{short_name_prefix}{model_name}{name_suffix}") not in self._seen_model_names:
            name = short_name
        elif (long_name := f"{long_name_prefix}{model_name}{name_suffix}") not in self._seen_model_names:
            name = long_name
        else:
            name = unique_name_for_scope(long_name, self._seen_model_names)

        self._seen_model_names.add(name)

        return name

    def create_transfer_model_type(
        self,
        model_name: str,
        field_definitions: tuple[TransferDTOFieldDefinition, ...],
    ) -> type[Struct]:
        """Create a model for data transfer.

        Args:
            model_name: name for the type that should be unique across all transfer types.
            field_definitions: field definitions for the container type.

        Returns:
            A ``BackendT`` class.
        """
        struct_name = self._create_transfer_model_name(model_name)

        struct = _create_struct_for_field_definitions(
            struct_name, field_definitions, self.dto_factory.config.rename_strategy
        )
        setattr(struct, "__schema_name__", struct_name)
        return struct

    def parse_raw(self, raw: bytes, asgi_connection: ASGIConnection) -> Struct | Collection[Struct]:
        """Parse raw bytes into transfer model type.

        Args:
            raw: bytes
            asgi_connection: The current ASGI Connection

        Returns:
            The raw bytes parsed into transfer model type.
        """
        request_encoding = RequestEncodingType.JSON

        if (content_type := getattr(asgi_connection, "content_type", None)) and (media_type := content_type[0]):
            request_encoding = media_type

        type_decoders = asgi_connection.route_handler.resolve_type_decoders()

        if request_encoding == RequestEncodingType.MESSAGEPACK:
            result = decode_msgpack(value=raw, target_type=self.annotation, type_decoders=type_decoders)
        else:
            result = decode_json(value=raw, target_type=self.annotation, type_decoders=type_decoders)

        return cast("Struct | Collection[Struct]", result)

    def parse_builtins(self, builtins: Any, asgi_connection: ASGIConnection) -> Any:
        """Parse builtin types into transfer model type.

        Args:
            builtins: Builtin type.
            asgi_connection: The current ASGI Connection

        Returns:
            The builtin type parsed into transfer model type.
        """
        return convert(
            obj=builtins,
            type=self.annotation,
            dec_hook=asgi_connection.route_handler.default_deserializer,
            strict=False,
            str_keys=True,
        )

    def populate_data_from_builtins(self, builtins: Any, asgi_connection: ASGIConnection) -> Any:
        """Populate model instance from builtin types.

        Args:
            builtins: Builtin type.
            asgi_connection: The current ASGI Connection

        Returns:
            Instance or collection of ``model_type`` instances.
        """
        if self.dto_data_type:
            return self.dto_data_type(
                backend=self,
                data_as_builtins=_transfer_data(
                    destination_type=dict,
                    source_data=self.parse_builtins(builtins, asgi_connection),
                    field_definitions=self.parsed_field_definitions,
                    field_definition=self.field_definition,
                    is_data_field=self.is_data_field,
                ),
            )
        return self.transfer_data_from_builtins(self.parse_builtins(builtins, asgi_connection))

    def transfer_data_from_builtins(self, builtins: Any) -> Any:
        """Populate model instance from builtin types.

        Args:
            builtins: Builtin type.

        Returns:
            Instance or collection of ``model_type`` instances.
        """
        return _transfer_data(
            destination_type=self.model_type,
            source_data=builtins,
            field_definitions=self.parsed_field_definitions,
            field_definition=self.field_definition,
            is_data_field=self.is_data_field,
        )

    def populate_data_from_raw(self, raw: bytes, asgi_connection: ASGIConnection) -> Any:
        """Parse raw bytes into instance of `model_type`.

        Args:
            raw: bytes
            asgi_connection: The current ASGI Connection

        Returns:
            Instance or collection of ``model_type`` instances.
        """
        if self.dto_data_type:
            return self.dto_data_type(
                backend=self,
                data_as_builtins=_transfer_data(
                    destination_type=dict,
                    source_data=self.parse_raw(raw, asgi_connection),
                    field_definitions=self.parsed_field_definitions,
                    field_definition=self.field_definition,
                    is_data_field=self.is_data_field,
                ),
            )
        return _transfer_data(
            destination_type=self.model_type,
            source_data=self.parse_raw(raw, asgi_connection),
            field_definitions=self.parsed_field_definitions,
            field_definition=self.field_definition,
            is_data_field=self.is_data_field,
        )

    def encode_data(self, data: Any) -> LitestarEncodableType:
        """Encode data into a ``LitestarEncodableType``.

        Args:
            data: Data to encode.

        Returns:
            Encoded data.
        """
        if self.wrapper_attribute_name:
            wrapped_transfer = _transfer_data(
                destination_type=self.transfer_model_type,
                source_data=getattr(data, self.wrapper_attribute_name),
                field_definitions=self.parsed_field_definitions,
                field_definition=self.field_definition,
                is_data_field=self.is_data_field,
            )
            setattr(
                data,
                self.wrapper_attribute_name,
                wrapped_transfer,
            )
            return cast("LitestarEncodableType", data)

        return cast(
            "LitestarEncodableType",
            _transfer_data(
                destination_type=self.transfer_model_type,
                source_data=data,
                field_definitions=self.parsed_field_definitions,
                field_definition=self.field_definition,
                is_data_field=self.is_data_field,
            ),
        )

    def _get_handler_for_field_definition(self, field_definition: FieldDefinition) -> CompositeTypeHandler | None:
        if field_definition.is_union:
            return self._create_union_type

        if field_definition.is_tuple:
            if len(field_definition.inner_types) == 2 and field_definition.inner_types[1].annotation is Ellipsis:
                return self._create_collection_type
            return self._create_tuple_type

        if field_definition.is_mapping:
            return self._create_mapping_type

        if field_definition.is_non_string_collection:
            return self._create_collection_type
        return None

    def _create_transfer_type(
        self,
        field_definition: FieldDefinition,
        exclude: AbstractSet[str],
        include: AbstractSet[str],
        rename_fields: dict[str, str],
        field_name: str,
        unique_name: str,
        nested_depth: int,
    ) -> CompositeType | SimpleType:
        exclude = _filter_nested_field(exclude, field_name)
        include = _filter_nested_field(include, field_name)
        rename_fields = _filter_nested_field_mapping(rename_fields, field_name)

        if composite_type_handler := self._get_handler_for_field_definition(field_definition):
            return composite_type_handler(
                field_definition=field_definition,
                exclude=exclude,
                include=include,
                rename_fields=rename_fields,
                unique_name=unique_name,
                nested_depth=nested_depth,
            )

        transfer_model: NestedFieldInfo | None = None

        if self.dto_factory.detect_nested_field(field_definition):
            if nested_depth == self.dto_factory.config.max_nested_depth:
                raise RecursionError

            unique_name = f"{unique_name}{field_definition.raw.__name__}"

            nested_field_definitions = self.parse_model(
                model_type=field_definition.annotation,
                exclude=exclude,
                include=include,
                rename_fields=rename_fields,
                nested_depth=nested_depth + 1,
            )

            transfer_model = NestedFieldInfo(
                model=self.create_transfer_model_type(unique_name, nested_field_definitions),
                field_definitions=nested_field_definitions,
            )

        return SimpleType(field_definition, nested_field_info=transfer_model)

    def _create_collection_type(
        self,
        field_definition: FieldDefinition,
        exclude: AbstractSet[str],
        include: AbstractSet[str],
        rename_fields: dict[str, str],
        unique_name: str,
        nested_depth: int,
    ) -> CollectionType:
        inner_types = field_definition.inner_types
        inner_type = self._create_transfer_type(
            field_definition=inner_types[0] if inner_types else FieldDefinition.from_annotation(Any),
            exclude=exclude,
            include=include,
            field_name="0",
            unique_name=f"{unique_name}_0",
            nested_depth=nested_depth,
            rename_fields=rename_fields,
        )
        return CollectionType(
            field_definition=field_definition, inner_type=inner_type, has_nested=inner_type.has_nested
        )

    def _create_mapping_type(
        self,
        field_definition: FieldDefinition,
        exclude: AbstractSet[str],
        include: AbstractSet[str],
        rename_fields: dict[str, str],
        unique_name: str,
        nested_depth: int,
    ) -> MappingType:
        inner_types = field_definition.inner_types
        key_type = self._create_transfer_type(
            field_definition=inner_types[0] if inner_types else FieldDefinition.from_annotation(Any),
            exclude=exclude,
            include=include,
            field_name="0",
            unique_name=f"{unique_name}_0",
            nested_depth=nested_depth,
            rename_fields=rename_fields,
        )
        value_type = self._create_transfer_type(
            field_definition=inner_types[1] if inner_types else FieldDefinition.from_annotation(Any),
            exclude=exclude,
            include=include,
            field_name="1",
            unique_name=f"{unique_name}_1",
            nested_depth=nested_depth,
            rename_fields=rename_fields,
        )
        return MappingType(
            field_definition=field_definition,
            key_type=key_type,
            value_type=value_type,
            has_nested=key_type.has_nested or value_type.has_nested,
        )

    def _create_tuple_type(
        self,
        field_definition: FieldDefinition,
        exclude: AbstractSet[str],
        include: AbstractSet[str],
        rename_fields: dict[str, str],
        unique_name: str,
        nested_depth: int,
    ) -> TupleType:
        inner_types = tuple(
            self._create_transfer_type(
                field_definition=inner_type,
                exclude=exclude,
                include=include,
                field_name=str(i),
                unique_name=f"{unique_name}_{i}",
                nested_depth=nested_depth,
                rename_fields=rename_fields,
            )
            for i, inner_type in enumerate(field_definition.inner_types)
        )
        return TupleType(
            field_definition=field_definition,
            inner_types=inner_types,
            has_nested=any(t.has_nested for t in inner_types),
        )

    def _create_union_type(
        self,
        field_definition: FieldDefinition,
        exclude: AbstractSet[str],
        include: AbstractSet[str],
        rename_fields: dict[str, str],
        unique_name: str,
        nested_depth: int,
    ) -> UnionType:
        inner_types = tuple(
            self._create_transfer_type(
                field_definition=inner_type,
                exclude=exclude,
                include=include,
                field_name=str(i),
                unique_name=f"{unique_name}_{i}",
                nested_depth=nested_depth,
                rename_fields=rename_fields,
            )
            for i, inner_type in enumerate(field_definition.inner_types)
        )
        return UnionType(
            field_definition=field_definition,
            inner_types=inner_types,
            has_nested=any(t.has_nested for t in inner_types),
        )


def _camelize(value: str, capitalize_first_letter: bool) -> str:
    return "".join(
        word if index == 0 and not capitalize_first_letter else word.capitalize()
        for index, word in enumerate(value.split("_"))
    )


def _filter_nested_field(field_name_set: AbstractSet[str], field_name: str) -> AbstractSet[str]:
    """Filter a nested field name."""
    return {split[1] for s in field_name_set if (split := s.split(".", 1))[0] == field_name and len(split) > 1}


def _filter_nested_field_mapping(field_name_mapping: Mapping[str, str], field_name: str) -> dict[str, str]:
    """Filter a nested field name."""
    return {
        split[1]: v
        for s, v in field_name_mapping.items()
        if (split := s.split(".", 1))[0] == field_name and len(split) > 1
    }


def _transfer_data(
    destination_type: type[Any],
    source_data: Any | Collection[Any],
    field_definitions: tuple[TransferDTOFieldDefinition, ...],
    field_definition: FieldDefinition,
    is_data_field: bool,
) -> Any:
    """Create instance or iterable of instances of ``destination_type``.

    Args:
        destination_type: the model type received by the DTO on type narrowing.
        source_data: data that has been parsed and validated via the backend.
        field_definitions: model field definitions.
        field_definition: the parsed type that represents the handler annotation for which the DTO is being applied.
        is_data_field: whether the DTO is being applied to a ``data`` field.

    Returns:
        Data parsed into ``destination_type``.
    """
    if field_definition.is_non_string_collection:
        if not field_definition.is_mapping:
            return field_definition.instantiable_origin(
                _transfer_data(
                    destination_type=destination_type,
                    source_data=item,
                    field_definitions=field_definitions,
                    field_definition=field_definition.inner_types[0],
                    is_data_field=is_data_field,
                )
                for item in source_data
            )
        return field_definition.instantiable_origin(
            (
                key,
                _transfer_data(
                    destination_type=destination_type,
                    source_data=value,
                    field_definitions=field_definitions,
                    field_definition=field_definition.inner_types[1],
                    is_data_field=is_data_field,
                ),
            )
            for key, value in source_data.items()  # type: ignore[union-attr]
        )

    return _transfer_instance_data(
        destination_type=destination_type,
        source_instance=source_data,
        field_definitions=field_definitions,
        is_data_field=is_data_field,
    )


def _transfer_instance_data(
    destination_type: type[Any],
    source_instance: Any,
    field_definitions: tuple[TransferDTOFieldDefinition, ...],
    is_data_field: bool,
) -> Any:
    """Create instance of ``destination_type`` with data from ``source_instance``.

    Args:
        destination_type: the model type received by the DTO on type narrowing.
        source_instance: primitive data that has been parsed and validated via the backend.
        field_definitions: model field definitions.
        is_data_field: whether the given field is a 'data' kwarg field.

    Returns:
        Data parsed into ``model_type``.
    """
    unstructured_data = {}

    for field_definition in field_definitions:
        if not is_data_field:
            if field_definition.is_excluded:
                continue
        elif not (
            field_definition.name in source_instance
            if isinstance(source_instance, Mapping)
            else hasattr(source_instance, field_definition.name)
        ):
            continue

        transfer_type = field_definition.transfer_type
        source_value = (
            source_instance[field_definition.name]
            if isinstance(source_instance, Mapping)
            else getattr(source_instance, field_definition.name)
        )

        if field_definition.is_partial and is_data_field and source_value is UNSET:
            continue

        unstructured_data[field_definition.name] = _transfer_type_data(
            source_value=source_value,
            transfer_type=transfer_type,
            nested_as_dict=destination_type is dict,
            is_data_field=is_data_field,
        )

    return destination_type(**unstructured_data)


def _transfer_type_data(
    source_value: Any,
    transfer_type: TransferType,
    nested_as_dict: bool,
    is_data_field: bool,
) -> Any:
    if isinstance(transfer_type, SimpleType) and transfer_type.nested_field_info:
        if nested_as_dict:
            destination_type: Any = dict
        elif is_data_field:
            destination_type = transfer_type.field_definition.annotation
        else:
            destination_type = transfer_type.nested_field_info.model

        return _transfer_instance_data(
            destination_type=destination_type,
            source_instance=source_value,
            field_definitions=transfer_type.nested_field_info.field_definitions,
            is_data_field=is_data_field,
        )

    if isinstance(transfer_type, UnionType) and transfer_type.has_nested:
        return _transfer_nested_union_type_data(
            transfer_type=transfer_type,
            source_value=source_value,
            is_data_field=is_data_field,
        )

    if isinstance(transfer_type, CollectionType):
        if transfer_type.has_nested:
            return transfer_type.field_definition.instantiable_origin(
                _transfer_type_data(
                    source_value=item,
                    transfer_type=transfer_type.inner_type,
                    nested_as_dict=False,
                    is_data_field=is_data_field,
                )
                for item in source_value
            )

        return transfer_type.field_definition.instantiable_origin(source_value)

    if isinstance(transfer_type, MappingType):
        if transfer_type.has_nested:
            return transfer_type.field_definition.instantiable_origin(
                (
                    key,
                    _transfer_type_data(
                        source_value=value,
                        transfer_type=transfer_type.value_type,
                        nested_as_dict=False,
                        is_data_field=is_data_field,
                    ),
                )
                for key, value in source_value.items()
            )

        return transfer_type.field_definition.instantiable_origin(source_value)

    return source_value


def _transfer_nested_union_type_data(
    transfer_type: UnionType,
    source_value: Any,
    is_data_field: bool,
) -> Any:
    for inner_type in transfer_type.inner_types:
        if isinstance(inner_type, CompositeType):
            raise RuntimeError("Composite inner types not (yet) supported for nested unions.")

        if inner_type.nested_field_info and isinstance(
            source_value,
            inner_type.nested_field_info.model if is_data_field else inner_type.field_definition.annotation,
        ):
            return _transfer_instance_data(
                destination_type=inner_type.field_definition.annotation
                if is_data_field
                else inner_type.nested_field_info.model,
                source_instance=source_value,
                field_definitions=inner_type.nested_field_info.field_definitions,
                is_data_field=is_data_field,
            )
    return source_value


def _create_msgspec_field(field_definition: TransferDTOFieldDefinition) -> Any:
    kwargs: dict[str, Any] = {}
    if field_definition.is_partial:
        kwargs["default"] = UNSET

    elif field_definition.default is not Empty:
        kwargs["default"] = field_definition.default

    elif field_definition.default_factory is not None:
        kwargs["default_factory"] = field_definition.default_factory

    if field_definition.serialization_name is not None:
        kwargs["name"] = field_definition.serialization_name

    return field(**kwargs)


def _create_struct_field_meta_for_field_definition(field_definition: TransferDTOFieldDefinition) -> msgspec.Meta | None:
    if (kwarg_definition := field_definition.kwarg_definition) is None or not isinstance(
        kwarg_definition, KwargDefinition
    ):
        return None

    return msgspec.Meta(
        description=kwarg_definition.description,
        examples=[e.value for e in kwarg_definition.examples or []],
        ge=kwarg_definition.ge,
        gt=kwarg_definition.gt,
        le=kwarg_definition.le,
        lt=kwarg_definition.lt,
        max_length=kwarg_definition.max_length if not field_definition.is_partial else None,
        min_length=kwarg_definition.min_length if not field_definition.is_partial else None,
        multiple_of=kwarg_definition.multiple_of,
        pattern=kwarg_definition.pattern,
        title=kwarg_definition.title,
    )


def _create_struct_for_field_definitions(
    model_name: str,
    field_definitions: tuple[TransferDTOFieldDefinition, ...],
    rename_strategy: RenameStrategy | dict[str, str] | None,
) -> type[Struct]:
    struct_fields: list[tuple[str, type] | tuple[str, type, type]] = []

    for field_definition in field_definitions:
        if field_definition.is_excluded:
            continue

        field_type = _create_transfer_model_type_annotation(field_definition.transfer_type)
        if field_definition.is_partial:
            field_type = Union[field_type, UnsetType]

        if (field_meta := _create_struct_field_meta_for_field_definition(field_definition)) is not None:
            field_type = Annotated[field_type, field_meta]

        struct_fields.append(
            (
                field_definition.name,
                field_type,
                _create_msgspec_field(field_definition),
            )
        )
    return defstruct(model_name, struct_fields, frozen=True, kw_only=True, rename=rename_strategy)


def build_annotation_for_backend(
    model_type: type[Any], field_definition: FieldDefinition, transfer_model: type[Struct]
) -> Any:
    """A helper to re-build a generic outer type with new inner type.

    Args:
        model_type: The original model type.
        field_definition: The parsed type that represents the handler annotation for which the DTO is being applied.
        transfer_model: The transfer model generated to represent the model type.

    Returns:
        Annotation with new inner type if applicable.
    """
    if not field_definition.inner_types:
        if field_definition.is_subclass_of(model_type):
            return transfer_model
        return field_definition.annotation

    inner_types = tuple(
        build_annotation_for_backend(model_type, inner_type, transfer_model)
        for inner_type in field_definition.inner_types
    )

    return field_definition.safe_generic_origin[inner_types]


def _should_mark_private(field_definition: DTOFieldDefinition, underscore_fields_private: bool) -> bool:
    """Returns ``True`` where a field should be marked as private.

    Fields should be marked as private when:
    - the ``underscore_fields_private`` flag is set.
    - the field is not already marked.
    - the field name is prefixed with an underscore

    Args:
        field_definition: defined DTO field
        underscore_fields_private: whether fields prefixed with an underscore should be marked as private.
    """
    return bool(
        underscore_fields_private and field_definition.dto_field.mark is None and field_definition.name.startswith("_")
    )


def _should_exclude_field(
    field_definition: DTOFieldDefinition, exclude: AbstractSet[str], include: AbstractSet[str], is_data_field: bool
) -> bool:
    """Returns ``True`` where a field should be excluded from data transfer.

    Args:
        field_definition: defined DTO field
        exclude: names of fields to exclude
        include: names of fields to exclude
        is_data_field: whether the field is a data field

    Returns:
        ``True`` if the field should not be included in any data transfer.
    """
    field_name = field_definition.name
    if field_name in exclude:
        return True
    if include and field_name not in include and not (any(f.startswith(f"{field_name}.") for f in include)):
        return True
    if field_definition.dto_field.mark is Mark.PRIVATE:
        return True
    if is_data_field and field_definition.dto_field.mark is Mark.READ_ONLY:
        return True
    return not is_data_field and field_definition.dto_field.mark is Mark.WRITE_ONLY


def _create_transfer_model_type_annotation(transfer_type: TransferType) -> Any:
    """Create a type annotation for a transfer model.

    Uses the parsed type that originates from the data model and the transfer model generated to represent a nested
    type to reconstruct the type annotation for the transfer model.
    """
    if isinstance(transfer_type, SimpleType):
        if transfer_type.nested_field_info:
            return transfer_type.nested_field_info.model
        return transfer_type.field_definition.annotation

    if isinstance(transfer_type, CollectionType):
        return _create_transfer_model_collection_type(transfer_type)

    if isinstance(transfer_type, MappingType):
        return _create_transfer_model_mapping_type(transfer_type)

    if isinstance(transfer_type, TupleType):
        return _create_transfer_model_tuple_type(transfer_type)

    if isinstance(transfer_type, UnionType):
        return _create_transfer_model_union_type(transfer_type)

    raise RuntimeError(f"Unexpected transfer type: {type(transfer_type)}")


def _create_transfer_model_collection_type(transfer_type: CollectionType) -> Any:
    generic_collection_type = transfer_type.field_definition.safe_generic_origin
    inner_type = _create_transfer_model_type_annotation(transfer_type.inner_type)
    if transfer_type.field_definition.origin is tuple:
        return generic_collection_type[inner_type, ...]
    return generic_collection_type[inner_type]


def _create_transfer_model_tuple_type(transfer_type: TupleType) -> Any:
    inner_types = tuple(_create_transfer_model_type_annotation(t) for t in transfer_type.inner_types)
    return transfer_type.field_definition.safe_generic_origin[inner_types]


def _create_transfer_model_union_type(transfer_type: UnionType) -> Any:
    inner_types = tuple(_create_transfer_model_type_annotation(t) for t in transfer_type.inner_types)
    return transfer_type.field_definition.safe_generic_origin[inner_types]


def _create_transfer_model_mapping_type(transfer_type: MappingType) -> Any:
    key_type = _create_transfer_model_type_annotation(transfer_type.key_type)
    value_type = _create_transfer_model_type_annotation(transfer_type.value_type)
    return transfer_type.field_definition.safe_generic_origin[key_type, value_type]
