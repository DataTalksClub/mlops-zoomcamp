from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from typing_extensions import Annotated

from litestar.contrib.pydantic.utils import (
    create_field_definitions_for_computed_fields,
    is_pydantic_2_model,
    is_pydantic_constrained_field,
    is_pydantic_model_class,
    is_pydantic_undefined,
    is_pydantic_v2,
    pydantic_get_type_hints_with_generics_resolved,
    pydantic_unwrap_and_get_origin,
)
from litestar.exceptions import MissingDependencyException
from litestar.openapi.spec import OpenAPIFormat, OpenAPIType, Schema
from litestar.plugins import OpenAPISchemaPlugin
from litestar.types import Empty
from litestar.typing import FieldDefinition
from litestar.utils import is_class_and_subclass, is_generic

try:
    import pydantic as _  # noqa: F401
except ImportError as e:
    raise MissingDependencyException("pydantic") from e

try:
    import pydantic as pydantic_v2

    if not is_pydantic_v2(pydantic_v2):
        raise ImportError

    from pydantic import v1 as pydantic_v1
except ImportError:
    import pydantic as pydantic_v1  # type: ignore[no-redef]

    pydantic_v2 = None  # type: ignore[assignment]

if TYPE_CHECKING:
    from litestar._openapi.schema_generation.schema import SchemaCreator

PYDANTIC_TYPE_MAP: dict[type[Any] | None | Any, Schema] = {
    pydantic_v1.ByteSize: Schema(type=OpenAPIType.INTEGER),
    pydantic_v1.EmailStr: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.EMAIL),
    pydantic_v1.IPvAnyAddress: Schema(
        one_of=[
            Schema(
                type=OpenAPIType.STRING,
                format=OpenAPIFormat.IPV4,
                description="IPv4 address",
            ),
            Schema(
                type=OpenAPIType.STRING,
                format=OpenAPIFormat.IPV6,
                description="IPv6 address",
            ),
        ]
    ),
    pydantic_v1.IPvAnyInterface: Schema(
        one_of=[
            Schema(
                type=OpenAPIType.STRING,
                format=OpenAPIFormat.IPV4,
                description="IPv4 interface",
            ),
            Schema(
                type=OpenAPIType.STRING,
                format=OpenAPIFormat.IPV6,
                description="IPv6 interface",
            ),
        ]
    ),
    pydantic_v1.IPvAnyNetwork: Schema(
        one_of=[
            Schema(
                type=OpenAPIType.STRING,
                format=OpenAPIFormat.IPV4,
                description="IPv4 network",
            ),
            Schema(
                type=OpenAPIType.STRING,
                format=OpenAPIFormat.IPV6,
                description="IPv6 network",
            ),
        ]
    ),
    pydantic_v1.Json: Schema(type=OpenAPIType.OBJECT, format=OpenAPIFormat.JSON_POINTER),
    pydantic_v1.NameEmail: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.EMAIL, description="Name and email"),
    # removed in v2
    pydantic_v1.PyObject: Schema(
        type=OpenAPIType.STRING,
        description="dot separated path identifying a python object, e.g. 'decimal.Decimal'",
    ),
    # annotated in v2
    pydantic_v1.UUID1: Schema(
        type=OpenAPIType.STRING,
        format=OpenAPIFormat.UUID,
        description="UUID1 string",
    ),
    pydantic_v1.UUID3: Schema(
        type=OpenAPIType.STRING,
        format=OpenAPIFormat.UUID,
        description="UUID3 string",
    ),
    pydantic_v1.UUID4: Schema(
        type=OpenAPIType.STRING,
        format=OpenAPIFormat.UUID,
        description="UUID4 string",
    ),
    pydantic_v1.UUID5: Schema(
        type=OpenAPIType.STRING,
        format=OpenAPIFormat.UUID,
        description="UUID5 string",
    ),
    pydantic_v1.DirectoryPath: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.URI_REFERENCE),
    pydantic_v1.AnyUrl: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.URL),
    pydantic_v1.AnyHttpUrl: Schema(
        type=OpenAPIType.STRING, format=OpenAPIFormat.URL, description="must be a valid HTTP based URL"
    ),
    pydantic_v1.FilePath: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.URI_REFERENCE),
    pydantic_v1.HttpUrl: Schema(
        type=OpenAPIType.STRING,
        format=OpenAPIFormat.URL,
        description="must be a valid HTTP based URL",
        max_length=2083,
    ),
    pydantic_v1.RedisDsn: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.URI, description="redis DSN"),
    pydantic_v1.PostgresDsn: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.URI, description="postgres DSN"),
    pydantic_v1.SecretBytes: Schema(type=OpenAPIType.STRING),
    pydantic_v1.SecretStr: Schema(type=OpenAPIType.STRING),
    pydantic_v1.StrictBool: Schema(type=OpenAPIType.BOOLEAN),
    pydantic_v1.StrictBytes: Schema(type=OpenAPIType.STRING),
    pydantic_v1.StrictFloat: Schema(type=OpenAPIType.NUMBER),
    pydantic_v1.StrictInt: Schema(type=OpenAPIType.INTEGER),
    pydantic_v1.StrictStr: Schema(type=OpenAPIType.STRING),
    pydantic_v1.NegativeFloat: Schema(type=OpenAPIType.NUMBER, exclusive_maximum=0.0),
    pydantic_v1.NegativeInt: Schema(type=OpenAPIType.INTEGER, exclusive_maximum=0),
    pydantic_v1.NonNegativeInt: Schema(type=OpenAPIType.INTEGER, minimum=0),
    pydantic_v1.NonPositiveFloat: Schema(type=OpenAPIType.NUMBER, maximum=0.0),
    pydantic_v1.PaymentCardNumber: Schema(type=OpenAPIType.STRING, min_length=12, max_length=19),
    pydantic_v1.PositiveFloat: Schema(type=OpenAPIType.NUMBER, exclusive_minimum=0.0),
    pydantic_v1.PositiveInt: Schema(type=OpenAPIType.INTEGER, exclusive_minimum=0),
}

if pydantic_v2 is not None:  # pragma: no cover
    PYDANTIC_TYPE_MAP.update(
        {
            pydantic_v2.SecretStr: Schema(type=OpenAPIType.STRING),
            pydantic_v2.SecretBytes: Schema(type=OpenAPIType.STRING),
            pydantic_v2.ByteSize: Schema(type=OpenAPIType.INTEGER),
            pydantic_v2.EmailStr: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.EMAIL),
            pydantic_v2.IPvAnyAddress: Schema(
                one_of=[
                    Schema(
                        type=OpenAPIType.STRING,
                        format=OpenAPIFormat.IPV4,
                        description="IPv4 address",
                    ),
                    Schema(
                        type=OpenAPIType.STRING,
                        format=OpenAPIFormat.IPV6,
                        description="IPv6 address",
                    ),
                ]
            ),
            pydantic_v2.IPvAnyInterface: Schema(
                one_of=[
                    Schema(
                        type=OpenAPIType.STRING,
                        format=OpenAPIFormat.IPV4,
                        description="IPv4 interface",
                    ),
                    Schema(
                        type=OpenAPIType.STRING,
                        format=OpenAPIFormat.IPV6,
                        description="IPv6 interface",
                    ),
                ]
            ),
            pydantic_v2.IPvAnyNetwork: Schema(
                one_of=[
                    Schema(
                        type=OpenAPIType.STRING,
                        format=OpenAPIFormat.IPV4,
                        description="IPv4 network",
                    ),
                    Schema(
                        type=OpenAPIType.STRING,
                        format=OpenAPIFormat.IPV6,
                        description="IPv6 network",
                    ),
                ]
            ),
            pydantic_v2.Json: Schema(type=OpenAPIType.OBJECT, format=OpenAPIFormat.JSON_POINTER),
            pydantic_v2.NameEmail: Schema(
                type=OpenAPIType.STRING, format=OpenAPIFormat.EMAIL, description="Name and email"
            ),
            pydantic_v2.AnyUrl: Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.URL),
        }
    )


_supported_types = (pydantic_v1.BaseModel, *PYDANTIC_TYPE_MAP.keys())
if pydantic_v2 is not None:  # pragma: no cover
    _supported_types = (pydantic_v2.BaseModel, *_supported_types)


class PydanticSchemaPlugin(OpenAPISchemaPlugin):
    __slots__ = ("prefer_alias",)

    def __init__(self, prefer_alias: bool = False) -> None:
        self.prefer_alias = prefer_alias

    @staticmethod
    def is_plugin_supported_type(value: Any) -> bool:
        return isinstance(value, _supported_types) or is_class_and_subclass(value, _supported_types)  # type: ignore[arg-type]

    @staticmethod
    def is_undefined_sentinel(value: Any) -> bool:
        return is_pydantic_undefined(value)

    @staticmethod
    def is_constrained_field(field_definition: FieldDefinition) -> bool:
        return is_pydantic_constrained_field(field_definition.annotation)

    def to_openapi_schema(self, field_definition: FieldDefinition, schema_creator: SchemaCreator) -> Schema:
        """Given a type annotation, transform it into an OpenAPI schema class.

        Args:
            field_definition: FieldDefinition instance.
            schema_creator: An instance of the schema creator class

        Returns:
            An :class:`OpenAPI <litestar.openapi.spec.schema.Schema>` instance.
        """
        if schema_creator.prefer_alias != self.prefer_alias:
            schema_creator.prefer_alias = True
        if is_pydantic_model_class(field_definition.annotation):
            return self.for_pydantic_model(field_definition=field_definition, schema_creator=schema_creator)
        return PYDANTIC_TYPE_MAP[field_definition.annotation]  # pragma: no cover

    @classmethod
    def for_pydantic_model(cls, field_definition: FieldDefinition, schema_creator: SchemaCreator) -> Schema:  # pyright: ignore
        """Create a schema object for a given pydantic model class.

        Args:
            field_definition: FieldDefinition instance.
            schema_creator: An instance of the schema creator class

        Returns:
            A schema instance.
        """

        annotation = field_definition.annotation
        if is_generic(annotation):
            is_generic_model = True
            model = pydantic_unwrap_and_get_origin(annotation) or annotation
        else:
            is_generic_model = False
            model = annotation

        if is_pydantic_2_model(model):
            model_config = model.model_config
            model_field_info = model.model_fields
            title = model_config.get("title")
            example = model_config.get("example")
            is_v2_model = True
        else:
            model_config = annotation.__config__
            model_field_info = model.__fields__
            title = getattr(model_config, "title", None)
            example = getattr(model_config, "example", None)
            is_v2_model = False

        model_fields: dict[str, pydantic_v1.fields.FieldInfo | pydantic_v2.fields.FieldInfo] = {  # pyright: ignore
            k: getattr(f, "field_info", f) for k, f in model_field_info.items()
        }

        if is_v2_model:
            # extract the annotations from the FieldInfo. This allows us to skip fields
            # which have been marked as private
            model_annotations = {k: field_info.annotation for k, field_info in model_fields.items()}  # type: ignore[union-attr]

        else:
            # pydantic v1 requires some workarounds here
            model_annotations = {
                k: f.outer_type_ if f.required or f.default else Optional[f.outer_type_]
                for k, f in model.__fields__.items()
            }

        if is_generic_model:
            # if the model is generic, resolve the type variables. We pass in the
            # already extracted annotations, to keep the logic of respecting private
            # fields consistent with the above
            model_annotations = pydantic_get_type_hints_with_generics_resolved(
                annotation, model_annotations=model_annotations, include_extras=True
            )

        property_fields = {
            field_info.alias if field_info.alias and schema_creator.prefer_alias else k: FieldDefinition.from_kwarg(
                annotation=Annotated[model_annotations[k], field_info, field_info.metadata]  # type: ignore[union-attr]
                if is_v2_model
                else Annotated[model_annotations[k], field_info],  # pyright: ignore
                name=field_info.alias if field_info.alias and schema_creator.prefer_alias else k,
                default=Empty if schema_creator.is_undefined(field_info.default) else field_info.default,
            )
            for k, field_info in model_fields.items()
        }

        computed_field_definitions = create_field_definitions_for_computed_fields(
            annotation, schema_creator.prefer_alias
        )
        property_fields.update(computed_field_definitions)

        return schema_creator.create_component_schema(
            field_definition,
            required=sorted(f.name for f in property_fields.values() if f.is_required),
            property_fields=property_fields,
            title=title,
            examples=None if example is None else [example],
        )
