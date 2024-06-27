from __future__ import annotations

from dataclasses import Field, dataclass
from typing import TYPE_CHECKING, Any, Iterator, Literal

from typing_extensions import override

from litestar.openapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar.openapi.spec.example import Example
    from litestar.openapi.spec.media_type import OpenAPIMediaType
    from litestar.openapi.spec.reference import Reference
    from litestar.openapi.spec.schema import Schema

__all__ = ("OpenAPIHeader",)


@dataclass
class OpenAPIHeader(BaseSchemaObject):
    """The Header Object follows the structure of the [Parameter
    Object](https://spec.openapis.org/oas/v3.1.0#parameterObject) with the
    following changes:

    1. ``name`` MUST NOT be specified, it is given in the corresponding ``headers`` map.
    2. ``in`` MUST NOT be specified, it is implicitly in ``header``.
    3. All traits that are affected by the location MUST be applicable to a location of ``header``
       (for example, `style <https://spec.openapis.org/oas/v3.1.0#parameterStyle>`__).
    """

    schema: Schema | Reference | None = None
    """The schema defining the type used for the parameter."""

    name: Literal[""] = ""
    """MUST NOT be specified, it is given in the corresponding ``headers`` map."""

    param_in: Literal["header"] = "header"
    """MUST NOT be specified, it is implicitly in ``header``."""

    description: str | None = None
    """A brief description of the parameter. This could contain examples of
    use.

    `CommonMark syntax <https://spec.commonmark.org/>`_ MAY be used for rich text representation.
    """

    required: bool = False
    """Determines whether this parameter is mandatory.

    If the `parameter location <https://spec.openapis.org/oas/v3.1.0#parameterIn>`_ is ``"path"``, this property is
    **REQUIRED** and its value MUST be ``True``. Otherwise, the property MAY be included and its default value is
    ``False``.
    """

    deprecated: bool = False
    """Specifies that a parameter is deprecated and SHOULD be transitioned out of usage. Default value is ``False``."""

    allow_empty_value: bool = False
    """Sets the ability to pass empty-valued parameters. This is valid only for ``query`` parameters and allows sending
    a parameter with an empty value. Default value is ``False``. If
    `style <https://spec.openapis.org/oas/v3.1.0#parameterStyle>`__ is used, and if behavior is ``n/a`` (cannot be
    serialized), the value of ``allowEmptyValue`` SHALL be ignored. Use of this property is NOT RECOMMENDED, as it is
    likely to be removed in a later revision.

    The rules for serialization of the parameter are specified in one of two ways.For simpler scenarios, a
    `schema <https://spec.openapis.org/oas/v3.1.0#parameterSchema>`_ and
    `style <https://spec.openapis.org/oas/v3.1.0#parameterStyle>`__ can describe the structure and syntax of the
    parameter.
    """

    style: str | None = None
    """Describes how the parameter value will be serialized depending on the
    type of the parameter value. Default values (based on value of ``in``):

    - for ``query`` - ``form``;
    - for ``path`` - ``simple``;
    - for ``header`` - ``simple``;
    - for ``cookie`` - ``form``.
    """

    explode: bool | None = None
    """When this is true, parameter values of type ``array`` or ``object`` generate separate parameters for each value
    of the array or key-value pair of the map.

    For other types of parameters this property has no effect.When
    `style <https://spec.openapis.org/oas/v3.1.0#parameterStyle>`__ is ``form``, the default value is ``True``. For all
    other styles, the default value is ``False``.
    """

    allow_reserved: bool = False
    """Determines whether the parameter value SHOULD allow reserved characters, as defined by. :rfc:`3986`
    (``:/?#[]@!$&'()*+,;=``) to be included without percent-encoding.

    This property only applies to parameters with an ``in`` value of ``query``. The default value is ``False``.
    """

    example: Any | None = None
    """Example of the parameter's potential value.

    The example SHOULD match the specified schema and encoding properties if present. The ``example`` field is mutually
    exclusive of the ``examples`` field. Furthermore, if referencing a ``schema`` that contains an example, the
    ``example`` value SHALL _override_ the example provided by the schema. To represent examples of media types that
    cannot naturally be represented in JSON or YAML, a string value can contain the example with escaping where
    necessary.
    """

    examples: dict[str, Example | Reference] | None = None
    """Examples of the parameter's potential value. Each example SHOULD contain a value in the correct format as
    specified in the parameter encoding. The ``examples`` field is mutually exclusive of the ``example`` field.
    Furthermore, if referencing a ``schema`` that contains an example, the ``examples`` value SHALL _override_ the
    example provided by the schema.

    For more complex scenarios, the `content <https://spec.openapis.org/oas/v3.1.0#parameterContent>`_ property can
    define the media type and schema of the parameter. A parameter MUST contain either a ``schema`` property, or a
    ``content`` property, but not both. When ``example`` or ``examples`` are provided in conjunction with the ``schema``
    object, the example MUST follow the prescribed serialization strategy for the parameter.
    """

    content: dict[str, OpenAPIMediaType] | None = None
    """A map containing the representations for the parameter.

    The key is the media type and the value describes it. The map MUST only contain one entry.
    """

    @override
    def _iter_fields(self) -> Iterator[Field[Any]]:
        yield from (f for f in super()._iter_fields() if f.name not in {"name", "param_in"})
