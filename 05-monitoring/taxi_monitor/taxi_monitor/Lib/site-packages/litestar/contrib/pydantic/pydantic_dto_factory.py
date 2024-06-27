from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Any, Collection, Generic, TypeVar
from warnings import warn

from typing_extensions import Annotated, TypeAlias, override

from litestar.contrib.pydantic.utils import is_pydantic_undefined, is_pydantic_v2
from litestar.dto.base_dto import AbstractDTO
from litestar.dto.data_structures import DTOFieldDefinition
from litestar.dto.field import DTO_FIELD_META_KEY, extract_dto_field
from litestar.exceptions import MissingDependencyException, ValidationException
from litestar.types.empty import Empty
from litestar.typing import FieldDefinition

if TYPE_CHECKING:
    from typing import Generator

try:
    import pydantic as _  # noqa: F401
except ImportError as e:
    raise MissingDependencyException("pydantic") from e


try:
    import pydantic as pydantic_v2

    if not is_pydantic_v2(pydantic_v2):
        raise ImportError

    from pydantic import ValidationError as ValidationErrorV2
    from pydantic import v1 as pydantic_v1
    from pydantic.v1 import ValidationError as ValidationErrorV1

    ModelType: TypeAlias = "pydantic_v1.BaseModel | pydantic_v2.BaseModel"

except ImportError:
    import pydantic as pydantic_v1  # type: ignore[no-redef]

    pydantic_v2 = Empty  # type: ignore[assignment]
    from pydantic import ValidationError as ValidationErrorV1  # type: ignore[assignment]

    ValidationErrorV2 = ValidationErrorV1  # type: ignore[assignment, misc]
    ModelType = "pydantic_v1.BaseModel"  # type: ignore[misc]


T = TypeVar("T", bound="ModelType | Collection[ModelType]")


__all__ = ("PydanticDTO",)

_down_types: dict[Any, Any] = {
    pydantic_v1.EmailStr: str,
    pydantic_v1.IPvAnyAddress: str,
    pydantic_v1.IPvAnyInterface: str,
    pydantic_v1.IPvAnyNetwork: str,
}

if pydantic_v2 is not Empty:  # type: ignore[comparison-overlap]  # pragma: no cover
    _down_types.update(
        {
            pydantic_v2.JsonValue: Any,
            pydantic_v2.EmailStr: str,
            pydantic_v2.IPvAnyAddress: str,
            pydantic_v2.IPvAnyInterface: str,
            pydantic_v2.IPvAnyNetwork: str,
        }
    )


def convert_validation_error(validation_error: ValidationErrorV1 | ValidationErrorV2) -> list[dict[str, Any]]:
    error_list = validation_error.errors()
    for error in error_list:
        if isinstance(exception := error.get("ctx", {}).get("error"), Exception):
            error["ctx"]["error"] = type(exception).__name__
    return error_list  # type: ignore[return-value]


def downtype_for_data_transfer(field_definition: FieldDefinition) -> FieldDefinition:
    if sub := _down_types.get(field_definition.annotation):
        return FieldDefinition.from_kwarg(
            annotation=Annotated[sub, field_definition.metadata], name=field_definition.name
        )
    return field_definition


class PydanticDTO(AbstractDTO[T], Generic[T]):
    """Support for domain modelling with Pydantic."""

    @override
    def decode_builtins(self, value: dict[str, Any]) -> Any:
        try:
            return super().decode_builtins(value)
        except (ValidationErrorV2, ValidationErrorV1) as ex:
            raise ValidationException(extra=convert_validation_error(ex)) from ex

    @override
    def decode_bytes(self, value: bytes) -> Any:
        try:
            return super().decode_bytes(value)
        except (ValidationErrorV2, ValidationErrorV1) as ex:
            raise ValidationException(extra=convert_validation_error(ex)) from ex

    @classmethod
    def generate_field_definitions(
        cls, model_type: type[pydantic_v1.BaseModel | pydantic_v2.BaseModel]
    ) -> Generator[DTOFieldDefinition, None, None]:
        model_field_definitions = cls.get_model_type_hints(model_type)

        model_fields: dict[str, pydantic_v1.fields.FieldInfo | pydantic_v2.fields.FieldInfo]
        try:
            model_fields = dict(model_type.model_fields)  # type: ignore[union-attr]
        except AttributeError:
            model_fields = {
                k: model_field.field_info
                for k, model_field in model_type.__fields__.items()  # type: ignore[union-attr]
            }

        for field_name, field_info in model_fields.items():
            field_definition = downtype_for_data_transfer(model_field_definitions[field_name])
            dto_field = extract_dto_field(field_definition, field_definition.extra)

            try:
                extra = field_info.extra  # type: ignore[union-attr]
            except AttributeError:
                extra = field_info.json_schema_extra  # type: ignore[union-attr]

            if extra is not None and extra.pop(DTO_FIELD_META_KEY, None):
                warn(
                    message="Declaring 'DTOField' via Pydantic's 'Field.extra' is deprecated. "
                    "Use 'Annotated', e.g., 'Annotated[str, DTOField(mark='read-only')]' instead. "
                    "Support for 'DTOField' in 'Field.extra' will be removed in v3.",
                    category=DeprecationWarning,
                    stacklevel=2,
                )

            if not is_pydantic_undefined(field_info.default):
                default = field_info.default
            elif field_definition.is_optional:
                default = None
            else:
                default = Empty

            yield replace(
                DTOFieldDefinition.from_field_definition(
                    field_definition=field_definition,
                    dto_field=dto_field,
                    model_name=model_type.__name__,
                    default_factory=field_info.default_factory
                    if field_info.default_factory and not is_pydantic_undefined(field_info.default_factory)
                    else None,
                ),
                default=default,
                name=field_name,
            )

    @classmethod
    def detect_nested_field(cls, field_definition: FieldDefinition) -> bool:
        if pydantic_v2 is not Empty:  # type: ignore[comparison-overlap]
            return field_definition.is_subclass_of((pydantic_v1.BaseModel, pydantic_v2.BaseModel))
        return field_definition.is_subclass_of(pydantic_v1.BaseModel)  # type: ignore[unreachable]
