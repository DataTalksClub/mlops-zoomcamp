"""The code in this files is adapted from https://github.com/crdoconnor/xeger/blob/master/xeger/xeger.py.Which in turn
adapted it from https://bitbucket.org/leapfrogdevelopment/rstr/.

Copyright (C) 2015, Colm O'Connor
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the Leapfrog Direct Response, LLC, including
      its subsidiaries and affiliates nor the names of its
      contributors, may be used to endorse or promote products derived
      from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL LEAPFROG DIRECT
RESPONSE, LLC, INCLUDING ITS SUBSIDIARIES AND AFFILIATES, BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from __future__ import annotations

from itertools import chain
from string import (
    ascii_letters,
    ascii_lowercase,
    ascii_uppercase,
    digits,
    printable,
    punctuation,
    whitespace,
)
from typing import TYPE_CHECKING, Any, Pattern

try:  # >=3.11
    from re._parser import SubPattern, parse
except ImportError:  # < 3.11
    from sre_parse import SubPattern, parse  # pylint: disable=deprecated-module

if TYPE_CHECKING:
    from random import Random

_alphabets = {
    "printable": printable,
    "letters": ascii_letters,
    "uppercase": ascii_uppercase,
    "lowercase": ascii_lowercase,
    "digits": digits,
    "punctuation": punctuation,
    "nondigits": ascii_letters + punctuation,
    "nonletters": digits + punctuation,
    "whitespace": whitespace,
    "nonwhitespace": printable.strip(),
    "normal": ascii_letters + digits + " ",
    "word": ascii_letters + digits + "_",
    "nonword": "".join(set(printable).difference(ascii_letters + digits + "_")),
    "postalsafe": ascii_letters + digits + " .-#/",
    "urlsafe": ascii_letters + digits + "-._~",
    "domainsafe": ascii_letters + digits + "-",
}

_categories = {
    "category_digit": _alphabets["digits"],
    "category_not_digit": _alphabets["nondigits"],
    "category_space": _alphabets["whitespace"],
    "category_not_space": _alphabets["nonwhitespace"],
    "category_word": _alphabets["word"],
    "category_not_word": _alphabets["nonword"],
}


class RegexFactory:
    """Factory for regexes."""

    def __init__(self, random: Random, limit: int = 10) -> None:
        """Create a RegexFactory"""
        self._limit = limit
        self._cache: dict[str, Any] = {}
        self._random = random

        self._cases = {
            "literal": chr,
            "not_literal": lambda x: self._random.choice(printable.replace(chr(x), "")),
            "at": lambda x: "",
            "in": self._handle_in,
            "any": lambda x: self._random.choice(printable.replace("\n", "")),
            "range": lambda x: [chr(i) for i in range(x[0], x[1] + 1)],
            "category": lambda x: _categories[str(x).lower()],
            "branch": lambda x: "".join(self._handle_state(i) for i in self._random.choice(x[1])),
            "subpattern": self._handle_group,
            "assert": lambda x: "".join(self._handle_state(i) for i in x[1]),
            "assert_not": lambda x: "",
            "groupref": lambda x: self._cache[x],
            "min_repeat": lambda x: self._handle_repeat(*x),
            "max_repeat": lambda x: self._handle_repeat(*x),
            "negate": lambda x: [False],
        }

    def __call__(self, string_or_regex: str | Pattern) -> str:
        """Generate a string matching a regex.

        :param string_or_regex: A string or pattern.

        :return: The generated string.
        """
        pattern = string_or_regex.pattern if isinstance(string_or_regex, Pattern) else string_or_regex
        parsed = parse(pattern)
        result = self._build_string(parsed)  # pyright: ignore[reportGeneralTypeIssues]
        self._cache.clear()
        return result

    def _build_string(self, parsed: SubPattern) -> str:
        return "".join([self._handle_state(state) for state in parsed])  # pyright:ignore[reportGeneralTypeIssues]

    def _handle_state(self, state: tuple[SubPattern, tuple[Any, ...]]) -> Any:
        opcode, value = state
        return self._cases[str(opcode).lower()](value)  # type: ignore[no-untyped-call]

    def _handle_group(self, value: tuple[Any, ...]) -> str:
        result = "".join(self._handle_state(i) for i in value[3])
        if value[0]:
            self._cache[value[0]] = result
        return result

    def _handle_in(self, value: tuple[Any, ...]) -> Any:
        candidates = list(chain(*(self._handle_state(i) for i in value)))
        if candidates and candidates[0] is False:
            candidates = list(set(printable).difference(candidates[1:]))
            return self._random.choice(candidates)
        return self._random.choice(candidates)

    def _handle_repeat(self, start_range: int, end_range: Any, value: SubPattern) -> str:
        end_range = min(end_range, self._limit)

        result = [
            "".join(self._handle_state(v) for v in list(value))  # pyright: ignore[reportGeneralTypeIssues]
            for _ in range(self._random.randint(start_range, max(start_range, end_range)))
        ]
        return "".join(result)
