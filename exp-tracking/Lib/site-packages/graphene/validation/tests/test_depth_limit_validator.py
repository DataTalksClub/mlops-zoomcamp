import re

from pytest import raises
from graphql import parse, get_introspection_query, validate

from ...types import Schema, ObjectType, Interface
from ...types import String, Int, List, Field
from ..depth_limit import depth_limit_validator


class PetType(Interface):
    name = String(required=True)

    class meta:
        name = "Pet"


class CatType(ObjectType):
    class meta:
        name = "Cat"
        interfaces = (PetType,)


class DogType(ObjectType):
    class meta:
        name = "Dog"
        interfaces = (PetType,)


class AddressType(ObjectType):
    street = String(required=True)
    number = Int(required=True)
    city = String(required=True)
    country = String(required=True)

    class Meta:
        name = "Address"


class HumanType(ObjectType):
    name = String(required=True)
    email = String(required=True)
    address = Field(AddressType, required=True)
    pets = List(PetType, required=True)

    class Meta:
        name = "Human"


class Query(ObjectType):
    user = Field(HumanType, required=True, name=String())
    version = String(required=True)
    user1 = Field(HumanType, required=True)
    user2 = Field(HumanType, required=True)
    user3 = Field(HumanType, required=True)

    @staticmethod
    def resolve_user(root, info, name=None):
        pass


schema = Schema(query=Query)


def run_query(query: str, max_depth: int, ignore=None):
    document = parse(query)

    result = None

    def callback(query_depths):
        nonlocal result
        result = query_depths

    errors = validate(
        schema=schema.graphql_schema,
        document_ast=document,
        rules=(
            depth_limit_validator(
                max_depth=max_depth, ignore=ignore, callback=callback
            ),
        ),
    )

    return errors, result


def test_should_count_depth_without_fragment():
    query = """
    query read0 {
      version
    }
    query read1 {
      version
      user {
        name
      }
    }
    query read2 {
      matt: user(name: "matt") {
        email
      }
      andy: user(name: "andy") {
        email
        address {
          city
        }
      }
    }
    query read3 {
      matt: user(name: "matt") {
        email
      }
      andy: user(name: "andy") {
        email
        address {
          city
        }
        pets {
          name
          owner {
            name
          }
        }
      }
    }
    """

    expected = {"read0": 0, "read1": 1, "read2": 2, "read3": 3}

    errors, result = run_query(query, 10)
    assert not errors
    assert result == expected


def test_should_count_with_fragments():
    query = """
    query read0 {
      ... on Query {
        version
      }
    }
    query read1 {
      version
      user {
        ... on Human {
          name
        }
      }
    }
    fragment humanInfo on Human {
      email
    }
    fragment petInfo on Pet {
      name
      owner {
        name
      }
    }
    query read2 {
      matt: user(name: "matt") {
        ...humanInfo
      }
      andy: user(name: "andy") {
        ...humanInfo
        address {
          city
        }
      }
    }
    query read3 {
      matt: user(name: "matt") {
        ...humanInfo
      }
      andy: user(name: "andy") {
        ... on Human {
          email
        }
        address {
          city
        }
        pets {
          ...petInfo
        }
      }
    }
  """

    expected = {"read0": 0, "read1": 1, "read2": 2, "read3": 3}

    errors, result = run_query(query, 10)
    assert not errors
    assert result == expected


def test_should_ignore_the_introspection_query():
    errors, result = run_query(get_introspection_query(), 10)
    assert not errors
    assert result == {"IntrospectionQuery": 0}


def test_should_catch_very_deep_query():
    query = """{
    user {
      pets {
        owner {
          pets {
            owner {
              pets {
                name
              }
            }
          }
        }
      }
    }
    }
    """
    errors, result = run_query(query, 4)

    assert len(errors) == 1
    assert errors[0].message == "'anonymous' exceeds maximum operation depth of 4."


def test_should_ignore_field():
    query = """
    query read1 {
      user { address { city } }
    }
    query read2 {
      user1 { address { city } }
      user2 { address { city } }
      user3 { address { city } }
    }
    """

    errors, result = run_query(
        query,
        10,
        ignore=["user1", re.compile("user2"), lambda field_name: field_name == "user3"],
    )

    expected = {"read1": 2, "read2": 0}
    assert not errors
    assert result == expected


def test_should_raise_invalid_ignore():
    query = """
    query read1 {
      user { address { city } }
    }
    """
    with raises(ValueError, match="Invalid ignore option:"):
        run_query(query, 10, ignore=[True])
