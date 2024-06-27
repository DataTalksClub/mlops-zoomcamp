from binascii import Error as _Error
from base64 import b64decode, b64encode

from graphql.error import GraphQLError
from graphql.language import StringValueNode, print_ast

from .scalars import Scalar


class Base64(Scalar):
    """
    The `Base64` scalar type represents a base64-encoded String.
    """

    @staticmethod
    def serialize(value):
        if not isinstance(value, bytes):
            if isinstance(value, str):
                value = value.encode("utf-8")
            else:
                value = str(value).encode("utf-8")
        return b64encode(value).decode("utf-8")

    @classmethod
    def parse_literal(cls, node, _variables=None):
        if not isinstance(node, StringValueNode):
            raise GraphQLError(
                f"Base64 cannot represent non-string value: {print_ast(node)}"
            )
        return cls.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        if not isinstance(value, bytes):
            if not isinstance(value, str):
                raise GraphQLError(
                    f"Base64 cannot represent non-string value: {repr(value)}"
                )
            value = value.encode("utf-8")
        try:
            return b64decode(value, validate=True).decode("utf-8")
        except _Error:
            raise GraphQLError(f"Base64 cannot decode value: {repr(value)}")
