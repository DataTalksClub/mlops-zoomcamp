import pytest

from ...types.base64 import Base64
from ...types.datetime import Date, DateTime
from ...types.decimal import Decimal
from ...types.generic import GenericScalar
from ...types.json import JSONString
from ...types.objecttype import ObjectType
from ...types.scalars import ID, BigInt, Boolean, Float, Int, String
from ...types.schema import Schema
from ...types.uuid import UUID


@pytest.mark.parametrize(
    "input_type,input_value",
    [
        (Date, '"2022-02-02"'),
        (GenericScalar, '"foo"'),
        (Int, "1"),
        (BigInt, "12345678901234567890"),
        (Float, "1.1"),
        (String, '"foo"'),
        (Boolean, "true"),
        (ID, "1"),
        (DateTime, '"2022-02-02T11:11:11"'),
        (UUID, '"cbebbc62-758e-4f75-a890-bc73b5017d81"'),
        (Decimal, '"1.1"'),
        (JSONString, '"{\\"key\\":\\"foo\\",\\"value\\":\\"bar\\"}"'),
        (Base64, '"Q2hlbG8gd29ycmxkCg=="'),
    ],
)
def test_parse_literal_with_variables(input_type, input_value):
    # input_b needs to be evaluated as literal while the variable dict for
    # input_a is passed along.

    class Query(ObjectType):
        generic = GenericScalar(input_a=GenericScalar(), input_b=input_type())

        def resolve_generic(self, info, input_a=None, input_b=None):
            return input

    schema = Schema(query=Query)

    query = f"""
        query Test($a: GenericScalar){{
            generic(inputA: $a, inputB: {input_value})
        }}
    """
    result = schema.execute(
        query,
        variables={"a": "bar"},
    )
    assert not result.errors
