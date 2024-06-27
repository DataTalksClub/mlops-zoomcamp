"""This module contains the dataclasses related to docstrings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from griffe.enumerations import DocstringSectionKind

if TYPE_CHECKING:
    from typing import Any, Literal

    from griffe.expressions import Expr


# Elements -----------------------------------------------
class DocstringElement:
    """This base class represents annotated, nameless elements."""

    def __init__(self, *, description: str, annotation: str | Expr | None = None) -> None:
        """Initialize the element.

        Parameters:
            annotation: The element annotation, if any.
            description: The element description.
        """
        self.description: str = description
        """The element description."""
        self.annotation: str | Expr | None = annotation
        """The element annotation."""

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
        """Return this element's data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        return {
            "annotation": self.annotation,
            "description": self.description,
        }


class DocstringNamedElement(DocstringElement):
    """This base class represents annotated, named elements."""

    def __init__(
        self,
        name: str,
        *,
        description: str,
        annotation: str | Expr | None = None,
        value: str | None = None,
    ) -> None:
        """Initialize the element.

        Parameters:
            name: The element name.
            description: The element description.
            annotation: The element annotation, if any.
            value: The element value, as a string.
        """
        super().__init__(description=description, annotation=annotation)
        self.name: str = name
        """The element name."""
        self.value: str | None = value
        """The element value, if any"""

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return this element's data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base = {"name": self.name, **super().as_dict(**kwargs)}
        if self.value is not None:
            base["value"] = self.value
        return base


class DocstringAdmonition(DocstringElement):
    """This class represents an admonition."""

    @property
    def kind(self) -> str | Expr | None:
        """The kind of this admonition."""
        return self.annotation

    @kind.setter
    def kind(self, value: str | Expr) -> None:
        self.annotation = value

    @property
    def contents(self) -> str:
        """The contents of this admonition."""
        return self.description

    @contents.setter
    def contents(self, value: str) -> None:
        self.description = value


class DocstringDeprecated(DocstringElement):
    """This class represents a documented deprecated item."""

    @property
    def version(self) -> str:
        """The version of this deprecation."""
        return self.annotation  # type: ignore[return-value]

    @version.setter
    def version(self, value: str) -> None:
        self.annotation = value


class DocstringRaise(DocstringElement):
    """This class represents a documented raise value."""


class DocstringWarn(DocstringElement):
    """This class represents a documented warn value."""


class DocstringReturn(DocstringNamedElement):
    """This class represents a documented return value."""


class DocstringYield(DocstringNamedElement):
    """This class represents a documented yield value."""


class DocstringReceive(DocstringNamedElement):
    """This class represents a documented receive value."""


class DocstringParameter(DocstringNamedElement):
    """This class represent a documented function parameter."""

    @property
    def default(self) -> str | None:
        """The default value of this parameter."""
        return self.value

    @default.setter
    def default(self, value: str) -> None:
        self.value = value


class DocstringAttribute(DocstringNamedElement):
    """This class represents a documented module/class attribute."""


class DocstringFunction(DocstringNamedElement):
    """This class represents a documented function."""

    @property
    def signature(self) -> str | Expr | None:
        return self.annotation


class DocstringClass(DocstringNamedElement):
    """This class represents a documented class."""

    @property
    def signature(self) -> str | Expr | None:
        return self.annotation


class DocstringModule(DocstringNamedElement):
    """This class represents a documented module."""


# Sections -----------------------------------------------
class DocstringSection:
    """This class represents a docstring section."""

    kind: DocstringSectionKind
    """The section kind."""

    def __init__(self, title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            title: An optional title.
        """
        self.title: str | None = title
        """The section title."""
        self.value: Any = None
        """The section value."""

    def __bool__(self) -> bool:
        return bool(self.value)

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return this section's data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        if hasattr(self.value, "as_dict"):  # noqa: SIM108
            serialized_value = self.value.as_dict(**kwargs)
        else:
            serialized_value = self.value
        base = {"kind": self.kind.value, "value": serialized_value}
        if self.title:
            base["title"] = self.title
        return base


class DocstringSectionText(DocstringSection):
    """This class represents a text section."""

    kind: DocstringSectionKind = DocstringSectionKind.text

    def __init__(self, value: str, title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            value: The section text.
            title: An optional title.
        """
        super().__init__(title)
        self.value: str = value


class DocstringSectionParameters(DocstringSection):
    """This class represents a parameters section."""

    kind: DocstringSectionKind = DocstringSectionKind.parameters

    def __init__(self, value: list[DocstringParameter], title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            value: The section parameters.
            title: An optional title.
        """
        super().__init__(title)
        self.value: list[DocstringParameter] = value


class DocstringSectionOtherParameters(DocstringSectionParameters):
    """This class represents an other parameters section."""

    kind: DocstringSectionKind = DocstringSectionKind.other_parameters


class DocstringSectionRaises(DocstringSection):
    """This class represents a raises section."""

    kind: DocstringSectionKind = DocstringSectionKind.raises

    def __init__(self, value: list[DocstringRaise], title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            value: The section exceptions.
            title: An optional title.
        """
        super().__init__(title)
        self.value: list[DocstringRaise] = value


class DocstringSectionWarns(DocstringSection):
    """This class represents a warns section."""

    kind: DocstringSectionKind = DocstringSectionKind.warns

    def __init__(self, value: list[DocstringWarn], title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            value: The section warnings.
            title: An optional title.
        """
        super().__init__(title)
        self.value: list[DocstringWarn] = value


class DocstringSectionReturns(DocstringSection):
    """This class represents a returns section."""

    kind: DocstringSectionKind = DocstringSectionKind.returns

    def __init__(self, value: list[DocstringReturn], title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            value: The section returned items.
            title: An optional title.
        """
        super().__init__(title)
        self.value: list[DocstringReturn] = value


class DocstringSectionYields(DocstringSection):
    """This class represents a yields section."""

    kind: DocstringSectionKind = DocstringSectionKind.yields

    def __init__(self, value: list[DocstringYield], title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            value: The section yielded items.
            title: An optional title.
        """
        super().__init__(title)
        self.value: list[DocstringYield] = value


class DocstringSectionReceives(DocstringSection):
    """This class represents a receives section."""

    kind: DocstringSectionKind = DocstringSectionKind.receives

    def __init__(self, value: list[DocstringReceive], title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            value: The section received items.
            title: An optional title.
        """
        super().__init__(title)
        self.value: list[DocstringReceive] = value


class DocstringSectionExamples(DocstringSection):
    """This class represents an examples section."""

    kind: DocstringSectionKind = DocstringSectionKind.examples

    def __init__(
        self,
        value: list[tuple[Literal[DocstringSectionKind.text, DocstringSectionKind.examples], str]],
        title: str | None = None,
    ) -> None:
        """Initialize the section.

        Parameters:
            value: The section examples.
            title: An optional title.
        """
        super().__init__(title)
        self.value: list[tuple[Literal[DocstringSectionKind.text, DocstringSectionKind.examples], str]] = value


class DocstringSectionAttributes(DocstringSection):
    """This class represents an attributes section."""

    kind: DocstringSectionKind = DocstringSectionKind.attributes

    def __init__(self, value: list[DocstringAttribute], title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            value: The section attributes.
            title: An optional title.
        """
        super().__init__(title)
        self.value: list[DocstringAttribute] = value


class DocstringSectionFunctions(DocstringSection):
    """This class represents a functions/methods section."""

    kind: DocstringSectionKind = DocstringSectionKind.functions

    def __init__(self, value: list[DocstringFunction], title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            value: The section functions.
            title: An optional title.
        """
        super().__init__(title)
        self.value: list[DocstringFunction] = value


class DocstringSectionClasses(DocstringSection):
    """This class represents a classes section."""

    kind: DocstringSectionKind = DocstringSectionKind.classes

    def __init__(self, value: list[DocstringClass], title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            value: The section classes.
            title: An optional title.
        """
        super().__init__(title)
        self.value: list[DocstringClass] = value


class DocstringSectionModules(DocstringSection):
    """This class represents a modules section."""

    kind: DocstringSectionKind = DocstringSectionKind.modules

    def __init__(self, value: list[DocstringModule], title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            value: The section modules.
            title: An optional title.
        """
        super().__init__(title)
        self.value: list[DocstringModule] = value


class DocstringSectionDeprecated(DocstringSection):
    """This class represents a deprecated section."""

    kind: DocstringSectionKind = DocstringSectionKind.deprecated

    def __init__(self, version: str, text: str, title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            version: The deprecation version.
            text: The deprecation text.
            title: An optional title.
        """
        super().__init__(title)
        self.value: DocstringDeprecated = DocstringDeprecated(annotation=version, description=text)


class DocstringSectionAdmonition(DocstringSection):
    """This class represents an admonition section."""

    kind: DocstringSectionKind = DocstringSectionKind.admonition

    def __init__(self, kind: str, text: str, title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            kind: The admonition kind.
            text: The admonition text.
            title: An optional title.
        """
        super().__init__(title)
        self.value: DocstringAdmonition = DocstringAdmonition(annotation=kind, description=text)


__all__ = [
    "DocstringAdmonition",
    "DocstringAttribute",
    "DocstringDeprecated",
    "DocstringElement",
    "DocstringNamedElement",
    "DocstringParameter",
    "DocstringRaise",
    "DocstringReceive",
    "DocstringReturn",
    "DocstringSection",
    "DocstringSectionAdmonition",
    "DocstringSectionAttributes",
    "DocstringSectionDeprecated",
    "DocstringSectionExamples",
    "DocstringSectionKind",
    "DocstringSectionOtherParameters",
    "DocstringSectionParameters",
    "DocstringSectionRaises",
    "DocstringSectionReceives",
    "DocstringSectionReturns",
    "DocstringSectionText",
    "DocstringSectionWarns",
    "DocstringSectionYields",
    "DocstringWarn",
    "DocstringYield",
]
