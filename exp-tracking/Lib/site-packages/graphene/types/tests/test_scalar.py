from ..objecttype import ObjectType, Field
from ..scalars import Scalar, Int, BigInt, Float, String, Boolean
from ..schema import Schema
from graphql import Undefined
from graphql.language.ast import IntValueNode


def test_scalar():
    class JSONScalar(Scalar):
        """Documentation"""

    assert JSONScalar._meta.name == "JSONScalar"
    assert JSONScalar._meta.description == "Documentation"


def test_ints():
    assert Int.parse_value(2**31 - 1) is not Undefined
    assert Int.parse_value("2.0") == 2
    assert Int.parse_value(2**31) is Undefined

    assert Int.parse_literal(IntValueNode(value=str(2**31 - 1))) == 2**31 - 1
    assert Int.parse_literal(IntValueNode(value=str(2**31))) is Undefined

    assert Int.parse_value(-(2**31)) is not Undefined
    assert Int.parse_value(-(2**31) - 1) is Undefined

    assert BigInt.parse_value(2**31) is not Undefined
    assert BigInt.parse_value("2.0") == 2
    assert BigInt.parse_value(-(2**31) - 1) is not Undefined

    assert BigInt.parse_literal(IntValueNode(value=str(2**31 - 1))) == 2**31 - 1
    assert BigInt.parse_literal(IntValueNode(value=str(2**31))) == 2**31


def return_input(_parent, _info, input):
    return input


class Optional(ObjectType):
    int = Int(input=Int(), resolver=return_input)
    big_int = BigInt(input=BigInt(), resolver=return_input)
    float = Float(input=Float(), resolver=return_input)
    bool = Boolean(input=Boolean(), resolver=return_input)
    string = String(input=String(), resolver=return_input)


class Query(ObjectType):
    optional = Field(Optional)

    def resolve_optional(self, info):
        return Optional()

    def resolve_required(self, info, input):
        return input


schema = Schema(query=Query)


class TestInt:
    def test_query(self):
        """
        Test that a normal query works.
        """
        result = schema.execute("{ optional { int(input: 20) } }")
        assert not result.errors
        assert result.data == {"optional": {"int": 20}}

    def test_optional_input(self):
        """
        Test that we can provide a null value to an optional input
        """
        result = schema.execute("{ optional { int(input: null) } }")
        assert not result.errors
        assert result.data == {"optional": {"int": None}}

    def test_invalid_input(self):
        """
        Test that if an invalid type is provided we get an error
        """
        result = schema.execute('{ optional { int(input: "20") } }')
        assert result.errors
        assert len(result.errors) == 1
        assert (
            result.errors[0].message == 'Int cannot represent non-integer value: "20"'
        )

        result = schema.execute('{ optional { int(input: "a") } }')
        assert result.errors
        assert len(result.errors) == 1
        assert result.errors[0].message == 'Int cannot represent non-integer value: "a"'

        result = schema.execute("{ optional { int(input: true) } }")
        assert result.errors
        assert len(result.errors) == 1
        assert (
            result.errors[0].message == "Int cannot represent non-integer value: true"
        )


class TestBigInt:
    def test_query(self):
        """
        Test that a normal query works.
        """
        value = 2**31
        result = schema.execute("{ optional { bigInt(input: %s) } }" % value)
        assert not result.errors
        assert result.data == {"optional": {"bigInt": value}}

    def test_optional_input(self):
        """
        Test that we can provide a null value to an optional input
        """
        result = schema.execute("{ optional { bigInt(input: null) } }")
        assert not result.errors
        assert result.data == {"optional": {"bigInt": None}}

    def test_invalid_input(self):
        """
        Test that if an invalid type is provided we get an error
        """
        result = schema.execute('{ optional { bigInt(input: "20") } }')
        assert result.errors
        assert len(result.errors) == 1
        assert (
            result.errors[0].message == "Expected value of type 'BigInt', found \"20\"."
        )

        result = schema.execute('{ optional { bigInt(input: "a") } }')
        assert result.errors
        assert len(result.errors) == 1
        assert (
            result.errors[0].message == "Expected value of type 'BigInt', found \"a\"."
        )

        result = schema.execute("{ optional { bigInt(input: true) } }")
        assert result.errors
        assert len(result.errors) == 1
        assert (
            result.errors[0].message == "Expected value of type 'BigInt', found true."
        )


class TestFloat:
    def test_query(self):
        """
        Test that a normal query works.
        """
        result = schema.execute("{ optional { float(input: 20) } }")
        assert not result.errors
        assert result.data == {"optional": {"float": 20.0}}

        result = schema.execute("{ optional { float(input: 20.2) } }")
        assert not result.errors
        assert result.data == {"optional": {"float": 20.2}}

    def test_optional_input(self):
        """
        Test that we can provide a null value to an optional input
        """
        result = schema.execute("{ optional { float(input: null) } }")
        assert not result.errors
        assert result.data == {"optional": {"float": None}}

    def test_invalid_input(self):
        """
        Test that if an invalid type is provided we get an error
        """
        result = schema.execute('{ optional { float(input: "20") } }')
        assert result.errors
        assert len(result.errors) == 1
        assert (
            result.errors[0].message == 'Float cannot represent non numeric value: "20"'
        )

        result = schema.execute('{ optional { float(input: "a") } }')
        assert result.errors
        assert len(result.errors) == 1
        assert (
            result.errors[0].message == 'Float cannot represent non numeric value: "a"'
        )

        result = schema.execute("{ optional { float(input: true) } }")
        assert result.errors
        assert len(result.errors) == 1
        assert (
            result.errors[0].message == "Float cannot represent non numeric value: true"
        )


class TestBoolean:
    def test_query(self):
        """
        Test that a normal query works.
        """
        result = schema.execute("{ optional { bool(input: true) } }")
        assert not result.errors
        assert result.data == {"optional": {"bool": True}}

        result = schema.execute("{ optional { bool(input: false) } }")
        assert not result.errors
        assert result.data == {"optional": {"bool": False}}

    def test_optional_input(self):
        """
        Test that we can provide a null value to an optional input
        """
        result = schema.execute("{ optional { bool(input: null) } }")
        assert not result.errors
        assert result.data == {"optional": {"bool": None}}

    def test_invalid_input(self):
        """
        Test that if an invalid type is provided we get an error
        """
        result = schema.execute('{ optional { bool(input: "True") } }')
        assert result.errors
        assert len(result.errors) == 1
        assert (
            result.errors[0].message
            == 'Boolean cannot represent a non boolean value: "True"'
        )

        result = schema.execute('{ optional { bool(input: "true") } }')
        assert result.errors
        assert len(result.errors) == 1
        assert (
            result.errors[0].message
            == 'Boolean cannot represent a non boolean value: "true"'
        )

        result = schema.execute('{ optional { bool(input: "a") } }')
        assert result.errors
        assert len(result.errors) == 1
        assert (
            result.errors[0].message
            == 'Boolean cannot represent a non boolean value: "a"'
        )

        result = schema.execute("{ optional { bool(input: 1) } }")
        assert result.errors
        assert len(result.errors) == 1
        assert (
            result.errors[0].message
            == "Boolean cannot represent a non boolean value: 1"
        )

        result = schema.execute("{ optional { bool(input: 0) } }")
        assert result.errors
        assert len(result.errors) == 1
        assert (
            result.errors[0].message
            == "Boolean cannot represent a non boolean value: 0"
        )


class TestString:
    def test_query(self):
        """
        Test that a normal query works.
        """
        result = schema.execute('{ optional { string(input: "something something") } }')
        assert not result.errors
        assert result.data == {"optional": {"string": "something something"}}

        result = schema.execute('{ optional { string(input: "True") } }')
        assert not result.errors
        assert result.data == {"optional": {"string": "True"}}

        result = schema.execute('{ optional { string(input: "0") } }')
        assert not result.errors
        assert result.data == {"optional": {"string": "0"}}

    def test_optional_input(self):
        """
        Test that we can provide a null value to an optional input
        """
        result = schema.execute("{ optional { string(input: null) } }")
        assert not result.errors
        assert result.data == {"optional": {"string": None}}

    def test_invalid_input(self):
        """
        Test that if an invalid type is provided we get an error
        """
        result = schema.execute("{ optional { string(input: 1) } }")
        assert result.errors
        assert len(result.errors) == 1
        assert (
            result.errors[0].message == "String cannot represent a non string value: 1"
        )

        result = schema.execute("{ optional { string(input: 3.2) } }")
        assert result.errors
        assert len(result.errors) == 1
        assert (
            result.errors[0].message
            == "String cannot represent a non string value: 3.2"
        )

        result = schema.execute("{ optional { string(input: true) } }")
        assert result.errors
        assert len(result.errors) == 1
        assert (
            result.errors[0].message
            == "String cannot represent a non string value: true"
        )
