from __future__ import absolute_import

from decimal import Decimal as _Decimal

from graphql import Undefined
from graphql.language.ast import StringValueNode, IntValueNode

from .scalars import Scalar


class Decimal(Scalar):
    """
    The `Decimal` scalar type represents a python Decimal.
    """

    @staticmethod
    def serialize(dec):
        if isinstance(dec, str):
            dec = _Decimal(dec)
        assert isinstance(
            dec, _Decimal
        ), f'Received not compatible Decimal "{repr(dec)}"'
        return str(dec)

    @classmethod
    def parse_literal(cls, node, _variables=None):
        if isinstance(node, (StringValueNode, IntValueNode)):
            return cls.parse_value(node.value)
        return Undefined

    @staticmethod
    def parse_value(value):
        try:
            return _Decimal(value)
        except Exception:
            return Undefined
