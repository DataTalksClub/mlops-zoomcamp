import decimal

from ..decimal import Decimal
from ..objecttype import ObjectType
from ..schema import Schema


class Query(ObjectType):
    decimal = Decimal(input=Decimal())

    def resolve_decimal(self, info, input):
        return input


schema = Schema(query=Query)


def test_decimal_string_query():
    decimal_value = decimal.Decimal("1969.1974")
    result = schema.execute("""{ decimal(input: "%s") }""" % decimal_value)
    assert not result.errors
    assert result.data == {"decimal": str(decimal_value)}
    assert decimal.Decimal(result.data["decimal"]) == decimal_value


def test_decimal_string_query_variable():
    decimal_value = decimal.Decimal("1969.1974")

    result = schema.execute(
        """query Test($decimal: Decimal){ decimal(input: $decimal) }""",
        variables={"decimal": decimal_value},
    )
    assert not result.errors
    assert result.data == {"decimal": str(decimal_value)}
    assert decimal.Decimal(result.data["decimal"]) == decimal_value


def test_bad_decimal_query():
    not_a_decimal = "Nobody expects the Spanish Inquisition!"

    result = schema.execute("""{ decimal(input: "%s") }""" % not_a_decimal)
    assert result.errors
    assert len(result.errors) == 1
    assert result.data is None
    assert (
        result.errors[0].message
        == "Expected value of type 'Decimal', found \"Nobody expects the Spanish Inquisition!\"."
    )

    result = schema.execute("{ decimal(input: true) }")
    assert result.errors
    assert len(result.errors) == 1
    assert result.data is None
    assert result.errors[0].message == "Expected value of type 'Decimal', found true."

    result = schema.execute("{ decimal(input: 1.2) }")
    assert result.errors
    assert len(result.errors) == 1
    assert result.data is None
    assert result.errors[0].message == "Expected value of type 'Decimal', found 1.2."


def test_decimal_string_query_integer():
    decimal_value = 1
    result = schema.execute("""{ decimal(input: %s) }""" % decimal_value)
    assert not result.errors
    assert result.data == {"decimal": str(decimal_value)}
    assert decimal.Decimal(result.data["decimal"]) == decimal_value
