from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Any, Hashable, Sequence

from litestar.enums import RequestEncodingType
from litestar.types import Empty

__all__ = (
    "Body",
    "BodyKwarg",
    "Dependency",
    "DependencyKwarg",
    "KwargDefinition",
    "Parameter",
    "ParameterKwarg",
)


if TYPE_CHECKING:
    from litestar.openapi.spec.example import Example
    from litestar.openapi.spec.external_documentation import (
        ExternalDocumentation,
    )


@dataclass(frozen=True)
class KwargDefinition:
    """Data container representing a constrained kwarg."""

    examples: list[Example] | None = field(default=None)
    """A list of Example models."""
    external_docs: ExternalDocumentation | None = field(default=None)
    """A url pointing at external documentation for the given parameter."""
    content_encoding: str | None = field(default=None)
    """The content encoding of the value.

    Applicable on to string values. See OpenAPI 3.1 for details.
    """
    default: Any = field(default=Empty)
    """A default value.

    If const is true, this value is required.
    """
    title: str | None = field(default=None)
    """String value used in the title section of the OpenAPI schema for the given parameter."""
    description: str | None = field(default=None)
    """String value used in the description section of the OpenAPI schema for the given parameter."""
    const: bool | None = field(default=None)
    """A boolean flag dictating whether this parameter is a constant.

    If True, the value passed to the parameter must equal its default value. This also causes the OpenAPI const field to
    be populated with the default value.
    """
    gt: float | None = field(default=None)
    """Constrict value to be greater than a given float or int.

    Equivalent to exclusiveMinimum in the OpenAPI specification.
    """
    ge: float | None = field(default=None)
    """Constrict value to be greater or equal to a given float or int.

    Equivalent to minimum in the OpenAPI specification.
    """
    lt: float | None = field(default=None)
    """Constrict value to be less than a given float or int.

    Equivalent to exclusiveMaximum in the OpenAPI specification.
    """
    le: float | None = field(default=None)
    """Constrict value to be less or equal to a given float or int.

    Equivalent to maximum in the OpenAPI specification.
    """
    multiple_of: float | None = field(default=None)
    """Constrict value to a multiple of a given float or int.

    Equivalent to multipleOf in the OpenAPI specification.
    """
    min_items: int | None = field(default=None)
    """Constrict a set or a list to have a minimum number of items.

    Equivalent to minItems in the OpenAPI specification.
    """
    max_items: int | None = field(default=None)
    """Constrict a set or a list to have a maximum number of items.

    Equivalent to maxItems in the OpenAPI specification.
    """
    min_length: int | None = field(default=None)
    """Constrict a string or bytes value to have a minimum length.

    Equivalent to minLength in the OpenAPI specification.
    """
    max_length: int | None = field(default=None)
    """Constrict a string or bytes value to have a maximum length.

    Equivalent to maxLength in the OpenAPI specification.
    """
    pattern: str | None = field(default=None)
    """A string representing a regex against which the given string will be matched.

    Equivalent to pattern in the OpenAPI specification.
    """
    lower_case: bool | None = field(default=None)
    """Constrict a string value to be lower case."""
    upper_case: bool | None = field(default=None)
    """Constrict a string value to be upper case."""
    format: str | None = field(default=None)
    """Specify the format to which a string value should be converted."""
    enum: Sequence[Any] | None = field(default=None)
    """A sequence of valid values."""
    read_only: bool | None = field(default=None)
    """A boolean flag dictating whether this parameter is read only."""
    schema_extra: dict[str, Any] | None = field(default=None)
    """Extensions to the generated schema.

    If set, will overwrite the matching fields in the generated schema.

    .. versionadded:: 2.8.0
    """

    @property
    def is_constrained(self) -> bool:
        """Return True if any of the constraints are set."""
        return any(
            attr if attr and attr is not Empty else False  # type: ignore[comparison-overlap]
            for attr in (
                self.gt,
                self.ge,
                self.lt,
                self.le,
                self.multiple_of,
                self.min_items,
                self.max_items,
                self.min_length,
                self.max_length,
                self.pattern,
                self.const,
                self.lower_case,
                self.upper_case,
            )
        )


@dataclass(frozen=True)
class ParameterKwarg(KwargDefinition):
    """Data container representing a parameter."""

    annotation: Any = field(default=Empty)
    """The field value - `Empty` by default."""
    header: str | None = field(default=None)
    """The header parameter key - required for header parameters."""
    cookie: str | None = field(default=None)
    """The cookie parameter key - required for cookie parameters."""
    query: str | None = field(default=None)
    """The query parameter key for this parameter."""
    required: bool | None = field(default=None)
    """A boolean flag dictating whether this parameter is required.

    If set to False, None values will be allowed. Defaults to True.
    """

    def __hash__(self) -> int:  # pragma: no cover
        """Hash the dataclass in a safe way.

        Returns:
            A hash
        """
        return sum(hash(v) for v in asdict(self) if isinstance(v, Hashable))


def Parameter(
    annotation: Any = Empty,
    *,
    const: bool | None = None,
    content_encoding: str | None = None,
    cookie: str | None = None,
    default: Any = Empty,
    description: str | None = None,
    examples: list[Example] | None = None,
    external_docs: ExternalDocumentation | None = None,
    ge: float | None = None,
    gt: float | None = None,
    header: str | None = None,
    le: float | None = None,
    lt: float | None = None,
    max_items: int | None = None,
    max_length: int | None = None,
    min_items: int | None = None,
    min_length: int | None = None,
    multiple_of: float | None = None,
    pattern: str | None = None,
    query: str | None = None,
    required: bool | None = None,
    title: str | None = None,
    schema_extra: dict[str, Any] | None = None,
) -> Any:
    """Create an extended parameter kwarg definition.

    Args:
        annotation: `Empty` by default.
        const: A boolean flag dictating whether this parameter is a constant. If True, the value passed to the parameter
            must equal its default value. This also causes the OpenAPI const field
            to be populated with the default value.
        content_encoding: The content encoding of the value.
            Applicable on to string values. See OpenAPI 3.1 for details.
        cookie: The cookie parameter key - required for cookie parameters.
        default: A default value. If const is true, this value is required.
        description: String value used in the description section of the OpenAPI schema for the given parameter.
        examples: A list of Example models.
        external_docs: A url pointing at external documentation for the given parameter.
        ge: Constrict value to be greater or equal to a given float or int.
            Equivalent to minimum in the OpenAPI specification.
        gt: Constrict value to be greater than a given float or int.
            Equivalent to exclusiveMinimum in the OpenAPI specification.
        header: The header parameter key - required for header parameters.
        le: Constrict value to be less or equal to a given float or int.
            Equivalent to maximum in the OpenAPI specification.
        lt: Constrict value to be less than a given float or int.
            Equivalent to exclusiveMaximum in the OpenAPI specification.
        max_items: Constrict a set or a list to have a maximum number of items.
            Equivalent to maxItems in the OpenAPI specification.
        max_length: Constrict a string or bytes value to have a maximum length.
            Equivalent to maxLength in the OpenAPI specification.
        min_items: Constrict a set or a list to have a minimum number of items. ֿ
            Equivalent to minItems in the OpenAPI specification.
        min_length: Constrict a string or bytes value to have a minimum length.
            Equivalent to minLength in the OpenAPI specification.
        multiple_of: Constrict value to a multiple of a given float or int.
            Equivalent to multipleOf in the OpenAPI specification.
        pattern: A string representing a regex against which the given string will be matched.
            Equivalent to pattern in the OpenAPI specification.
        query: The query parameter key for this parameter.
        required: A boolean flag dictating whether this parameter is required.
            If set to False, None values will be allowed. Defaults to True.
        title: String value used in the title section of the OpenAPI schema for the given parameter.
        schema_extra: Extensions to the generated schema. If set, will overwrite the matching fields in the generated
            schema.

            .. versionadded:: 2.8.0
    """
    return ParameterKwarg(
        annotation=annotation,
        header=header,
        cookie=cookie,
        query=query,
        examples=examples,
        external_docs=external_docs,
        content_encoding=content_encoding,
        required=required,
        default=default,
        title=title,
        description=description,
        const=const,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        min_items=min_items,
        max_items=max_items,
        min_length=min_length,
        max_length=max_length,
        pattern=pattern,
        schema_extra=schema_extra,
    )


@dataclass(frozen=True)
class BodyKwarg(KwargDefinition):
    """Data container representing a request body."""

    media_type: str | RequestEncodingType = field(default=RequestEncodingType.JSON)
    """Media-Type of the body."""

    multipart_form_part_limit: int | None = field(default=None)
    """The maximal number of allowed parts in a multipart/formdata request. This limit is intended to protect from DoS attacks."""

    def __hash__(self) -> int:  # pragma: no cover
        """Hash the dataclass in a safe way.

        Returns:
            A hash
        """
        return sum(hash(v) for v in asdict(self) if isinstance(v, Hashable))


def Body(
    *,
    const: bool | None = None,
    content_encoding: str | None = None,
    default: Any = Empty,
    description: str | None = None,
    examples: list[Example] | None = None,
    external_docs: ExternalDocumentation | None = None,
    ge: float | None = None,
    gt: float | None = None,
    le: float | None = None,
    lt: float | None = None,
    max_items: int | None = None,
    max_length: int | None = None,
    media_type: str | RequestEncodingType = RequestEncodingType.JSON,
    min_items: int | None = None,
    min_length: int | None = None,
    multipart_form_part_limit: int | None = None,
    multiple_of: float | None = None,
    pattern: str | None = None,
    title: str | None = None,
    schema_extra: dict[str, Any] | None = None,
) -> Any:
    """Create an extended request body kwarg definition.

    Args:
        const: A boolean flag dictating whether this parameter is a constant. If True, the value passed to the parameter
            must equal its default value. This also causes the OpenAPI const field to be
            populated with the default value.
        content_encoding: The content encoding of the value. Applicable on to string values.
            See OpenAPI 3.1 for details.
        default: A default value. If const is true, this value is required.
        description: String value used in the description section of the OpenAPI schema for the given parameter.
        examples: A list of Example models.
        external_docs: A url pointing at external documentation for the given parameter.
        ge: Constrict value to be greater or equal to a given float or int.
            Equivalent to minimum in the OpenAPI specification.
        gt: Constrict value to be greater than a given float or int.
            Equivalent to exclusiveMinimum in the OpenAPI specification.
        le: Constrict value to be less or equal to a given float or int.
            Equivalent to maximum in the OpenAPI specification.
        lt: Constrict value to be less than a given float or int.
            Equivalent to exclusiveMaximum in the OpenAPI specification.
        max_items: Constrict a set or a list to have a maximum number of items.
            Equivalent to maxItems in the OpenAPI specification.
        max_length: Constrict a string or bytes value to have a maximum length.
            Equivalent to maxLength in the OpenAPI specification.
        media_type: Defaults to RequestEncodingType.JSON.
        min_items: Constrict a set or a list to have a minimum number of items.
            Equivalent to minItems in the OpenAPI specification.
        min_length: Constrict a string or bytes value to have a minimum length.
            Equivalent to minLength in the OpenAPI specification.
        multipart_form_part_limit: The maximal number of allowed parts in a multipart/formdata request.
            This limit is intended to protect from DoS attacks.
        multiple_of: Constrict value to a multiple of a given float or int.
            Equivalent to multipleOf in the OpenAPI specification.
        pattern: A string representing a regex against which the given string will be matched.
            Equivalent to pattern in the OpenAPI specification.
        title: String value used in the title section of the OpenAPI schema for the given parameter.
        schema_extra: Extensions to the generated schema. If set, will overwrite the matching fields in the generated
            schema.

            .. versionadded:: 2.8.0
    """
    return BodyKwarg(
        media_type=media_type,
        examples=examples,
        external_docs=external_docs,
        content_encoding=content_encoding,
        default=default,
        title=title,
        description=description,
        const=const,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        min_items=min_items,
        max_items=max_items,
        min_length=min_length,
        max_length=max_length,
        pattern=pattern,
        multipart_form_part_limit=multipart_form_part_limit,
        schema_extra=schema_extra,
    )


@dataclass(frozen=True)
class DependencyKwarg:
    """Data container representing a dependency."""

    default: Any = field(default=Empty)
    """A default value."""
    skip_validation: bool = field(default=False)
    """Flag dictating whether to skip validation."""

    def __hash__(self) -> int:
        """Hash the dataclass in a safe way.

        Returns:
            A hash
        """
        return sum(hash(v) for v in asdict(self) if isinstance(v, Hashable))


def Dependency(*, default: Any = Empty, skip_validation: bool = False) -> Any:
    """Create a dependency kwarg definition.

    Args:
        default: A default value to use in case a dependency is not provided.
        skip_validation: If `True` provided dependency values are not validated by signature model.
    """
    return DependencyKwarg(default=default, skip_validation=skip_validation)
