from __future__ import annotations

from dataclasses import dataclass

from litestar.openapi.spec.base import BaseSchemaObject

__all__ = ("Discriminator",)


@dataclass(unsafe_hash=True)
class Discriminator(BaseSchemaObject):
    """When request bodies or response payloads may be one of a number of different schemas, a ``discriminator``
    object can be used to aid in serialization, deserialization, and validation.

    The discriminator is a specific object in a schema which is used to inform the consumer of the specification of an
    alternative schema based on the value associated with it.

    When using the discriminator, _inline_ schemas will not be considered.
    """

    property_name: str
    """**REQUIRED**. The name of the property in the payload that will hold the discriminator value."""

    mapping: dict[str, str] | None = None
    """An object to hold mappings between payload values and schema names or references."""
