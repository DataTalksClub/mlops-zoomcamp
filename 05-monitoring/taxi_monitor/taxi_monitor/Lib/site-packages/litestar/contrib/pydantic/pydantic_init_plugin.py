from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, Any, Callable, TypeVar, cast
from uuid import UUID

from msgspec import ValidationError
from typing_extensions import Buffer, TypeGuard

from litestar._signature.types import ExtendedMsgSpecValidationError
from litestar.contrib.pydantic.utils import is_pydantic_constrained_field, is_pydantic_v2
from litestar.exceptions import MissingDependencyException
from litestar.plugins import InitPluginProtocol
from litestar.typing import _KWARG_META_EXTRACTORS
from litestar.utils import is_class_and_subclass

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
    from litestar.config.app import AppConfig


T = TypeVar("T")


def _dec_pydantic_v1(model_type: type[pydantic_v1.BaseModel], value: Any) -> pydantic_v1.BaseModel:
    try:
        return model_type.parse_obj(value)
    except pydantic_v1.ValidationError as e:
        raise ExtendedMsgSpecValidationError(errors=cast("list[dict[str, Any]]", e.errors())) from e


def _dec_pydantic_v2(model_type: type[pydantic_v2.BaseModel], value: Any) -> pydantic_v2.BaseModel:
    try:
        return model_type.model_validate(value, strict=False)
    except pydantic_v2.ValidationError as e:
        raise ExtendedMsgSpecValidationError(errors=cast("list[dict[str, Any]]", e.errors())) from e


def _dec_pydantic_uuid(
    uuid_type: type[pydantic_v1.UUID1] | type[pydantic_v1.UUID3] | type[pydantic_v1.UUID4] | type[pydantic_v1.UUID5],
    value: Any,
) -> (
    type[pydantic_v1.UUID1] | type[pydantic_v1.UUID3] | type[pydantic_v1.UUID4] | type[pydantic_v1.UUID5]
):  # pragma: no cover
    if isinstance(value, str):
        value = uuid_type(value)

    elif isinstance(value, Buffer):
        value = bytes(value)
        try:
            value = uuid_type(value.decode())
        except ValueError:
            # 16 bytes in big-endian order as the bytes argument fail
            # the above check
            value = uuid_type(bytes=value)
    elif isinstance(value, UUID):
        value = uuid_type(str(value))

    if not isinstance(value, uuid_type):
        raise ValidationError(f"Invalid UUID: {value!r}")

    if value._required_version != value.version:
        raise ValidationError(f"Invalid UUID version: {value!r}")

    return cast(
        "type[pydantic_v1.UUID1] | type[pydantic_v1.UUID3] | type[pydantic_v1.UUID4] | type[pydantic_v1.UUID5]", value
    )


def _is_pydantic_v1_uuid(value: Any) -> bool:  # pragma: no cover
    return is_class_and_subclass(value, (pydantic_v1.UUID1, pydantic_v1.UUID3, pydantic_v1.UUID4, pydantic_v1.UUID5))


_base_encoders: dict[Any, Callable[[Any], Any]] = {
    pydantic_v1.EmailStr: str,
    pydantic_v1.NameEmail: str,
    pydantic_v1.ByteSize: lambda val: val.real,
}

if pydantic_v2 is not None:  # pragma: no cover
    _base_encoders.update(
        {
            pydantic_v2.EmailStr: str,
            pydantic_v2.NameEmail: str,
            pydantic_v2.ByteSize: lambda val: val.real,
        }
    )


def is_pydantic_v1_model_class(annotation: Any) -> TypeGuard[type[pydantic_v1.BaseModel]]:
    return is_class_and_subclass(annotation, pydantic_v1.BaseModel)


def is_pydantic_v2_model_class(annotation: Any) -> TypeGuard[type[pydantic_v2.BaseModel]]:
    return is_class_and_subclass(annotation, pydantic_v2.BaseModel)


class ConstrainedFieldMetaExtractor:
    @staticmethod
    def matches(annotation: Any, name: str | None, default: Any) -> bool:
        return is_pydantic_constrained_field(annotation)

    @staticmethod
    def extract(annotation: Any, default: Any) -> Any:
        return [annotation]


class PydanticInitPlugin(InitPluginProtocol):
    __slots__ = ("prefer_alias",)

    def __init__(self, prefer_alias: bool = False) -> None:
        self.prefer_alias = prefer_alias

    @classmethod
    def encoders(cls, prefer_alias: bool = False) -> dict[Any, Callable[[Any], Any]]:
        encoders = {**_base_encoders, **cls._create_pydantic_v1_encoders(prefer_alias)}
        if pydantic_v2 is not None:  # pragma: no cover
            encoders.update(cls._create_pydantic_v2_encoders(prefer_alias))
        return encoders

    @classmethod
    def decoders(cls) -> list[tuple[Callable[[Any], bool], Callable[[Any, Any], Any]]]:
        decoders: list[tuple[Callable[[Any], bool], Callable[[Any, Any], Any]]] = [
            (is_pydantic_v1_model_class, _dec_pydantic_v1)
        ]

        if pydantic_v2 is not None:  # pragma: no cover
            decoders.append((is_pydantic_v2_model_class, _dec_pydantic_v2))

        decoders.append((_is_pydantic_v1_uuid, _dec_pydantic_uuid))

        return decoders

    @staticmethod
    def _create_pydantic_v1_encoders(prefer_alias: bool = False) -> dict[Any, Callable[[Any], Any]]:  # pragma: no cover
        return {
            pydantic_v1.BaseModel: lambda model: {
                k: v.decode() if isinstance(v, bytes) else v for k, v in model.dict(by_alias=prefer_alias).items()
            },
            pydantic_v1.SecretField: str,
            pydantic_v1.StrictBool: int,
            pydantic_v1.color.Color: str,
            pydantic_v1.ConstrainedBytes: lambda val: val.decode("utf-8"),
            pydantic_v1.ConstrainedDate: lambda val: val.isoformat(),
            pydantic_v1.AnyUrl: str,
        }

    @staticmethod
    def _create_pydantic_v2_encoders(prefer_alias: bool = False) -> dict[Any, Callable[[Any], Any]]:
        encoders: dict[Any, Callable[[Any], Any]] = {
            pydantic_v2.BaseModel: lambda model: model.model_dump(mode="json", by_alias=prefer_alias),
            pydantic_v2.types.SecretStr: lambda val: "**********" if val else "",
            pydantic_v2.types.SecretBytes: lambda val: "**********" if val else "",
            pydantic_v2.AnyUrl: str,
        }

        with suppress(ImportError):
            from pydantic_extra_types import color

            encoders[color.Color] = str

        return encoders

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        app_config.type_encoders = {**self.encoders(self.prefer_alias), **(app_config.type_encoders or {})}
        app_config.type_decoders = [*self.decoders(), *(app_config.type_decoders or [])]

        _KWARG_META_EXTRACTORS.add(ConstrainedFieldMetaExtractor)
        return app_config
