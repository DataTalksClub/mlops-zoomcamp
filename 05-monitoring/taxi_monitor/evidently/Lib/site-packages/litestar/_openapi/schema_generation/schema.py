from __future__ import annotations

from collections import deque
from copy import copy
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum, EnumMeta
from ipaddress import IPv4Address, IPv4Interface, IPv4Network, IPv6Address, IPv6Interface, IPv6Network
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    DefaultDict,
    Deque,
    Dict,
    FrozenSet,
    Hashable,
    Iterable,
    List,
    Literal,
    Mapping,
    MutableMapping,
    MutableSequence,
    OrderedDict,
    Pattern,
    Sequence,
    Set,
    Tuple,
    Union,
    cast,
)
from uuid import UUID

from typing_extensions import Self, get_args

from litestar._openapi.datastructures import SchemaRegistry
from litestar._openapi.schema_generation.constrained_fields import (
    create_date_constrained_field_schema,
    create_numerical_constrained_field_schema,
    create_string_constrained_field_schema,
)
from litestar._openapi.schema_generation.utils import (
    _get_normalized_schema_key,
    _should_create_enum_schema,
    _should_create_literal_schema,
    _type_or_first_not_none_inner_type,
    get_json_schema_formatted_examples,
)
from litestar.datastructures import SecretBytes, SecretString, UploadFile
from litestar.exceptions import ImproperlyConfiguredException
from litestar.openapi.spec.enums import OpenAPIFormat, OpenAPIType
from litestar.openapi.spec.schema import Schema, SchemaDataContainer
from litestar.params import BodyKwarg, KwargDefinition, ParameterKwarg
from litestar.plugins import OpenAPISchemaPlugin
from litestar.types import Empty
from litestar.types.builtin_types import NoneType
from litestar.typing import FieldDefinition
from litestar.utils.helpers import get_name
from litestar.utils.predicates import (
    is_class_and_subclass,
    is_undefined_sentinel,
)
from litestar.utils.typing import (
    get_origin_or_inner_type,
    make_non_optional_union,
    unwrap_new_type,
)

if TYPE_CHECKING:
    from litestar._openapi.datastructures import OpenAPIContext
    from litestar.openapi.spec import Example, Reference
    from litestar.plugins import OpenAPISchemaPluginProtocol

KWARG_DEFINITION_ATTRIBUTE_TO_OPENAPI_PROPERTY_MAP: dict[str, str] = {
    "content_encoding": "content_encoding",
    "default": "default",
    "description": "description",
    "enum": "enum",
    "examples": "examples",
    "external_docs": "external_docs",
    "format": "format",
    "ge": "minimum",
    "gt": "exclusive_minimum",
    "le": "maximum",
    "lt": "exclusive_maximum",
    "max_items": "max_items",
    "max_length": "max_length",
    "min_items": "min_items",
    "min_length": "min_length",
    "multiple_of": "multiple_of",
    "pattern": "pattern",
    "title": "title",
    "read_only": "read_only",
}

TYPE_MAP: dict[type[Any] | None | Any, Schema] = {
    Decimal: Schema(type=OpenAPIType.NUMBER),
    DefaultDict: Schema(type=OpenAPIType.OBJECT),
    Deque: Schema(type=OpenAPIType.ARRAY),
    Dict: Schema(type=OpenAPIType.OBJECT),
    FrozenSet: Schema(type=OpenAPIType.ARRAY),
    IPv4Address: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.IPV4),
    IPv4Interface: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.IPV4),
    IPv4Network: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.IPV4),
    IPv6Address: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.IPV6),
    IPv6Interface: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.IPV6),
    IPv6Network: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.IPV6),
    Iterable: Schema(type=OpenAPIType.ARRAY),
    List: Schema(type=OpenAPIType.ARRAY),
    Mapping: Schema(type=OpenAPIType.OBJECT),
    MutableMapping: Schema(type=OpenAPIType.OBJECT),
    MutableSequence: Schema(type=OpenAPIType.ARRAY),
    None: Schema(type=OpenAPIType.NULL),
    NoneType: Schema(type=OpenAPIType.NULL),
    OrderedDict: Schema(type=OpenAPIType.OBJECT),
    Path: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.URI),
    Pattern: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.REGEX),
    SecretBytes: Schema(type=OpenAPIType.STRING),
    SecretString: Schema(type=OpenAPIType.STRING),
    Sequence: Schema(type=OpenAPIType.ARRAY),
    Set: Schema(type=OpenAPIType.ARRAY),
    Tuple: Schema(type=OpenAPIType.ARRAY),
    UUID: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.UUID),
    bool: Schema(type=OpenAPIType.BOOLEAN),
    bytearray: Schema(type=OpenAPIType.STRING),
    bytes: Schema(type=OpenAPIType.STRING),
    date: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.DATE),
    datetime: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.DATE_TIME),
    deque: Schema(type=OpenAPIType.ARRAY),
    dict: Schema(type=OpenAPIType.OBJECT),
    float: Schema(type=OpenAPIType.NUMBER),
    frozenset: Schema(type=OpenAPIType.ARRAY),
    int: Schema(type=OpenAPIType.INTEGER),
    list: Schema(type=OpenAPIType.ARRAY),
    set: Schema(type=OpenAPIType.ARRAY),
    str: Schema(type=OpenAPIType.STRING),
    time: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.DURATION),
    timedelta: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.DURATION),
    tuple: Schema(type=OpenAPIType.ARRAY),
}


def _types_in_list(lst: list[Any]) -> list[OpenAPIType] | OpenAPIType:
    """Extract unique OpenAPITypes present in the values of a list.

    Args:
        lst: A list of values

    Returns:
        OpenAPIType in the given list. If more then one exists, return
        a list of OpenAPITypes.
    """
    schema_types: list[OpenAPIType] = []
    for item in lst:
        schema_type = TYPE_MAP[type(item)].type
        if isinstance(schema_type, OpenAPIType):
            schema_types.append(schema_type)
        else:
            raise RuntimeError("Unexpected type for schema item")  # pragma: no cover
    schema_types = list(set(schema_types))
    return schema_types[0] if len(schema_types) == 1 else schema_types


def _get_type_schema_name(field_definition: FieldDefinition) -> str:
    """Extract the schema name from a data container.

    Args:
        field_definition: A field definition instance.

    Returns:
        A string
    """

    if name := getattr(field_definition.annotation, "__schema_name__", None):
        return cast("str", name)

    name = get_name(field_definition.annotation)
    if field_definition.inner_types:
        inner_parts = ", ".join(_get_type_schema_name(t) for t in field_definition.inner_types)
        return f"{name}[{inner_parts}]"

    return name


def create_enum_schema(annotation: EnumMeta, include_null: bool = False) -> Schema:
    """Create a schema instance for an enum.

    Args:
        annotation: An enum.
        include_null: Whether to include null as a possible value.

    Returns:
        A schema instance.
    """
    enum_values: list[str | int | None] = [v.value for v in annotation]  # type: ignore[var-annotated]
    if include_null and None not in enum_values:
        enum_values.append(None)
    return Schema(type=_types_in_list(enum_values), enum=enum_values)


def _iter_flat_literal_args(annotation: Any) -> Iterable[Any]:
    """Iterate over the flattened arguments of a Literal.

    Args:
        annotation: An Literal annotation.

    Yields:
        The flattened arguments of the Literal.
    """
    for arg in get_args(annotation):
        if get_origin_or_inner_type(arg) is Literal:
            yield from _iter_flat_literal_args(arg)
        else:
            yield arg.value if isinstance(arg, Enum) else arg


def create_literal_schema(annotation: Any, include_null: bool = False) -> Schema:
    """Create a schema instance for a Literal.

    Args:
        annotation: An Literal annotation.
        include_null: Whether to include null as a possible value.

    Returns:
        A schema instance.
    """
    args = list(_iter_flat_literal_args(annotation))
    if include_null and None not in args:
        args.append(None)
    schema = Schema(type=_types_in_list(args))
    if len(args) > 1:
        schema.enum = args
    else:
        schema.const = args[0]
    return schema


def create_schema_for_annotation(annotation: Any) -> Schema:
    """Get a schema from the type mapping - if possible.

    Args:
        annotation: A type annotation.

    Returns:
        A schema instance or None.
    """

    return copy(TYPE_MAP[annotation]) if annotation in TYPE_MAP else Schema()


class SchemaCreator:
    __slots__ = ("generate_examples", "plugins", "prefer_alias", "schema_registry")

    def __init__(
        self,
        generate_examples: bool = False,
        plugins: Iterable[OpenAPISchemaPluginProtocol] | None = None,
        prefer_alias: bool = True,
        schema_registry: SchemaRegistry | None = None,
    ) -> None:
        """Instantiate a SchemaCreator.

        Args:
            generate_examples: Whether to generate examples if none are given.
            plugins: A list of plugins.
            prefer_alias: Whether to prefer the alias name for the schema.
            schema_registry: A SchemaRegistry instance.
        """
        self.generate_examples = generate_examples
        self.plugins = plugins if plugins is not None else []
        self.prefer_alias = prefer_alias
        self.schema_registry = schema_registry or SchemaRegistry()

    @classmethod
    def from_openapi_context(cls, context: OpenAPIContext, prefer_alias: bool = True, **kwargs: Any) -> Self:
        kwargs.setdefault("generate_examples", context.openapi_config.create_examples)
        kwargs.setdefault("plugins", context.plugins)
        kwargs.setdefault("schema_registry", context.schema_registry)
        return cls(**kwargs, prefer_alias=prefer_alias)

    @property
    def not_generating_examples(self) -> SchemaCreator:
        """Return a SchemaCreator with generate_examples set to False."""
        if not self.generate_examples:
            return self
        return type(self)(generate_examples=False, plugins=self.plugins, prefer_alias=False)

    @staticmethod
    def plugin_supports_field(plugin: OpenAPISchemaPluginProtocol, field: FieldDefinition) -> bool:
        if predicate := getattr(plugin, "is_plugin_supported_field", None):
            return predicate(field)  # type: ignore[no-any-return]
        return plugin.is_plugin_supported_type(field.annotation)

    def get_plugin_for(self, field_definition: FieldDefinition) -> OpenAPISchemaPluginProtocol | None:
        return next(
            (plugin for plugin in self.plugins if self.plugin_supports_field(plugin, field_definition)),
            None,
        )

    def is_constrained_field(self, field_definition: FieldDefinition) -> bool:
        """Return if the field is constrained, taking into account constraints defined by plugins"""
        return (
            isinstance(field_definition.kwarg_definition, (ParameterKwarg, BodyKwarg))
            and field_definition.kwarg_definition.is_constrained
        ) or any(
            p.is_constrained_field(field_definition)
            for p in self.plugins
            if isinstance(p, OpenAPISchemaPlugin) and p.is_plugin_supported_field(field_definition)
        )

    def is_undefined(self, value: Any) -> bool:
        """Return if the field is undefined, taking into account undefined types defined by plugins"""
        return is_undefined_sentinel(value) or any(
            p.is_undefined_sentinel(value) for p in self.plugins if isinstance(p, OpenAPISchemaPlugin)
        )

    def for_field_definition(self, field_definition: FieldDefinition) -> Schema | Reference:
        """Create a Schema for a given FieldDefinition.

        Args:
            field_definition: A signature field instance.

        Returns:
            A schema instance.
        """

        result: Schema | Reference

        if field_definition.is_new_type:
            result = self.for_new_type(field_definition)
        elif plugin_for_annotation := self.get_plugin_for(field_definition):
            result = self.for_plugin(field_definition, plugin_for_annotation)
        elif _should_create_enum_schema(field_definition):
            annotation = _type_or_first_not_none_inner_type(field_definition)
            result = create_enum_schema(annotation, include_null=field_definition.is_optional)
        elif _should_create_literal_schema(field_definition):
            annotation = (
                make_non_optional_union(field_definition.annotation)
                if field_definition.is_optional
                else field_definition.annotation
            )
            result = create_literal_schema(annotation, include_null=field_definition.is_optional)
        elif field_definition.is_optional:
            result = self.for_optional_field(field_definition)
        elif field_definition.is_union:
            result = self.for_union_field(field_definition)
        elif field_definition.is_type_var:
            result = self.for_typevar()
        elif field_definition.inner_types and not field_definition.is_generic:
            result = self.for_object_type(field_definition)
        elif self.is_constrained_field(field_definition):
            result = self.for_constrained_field(field_definition)
        elif field_definition.is_subclass_of(UploadFile):
            result = self.for_upload_file(field_definition)
        else:
            result = create_schema_for_annotation(field_definition.annotation)

        return self.process_schema_result(field_definition, result) if isinstance(result, Schema) else result

    def for_new_type(self, field_definition: FieldDefinition) -> Schema | Reference:
        return self.for_field_definition(
            FieldDefinition.from_kwarg(
                annotation=unwrap_new_type(field_definition.raw),
                name=field_definition.name,
                default=field_definition.default,
            )
        )

    @staticmethod
    def for_upload_file(field_definition: FieldDefinition) -> Schema:
        """Create schema for UploadFile.

        Args:
            field_definition: A field definition instance.

        Returns:
            A Schema instance.
        """

        property_key = "file"
        schema = Schema(
            type=OpenAPIType.STRING,
            content_media_type="application/octet-stream",
            format=OpenAPIFormat.BINARY,
        )

        # If the type is `dict[str, UploadFile]`, then it's the same as a `list[UploadFile]`
        # but we will internally convert that into a `dict[str, UploadFile]`.
        if field_definition.is_non_string_sequence or field_definition.is_mapping:
            property_key = "files"
            schema = Schema(type=OpenAPIType.ARRAY, items=schema)

        # If the uploadfile is annotated directly on the handler, then the
        # 'properties' needs to be created. Else, the 'properties' will be
        # created by the corresponding plugin.
        is_defined_on_handler = field_definition.name == "data" and isinstance(
            field_definition.kwarg_definition, BodyKwarg
        )
        if is_defined_on_handler:
            return Schema(type=OpenAPIType.OBJECT, properties={property_key: schema})

        return schema

    @staticmethod
    def for_typevar() -> Schema:
        """Create a schema for a TypeVar.

        Returns:
            A schema instance.
        """

        return Schema(type=OpenAPIType.OBJECT)

    def for_optional_field(self, field_definition: FieldDefinition) -> Schema:
        """Create a Schema for an optional FieldDefinition.

        Args:
            field_definition: A signature field instance.

        Returns:
            A schema instance.
        """
        schema_or_reference = self.for_field_definition(
            FieldDefinition.from_kwarg(
                annotation=make_non_optional_union(field_definition.annotation),
                name=field_definition.name,
                default=field_definition.default,
            )
        )
        if isinstance(schema_or_reference, Schema) and isinstance(schema_or_reference.one_of, list):
            result = schema_or_reference.one_of
        else:
            result = [schema_or_reference]

        return Schema(one_of=[Schema(type=OpenAPIType.NULL), *result])

    def for_union_field(self, field_definition: FieldDefinition) -> Schema:
        """Create a Schema for a union FieldDefinition.

        Args:
            field_definition: A signature field instance.

        Returns:
            A schema instance.
        """
        inner_types = (f for f in (field_definition.inner_types or []) if not self.is_undefined(f.annotation))
        values = list(map(self.for_field_definition, inner_types))
        return Schema(one_of=values)

    def for_object_type(self, field_definition: FieldDefinition) -> Schema:
        """Create schema for object types (dict, Mapping, list, Sequence etc.) types.

        Args:
            field_definition: A signature field instance.

        Returns:
            A schema instance.
        """
        if field_definition.has_inner_subclass_of(UploadFile):
            return self.for_upload_file(field_definition)

        if field_definition.is_mapping:
            return Schema(
                type=OpenAPIType.OBJECT,
                additional_properties=(
                    self.for_field_definition(field_definition.inner_types[1])
                    if field_definition.inner_types and len(field_definition.inner_types) == 2
                    else None
                ),
            )

        if field_definition.is_non_string_sequence or field_definition.is_non_string_iterable:
            # filters out ellipsis from tuple[int, ...] type annotations
            inner_types = (f for f in field_definition.inner_types if f.annotation is not Ellipsis)
            items = list(map(self.for_field_definition, inner_types or ()))

            return Schema(
                type=OpenAPIType.ARRAY,
                items=Schema(one_of=items) if len(items) > 1 else items[0],
            )

        raise ImproperlyConfiguredException(  # pragma: no cover
            f"Parameter '{field_definition.name}' with type '{field_definition.annotation}' could not be mapped to an Open API type. "
            f"This can occur if a user-defined generic type is resolved as a parameter. If '{field_definition.name}' should "
            "not be documented as a parameter, annotate it using the `Dependency` function, e.g., "
            f"`{field_definition.name}: ... = Dependency(...)`."
        )

    def for_plugin(self, field_definition: FieldDefinition, plugin: OpenAPISchemaPluginProtocol) -> Schema | Reference:
        """Create a schema using a plugin.

        Args:
            field_definition: A signature field instance.
            plugin: A plugin for the field type.

        Returns:
            A schema instance.
        """
        key = _get_normalized_schema_key(field_definition.annotation)
        if (ref := self.schema_registry.get_reference_for_key(key)) is not None:
            return ref

        schema = plugin.to_openapi_schema(field_definition=field_definition, schema_creator=self)
        if isinstance(schema, SchemaDataContainer):  # pragma: no cover
            return self.for_field_definition(
                FieldDefinition.from_kwarg(
                    annotation=schema.data_container,
                    name=field_definition.name,
                    default=field_definition.default,
                    extra=field_definition.extra,
                    kwarg_definition=field_definition.kwarg_definition,
                )
            )
        return schema

    def for_constrained_field(self, field: FieldDefinition) -> Schema:
        """Create Schema for Pydantic Constrained fields (created using constr(), conint() and so forth, or by subclassing
        Constrained*)

        Args:
            field: A signature field instance.

        Returns:
            A schema instance.
        """
        kwarg_definition = cast(Union[ParameterKwarg, BodyKwarg], field.kwarg_definition)
        if any(is_class_and_subclass(field.annotation, t) for t in (int, float, Decimal)):
            return create_numerical_constrained_field_schema(field.annotation, kwarg_definition)
        if any(is_class_and_subclass(field.annotation, t) for t in (str, bytes)):  # type: ignore[arg-type]
            return create_string_constrained_field_schema(field.annotation, kwarg_definition)
        if any(is_class_and_subclass(field.annotation, t) for t in (date, datetime)):
            return create_date_constrained_field_schema(field.annotation, kwarg_definition)
        return self.for_collection_constrained_field(field)

    def for_collection_constrained_field(self, field_definition: FieldDefinition) -> Schema:
        """Create Schema from Constrained List/Set field.

        Args:
            field_definition: A signature field instance.

        Returns:
            A schema instance.
        """
        schema = Schema(type=OpenAPIType.ARRAY)
        kwarg_definition = cast(Union[ParameterKwarg, BodyKwarg], field_definition.kwarg_definition)
        if kwarg_definition.min_items:
            schema.min_items = kwarg_definition.min_items
        if kwarg_definition.max_items:
            schema.max_items = kwarg_definition.max_items
        if any(is_class_and_subclass(field_definition.annotation, t) for t in (set, frozenset)):  # type: ignore[arg-type]
            schema.unique_items = True

        item_creator = self.not_generating_examples
        if field_definition.inner_types:
            items = list(map(item_creator.for_field_definition, field_definition.inner_types))
            schema.items = Schema(one_of=items) if len(items) > 1 else items[0]
        else:
            schema.items = item_creator.for_field_definition(
                FieldDefinition.from_kwarg(
                    field_definition.annotation.item_type, f"{field_definition.annotation.__name__}Field"
                )
            )
        return schema

    def process_schema_result(self, field: FieldDefinition, schema: Schema) -> Schema | Reference:
        if field.kwarg_definition and field.is_const and field.has_default and schema.const is None:
            schema.const = field.default

        if field.kwarg_definition:
            for kwarg_definition_key, schema_key in KWARG_DEFINITION_ATTRIBUTE_TO_OPENAPI_PROPERTY_MAP.items():
                if (value := getattr(field.kwarg_definition, kwarg_definition_key, Empty)) and (
                    not isinstance(value, Hashable) or not self.is_undefined(value)
                ):
                    if schema_key == "examples":
                        value = get_json_schema_formatted_examples(cast("list[Example]", value))

                    # we only want to transfer values from the `KwargDefinition` to `Schema` if the schema object
                    # doesn't already have a value for that property. For example, if a field is a constrained date,
                    # by this point, we have already set the `exclusive_minimum` and/or `exclusive_maximum` fields
                    # to floating point timestamp values on the schema object. However, the original `date` objects
                    # that define those constraints on `KwargDefinition` are still `date` objects. We don't want to
                    # overwrite them here.
                    if getattr(schema, schema_key, None) is None:
                        setattr(schema, schema_key, value)

            if isinstance(field.kwarg_definition, KwargDefinition) and (extra := field.kwarg_definition.schema_extra):
                for schema_key, value in extra.items():
                    if not hasattr(schema, schema_key):
                        raise ValueError(
                            f"`schema_extra` declares key `{schema_key}` which does not exist in `Schema` object"
                        )
                    setattr(schema, schema_key, value)

        if schema.default is None and field.default is not Empty:
            schema.default = field.default

        if not schema.examples and self.generate_examples:
            from litestar._openapi.schema_generation.examples import create_examples_for_field

            schema.examples = get_json_schema_formatted_examples(create_examples_for_field(field))

        if schema.title and schema.type == OpenAPIType.OBJECT:
            key = _get_normalized_schema_key(field.annotation)
            return self.schema_registry.get_reference_for_key(key) or schema
        return schema

    def create_component_schema(
        self,
        type_: FieldDefinition,
        /,
        required: list[str],
        property_fields: Mapping[str, FieldDefinition],
        openapi_type: OpenAPIType = OpenAPIType.OBJECT,
        title: str | None = None,
        examples: list[Any] | None = None,
    ) -> Schema:
        """Create a schema for the components/schemas section of the OpenAPI spec.

        These are schemas that can be referenced by other schemas in the document, including self references.

        To support self referencing schemas, the schema is added to the registry before schemas for its properties
        are created. This allows the schema to be referenced by its properties.

        Args:
            type_: ``FieldDefinition`` instance of the type to create a schema for.
            required: A list of required fields.
            property_fields: Mapping of name to ``FieldDefinition`` instances for the properties of the schema.
            openapi_type: The OpenAPI type, defaults to ``OpenAPIType.OBJECT``.
            title: The schema title, generated if not provided.
            examples: A mapping of example names to ``Example`` instances, not required.

        Returns:
            A schema instance.
        """
        schema = self.schema_registry.get_schema_for_key(_get_normalized_schema_key(type_.annotation))
        schema.title = title or _get_type_schema_name(type_)
        schema.required = required
        schema.type = openapi_type
        schema.properties = {k: self.for_field_definition(v) for k, v in property_fields.items()}
        schema.examples = examples
        return schema
