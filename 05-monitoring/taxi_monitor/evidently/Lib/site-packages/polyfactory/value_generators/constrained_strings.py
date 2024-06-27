from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Pattern, TypeVar, Union, cast

from polyfactory.exceptions import ParameterException
from polyfactory.value_generators.primitives import create_random_bytes, create_random_string
from polyfactory.value_generators.regex import RegexFactory

T = TypeVar("T", bound=Union[bytes, str])

if TYPE_CHECKING:
    from random import Random


def _validate_length(
    min_length: int | None = None,
    max_length: int | None = None,
) -> None:
    """Validate the length parameters make sense.

    :param min_length: Minimum length.
    :param max_length: Maximum length.

    :raises: ParameterException.

    :returns: None.
    """
    if min_length is not None and min_length < 0:
        msg = "min_length must be greater or equal to 0"
        raise ParameterException(msg)

    if max_length is not None and max_length < 0:
        msg = "max_length must be greater or equal to 0"
        raise ParameterException(msg)

    if max_length is not None and min_length is not None and max_length < min_length:
        msg = "max_length must be greater than min_length"
        raise ParameterException(msg)


def _generate_pattern(
    random: Random,
    pattern: str | Pattern,
    lower_case: bool = False,
    upper_case: bool = False,
    min_length: int | None = None,
    max_length: int | None = None,
) -> str:
    """Generate a regex.

    :param random: An instance of random.
    :param pattern: A regex or string pattern.
    :param lower_case: Whether to lowercase the result.
    :param upper_case: Whether to uppercase the result.
    :param min_length: A minimum length.
    :param max_length: A maximum length.

    :returns: A string matching the given pattern.
    """
    regex_factory = RegexFactory(random=random)
    result = regex_factory(pattern)
    if min_length:
        while len(result) < min_length:
            result += regex_factory(pattern)

    if max_length is not None and len(result) > max_length:
        result = result[:max_length]

    if lower_case:
        result = result.lower()

    if upper_case:
        result = result.upper()

    return result


def handle_constrained_string_or_bytes(
    random: Random,
    t_type: Callable[[], T],
    lower_case: bool = False,
    upper_case: bool = False,
    min_length: int | None = None,
    max_length: int | None = None,
    pattern: str | Pattern | None = None,
) -> T:
    """Handle constrained string or bytes, for example - pydantic `constr` or `conbytes`.

    :param random: An instance of random.
    :param t_type: A type (str or bytes)
    :param lower_case: Whether to lowercase the result.
    :param upper_case: Whether to uppercase the result.
    :param min_length: A minimum length.
    :param max_length: A maximum length.
    :param pattern: A regex or string pattern.

    :returns: A value of type T.
    """
    _validate_length(min_length=min_length, max_length=max_length)

    if max_length == 0:
        return t_type()

    if pattern:
        return cast(
            "T",
            _generate_pattern(
                random=random,
                pattern=pattern,
                lower_case=lower_case,
                upper_case=upper_case,
                min_length=min_length,
                max_length=max_length,
            ),
        )

    if t_type is str:
        return cast(
            "T",
            create_random_string(
                min_length=min_length,
                max_length=max_length,
                lower_case=lower_case,
                upper_case=upper_case,
                random=random,
            ),
        )

    return cast(
        "T",
        create_random_bytes(
            min_length=min_length,
            max_length=max_length,
            lower_case=lower_case,
            upper_case=upper_case,
            random=random,
        ),
    )
