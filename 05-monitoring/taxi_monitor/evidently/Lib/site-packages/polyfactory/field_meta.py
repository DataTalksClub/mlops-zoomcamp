from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import TYPE_CHECKING, Any, Literal, Mapping, Pattern, TypedDict, cast

from typing_extensions import get_args, get_origin

from polyfactory.collection_extender import CollectionExtender
from polyfactory.constants import DEFAULT_RANDOM, TYPE_MAPPING
from polyfactory.utils.deprecation import check_for_deprecated_parameters
from polyfactory.utils.helpers import (
    get_annotation_metadata,
    unwrap_annotated,
    unwrap_new_type,
)
from polyfactory.utils.predicates import is_annotated
from polyfactory.utils.types import NoneType

if TYPE_CHECKING:
    import datetime
    from decimal import Decimal
    from random import Random
    from typing import Sequence

    from typing_extensions import NotRequired, Self


class Null:
    """Sentinel class for empty values"""


class UrlConstraints(TypedDict):
    max_length: NotRequired[int]
    allowed_schemes: NotRequired[list[str]]
    host_required: NotRequired[bool]
    default_host: NotRequired[str]
    default_port: NotRequired[int]
    default_path: NotRequired[str]


class Constraints(TypedDict):
    """Metadata regarding a type constraints, if any"""

    allow_inf_nan: NotRequired[bool]
    decimal_places: NotRequired[int]
    ge: NotRequired[int | float | Decimal]
    gt: NotRequired[int | float | Decimal]
    item_type: NotRequired[Any]
    le: NotRequired[int | float | Decimal]
    lower_case: NotRequired[bool]
    lt: NotRequired[int | float | Decimal]
    max_digits: NotRequired[int]
    max_length: NotRequired[int]
    min_length: NotRequired[int]
    multiple_of: NotRequired[int | float | Decimal]
    path_type: NotRequired[Literal["file", "dir", "new"]]
    pattern: NotRequired[str | Pattern]
    tz: NotRequired[datetime.tzinfo]
    unique_items: NotRequired[bool]
    upper_case: NotRequired[bool]
    url: NotRequired[UrlConstraints]
    uuid_version: NotRequired[Literal[1, 3, 4, 5]]


class FieldMeta:
    """Factory field metadata container. This class is used to store the data about a field of a factory's model."""

    __slots__ = ("name", "annotation", "random", "children", "default", "constraints")

    annotation: Any
    random: Random
    children: list[FieldMeta] | None
    default: Any
    name: str
    constraints: Constraints | None

    def __init__(
        self,
        *,
        name: str,
        annotation: type,
        random: Random | None = None,
        default: Any = Null,
        children: list[FieldMeta] | None = None,
        constraints: Constraints | None = None,
    ) -> None:
        """Create a factory field metadata instance."""
        self.annotation = annotation
        self.random = random or DEFAULT_RANDOM
        self.children = children
        self.default = default
        self.name = name
        self.constraints = constraints

    @property
    def type_args(self) -> tuple[Any, ...]:
        """Return the normalized type args of the annotation, if any.

        :returns: a tuple of types.
        """
        return tuple(TYPE_MAPPING.get(arg, arg) for arg in get_args(self.annotation))

    @classmethod
    def from_type(
        cls,
        annotation: Any,
        random: Random = DEFAULT_RANDOM,
        name: str = "",
        default: Any = Null,
        constraints: Constraints | None = None,
        randomize_collection_length: bool | None = None,
        min_collection_length: int | None = None,
        max_collection_length: int | None = None,
        children: list[FieldMeta] | None = None,
    ) -> Self:
        """Builder method to create a FieldMeta from a type annotation.

        :param annotation: A type annotation.
        :param random: An instance of random.Random.
        :param name: Field name
        :param default: Default value, if any.
        :param constraints: A dictionary of constraints, if any.
        :param randomize_collection_length: A boolean flag whether to randomize collections lengths
        :param min_collection_length: Minimum number of elements in randomized collection
        :param max_collection_length: Maximum number of elements in randomized collection

        :returns: A field meta instance.
        """
        check_for_deprecated_parameters(
            "2.11.0",
            parameters=(
                ("randomize_collection_length", randomize_collection_length),
                ("min_collection_length", min_collection_length),
                ("max_collection_length", max_collection_length),
            ),
        )

        annotated = is_annotated(annotation)
        if not constraints and annotated:
            metadata = cls.get_constraints_metadata(annotation)
            constraints = cls.parse_constraints(metadata)

        if annotated:
            annotation = get_args(annotation)[0]
        elif (origin := get_origin(annotation)) and origin in TYPE_MAPPING:  # pragma: no cover
            container = TYPE_MAPPING[origin]
            annotation = container[get_args(annotation)]  # type: ignore[index]

        field = cls(
            annotation=annotation,
            random=random,
            name=name,
            default=default,
            children=children,
            constraints=constraints,
        )

        if field.type_args and not field.children:
            number_of_args = 1
            extended_type_args = CollectionExtender.extend_type_args(field.annotation, field.type_args, number_of_args)
            field.children = [
                cls.from_type(
                    annotation=unwrap_new_type(arg),
                    random=random,
                )
                for arg in extended_type_args
                if arg is not NoneType
            ]
        return field

    @classmethod
    def parse_constraints(cls, metadata: Sequence[Any]) -> "Constraints":
        constraints = {}

        for value in metadata:
            if is_annotated(value):
                _, inner_metadata = unwrap_annotated(value, random=DEFAULT_RANDOM)
                constraints.update(cast("dict[str, Any]", cls.parse_constraints(metadata=inner_metadata)))
            elif func := getattr(value, "func", None):
                if func is str.islower:
                    constraints["lower_case"] = True
                elif func is str.isupper:
                    constraints["upper_case"] = True
                elif func is str.isascii:
                    constraints["pattern"] = "[[:ascii:]]"
                elif func is str.isdigit:
                    constraints["pattern"] = "[[:digit:]]"
            elif is_dataclass(value) and (value_dict := asdict(value)) and ("allowed_schemes" in value_dict):
                constraints["url"] = {k: v for k, v in value_dict.items() if v is not None}
            # This is to support `Constraints`, but we can't do a isinstance with `Constraints` since isinstance
            # checks with `TypedDict` is not supported.
            elif isinstance(value, Mapping):
                constraints.update(value)
            else:
                constraints.update(
                    {
                        k: v
                        for k, v in {
                            "allow_inf_nan": getattr(value, "allow_inf_nan", None),
                            "decimal_places": getattr(value, "decimal_places", None),
                            "ge": getattr(value, "ge", None),
                            "gt": getattr(value, "gt", None),
                            "item_type": getattr(value, "item_type", None),
                            "le": getattr(value, "le", None),
                            "lower_case": getattr(value, "to_lower", None),
                            "lt": getattr(value, "lt", None),
                            "max_digits": getattr(value, "max_digits", None),
                            "max_length": getattr(value, "max_length", getattr(value, "max_length", None)),
                            "min_length": getattr(value, "min_length", getattr(value, "min_items", None)),
                            "multiple_of": getattr(value, "multiple_of", None),
                            "path_type": getattr(value, "path_type", None),
                            "pattern": getattr(value, "regex", getattr(value, "pattern", None)),
                            "tz": getattr(value, "tz", None),
                            "unique_items": getattr(value, "unique_items", None),
                            "upper_case": getattr(value, "to_upper", None),
                            "uuid_version": getattr(value, "uuid_version", None),
                        }.items()
                        if v is not None
                    },
                )
        return cast("Constraints", constraints)

    @classmethod
    def get_constraints_metadata(cls, annotation: Any) -> Sequence[Any]:
        """Get the metadatas of the constraints from the given annotation.

        :param annotation: A type annotation.
        :param random: An instance of random.Random.

        :returns: A list of the metadata in the annotation.
        """

        return get_annotation_metadata(annotation)
