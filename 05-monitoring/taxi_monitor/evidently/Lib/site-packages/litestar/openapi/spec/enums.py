from enum import Enum

__all__ = ("OpenAPIFormat", "OpenAPIType")


class OpenAPIFormat(str, Enum):
    """Formats extracted from: https://datatracker.ietf.org/doc/html/draft-bhutton-json-schema-validation-00#page-13"""

    DATE = "date"
    DATE_TIME = "date-time"
    TIME = "time"
    DURATION = "duration"
    URL = "url"
    EMAIL = "email"
    IDN_EMAIL = "idn-email"
    HOST_NAME = "hostname"
    IDN_HOST_NAME = "idn-hostname"
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    URI = "uri"
    URI_REFERENCE = "uri-reference"
    URI_TEMPLATE = "uri-template"
    JSON_POINTER = "json-pointer"
    RELATIVE_JSON_POINTER = "relative-json-pointer"
    IRI = "iri-reference"
    IRI_REFERENCE = "iri-reference"  # noqa: PIE796
    UUID = "uuid"
    REGEX = "regex"
    BINARY = "binary"


class OpenAPIType(str, Enum):
    """An OopenAPI type."""

    ARRAY = "array"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    NULL = "null"
    NUMBER = "number"
    OBJECT = "object"
    STRING = "string"
