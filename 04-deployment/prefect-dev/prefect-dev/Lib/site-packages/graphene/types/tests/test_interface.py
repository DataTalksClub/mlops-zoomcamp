from ..field import Field
from ..interface import Interface
from ..objecttype import ObjectType
from ..scalars import String
from ..schema import Schema
from ..unmountedtype import UnmountedType


class MyType:
    pass


class MyScalar(UnmountedType):
    def get_type(self):
        return MyType


def test_generate_interface():
    class MyInterface(Interface):
        """Documentation"""

    assert MyInterface._meta.name == "MyInterface"
    assert MyInterface._meta.description == "Documentation"
    assert MyInterface._meta.fields == {}


def test_generate_interface_with_meta():
    class MyFirstInterface(Interface):
        pass

    class MyInterface(Interface):
        class Meta:
            name = "MyOtherInterface"
            description = "Documentation"
            interfaces = [MyFirstInterface]

    assert MyInterface._meta.name == "MyOtherInterface"
    assert MyInterface._meta.description == "Documentation"
    assert MyInterface._meta.interfaces == [MyFirstInterface]


def test_generate_interface_with_fields():
    class MyInterface(Interface):
        field = Field(MyType)

    assert "field" in MyInterface._meta.fields


def test_ordered_fields_in_interface():
    class MyInterface(Interface):
        b = Field(MyType)
        a = Field(MyType)
        field = MyScalar()
        asa = Field(MyType)

    assert list(MyInterface._meta.fields) == ["b", "a", "field", "asa"]


def test_generate_interface_unmountedtype():
    class MyInterface(Interface):
        field = MyScalar()

    assert "field" in MyInterface._meta.fields
    assert isinstance(MyInterface._meta.fields["field"], Field)


def test_generate_interface_inherit_abstracttype():
    class MyAbstractType:
        field1 = MyScalar()

    class MyInterface(Interface, MyAbstractType):
        field2 = MyScalar()

    assert list(MyInterface._meta.fields) == ["field1", "field2"]
    assert [type(x) for x in MyInterface._meta.fields.values()] == [Field, Field]


def test_generate_interface_inherit_interface():
    class MyBaseInterface(Interface):
        field1 = MyScalar()

    class MyInterface(MyBaseInterface):
        field2 = MyScalar()

    assert MyInterface._meta.name == "MyInterface"
    assert list(MyInterface._meta.fields) == ["field1", "field2"]
    assert [type(x) for x in MyInterface._meta.fields.values()] == [Field, Field]


def test_generate_interface_inherit_abstracttype_reversed():
    class MyAbstractType:
        field1 = MyScalar()

    class MyInterface(MyAbstractType, Interface):
        field2 = MyScalar()

    assert list(MyInterface._meta.fields) == ["field1", "field2"]
    assert [type(x) for x in MyInterface._meta.fields.values()] == [Field, Field]


def test_resolve_type_default():
    class MyInterface(Interface):
        field2 = String()

    class MyTestType(ObjectType):
        class Meta:
            interfaces = (MyInterface,)

    class Query(ObjectType):
        test = Field(MyInterface)

        def resolve_test(_, info):
            return MyTestType()

    schema = Schema(query=Query, types=[MyTestType])

    result = schema.execute(
        """
        query {
            test {
                __typename
            }
        }
    """
    )
    assert not result.errors
    assert result.data == {"test": {"__typename": "MyTestType"}}


def test_resolve_type_custom():
    class MyInterface(Interface):
        field2 = String()

        @classmethod
        def resolve_type(cls, instance, info):
            if instance["type"] == 1:
                return MyTestType1
            return MyTestType2

    class MyTestType1(ObjectType):
        class Meta:
            interfaces = (MyInterface,)

    class MyTestType2(ObjectType):
        class Meta:
            interfaces = (MyInterface,)

    class Query(ObjectType):
        test = Field(MyInterface)

        def resolve_test(_, info):
            return {"type": 1}

    schema = Schema(query=Query, types=[MyTestType1, MyTestType2])

    result = schema.execute(
        """
        query {
            test {
                __typename
            }
        }
    """
    )
    assert not result.errors
    assert result.data == {"test": {"__typename": "MyTestType1"}}


def test_resolve_type_custom_interferes():
    class MyInterface(Interface):
        field2 = String()
        type_ = String(name="type")

        def resolve_type_(_, info):
            return "foo"

    class MyTestType1(ObjectType):
        class Meta:
            interfaces = (MyInterface,)

    class MyTestType2(ObjectType):
        class Meta:
            interfaces = (MyInterface,)

    class Query(ObjectType):
        test = Field(MyInterface)

        def resolve_test(_, info):
            return MyTestType1()

    schema = Schema(query=Query, types=[MyTestType1, MyTestType2])

    result = schema.execute(
        """
        query {
            test {
                __typename
                type
            }
        }
    """
    )
    assert not result.errors
    assert result.data == {"test": {"__typename": "MyTestType1", "type": "foo"}}
