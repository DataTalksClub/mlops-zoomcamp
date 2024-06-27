"""This module imports all the defined parsers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from griffe.docstrings.dataclasses import DocstringSection, DocstringSectionText
from griffe.docstrings.google import parse as parse_google
from griffe.docstrings.numpy import parse as parse_numpy
from griffe.docstrings.sphinx import parse as parse_sphinx
from griffe.enumerations import Parser

if TYPE_CHECKING:
    from griffe.dataclasses import Docstring

parsers = {
    Parser.google: parse_google,
    Parser.sphinx: parse_sphinx,
    Parser.numpy: parse_numpy,
}


def parse(
    docstring: Docstring,
    parser: Literal["google", "numpy", "sphinx"] | Parser | None,
    **options: Any,
) -> list[DocstringSection]:
    """Parse the docstring.

    Parameters:
        docstring: The docstring to parse.
        parser: The docstring parser to use. If None, return a single text section.
        **options: The options accepted by the parser.

    Returns:
        A list of docstring sections.
    """
    if parser:
        if isinstance(parser, str):
            parser = Parser(parser)
        return parsers[parser](docstring, **options)  # type: ignore[operator]
    return [DocstringSectionText(docstring.value)]


__all__ = ["parse", "Parser", "parsers"]
