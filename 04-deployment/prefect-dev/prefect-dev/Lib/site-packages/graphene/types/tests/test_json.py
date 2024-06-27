from ..json import JSONString
from ..objecttype import ObjectType
from ..schema import Schema


class Query(ObjectType):
    json = JSONString(input=JSONString())

    def resolve_json(self, info, input):
        return input


schema = Schema(query=Query)


def test_jsonstring_query():
    json_value = '{"key": "value"}'

    json_value_quoted = json_value.replace('"', '\\"')
    result = schema.execute("""{ json(input: "%s") }""" % json_value_quoted)
    assert not result.errors
    assert result.data == {"json": json_value}

    result = schema.execute("""{ json(input: "{}") }""")
    assert not result.errors
    assert result.data == {"json": "{}"}


def test_jsonstring_query_variable():
    json_value = '{"key": "value"}'

    result = schema.execute(
        """query Test($json: JSONString){ json(input: $json) }""",
        variables={"json": json_value},
    )
    assert not result.errors
    assert result.data == {"json": json_value}


def test_jsonstring_optional_uuid_input():
    """
    Test that we can provide a null value to an optional input
    """
    result = schema.execute("{ json(input: null) }")
    assert not result.errors
    assert result.data == {"json": None}


def test_jsonstring_invalid_query():
    """
    Test that if an invalid type is provided we get an error
    """
    result = schema.execute("{ json(input: 1) }")
    assert result.errors
    assert len(result.errors) == 1
    assert result.errors[0].message == "Expected value of type 'JSONString', found 1."

    result = schema.execute("{ json(input: {}) }")
    assert result.errors
    assert len(result.errors) == 1
    assert result.errors[0].message == "Expected value of type 'JSONString', found {}."

    result = schema.execute('{ json(input: "a") }')
    assert result.errors
    assert len(result.errors) == 1
    assert result.errors[0].message == (
        "Expected value of type 'JSONString', found \"a\"; "
        "Badly formed JSONString: Expecting value: line 1 column 1 (char 0)"
    )

    result = schema.execute("""{ json(input: "{\\'key\\': 0}") }""")
    assert result.errors
    assert len(result.errors) == 1
    assert (
        result.errors[0].message
        == "Syntax Error: Invalid character escape sequence: '\\''."
    )

    result = schema.execute("""{ json(input: "{\\"key\\": 0,}") }""")
    assert result.errors
    assert len(result.errors) == 1
    assert result.errors[0].message == (
        'Expected value of type \'JSONString\', found "{\\"key\\": 0,}"; '
        "Badly formed JSONString: Expecting property name enclosed in double quotes: line 1 column 11 (char 10)"
    )
