from textwrap import dedent

from pytest import raises

from graphql.type import GraphQLObjectType, GraphQLSchema

from ..field import Field
from ..objecttype import ObjectType
from ..scalars import String
from ..schema import Schema


class MyOtherType(ObjectType):
    field = String()


class Query(ObjectType):
    inner = Field(MyOtherType)


def test_schema():
    schema = Schema(Query)
    graphql_schema = schema.graphql_schema
    assert isinstance(graphql_schema, GraphQLSchema)
    query_type = graphql_schema.query_type
    assert isinstance(query_type, GraphQLObjectType)
    assert query_type.name == "Query"
    assert query_type.graphene_type is Query


def test_schema_get_type():
    schema = Schema(Query)
    assert schema.Query == Query
    assert schema.MyOtherType == MyOtherType


def test_schema_get_type_error():
    schema = Schema(Query)
    with raises(AttributeError) as exc_info:
        schema.X

    assert str(exc_info.value) == 'Type "X" not found in the Schema'


def test_schema_str():
    schema = Schema(Query)
    assert (
        str(schema).strip()
        == dedent(
            """
        type Query {
          inner: MyOtherType
        }

        type MyOtherType {
          field: String
        }
        """
        ).strip()
    )


def test_schema_introspect():
    schema = Schema(Query)
    assert "__schema" in schema.introspect()


def test_schema_requires_query_type():
    schema = Schema()
    result = schema.execute("query {}")

    assert len(result.errors) == 1
    error = result.errors[0]
    assert error.message == "Query root type must be provided."
