from __future__ import unicode_literals

from graphql.language.ast import (
    BooleanValueNode,
    FloatValueNode,
    IntValueNode,
    ListValueNode,
    ObjectValueNode,
    StringValueNode,
)

from graphene.types.scalars import MAX_INT, MIN_INT

from .scalars import Scalar


class GenericScalar(Scalar):
    """
    The `GenericScalar` scalar type represents a generic
    GraphQL scalar value that could be:
    String, Boolean, Int, Float, List or Object.
    """

    @staticmethod
    def identity(value):
        return value

    serialize = identity
    parse_value = identity

    @staticmethod
    def parse_literal(ast, _variables=None):
        if isinstance(ast, (StringValueNode, BooleanValueNode)):
            return ast.value
        elif isinstance(ast, IntValueNode):
            num = int(ast.value)
            if MIN_INT <= num <= MAX_INT:
                return num
        elif isinstance(ast, FloatValueNode):
            return float(ast.value)
        elif isinstance(ast, ListValueNode):
            return [GenericScalar.parse_literal(value) for value in ast.values]
        elif isinstance(ast, ObjectValueNode):
            return {
                field.name.value: GenericScalar.parse_literal(field.value)
                for field in ast.fields
            }
        else:
            return None
