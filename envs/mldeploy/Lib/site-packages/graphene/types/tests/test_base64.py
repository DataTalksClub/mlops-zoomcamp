import base64

from graphql import GraphQLError

from ..objecttype import ObjectType
from ..scalars import String
from ..schema import Schema
from ..base64 import Base64


class Query(ObjectType):
    base64 = Base64(_in=Base64(name="input"), _match=String(name="match"))
    bytes_as_base64 = Base64()
    string_as_base64 = Base64()
    number_as_base64 = Base64()

    def resolve_base64(self, info, _in=None, _match=None):
        if _match:
            assert _in == _match
        return _in

    def resolve_bytes_as_base64(self, info):
        return b"Hello world"

    def resolve_string_as_base64(self, info):
        return "Spam and eggs"

    def resolve_number_as_base64(self, info):
        return 42


schema = Schema(query=Query)


def test_base64_query():
    base64_value = base64.b64encode(b"Random string").decode("utf-8")
    result = schema.execute(
        """{{ base64(input: "{}", match: "Random string") }}""".format(base64_value)
    )
    assert not result.errors
    assert result.data == {"base64": base64_value}


def test_base64_query_with_variable():
    base64_value = base64.b64encode(b"Another string").decode("utf-8")

    # test datetime variable in string representation
    result = schema.execute(
        """
        query GetBase64($base64: Base64) {
            base64(input: $base64, match: "Another string")
        }
        """,
        variables={"base64": base64_value},
    )
    assert not result.errors
    assert result.data == {"base64": base64_value}


def test_base64_query_none():
    result = schema.execute("""{ base64 }""")
    assert not result.errors
    assert result.data == {"base64": None}


def test_base64_query_invalid():
    bad_inputs = [dict(), 123, "This is not valid base64"]

    for input_ in bad_inputs:
        result = schema.execute(
            """{ base64(input: $input) }""", variables={"input": input_}
        )
        assert isinstance(result.errors, list)
        assert len(result.errors) == 1
        assert isinstance(result.errors[0], GraphQLError)
        assert result.data is None


def test_base64_from_bytes():
    base64_value = base64.b64encode(b"Hello world").decode("utf-8")
    result = schema.execute("""{ bytesAsBase64 }""")
    assert not result.errors
    assert result.data == {"bytesAsBase64": base64_value}


def test_base64_from_string():
    base64_value = base64.b64encode(b"Spam and eggs").decode("utf-8")
    result = schema.execute("""{ stringAsBase64 }""")
    assert not result.errors
    assert result.data == {"stringAsBase64": base64_value}


def test_base64_from_number():
    base64_value = base64.b64encode(b"42").decode("utf-8")
    result = schema.execute("""{ numberAsBase64 }""")
    assert not result.errors
    assert result.data == {"numberAsBase64": base64_value}
