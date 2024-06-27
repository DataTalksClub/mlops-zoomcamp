"""This module is the public interface to import elements from the base."""

from griffe.enumerations import When
from griffe.extensions.base import (
    Extension,
    Extensions,
    ExtensionType,
    InspectorExtension,
    VisitorExtension,
    load_extensions,
)

__all__ = [
    "Extension",
    "Extensions",
    "ExtensionType",
    "InspectorExtension",
    "load_extensions",
    "VisitorExtension",
    "When",
]
