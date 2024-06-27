from __future__ import annotations

from contextlib import suppress
from datetime import timezone
from functools import partial
from os.path import realpath
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, ForwardRef, Generic, Mapping, Tuple, TypeVar, cast
from uuid import NAMESPACE_DNS, uuid1, uuid3, uuid5

from typing_extensions import Literal, get_args, get_origin

from polyfactory.collection_extender import CollectionExtender
from polyfactory.constants import DEFAULT_RANDOM
from polyfactory.exceptions import MissingDependencyException
from polyfactory.factories.base import BaseFactory
from polyfactory.field_meta import Constraints, FieldMeta, Null
from polyfactory.utils.deprecation import check_for_deprecated_parameters
from polyfactory.utils.helpers import unwrap_new_type, unwrap_optional
from polyfactory.utils.predicates import is_optional, is_safe_subclass, is_union
from polyfactory.utils.types import NoneType
from polyfactory.value_generators.primitives import create_random_bytes

try:
    import pydantic
    from pydantic import VERSION, Json
    from pydantic.fields import FieldInfo
except ImportError as e:
    msg = "pydantic is not installed"
    raise MissingDependencyException(msg) from e

try:
    # pydantic v1
    from pydantic import (  # noqa: I001
        UUID1,
        UUID3,
        UUID4,
        UUID5,
        AmqpDsn,
        AnyHttpUrl,
        AnyUrl,
        DirectoryPath,
        FilePath,
        HttpUrl,
        KafkaDsn,
        PostgresDsn,
        RedisDsn,
    )
    from pydantic import BaseModel as BaseModelV1
    from pydantic.color import Color
    from pydantic.fields import (  # type: ignore[attr-defined]
        DeferredType,  # pyright: ignore[reportGeneralTypeIssues]
        ModelField,  # pyright: ignore[reportGeneralTypeIssues]
        Undefined,  # pyright: ignore[reportGeneralTypeIssues]
    )

    # Keep this import last to prevent warnings from pydantic if pydantic v2
    # is installed.
    from pydantic import PyObject

    # prevent unbound variable warnings
    BaseModelV2 = BaseModelV1
    UndefinedV2 = Undefined
except ImportError:
    # pydantic v2

    # v2 specific imports
    from pydantic import BaseModel as BaseModelV2
    from pydantic_core import PydanticUndefined as UndefinedV2
    from pydantic_core import to_json

    from pydantic.v1 import (  # v1 compat imports
        UUID1,
        UUID3,
        UUID4,
        UUID5,
        AmqpDsn,
        AnyHttpUrl,
        AnyUrl,
        DirectoryPath,
        FilePath,
        HttpUrl,
        KafkaDsn,
        PostgresDsn,
        PyObject,
        RedisDsn,
    )
    from pydantic.v1 import BaseModel as BaseModelV1  # type: ignore[assignment]
    from pydantic.v1.color import Color  # type: ignore[assignment]
    from pydantic.v1.fields import DeferredType, ModelField, Undefined


if TYPE_CHECKING:
    from random import Random
    from typing import Callable, Sequence

    from typing_extensions import NotRequired, TypeGuard

T = TypeVar("T", bound="BaseModelV1 | BaseModelV2")

_IS_PYDANTIC_V1 = VERSION.startswith("1")


class PydanticConstraints(Constraints):
    """Metadata regarding a Pydantic type constraints, if any"""

    json: NotRequired[bool]


class PydanticFieldMeta(FieldMeta):
    """Field meta subclass capable of handling pydantic ModelFields"""

    def __init__(
        self,
        *,
        name: str,
        annotation: type,
        random: Random | None = None,
        default: Any = ...,
        children: list[FieldMeta] | None = None,
        constraints: PydanticConstraints | None = None,
    ) -> None:
        super().__init__(
            name=name,
            annotation=annotation,
            random=random,
            default=default,
            children=children,
            constraints=constraints,
        )

    @classmethod
    def from_field_info(
        cls,
        field_name: str,
        field_info: FieldInfo,
        use_alias: bool,
        random: Random | None,
        randomize_collection_length: bool | None = None,
        min_collection_length: int | None = None,
        max_collection_length: int | None = None,
    ) -> PydanticFieldMeta:
        """Create an instance from a pydantic field info.

        :param field_name: The name of the field.
        :param field_info: A pydantic FieldInfo instance.
        :param use_alias: Whether to use the field alias.
        :param random: A random.Random instance.
        :param randomize_collection_length: Whether to randomize collection length.
        :param min_collection_length: Minimum collection length.
        :param max_collection_length: Maximum collection length.

        :returns: A PydanticFieldMeta instance.
        """
        check_for_deprecated_parameters(
            "2.11.0",
            parameters=(
                ("randomize_collection_length", randomize_collection_length),
                ("min_collection_length", min_collection_length),
                ("max_collection_length", max_collection_length),
            ),
        )
        if callable(field_info.default_factory):
            default_value = field_info.default_factory()
        else:
            default_value = field_info.default if field_info.default is not UndefinedV2 else Null

        annotation = unwrap_new_type(field_info.annotation)
        children: list[FieldMeta,] | None = None
        name = field_info.alias if field_info.alias and use_alias else field_name

        constraints: PydanticConstraints
        # pydantic v2 does not always propagate metadata for Union types
        if is_union(annotation):
            constraints = {}
            children = []
            for arg in get_args(annotation):
                if arg is NoneType:
                    continue
                child_field_info = FieldInfo.from_annotation(arg)
                merged_field_info = FieldInfo.merge_field_infos(field_info, child_field_info)
                children.append(
                    cls.from_field_info(
                        field_name="",
                        field_info=merged_field_info,
                        use_alias=use_alias,
                        random=random,
                    ),
                )
        else:
            metadata, is_json = [], False
            for m in field_info.metadata:
                if not is_json and isinstance(m, Json):  # type: ignore[misc]
                    is_json = True
                elif m is not None:
                    metadata.append(m)

            constraints = cast(
                PydanticConstraints,
                cls.parse_constraints(metadata=metadata) if metadata else {},
            )

            if "url" in constraints:
                # pydantic uses a sentinel value for url constraints
                annotation = str

            if is_json:
                constraints["json"] = True

        return PydanticFieldMeta.from_type(
            annotation=annotation,
            children=children,
            constraints=cast("Constraints", {k: v for k, v in constraints.items() if v is not None}) or None,
            default=default_value,
            name=name,
            random=random or DEFAULT_RANDOM,
        )

    @classmethod
    def from_model_field(  # pragma: no cover
        cls,
        model_field: ModelField,  # pyright: ignore[reportGeneralTypeIssues]
        use_alias: bool,
        randomize_collection_length: bool | None = None,
        min_collection_length: int | None = None,
        max_collection_length: int | None = None,
        random: Random = DEFAULT_RANDOM,
    ) -> PydanticFieldMeta:
        """Create an instance from a pydantic model field.
        :param model_field: A pydantic ModelField.
        :param use_alias: Whether to use the field alias.
        :param randomize_collection_length: A boolean flag whether to randomize collections lengths
        :param min_collection_length: Minimum number of elements in randomized collection
        :param max_collection_length: Maximum number of elements in randomized collection
        :param random: An instance of random.Random.

        :returns: A PydanticFieldMeta instance.

        """
        check_for_deprecated_parameters(
            "2.11.0",
            parameters=(
                ("randomize_collection_length", randomize_collection_length),
                ("min_collection_length", min_collection_length),
                ("max_collection_length", max_collection_length),
            ),
        )

        if model_field.default is not Undefined:
            default_value = model_field.default
        elif callable(model_field.default_factory):
            default_value = model_field.default_factory()
        else:
            default_value = model_field.default if model_field.default is not Undefined else Null

        name = model_field.alias if model_field.alias and use_alias else model_field.name

        outer_type = unwrap_new_type(model_field.outer_type_)
        annotation = (
            model_field.outer_type_
            if isinstance(model_field.annotation, (DeferredType, ForwardRef))
            else unwrap_new_type(model_field.annotation)
        )

        constraints = cast(
            "Constraints",
            {
                "ge": getattr(outer_type, "ge", model_field.field_info.ge),
                "gt": getattr(outer_type, "gt", model_field.field_info.gt),
                "le": getattr(outer_type, "le", model_field.field_info.le),
                "lt": getattr(outer_type, "lt", model_field.field_info.lt),
                "min_length": (
                    getattr(outer_type, "min_length", model_field.field_info.min_length)
                    or getattr(outer_type, "min_items", model_field.field_info.min_items)
                ),
                "max_length": (
                    getattr(outer_type, "max_length", model_field.field_info.max_length)
                    or getattr(outer_type, "max_items", model_field.field_info.max_items)
                ),
                "pattern": getattr(outer_type, "regex", model_field.field_info.regex),
                "unique_items": getattr(outer_type, "unique_items", model_field.field_info.unique_items),
                "decimal_places": getattr(outer_type, "decimal_places", None),
                "max_digits": getattr(outer_type, "max_digits", None),
                "multiple_of": getattr(outer_type, "multiple_of", None),
                "upper_case": getattr(outer_type, "to_upper", None),
                "lower_case": getattr(outer_type, "to_lower", None),
                "item_type": getattr(outer_type, "item_type", None),
            },
        )

        # pydantic v1 has constraints set for these values, but we generate them using faker
        if unwrap_optional(annotation) in (
            AnyUrl,
            HttpUrl,
            KafkaDsn,
            PostgresDsn,
            RedisDsn,
            AmqpDsn,
            AnyHttpUrl,
        ):
            constraints = {}

        if model_field.field_info.const and (
            default_value is None or isinstance(default_value, (int, bool, str, bytes))
        ):
            annotation = Literal[default_value]  # pyright: ignore  # noqa: PGH003

        children: list[FieldMeta] = []

        # Refer #412.
        args = get_args(model_field.annotation)
        if is_optional(model_field.annotation) and len(args) == 2:  # noqa: PLR2004
            child_annotation = args[0] if args[0] is not NoneType else args[1]
            children.append(PydanticFieldMeta.from_type(child_annotation))
        elif model_field.key_field or model_field.sub_fields:
            fields_to_iterate = (
                ([model_field.key_field, *model_field.sub_fields])
                if model_field.key_field is not None
                else model_field.sub_fields
            )
            type_args = tuple(
                (
                    sub_field.outer_type_
                    if isinstance(sub_field.annotation, DeferredType)
                    else unwrap_new_type(sub_field.annotation)
                )
                for sub_field in fields_to_iterate
            )
            type_arg_to_sub_field = dict(zip(type_args, fields_to_iterate))
            if get_origin(outer_type) in (tuple, Tuple) and get_args(outer_type)[-1] == Ellipsis:
                # pydantic removes ellipses from Tuples in sub_fields
                type_args += (...,)
            extended_type_args = CollectionExtender.extend_type_args(annotation, type_args, 1)
            children.extend(
                PydanticFieldMeta.from_model_field(
                    model_field=type_arg_to_sub_field[arg],
                    use_alias=use_alias,
                    random=random,
                )
                for arg in extended_type_args
            )

        return PydanticFieldMeta(
            name=name,
            random=random or DEFAULT_RANDOM,
            annotation=annotation,
            children=children or None,
            default=default_value,
            constraints=cast("PydanticConstraints", {k: v for k, v in constraints.items() if v is not None}) or None,
        )

    if not _IS_PYDANTIC_V1:

        @classmethod
        def get_constraints_metadata(cls, annotation: Any) -> Sequence[Any]:
            metadata = []
            for m in super().get_constraints_metadata(annotation):
                if isinstance(m, FieldInfo):
                    metadata.extend(m.metadata)
                else:
                    metadata.append(m)

            return metadata


class ModelFactory(Generic[T], BaseFactory[T]):
    """Base factory for pydantic models"""

    __forward_ref_resolution_type_mapping__: ClassVar[Mapping[str, type]] = {}
    __is_base_factory__ = True

    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        super().__init_subclass__(*args, **kwargs)

        if (
            getattr(cls, "__model__", None)
            and _is_pydantic_v1_model(cls.__model__)
            and hasattr(cls.__model__, "update_forward_refs")
        ):
            with suppress(NameError):  # pragma: no cover
                cls.__model__.update_forward_refs(**cls.__forward_ref_resolution_type_mapping__)  # type: ignore[attr-defined]

    @classmethod
    def is_supported_type(cls, value: Any) -> TypeGuard[type[T]]:
        """Determine whether the given value is supported by the factory.

        :param value: An arbitrary value.
        :returns: A typeguard
        """

        return _is_pydantic_v1_model(value) or _is_pydantic_v2_model(value)

    @classmethod
    def get_model_fields(cls) -> list["FieldMeta"]:
        """Retrieve a list of fields from the factory's model.


        :returns: A list of field MetaData instances.

        """
        if "_fields_metadata" not in cls.__dict__:
            if _is_pydantic_v1_model(cls.__model__):
                cls._fields_metadata = [
                    PydanticFieldMeta.from_model_field(
                        field,
                        use_alias=not cls.__model__.__config__.allow_population_by_field_name,  # type: ignore[attr-defined]
                        random=cls.__random__,
                    )
                    for field in cls.__model__.__fields__.values()
                ]
            else:
                cls._fields_metadata = [
                    PydanticFieldMeta.from_field_info(
                        field_info=field_info,
                        field_name=field_name,
                        random=cls.__random__,
                        use_alias=not cls.__model__.model_config.get(  # pyright: ignore[reportGeneralTypeIssues]
                            "populate_by_name",
                            False,
                        ),
                    )
                    for field_name, field_info in cls.__model__.model_fields.items()  # pyright: ignore[reportGeneralTypeIssues]
                ]
        return cls._fields_metadata

    @classmethod
    def get_constrained_field_value(cls, annotation: Any, field_meta: FieldMeta) -> Any:
        constraints = cast(PydanticConstraints, field_meta.constraints)
        if constraints.pop("json", None):
            value = cls.get_field_value(field_meta)
            return to_json(value)  # pyright: ignore[reportUnboundVariable]

        return super().get_constrained_field_value(annotation, field_meta)

    @classmethod
    def build(
        cls,
        factory_use_construct: bool = False,
        **kwargs: Any,
    ) -> T:
        """Build an instance of the factory's __model__

        :param factory_use_construct: A boolean that determines whether validations will be made when instantiating the
                model. This is supported only for pydantic models.
        :param kwargs: Any kwargs. If field_meta names are set in kwargs, their values will be used.

        :returns: An instance of type T.

        """
        processed_kwargs = cls.process_kwargs(**kwargs)

        if factory_use_construct:
            if _is_pydantic_v1_model(cls.__model__):
                return cls.__model__.construct(**processed_kwargs)  # type: ignore[return-value]
            return cls.__model__.model_construct(**processed_kwargs)  # type: ignore[return-value]

        return cls.__model__(**processed_kwargs)  # type: ignore[return-value]

    @classmethod
    def is_custom_root_field(cls, field_meta: FieldMeta) -> bool:
        """Determine whether the field is a custom root field.

        :param field_meta: FieldMeta instance.

        :returns: A boolean determining whether the field is a custom root.

        """
        return field_meta.name == "__root__"

    @classmethod
    def should_set_field_value(cls, field_meta: FieldMeta, **kwargs: Any) -> bool:
        """Determine whether to set a value for a given field_name.
        This is an override of BaseFactory.should_set_field_value.

        :param field_meta: FieldMeta instance.
        :param kwargs: Any kwargs passed to the factory.

        :returns: A boolean determining whether a value should be set for the given field_meta.

        """
        return field_meta.name not in kwargs and (
            not field_meta.name.startswith("_") or cls.is_custom_root_field(field_meta)
        )

    @classmethod
    def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
        mapping: dict[Any, Callable[[], Any]] = {
            pydantic.ByteSize: cls.__faker__.pyint,
            pydantic.PositiveInt: cls.__faker__.pyint,
            pydantic.NegativeFloat: lambda: cls.__random__.uniform(-100, -1),
            pydantic.NegativeInt: lambda: cls.__faker__.pyint() * -1,
            pydantic.PositiveFloat: cls.__faker__.pyint,
            pydantic.NonPositiveFloat: lambda: cls.__random__.uniform(-100, 0),
            pydantic.NonNegativeInt: cls.__faker__.pyint,
            pydantic.StrictInt: cls.__faker__.pyint,
            pydantic.StrictBool: cls.__faker__.pybool,
            pydantic.StrictBytes: partial(create_random_bytes, cls.__random__),
            pydantic.StrictFloat: cls.__faker__.pyfloat,
            pydantic.StrictStr: cls.__faker__.pystr,
            pydantic.EmailStr: cls.__faker__.free_email,
            pydantic.NameEmail: cls.__faker__.free_email,
            pydantic.Json: cls.__faker__.json,
            pydantic.PaymentCardNumber: cls.__faker__.credit_card_number,
            pydantic.AnyUrl: cls.__faker__.url,
            pydantic.AnyHttpUrl: cls.__faker__.url,
            pydantic.HttpUrl: cls.__faker__.url,
            pydantic.SecretBytes: partial(create_random_bytes, cls.__random__),
            pydantic.SecretStr: cls.__faker__.pystr,
            pydantic.IPvAnyAddress: cls.__faker__.ipv4,
            pydantic.IPvAnyInterface: cls.__faker__.ipv4,
            pydantic.IPvAnyNetwork: lambda: cls.__faker__.ipv4(network=True),
            pydantic.PastDate: cls.__faker__.past_date,
            pydantic.FutureDate: cls.__faker__.future_date,
        }

        # v1 only values
        mapping.update(
            {
                PyObject: lambda: "decimal.Decimal",
                AmqpDsn: lambda: "amqps://example.com",
                KafkaDsn: lambda: "kafka://localhost:9092",
                PostgresDsn: lambda: "postgresql://user:secret@localhost",
                RedisDsn: lambda: "redis://localhost:6379/0",
                FilePath: lambda: Path(realpath(__file__)),
                DirectoryPath: lambda: Path(realpath(__file__)).parent,
                UUID1: uuid1,
                UUID3: lambda: uuid3(NAMESPACE_DNS, cls.__faker__.pystr()),
                UUID4: cls.__faker__.uuid4,
                UUID5: lambda: uuid5(NAMESPACE_DNS, cls.__faker__.pystr()),
                Color: cls.__faker__.hex_color,  # pyright: ignore[reportGeneralTypeIssues]
            },
        )

        if not _IS_PYDANTIC_V1:
            mapping.update(
                {
                    # pydantic v2 specific types
                    pydantic.PastDatetime: cls.__faker__.past_datetime,
                    pydantic.FutureDatetime: cls.__faker__.future_datetime,
                    pydantic.AwareDatetime: partial(cls.__faker__.date_time, timezone.utc),
                    pydantic.NaiveDatetime: cls.__faker__.date_time,
                },
            )

        mapping.update(super().get_provider_map())
        return mapping


def _is_pydantic_v1_model(model: Any) -> TypeGuard[BaseModelV1]:
    return is_safe_subclass(model, BaseModelV1)


def _is_pydantic_v2_model(model: Any) -> TypeGuard[BaseModelV2]:
    return not _IS_PYDANTIC_V1 and is_safe_subclass(model, BaseModelV2)
