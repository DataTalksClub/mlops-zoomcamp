"""This module contains all the enumerations of the package."""

from __future__ import annotations

import enum


class DocstringSectionKind(enum.Enum):
    """Enumeration of the possible docstring section kinds."""

    text = "text"
    """Text section."""
    parameters = "parameters"
    """Parameters section."""
    other_parameters = "other parameters"
    """Other parameters (keyword arguments) section."""
    raises = "raises"
    """Raises (exceptions) section."""
    warns = "warns"
    """Warnings section."""
    returns = "returns"
    """Returned value(s) section."""
    yields = "yields"
    """Yielded value(s) (generators) section."""
    receives = "receives"
    """Received value(s) (generators) section."""
    examples = "examples"
    """Examples section."""
    attributes = "attributes"
    """Attributes section."""
    functions = "functions"
    """Functions section."""
    classes = "classes"
    """Classes section."""
    modules = "modules"
    """Modules section."""
    deprecated = "deprecated"
    """Deprecation section."""
    admonition = "admonition"
    """Admonition block."""


class ParameterKind(enum.Enum):
    """Enumeration of the different parameter kinds."""

    positional_only: str = "positional-only"
    """Positional-only parameter."""
    positional_or_keyword: str = "positional or keyword"
    """Positional or keyword parameter."""
    var_positional: str = "variadic positional"
    """Variadic positional parameter."""
    keyword_only: str = "keyword-only"
    """Keyword-only parameter."""
    var_keyword: str = "variadic keyword"
    """Variadic keyword parameter."""


class Kind(enum.Enum):
    """Enumeration of the different object kinds."""

    MODULE: str = "module"
    """Modules."""
    CLASS: str = "class"
    """Classes."""
    FUNCTION: str = "function"
    """Functions and methods."""
    ATTRIBUTE: str = "attribute"
    """Attributes and properties."""
    ALIAS: str = "alias"
    """Aliases (imported objects)."""


class ExplanationStyle(enum.Enum):
    """Enumeration of the possible styles for explanations."""

    ONE_LINE: str = "oneline"
    """Explanations on one-line."""
    VERBOSE: str = "verbose"
    """Explanations on multiple lines."""
    MARKDOWN: str = "markdown"
    """Explanations in Markdown, adapted to changelogs."""
    GITHUB: str = "github"
    """Explanation as GitHub workflow commands warnings, adapted to CI."""


class BreakageKind(enum.Enum):
    """Enumeration of the possible API breakages."""

    PARAMETER_MOVED: str = "Positional parameter was moved"
    PARAMETER_REMOVED: str = "Parameter was removed"
    PARAMETER_CHANGED_KIND: str = "Parameter kind was changed"
    PARAMETER_CHANGED_DEFAULT: str = "Parameter default was changed"
    PARAMETER_CHANGED_REQUIRED: str = "Parameter is now required"
    PARAMETER_ADDED_REQUIRED: str = "Parameter was added as required"
    RETURN_CHANGED_TYPE: str = "Return types are incompatible"
    OBJECT_REMOVED: str = "Public object was removed"
    OBJECT_CHANGED_KIND: str = "Public object points to a different kind of object"
    ATTRIBUTE_CHANGED_TYPE: str = "Attribute types are incompatible"
    ATTRIBUTE_CHANGED_VALUE: str = "Attribute value was changed"
    CLASS_REMOVED_BASE: str = "Base class was removed"


class Parser(enum.Enum):
    """Enumeration of the different docstring parsers."""

    google = "google"
    """Google-style docstrings parser."""
    sphinx = "sphinx"
    """Sphinx-style docstrings parser."""
    numpy = "numpy"
    """Numpydoc-style docstrings parser."""


class ObjectKind(enum.Enum):
    """Enumeration of the different runtime object kinds."""

    MODULE: str = "module"
    """Modules."""
    CLASS: str = "class"
    """Classes."""
    STATICMETHOD: str = "staticmethod"
    """Static methods."""
    CLASSMETHOD: str = "classmethod"
    """Class methods."""
    METHOD_DESCRIPTOR: str = "method_descriptor"
    """Method descriptors."""
    METHOD: str = "method"
    """Methods."""
    BUILTIN_METHOD: str = "builtin_method"
    """Built-in ethods."""
    COROUTINE: str = "coroutine"
    """Coroutines"""
    FUNCTION: str = "function"
    """Functions."""
    BUILTIN_FUNCTION: str = "builtin_function"
    """Built-in functions."""
    CACHED_PROPERTY: str = "cached_property"
    """Cached properties."""
    PROPERTY: str = "property"
    """Properties."""
    ATTRIBUTE: str = "attribute"
    """Attributes."""

    def __str__(self) -> str:
        return self.value


class When(enum.Enum):
    """Enumeration of the different times at which an extension is used."""

    before_all: int = 1
    """For each node, before the visit/inspection."""
    before_children: int = 2
    """For each node, after the visit has started, and before the children visit/inspection."""
    after_children: int = 3
    """For each node, after the children have been visited/inspected, and before finishing the visit/inspection."""
    after_all: int = 4
    """For each node, after the visit/inspection."""
