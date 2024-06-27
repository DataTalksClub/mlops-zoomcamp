"""This module exposes objects related to docstrings."""

from griffe.docstrings.parsers import parse, parsers
from griffe.enumerations import Parser

__all__ = ["Parser", "parse", "parsers"]
