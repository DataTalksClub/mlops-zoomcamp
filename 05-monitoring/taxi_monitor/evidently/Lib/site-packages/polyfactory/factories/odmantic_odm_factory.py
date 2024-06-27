from __future__ import annotations

import decimal
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar, Union

from polyfactory.exceptions import MissingDependencyException
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.utils.predicates import is_safe_subclass
from polyfactory.value_generators.primitives import create_random_bytes

try:
    from bson.decimal128 import Decimal128, create_decimal128_context
    from odmantic import EmbeddedModel, Model
    from odmantic import bson as odbson

except ImportError as e:
    msg = "odmantic is not installed"
    raise MissingDependencyException(msg) from e

T = TypeVar("T", bound=Union[Model, EmbeddedModel])

if TYPE_CHECKING:
    from typing_extensions import TypeGuard


class OdmanticModelFactory(Generic[T], ModelFactory[T]):
    """Base factory for odmantic models"""

    __is_base_factory__ = True

    @classmethod
    def is_supported_type(cls, value: Any) -> "TypeGuard[type[T]]":
        """Determine whether the given value is supported by the factory.

        :param value: An arbitrary value.
        :returns: A typeguard
        """
        return is_safe_subclass(value, (Model, EmbeddedModel))

    @classmethod
    def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
        provider_map = super().get_provider_map()
        provider_map.update(
            {
                odbson.Int64: lambda: odbson.Int64.validate(cls.__faker__.pyint()),
                odbson.Decimal128: lambda: _to_decimal128(cls.__faker__.pydecimal()),
                odbson.Binary: lambda: odbson.Binary.validate(create_random_bytes(cls.__random__)),
                odbson._datetime: lambda: odbson._datetime.validate(cls.__faker__.date_time_between()),
                # bson.Regex and bson._Pattern not supported as there is no way to generate
                # a random regular expression with Faker
                # bson.Regex:
                # bson._Pattern:
            },
        )
        return provider_map


def _to_decimal128(value: decimal.Decimal) -> Decimal128:
    with decimal.localcontext(create_decimal128_context()) as ctx:
        return Decimal128(ctx.create_decimal(value))
