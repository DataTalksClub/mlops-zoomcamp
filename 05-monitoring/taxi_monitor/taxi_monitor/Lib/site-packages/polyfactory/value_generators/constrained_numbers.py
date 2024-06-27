from __future__ import annotations

from decimal import Decimal
from sys import float_info
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, cast

from polyfactory.exceptions import ParameterException
from polyfactory.value_generators.primitives import create_random_decimal, create_random_float, create_random_integer

if TYPE_CHECKING:
    from random import Random

T = TypeVar("T", Decimal, int, float)


class NumberGeneratorProtocol(Protocol[T]):
    """Protocol for custom callables used to generate numerical values"""

    def __call__(self, random: "Random", minimum: T | None = None, maximum: T | None = None) -> T:
        """Signature of the callable.

        :param random: An instance of random.
        :param minimum: A minimum value.
        :param maximum: A maximum value.
        :return: The generated numeric value.
        """
        ...


def almost_equal_floats(value_1: float, value_2: float, *, delta: float = 1e-8) -> bool:
    """Return True if two floats are almost equal

    :param value_1: A float value.
    :param value_2: A float value.
    :param delta: A minimal delta.

    :returns: Boolean dictating whether the floats can be considered equal - given python's problematic comparison of floats.
    """
    return abs(value_1 - value_2) <= delta


def is_multiply_of_multiple_of_in_range(
    minimum: T,
    maximum: T,
    multiple_of: T,
) -> bool:
    """Determine if at least one multiply of `multiple_of` lies in the given range.

    :param minimum: T: A minimum value.
    :param maximum: T: A maximum value.
    :param multiple_of: T: A value to use as a base for multiplication.

    :returns: Boolean dictating whether at least one multiply of `multiple_of` lies in the given range between minimum and maximum.
    """

    # if the range has infinity on one of its ends then infinite number of multipliers
    # can be found within the range

    # if we were given floats and multiple_of is really close to zero then it doesn't make sense
    # to continue trying to check the range
    if (
        isinstance(minimum, float)
        and isinstance(multiple_of, float)
        and minimum / multiple_of in [float("+inf"), float("-inf")]
    ):
        return False

    multiplier = round(minimum / multiple_of)
    step = 1 if multiple_of > 0 else -1

    # since rounding can go either up or down we may end up in a situation when
    # minimum is less or equal to `multiplier * multiple_of`
    # or when it is greater than `multiplier * multiple_of`
    # (in this case minimum is less than `(multiplier + 1)* multiple_of`). So we need to check
    # that any of two values is inside the given range. ASCII graphic below explain this
    #
    #                minimum
    # -----------------+-------+-----------------------------------+----------------------------
    #
    #
    #                                minimum
    # -------------------------+--------+--------------------------+----------------------------
    #
    # since `multiple_of` can be a negative number adding +1 to `multiplier` drives `(multiplier + 1) * multiple_of``
    # away from `minimum` to the -infinity. It looks like this:
    #                                                                               minimum
    # -----------------------+--------------------------------+------------------------+--------
    #
    # so for negative `multiple_of` we want to subtract 1 from multiplier
    for multiply in [multiplier * multiple_of, (multiplier + step) * multiple_of]:
        multiply_float = float(multiply)
        if (
            almost_equal_floats(multiply_float, float(minimum))
            or almost_equal_floats(multiply_float, float(maximum))
            or minimum < multiply < maximum
        ):
            return True

    return False


def passes_pydantic_multiple_validator(value: T, multiple_of: T) -> bool:
    """Determine whether a given value passes the pydantic multiple_of validation.

    :param value: A numeric value.
    :param multiple_of: Another numeric value.

    :returns: Boolean dictating whether value is a multiple of value.

    """
    if multiple_of == 0:
        return True
    mod = float(value) / float(multiple_of) % 1
    return almost_equal_floats(mod, 0.0) or almost_equal_floats(mod, 1.0)


def get_increment(t_type: type[T]) -> T:
    """Get a small increment base to add to constrained values, i.e. lt/gt entries.

    :param t_type: A value of type T.

    :returns: An increment T.
    """
    values: dict[Any, Any] = {
        int: 1,
        float: float_info.epsilon,
        Decimal: Decimal("0.001"),
    }
    return cast("T", values[t_type])


def get_value_or_none(
    t_type: type[T],
    lt: T | None = None,
    le: T | None = None,
    gt: T | None = None,
    ge: T | None = None,
) -> tuple[T | None, T | None]:
    """Return an optional value.

    :param equal_value: An GE/LE value.
    :param constrained: An GT/LT value.
    :param increment: increment

    :returns: Optional T.
    """
    if ge is not None:
        minimum_value = ge
    elif gt is not None:
        minimum_value = gt + get_increment(t_type)
    else:
        minimum_value = None

    if le is not None:
        maximum_value = le
    elif lt is not None:
        maximum_value = lt - get_increment(t_type)
    else:
        maximum_value = None
    return minimum_value, maximum_value


def get_constrained_number_range(
    t_type: type[T],
    random: Random,
    lt: T | None = None,
    le: T | None = None,
    gt: T | None = None,
    ge: T | None = None,
    multiple_of: T | None = None,
) -> tuple[T | None, T | None]:
    """Return the minimum and maximum values given a field_meta's constraints.

    :param t_type: A primitive constructor - int, float or Decimal.
    :param random: An instance of Random.
    :param lt: Less than value.
    :param le: Less than or equal value.
    :param gt: Greater than value.
    :param ge: Greater than or equal value.
    :param multiple_of: Multiple of value.

    :returns: a tuple of optional minimum and maximum values.
    """
    seed = t_type(random.random() * 10)
    minimum, maximum = get_value_or_none(lt=lt, le=le, gt=gt, ge=ge, t_type=t_type)

    if minimum is not None and maximum is not None and maximum < minimum:
        msg = "maximum value must be greater than minimum value"
        raise ParameterException(msg)

    if multiple_of is None:
        if minimum is not None and maximum is None:
            return (minimum, seed) if minimum == 0 else (minimum, minimum + seed)  # pyright: ignore[reportGeneralTypeIssues]
        if maximum is not None and minimum is None:
            return maximum - seed, maximum
    else:
        if multiple_of == 0.0:  # TODO: investigate @guacs # noqa: FIX002
            msg = "multiple_of can not be zero"
            raise ParameterException(msg)
        if (
            minimum is not None
            and maximum is not None
            and not is_multiply_of_multiple_of_in_range(minimum=minimum, maximum=maximum, multiple_of=multiple_of)
        ):
            msg = "given range should include at least one multiply of multiple_of"
            raise ParameterException(msg)

    return minimum, maximum


def generate_constrained_number(
    random: Random,
    minimum: T | None,
    maximum: T | None,
    multiple_of: T | None,
    method: "NumberGeneratorProtocol[T]",
) -> T:
    """Generate a constrained number, output depends on the passed in callbacks.

    :param random: An instance of random.
    :param minimum: A minimum value.
    :param maximum: A maximum value.
    :param multiple_of: A multiple of value.
    :param method: A function that generates numbers of type T.

    :returns: A value of type T.
    """
    if minimum is None or maximum is None:
        return multiple_of if multiple_of is not None else method(random=random)
    if multiple_of is None:
        return method(random=random, minimum=minimum, maximum=maximum)
    if multiple_of >= minimum:
        return multiple_of
    result = minimum
    while not passes_pydantic_multiple_validator(result, multiple_of):
        result = round(method(random=random, minimum=minimum, maximum=maximum) / multiple_of) * multiple_of
    return result


def handle_constrained_int(
    random: Random,
    multiple_of: int | None = None,
    gt: int | None = None,
    ge: int | None = None,
    lt: int | None = None,
    le: int | None = None,
) -> int:
    """Handle constrained integers.

    :param random: An instance of Random.
    :param lt: Less than value.
    :param le: Less than or equal value.
    :param gt: Greater than value.
    :param ge: Greater than or equal value.
    :param multiple_of: Multiple of value.

    :returns: An integer.

    """

    minimum, maximum = get_constrained_number_range(
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        t_type=int,
        multiple_of=multiple_of,
        random=random,
    )
    return generate_constrained_number(
        random=random,
        minimum=minimum,
        maximum=maximum,
        multiple_of=multiple_of,
        method=create_random_integer,
    )


def handle_constrained_float(
    random: Random,
    multiple_of: float | None = None,
    gt: float | None = None,
    ge: float | None = None,
    lt: float | None = None,
    le: float | None = None,
) -> float:
    """Handle constrained floats.

    :param random: An instance of Random.
    :param lt: Less than value.
    :param le: Less than or equal value.
    :param gt: Greater than value.
    :param ge: Greater than or equal value.
    :param multiple_of: Multiple of value.

    :returns: A float.
    """

    minimum, maximum = get_constrained_number_range(
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        t_type=float,
        multiple_of=multiple_of,
        random=random,
    )

    return generate_constrained_number(
        random=random,
        minimum=minimum,
        maximum=maximum,
        multiple_of=multiple_of,
        method=create_random_float,
    )


def validate_max_digits(
    max_digits: int,
    minimum: Decimal | None,
    decimal_places: int | None,
) -> None:
    """Validate that max digits is greater than minimum and decimal places.

    :param max_digits: The maximal number of digits for the decimal.
    :param minimum: Minimal value.
    :param decimal_places: Number of decimal places

    :returns: 'None'

    """
    if max_digits <= 0:
        msg = "max_digits must be greater than 0"
        raise ParameterException(msg)

    if minimum is not None:
        min_str = str(minimum).split(".")[1] if "." in str(minimum) else str(minimum)

        if max_digits <= len(min_str):
            msg = "minimum is greater than max_digits"
            raise ParameterException(msg)

    if decimal_places is not None and max_digits <= decimal_places:
        msg = "max_digits must be greater than decimal places"
        raise ParameterException(msg)


def handle_decimal_length(
    generated_decimal: Decimal,
    decimal_places: int | None,
    max_digits: int | None,
) -> Decimal:
    """Handle the length of the decimal.

    :param generated_decimal: A decimal value.
    :param decimal_places: Number of decimal places.
    :param max_digits: Maximal number of digits.

    """
    string_number = str(generated_decimal)
    sign = "-" if "-" in string_number else "+"
    string_number = string_number.replace("-", "")
    whole_numbers, decimals = string_number.split(".")

    if (
        max_digits is not None
        and decimal_places is not None
        and len(whole_numbers) + decimal_places > max_digits
        or (max_digits is None or decimal_places is None)
        and max_digits is not None
    ):
        max_decimals = max_digits - len(whole_numbers)
    elif max_digits is not None:
        max_decimals = decimal_places  # type: ignore[assignment]
    else:
        max_decimals = cast("int", decimal_places)

    if max_decimals < 0:  # pyright: ignore[reportOptionalOperand]
        return Decimal(sign + whole_numbers[:max_decimals])

    decimals = decimals[:max_decimals]
    return Decimal(sign + whole_numbers + "." + decimals[:decimal_places])


def handle_constrained_decimal(
    random: Random,
    multiple_of: Decimal | None = None,
    decimal_places: int | None = None,
    max_digits: int | None = None,
    gt: Decimal | None = None,
    ge: Decimal | None = None,
    lt: Decimal | None = None,
    le: Decimal | None = None,
) -> Decimal:
    """Handle a constrained decimal.

    :param random: An instance of Random.
    :param multiple_of: Multiple of value.
    :param decimal_places: Number of decimal places.
    :param max_digits: Maximal number of digits.
    :param lt: Less than value.
    :param le: Less than or equal value.
    :param gt: Greater than value.
    :param ge: Greater than or equal value.

    :returns: A decimal.

    """

    minimum, maximum = get_constrained_number_range(
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        t_type=Decimal,
        random=random,
    )

    if max_digits is not None:
        validate_max_digits(max_digits=max_digits, minimum=minimum, decimal_places=decimal_places)

    generated_decimal = generate_constrained_number(
        random=random,
        minimum=minimum,
        maximum=maximum,
        multiple_of=multiple_of,
        method=create_random_decimal,
    )

    if max_digits is not None or decimal_places is not None:
        return handle_decimal_length(
            generated_decimal=generated_decimal,
            max_digits=max_digits,
            decimal_places=decimal_places,
        )

    return generated_decimal
