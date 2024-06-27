from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import TYPE_CHECKING, Any, Hashable, Mapping, Sequence

from litestar.openapi.spec.base import BaseSchemaObject
from litestar.utils.predicates import is_non_string_sequence

if TYPE_CHECKING:
    from litestar.openapi.spec.discriminator import Discriminator
    from litestar.openapi.spec.enums import OpenAPIFormat, OpenAPIType
    from litestar.openapi.spec.external_documentation import ExternalDocumentation
    from litestar.openapi.spec.reference import Reference
    from litestar.openapi.spec.xml import XML
    from litestar.types import DataclassProtocol

__all__ = ("Schema", "SchemaDataContainer")


def _recursive_hash(value: Hashable | Sequence | Mapping | DataclassProtocol | type[DataclassProtocol]) -> int:
    if isinstance(value, Mapping):
        hash_value = 0
        for k, v in value.items():
            if k != "examples":
                hash_value += hash(k)
                hash_value += _recursive_hash(v)
        return hash_value
    if is_dataclass(value):
        hash_value = hash(type(value).__name__)
        for field in fields(value):
            if field.name != "examples":
                hash_value += hash(field.name)
                hash_value += _recursive_hash(getattr(value, field.name, None))
        return hash_value
    if is_non_string_sequence(value):
        return sum(_recursive_hash(v) for v in value)
    return hash(value) if isinstance(value, Hashable) else 0


@dataclass
class Schema(BaseSchemaObject):
    """The Schema Object allows the definition of input and output data types. These types can be objects, but also
    primitives and arrays. This object is a superset of the
    `JSON Schema Specification Draft 2020-12 <https://tools.ietf.org/html/draft-bhutton-json-schema-00>`_.

    For more information about the properties, see
    `JSON Schema Core <https://tools.ietf.org/html/draft-wright-json-schema-00>`_ and
    `JSON Schema Validation <https://tools.ietf.org/html/draft-wright-json-schema-validation-00>`_.

    Unless stated otherwise, the property definitions follow those of JSON Schema and do not add any additional
    semantics. Where JSON Schema indicates that behavior is defined by the application (e.g. for annotations), OAS also
    defers the definition of semantics to the application consuming the OpenAPI document.

    The following properties are taken directly from the
    `JSON Schema Core <https://tools.ietf.org/html/draft-wright-json-schema-00>`_ and follow the same specifications.
    """

    all_of: Sequence[Reference | Schema] | None = None
    """This keyword's value MUST be a non-empty array.  Each item of the array MUST be a valid JSON Schema.

    An instance validates successfully against this keyword if it validates successfully against all schemas defined by
    this keyword's value.
    """

    any_of: Sequence[Reference | Schema] | None = None
    """This keyword's value MUST be a non-empty array. Each item of the array MUST be a valid JSON Schema.

    An instance validates successfully against this keyword if it validates successfully against at least one schema
    defined by this keyword's value.  Note that when annotations are being collected, all subschemas MUST be examined so
    that annotations are collected from each subschema that validates successfully.
    """

    one_of: Sequence[Reference | Schema] | None = None
    """This keyword's value MUST be a non-empty array.  Each item of the array MUST be a valid JSON Schema.

    An instance validates successfully against this keyword if it validates successfully against exactly one schema
    defined by this keyword's value.
    """

    schema_not: Reference | Schema | None = None
    """This keyword's value MUST be a valid JSON Schema.

    An instance is valid against this keyword if it fails to validate successfully against the schema defined by this
    keyword.
    """

    schema_if: Reference | Schema | None = None
    """This keyword's value MUST be a valid JSON Schema.

    This validation outcome of this keyword's subschema has no direct effect on the overall validation result. Rather,
    it controls which of the "then" or "else" keywords are evaluated.

    Instances that successfully validate against this keyword's subschema MUST also be valid against the subschema
    value of the "then" keyword, if present.

    Instances that fail to validate against this keyword's subschema MUST also be valid against the subschema value of
    the "else" keyword, if present.

    If annotations (Section 7.7) are being collected, they are collected rom this keyword's subschema in the usual way,
    including when the keyword is present without either "then" or "else".
    """

    then: Reference | Schema | None = None
    """This keyword's value MUST be a valid JSON Schema.

    When "if" is present, and the instance successfully validates against its subschema, then validation succeeds
    against this keyword if the instance also successfully validates against this keyword's subschema.

    This keyword has no effect when "if" is absent, or when the instance fails to validate against its subschema.
    Implementations MUST NOT evaluate the instance against this keyword, for either validation or annotation collection
    purposes, in such cases.
    """

    schema_else: Reference | Schema | None = None
    """This keyword's value MUST be a valid JSON Schema.

    When "if" is present, and the instance fails to validate against its subschema, then validation succeeds against
    this keyword if the instance successfully validates against this keyword's subschema.

    This keyword has no effect when "if" is absent, or when the instance successfully validates against its subschema.
    Implementations MUST NOT evaluate the instance against this keyword, for either validation or annotation collection
    purposes, in such cases.
    """

    dependent_schemas: dict[str, Reference | Schema] | None = None
    """This keyword specifies subschemas that are evaluated if the instance is
    an object and contains a certain property.

    This keyword's value MUST be an object.  Each value in the object MUST be a valid JSON Schema.

    If the object key is a property in the instance, the entire instance must validate against the subschema. Its use is
    dependent on the presence of the property.

    Omitting this keyword has the same behavior as an empty object.
    """

    prefix_items: Sequence[Reference | Schema] | None = None
    """The value of "prefixItems" MUST be a non-empty array of valid JSON Schemas.

    Validation succeeds if each element of the instance validates against the schema at the same position, if any.
    This keyword does not constrain the length of the array.  If the array is longer than this keyword's value, this
    keyword validates only the prefix of matching length.

    This keyword produces an annotation value which is the largest index to which this keyword applied a subschema.
    he value MAY be a boolean true if a subschema was applied to every index of the instance, such as is produced by the
    "items" keyword.  This annotation affects the behavior of "items" and "unevaluatedItems".

    Omitting this keyword has the same assertion behavior as an empty array.
    """

    items: Reference | Schema | None = None
    """The value of "items" MUST be a valid JSON Schema.

    This keyword applies its subschema to all instance elements at indexes greater than the length of the "prefixItems"
    array in the same schema object, as reported by the annotation result of that "prefixItems" keyword.  If no such
    annotation result exists, "items" applies its subschema to all instance array elements.  [[CREF11: Note that the
    behavior of "items" without "prefixItems" is identical to that of the schema form of "items" in prior drafts. When
    "prefixItems" is present, the behavior of "items" is identical to the former "additionalItems" keyword.  ]]

    If the "items" subschema is applied to any positions within the instance array, it produces an annotation result of
    boolean true, indicating that all remaining array elements have been evaluated against this keyword's subschema.

    Omitting this keyword has the same assertion behavior as an empty schema.

    Implementations MAY choose to implement or optimize this keyword in another way that produces the same effect, such
    as by directly checking for the presence and size of a "prefixItems" array. Implementations that do not support
    annotation collection MUST do so.
    """

    contains: Reference | Schema | None = None
    """The value of this keyword MUST be a valid JSON Schema.

    An array instance is valid against "contains" if at least one of its elements is valid against the given schema.
    The subschema MUST be applied to every array element even after the first match has been found, in order to collect
    annotations for use by other keywords. This is to ensure that all possible annotations are collected.

    Logically, the validation result of applying the value subschema to each item in the array MUST be ORed with
    "false", resulting in an overall validation result.

    This keyword produces an annotation value which is an array of the indexes to which this keyword validates
    successfully when applying its subschema, in ascending order.  The value MAY be a boolean "true" if the subschema
    validates successfully when applied to every index of the instance.  The annotation MUST be present if the instance
    array to which this keyword's schema applies is empty.
    """

    properties: dict[str, Reference | Schema] | None = None
    """The value of "properties" MUST be an object.  Each value of this object MUST be a valid JSON Schema.

    Validation succeeds if, for each name that appears in both the instance and as a name within this keyword's value,
    the child instance for that name successfully validates against the corresponding schema.

    The annotation result of this keyword is the set of instance property names matched by this keyword.

    Omitting this keyword has the same assertion behavior as an empty object.
    """

    pattern_properties: dict[str, Reference | Schema] | None = None
    """The value of "patternProperties" MUST be an object.  Each property name of this object SHOULD be a valid
    regular expression, according to the ECMA-262 regular expression dialect.  Each property value of this object
    MUST be a valid JSON Schema.

    Validation succeeds if, for each instance name that matches any regular expressions that appear as a property name
    in this keyword's value, the child instance for that name successfully validates against each schema that
    corresponds to a matching regular expression.

    The annotation result of this keyword is the set of instance property names matched by this keyword.

    Omitting this keyword has the same assertion behavior as an empty object.
    """

    additional_properties: Reference | Schema | bool | None = None
    """The value of "additionalProperties" MUST be a valid JSON Schema.

    The behavior of this keyword depends on the presence and annotation results of "properties" and "patternProperties"
    within the same schema object.  Validation with "additionalProperties" applies only to the child values of instance
    names that do not appear in the annotation results of either "properties" or "patternProperties".

    For all such properties, validation succeeds if the child instance validates against the "additionalProperties"
    schema.

    The annotation result of this keyword is the set of instance property names validated by this keyword's subschema.

    Omitting this keyword has the same assertion behavior as an empty schema.

    Implementations MAY choose to implement or optimize this keyword in another way that produces the same effect, such
    as by directly checking the names in "properties" and the patterns in "patternProperties" against the instance
    property set. Implementations that do not support annotation collection MUST do so.
    """

    property_names: Reference | Schema | None = None
    """The value of "propertyNames" MUST be a valid JSON Schema.

    If the instance is an object, this keyword validates if every property name in the instance validates against the
    provided schema. Note the property name that the schema is testing will always be a string.

    Omitting this keyword has the same behavior as an empty schema.
    """

    unevaluated_items: Reference | Schema | None = None
    """The value of "unevaluatedItems" MUST be a valid JSON Schema.

    The behavior of this keyword depends on the annotation results of adjacent keywords that apply to the instance
    location being validated.  Specifically, the annotations from "prefixItems" items", and "contains", which can come
    from those keywords when they are adjacent to the "unevaluatedItems" keyword.  Those three annotations, as well as
    "unevaluatedItems", can also result from any and all adjacent in-place applicator (Section 10.2) keywords.  This
    includes but is not limited to the in-place applicators defined in this document.

    If no relevant annotations are present, the "unevaluatedItems" subschema MUST be applied to all locations in the
    array. If a boolean true value is present from any of the relevant annotations, unevaluatedItems" MUST be ignored.
    Otherwise, the subschema MUST be applied to any index greater than the largest annotation value for "prefixItems",
    which does not appear in any annotation value for
    "contains".

    This means that "prefixItems", "items", "contains", and all in-place applicators MUST be evaluated before this
    keyword can be evaluated. Authors of extension keywords MUST NOT define an in-place applicator that would need to be
    evaluated after this keyword.

    If the "unevaluatedItems" subschema is applied to any positions within the instance array, it produces an annotation
    result of boolean true, analogous to the behavior of "items".

    Omitting this keyword has the same assertion behavior as an empty schema.
    """

    unevaluated_properties: Reference | Schema | None = None
    """The value of "unevaluatedProperties" MUST be a valid JSON Schema.

    The behavior of this keyword depends on the annotation results of adjacent keywords that apply to the instance
    location being validated.  Specifically, the annotations from "properties", "patternProperties", and
    "additionalProperties", which can come from those keywords when they are adjacent to the "unevaluatedProperties"
    keyword. Those three annotations, as well as "unevaluatedProperties", can also result from any and all adjacent
    in-place applicator (Section 10.2) keywords.  This includes but is not limited to the in-place applicators defined
    in this document.

    Validation with "unevaluatedProperties" applies only to the child values of instance names that do not appear in
    the "properties", "patternProperties", "additionalProperties", or "unevaluatedProperties" annotation results that
    apply to the instance location being validated.

    For all such properties, validation succeeds if the child instance validates against the "unevaluatedProperties"
    schema.

    This means that "properties", "patternProperties", "additionalProperties", and all in-place applicators MUST be
    evaluated before this keyword can be evaluated.  Authors of extension keywords MUST NOT define an in-place
    applicator that would need to be evaluated after this keyword.

    The annotation result of this keyword is the set of instance property names validated by this keyword's subschema.

    Omitting this keyword has the same assertion behavior as an empty schema.

    The following properties are taken directly from the
    `JSON Schema Validation <https://tools.ietf.org/html/draft-wright-json-schema-validation-00>`_ and follow the same
    specifications:
    """

    type: OpenAPIType | Sequence[OpenAPIType] | None = None
    """The value of this keyword MUST be either a string or an array.  If it is an array, elements of the array MUST be
    strings and MUST be unique.

    String values MUST be one of the six primitive types (``"null"``, ``"boolean"``, ``"object"``, ``"array"``,
    ``"number"``, and ``"string"``), or ``"integer"`` which matches any number with a zero fractional part.

    An instance validates if and only if the instance is in any of the sets listed for this keyword.
    """

    enum: Sequence[Any] | None = None
    """The value of this keyword MUST be an array.  This array SHOULD have at least one element.  Elements in the array
    SHOULD be unique.

    An instance validates successfully against this keyword if its value is equal to one of the elements in this
    keyword's array value.

    Elements in the array might be of any type, including null.
    """

    const: Any | None = None
    """The value of this keyword MAY be of any type, including null.

    Use of this keyword is functionally equivalent to an "enum" (Section 6.1.2) with a single value.

    An instance validates successfully against this keyword if its value is equal to the value of the keyword.
    """

    multiple_of: float | None = None
    """The value of "multipleOf" MUST be a number, strictly greater than 0.

    A numeric instance is only valid if division by this keyword's value results in an integer.
    """

    maximum: float | None = None
    """The value of "maximum" MUST be a number, representing an inclusive upper limit for a numeric instance.

    If the instance is a number, then this keyword validates only if the instance is less than or exactly equal to
    "maximum".
    """

    exclusive_maximum: float | None = None
    """The value of "exclusiveMaximum" MUST be a number, representing an exclusive upper limit for a numeric instance.

    If the instance is a number, then the instance is valid only if it has a value strictly less than (not equal to)
    "exclusiveMaximum".
    """

    minimum: float | None = None
    """The value of "minimum" MUST be a number, representing an inclusive lower limit for a numeric instance.

    If the instance is a number, then this keyword validates only if the instance is greater than or exactly equal to
    "minimum".
    """

    exclusive_minimum: float | None = None
    """The value of "exclusiveMinimum" MUST be a number, representing an exclusive lower limit for a numeric instance.

    If the instance is a number, then the instance is valid only if it has a value strictly greater than (not equal to)
    "exclusiveMinimum".
    """

    max_length: int | None = None
    """The value of this keyword MUST be a non-negative integer.

    A string instance is valid against this keyword if its length is less than, or equal to, the value of this keyword.

    The length of a string instance is defined as the number of its characters as defined by :rfc:`8259`.
    """

    min_length: int | None = None
    """The value of this keyword MUST be a non-negative integer.

    A string instance is valid against this keyword if its length is greater than, or equal to, the value of this
    keyword.

    The length of a string instance is defined as the number of its characters as defined by :rfc:`8259`.

    Omitting this keyword has the same behavior as a value of 0.
    """

    pattern: str | None = None
    """The value of this keyword MUST be a string.  This string SHOULD be a valid regular expression, according to the
    ECMA-262 regular expression dialect.

    A string instance is considered valid if the regular expression matches the instance successfully.  Recall: regular
    expressions are not implicitly anchored.
    """

    max_items: int | None = None
    """The value of this keyword MUST be a non-negative integer.

    An array instance is valid against "maxItems" if its size is less than, or equal to, the value of this keyword.
    """

    min_items: int | None = None
    """The value of this keyword MUST be a non-negative integer.

    An array instance is valid against "minItems" if its size is greater than, or equal to, the value of this keyword.

    Omitting this keyword has the same behavior as a value of 0.
    """

    unique_items: bool | None = None
    """The value of this keyword MUST be a boolean.

    If this keyword has boolean value false, the instance validates successfully.  If it has boolean value true, the
    instance validates successfully if all of its elements are unique.

    Omitting this keyword has the same behavior as a value of false.
    """

    max_contains: int | None = None
    """The value of this keyword MUST be a non-negative integer.

    If "contains" is not present within the same schema object, then this keyword has no effect.

    An instance array is valid against "maxContains" in two ways, depending on the form of the annotation result of an
    adjacent "contains" [json-schema] keyword.  The first way is if the annotation result is an array and the length of
    that array is less than or equal to the "maxContains" value.  The second way is if the annotation result is a
    boolean "true" and the instance array length is less than r equal to the "maxContains" value.
    """

    min_contains: int | None = None
    """The value of this keyword MUST be a non-negative integer.

    If "contains" is not present within the same schema object, then this keyword has no effect.

    An instance array is valid against "minContains" in two ways, depending on the form of the annotation result of an
    adjacent "contains" [json-schema] keyword.  The first way is if the annotation result is an array and the length of
    that array is greater than or equal to the "minContains" value.  The second way is if the annotation result is a
    boolean "true" and the instance array length is greater than or equal to the "minContains" value.

    A value of 0 is allowed, but is only useful for setting a range of occurrences from 0 to the value of "maxContains".
    A value of 0 with no "maxContains" causes "contains" to always pass validation.

    Omitting this keyword has the same behavior as a value of 1.
    """

    max_properties: int | None = None
    """The value of this keyword MUST be a non-negative integer.

    An object instance is valid against "maxProperties" if its number of properties is less than, or equal to, the value
    of this keyword.
    """

    min_properties: int | None = None
    """The value of this keyword MUST be a non-negative integer.

    An object instance is valid against "minProperties" if its number of properties is greater than, or equal to, the
    value of this keyword.

    Omitting this keyword has the same behavior as a value of 0.
    """

    required: Sequence[str] | None = None
    """The value of this keyword MUST be an array.  Elements of this array, if any, MUST be strings, and MUST be unique.

    An object instance is valid against this keyword if every item in the rray is the name of a property in the instance.

    Omitting this keyword has the same behavior as an empty array.
    """

    dependent_required: dict[str, Sequence[str]] | None = None
    """The value of this keyword MUST be an object.  Properties in this object, f any, MUST be arrays.  Elements in each
    array, if any, MUST be strings, and MUST be unique.

    This keyword specifies properties that are required if a specific other property is present.  Their requirement is
    dependent on the presence of the other property.

    Validation succeeds if, for each name that appears in both the instance and as a name within this keyword's value,
    every item in the corresponding array is also the name of a property in the instance.

    Omitting this keyword has the same behavior as an empty object.
    """

    format: OpenAPIFormat | None = None
    """From OpenAPI:

    See `Data Type Formats <https://spec.openapis.org/oas/v3.1.0#dataTypeFormat>`_ for further details. While relying on
    JSON Schema's defined formats, the OAS offers a few additional predefined formats.

    From JSON Schema:

    Structural validation alone may be insufficient to allow an application to correctly utilize certain values.
    The "format" annotation keyword is defined to allow schema authors to convey semantic information for a fixed subset
    of values which are accurately described by authoritative resources, be they RFCs or other external specifications.

    The value of this keyword is called a format attribute.  It MUST be a string.  A format attribute can generally only
    validate a given set of instance types.  If the type of the instance to validate is not in this set, validation for
    this format attribute and instance SHOULD succeed.  All format attributes defined in this section apply to strings,
    but a format attribute can be specified to apply to any instance types defined in the data model defined in the core
    JSON Schema. [json-schema] [[CREF1: Note that the "type" keyword in this specification defines an "integer" type
    which is not part of the data model. Therefore a format attribute can be limited to numbers, but not specifically to
    integers.  However, a numeric format can be used alongside the "type" keyword with a value of "integer", or could be
    explicitly defined to always pass if the number is not an integer, which produces essentially the same behavior as
    only applying to integers.  ]]
    """

    content_encoding: str | None = None
    """If the instance value is a string, this property defines that the string SHOULD be interpreted as binary data and
    decoded using the encoding named by this property.

    Possible values indicating base 16, 32, and 64 encodings with several variations are listed in :rfc:`4648`.
    Additionally, sections 6.7 and 6.8 of :rfc:`2045` provide encodings used in MIME.  As "base64" is defined in both
    RFCs, the definition from :rfc:`4648` SHOULD be assumed unless the string is specifically intended for use in a
    MIME context.  Note that all of these encodings result in strings consisting only of 7-bit ASCII characters.
    therefore, this keyword has no meaning for strings containing characters outside of that range.

    If this keyword is absent, but "contentMediaType" is present, this indicates that the encoding is the identity
    encoding, meaning that no transformation was needed in order to represent the content in a UTF-8 string.
    """

    content_media_type: str | None = None
    """If the instance is a string, this property indicates the media type of the contents of the string. If
    "contentEncoding" is present, this property describes the decoded string.

    The value of this property MUST be a string, which MUST be a media type, as defined by :rfc:`2046`
    """

    content_schema: Reference | Schema | None = None
    """If the instance is a string, and if "contentMediaType" is present, this property contains a schema which
    describes the structure of the string.

    This keyword MAY be used with any media type that can be mapped into JSON Schema's data model.

    The value of this property MUST be a valid JSON schema. It SHOULD be ignored if "contentMediaType" is not present.
    """

    title: str | None = None
    """The value of "title" MUST be a string.

    The title can be used to decorate a user interface with information about the data produced by this user interface.
    A title will preferably be short.
    """

    description: str | None = None
    """From OpenAPI:

    `CommonMark syntax <https://spec.commonmark.org/>`_ MAY be used for rich text representation.

    From JSON Schema:
    The value "description" MUST be a string.

    The description can be used to decorate a user interface with information about the data produced by this user
    interface. A description will provide explanation about the purpose of the instance described by this schema.
    """

    default: Any | None = None
    """There are no restrictions placed on the value of this keyword.  When multiple occurrences of this keyword are
    applicable to a single sub-instance, implementations SHOULD remove duplicates.

    This keyword can be used to supply a default JSON value associated with a particular schema.  It is RECOMMENDED that
    a default value be valid against the associated schema.
    """

    deprecated: bool | None = None
    """The value of this keyword MUST be a boolean.  When multiple occurrences of this keyword are applicable to a
    single sub-instance, applications SHOULD consider the instance location to be deprecated if any occurrence specifies
    a true value.

    If "deprecated" has a value of boolean true, it indicates that applications SHOULD refrain from usage of the
    declared property.  It  MAY mean the property is going to be removed in the future.

    A root schema containing "deprecated" with a value of true indicates that the entire resource being described MAY be
    removed in the future.

    The "deprecated" keyword applies to each instance location to which the schema object containing the keyword
    successfully applies. This  can result in scenarios where every array item or object property is deprecated even
    though the containing array or object is not.

    Omitting this keyword has the same behavior as a value of false.
    """

    read_only: bool | None = None
    """The value of "readOnly" MUST be a boolean.  When multiple occurrences of this keyword are applicable to a single
    sub-instance, the resulting behavior SHOULD be as for a true value if any occurrence specifies a true value, and
    SHOULD be as for a false value otherwise.

    If "readOnly" has a value of boolean true, it indicates that the value of the instance is managed exclusively by
    the owning authority, and attempts by an application to modify the value of this property are expected to be ignored
    or rejected by that owning authority.

    An instance document that is marked as "readOnly" for the entire document MAY be ignored if sent to the owning
    authority, or MAY result in an error, at the authority's discretion.

    For example, "readOnly" would be used to mark a database-generated serial number as read-only, while "writeOnly"
    would be used to mark a password input field.

    This keyword can be used to assist in user interface instance generation.  In particular, an application MAY choose
    to use a widget that hides input values as they are typed for write-only fields.

    Omitting these keywords has the same behavior as values of false.
    """

    write_only: bool | None = None
    """The value of "writeOnly" MUST be a boolean.  When multiple occurrences of this keyword are applicable to a
    single sub-instance, the resulting behavior SHOULD be as for a true value if any occurrence specifies a true value,
    and SHOULD be as for a false value otherwise.

    If "writeOnly" has a value of boolean true, it indicates that the value is never present when the instance is
    retrieved from the owning authority.  It can be present when sent to the owning authority to update or create the
    document (or the resource it represents), but it will not be included in any updated or newly created version of the
    instance.

    An instance document that is marked as "writeOnly" for the entire document MAY be returned as a blank document of
    some sort, or MAY produce an error upon retrieval, or have the retrieval request ignored, at the authority's
    discretion.

    For example, "readOnly" would be used to mark a database-generated serial number as read-only, while "writeOnly"
    would be used to mark a  password input field.

    This keyword can be used to assist in user interface instance generation. In particular, an application MAY choose
    to use a widget that hides input values as they are typed for write-only fields.

    Omitting these keywords has the same behavior as values of false.
    """

    examples: list[Any] | None = None
    """The value of this must be an array containing the example values."""

    discriminator: Discriminator | None = None
    """Adds support for polymorphism.

    The discriminator is an object name that is used to differentiate between other schemas which may satisfy the
    payload description. See `Composition and Inheritance <https://spec.openapis.org/oas/v3.1.0#schemaComposition>`_
    for more details.
    """

    xml: XML | None = None
    """This MAY be used only on properties schemas.

    It has no effect on root schemas. Adds additional metadata to describe the XML representation of this property.
    """

    external_docs: ExternalDocumentation | None = None
    """Additional external documentation for this schema."""

    example: Any | None = None
    """A free-form property to include an example of an instance for this schema. To represent examples that cannot be
    naturally represented in JSON or YAML, a string value can be used to contain the example with escaping where
    necessary.

    Deprecated: The example property has been deprecated in favor of the JSON Schema examples keyword. Use of example is
    discouraged, and later versions of this specification may remove it.
    """

    def __hash__(self) -> int:
        return _recursive_hash(self)


@dataclass
class SchemaDataContainer(Schema):
    """Special class that allows using python data containers, e.g. dataclasses or pydantic models, to represent a
    schema
    """

    data_container: Any = None
    """A data container instance that will be used to generate the schema."""
