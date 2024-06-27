from __future__ import annotations

from binascii import hexlify
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from random import Random


def create_random_float(
    random: Random,
    minimum: Decimal | float | None = None,
    maximum: Decimal | float | None = None,
) -> float:
    """Generate a random float given the constraints.

    :param random: An instance of random.
    :param minimum: A minimum value
    :param maximum: A maximum value.

    :returns: A random float.
    """
    if minimum is None:
        minimum = float(random.randint(0, 100)) if maximum is None else float(maximum) - 100.0
    if maximum is None:
        maximum = float(minimum) + 1.0 * 2.0 if minimum >= 0 else float(minimum) + 1.0 / 2.0
    return random.uniform(float(minimum), float(maximum))


def create_random_integer(random: Random, minimum: int | None = None, maximum: int | None = None) -> int:
    """Generate a random int given the constraints.

    :param random: An instance of random.
    :param minimum: A minimum value
    :param maximum: A maximum value.

    :returns: A random integer.
    """
    return round(create_random_float(random=random, minimum=minimum, maximum=maximum))


def create_random_decimal(
    random: Random,
    minimum: Decimal | None = None,
    maximum: Decimal | None = None,
) -> Decimal:
    """Generate a random Decimal given the constraints.

    :param random: An instance of random.
    :param minimum: A minimum value
    :param maximum: A maximum value.

    :returns: A random decimal.
    """
    return Decimal(str(create_random_float(random=random, minimum=minimum, maximum=maximum)))


def create_random_bytes(
    random: Random,
    min_length: int | None = None,
    max_length: int | None = None,
    lower_case: bool = False,
    upper_case: bool = False,
) -> bytes:
    """Generate a random bytes given the constraints.

    :param random: An instance of random.
    :param min_length: A minimum length.
    :param max_length: A maximum length.
    :param lower_case: Whether to lowercase the result.
    :param upper_case: Whether to uppercase the result.

    :returns: A random byte-string.
    """
    if min_length is None:
        min_length = 0
    if max_length is None:
        max_length = min_length + 1 * 2

    length = random.randint(min_length, max_length)
    result = b"" if length == 0 else hexlify(random.getrandbits(length * 8).to_bytes(length, "little"))

    if lower_case:
        result = result.lower()
    elif upper_case:
        result = result.upper()

    if max_length and len(result) > max_length:
        end = random.randint(min_length or 0, max_length)
        return result[:end]

    return result


def create_random_string(
    random: Random,
    min_length: int | None = None,
    max_length: int | None = None,
    lower_case: bool = False,
    upper_case: bool = False,
) -> str:
    """Generate a random string given the constraints.

    :param random: An instance of random.
    :param min_length: A minimum length.
    :param max_length: A maximum length.
    :param lower_case: Whether to lowercase the result.
    :param upper_case: Whether to uppercase the result.

    :returns: A random string.
    """
    return create_random_bytes(
        random=random,
        min_length=min_length,
        max_length=max_length,
        lower_case=lower_case,
        upper_case=upper_case,
    ).decode("utf-8")


def create_random_boolean(random: Random) -> bool:
    """Generate a random boolean value.

    :param random: An instance of random.

    :returns: A random boolean.
    """
    return bool(random.getrandbits(1))
