from pytest import raises

from ..field import Field
from ..interface import Interface
from ..objecttype import ObjectType
from ..scalars import String
from ..schema import Schema
from ..structures import NonNull
from ..unmountedtype import UnmountedType


class MyType(Interface):
    pass


class Container(ObjectType):
    field1 = Field(MyType)
    field2 = Field(MyType)


class MyInterface(Interface):
    ifield = Field(MyType)


class ContainerWithInterface(ObjectType):
    class Meta:
        interfaces = (MyInterface,)

    field1 = Field(MyType)
    field2 = Field(MyType)


class MyScalar(UnmountedType):
    def get_type(self):
        return MyType


def test_generate_objecttype():
    class MyObjectType(ObjectType):
        """Documentation"""

    assert MyObjectType._meta.name == "MyObjectType"
    assert MyObjectType._meta.description == "Documentation"
    assert MyObjectType._meta.interfaces == tuple()
    assert MyObjectType._meta.fields == {}
    assert (
        repr(MyObjectType)
        == "<MyObjectType meta=<ObjectTypeOptions name='MyObjectType'>>"
    )


def test_generate_objecttype_with_meta():
    class MyObjectType(ObjectType):
        class Meta:
            name = "MyOtherObjectType"
            description = "Documentation"
            interfaces = (MyType,)

    assert MyObjectType._meta.name == "MyOtherObjectType"
    assert MyObjectType._meta.description == "Documentation"
    assert MyObjectType._meta.interfaces == (MyType,)


def test_generate_lazy_objecttype():
    class MyObjectType(ObjectType):
        example = Field(lambda: InnerObjectType, required=True)

    class InnerObjectType(ObjectType):
        field = Field(MyType)

    assert MyObjectType._meta.name == "MyObjectType"
    example_field = MyObjectType._meta.fields["example"]
    assert isinstance(example_field.type, NonNull)
    assert example_field.type.of_type == InnerObjectType


def test_generate_objecttype_with_fields():
    class MyObjectType(ObjectType):
        field = Field(MyType)

    assert "field" in MyObjectType._meta.fields


def test_generate_objecttype_with_private_attributes():
    class MyObjectType(ObjectType):
        def __init__(self, _private_state=None, **kwargs):
            self._private_state = _private_state
            super().__init__(**kwargs)

        _private_state = None

    assert "_private_state" not in MyObjectType._meta.fields
    assert hasattr(MyObjectType, "_private_state")

    m = MyObjectType(_private_state="custom")
    assert m._private_state == "custom"

    with raises(TypeError):
        MyObjectType(_other_private_state="Wrong")


def test_ordered_fields_in_objecttype():
    class MyObjectType(ObjectType):
        b = Field(MyType)
        a = Field(MyType)
        field = MyScalar()
        asa = Field(MyType)

    assert list(MyObjectType._meta.fields) == ["b", "a", "field", "asa"]


def test_generate_objecttype_inherit_abstracttype():
    class MyAbstractType:
        field1 = MyScalar()

    class MyObjectType(ObjectType, MyAbstractType):
        field2 = MyScalar()

    assert MyObjectType._meta.description is None
    assert MyObjectType._meta.interfaces == ()
    assert MyObjectType._meta.name == "MyObjectType"
    assert list(MyObjectType._meta.fields) == ["field1", "field2"]
    assert list(map(type, MyObjectType._meta.fields.values())) == [Field, Field]


def test_generate_objecttype_inherit_abstracttype_reversed():
    class MyAbstractType:
        field1 = MyScalar()

    class MyObjectType(MyAbstractType, ObjectType):
        field2 = MyScalar()

    assert MyObjectType._meta.description is None
    assert MyObjectType._meta.interfaces == ()
    assert MyObjectType._meta.name == "MyObjectType"
    assert list(MyObjectType._meta.fields) == ["field1", "field2"]
    assert list(map(type, MyObjectType._meta.fields.values())) == [Field, Field]


def test_generate_objecttype_unmountedtype():
    class MyObjectType(ObjectType):
        field = MyScalar()

    assert "field" in MyObjectType._meta.fields
    assert isinstance(MyObjectType._meta.fields["field"], Field)


def test_parent_container_get_fields():
    assert list(Container._meta.fields) == ["field1", "field2"]


def test_parent_container_interface_get_fields():
    assert list(ContainerWithInterface._meta.fields) == ["ifield", "field1", "field2"]


def test_objecttype_as_container_only_args():
    container = Container("1", "2")
    assert container.field1 == "1"
    assert container.field2 == "2"


def test_objecttype_repr():
    container = Container("1", "2")
    assert repr(container) == "Container(field1='1', field2='2')"


def test_objecttype_eq():
    container1 = Container("1", "2")
    container2 = Container("1", "2")
    container3 = Container("2", "3")
    assert container1 == container1
    assert container1 == container2
    assert container2 != container3


def test_objecttype_as_container_args_kwargs():
    container = Container("1", field2="2")
    assert container.field1 == "1"
    assert container.field2 == "2"


def test_objecttype_as_container_few_kwargs():
    container = Container(field2="2")
    assert container.field2 == "2"


def test_objecttype_as_container_all_kwargs():
    container = Container(field1="1", field2="2")
    assert container.field1 == "1"
    assert container.field2 == "2"


def test_objecttype_as_container_extra_args():
    msg = r"__init__\(\) takes from 1 to 3 positional arguments but 4 were given"
    with raises(TypeError, match=msg):
        Container("1", "2", "3")  # type: ignore


def test_objecttype_as_container_invalid_kwargs():
    msg = r"__init__\(\) got an unexpected keyword argument 'unexisting_field'"
    with raises(TypeError, match=msg):
        Container(unexisting_field="3")  # type: ignore


def test_objecttype_container_benchmark(benchmark):
    @benchmark
    def create_objecttype():
        Container(field1="field1", field2="field2")


def test_generate_objecttype_description():
    class MyObjectType(ObjectType):
        """
        Documentation

        Documentation line 2
        """

    assert MyObjectType._meta.description == "Documentation\n\nDocumentation line 2"


def test_objecttype_with_possible_types():
    class MyObjectType(ObjectType):
        class Meta:
            possible_types = (dict,)

    assert MyObjectType._meta.possible_types == (dict,)


def test_objecttype_with_possible_types_and_is_type_of_should_raise():
    with raises(AssertionError) as excinfo:

        class MyObjectType(ObjectType):
            class Meta:
                possible_types = (dict,)

            @classmethod
            def is_type_of(cls, root, context, info):
                return False

    assert str(excinfo.value) == (
        "MyObjectType.Meta.possible_types will cause type collision with "
        "MyObjectType.is_type_of. Please use one or other."
    )


def test_objecttype_no_fields_output():
    class User(ObjectType):
        name = String()

    class Query(ObjectType):
        user = Field(User)

        def resolve_user(self, info):
            return User()

    schema = Schema(query=Query)
    result = schema.execute(
        """ query basequery {
        user {
            name
        }
    }
    """
    )
    assert not result.errors
    assert result.data == {"user": {"name": None}}


def test_abstract_objecttype_can_str():
    class MyObjectType(ObjectType):
        class Meta:
            abstract = True

        field = MyScalar()

    assert str(MyObjectType) == "MyObjectType"


def test_objecttype_meta_with_annotations():
    class Query(ObjectType):
        class Meta:
            name: str = "oops"

        hello = String()

        def resolve_hello(self, info):
            return "Hello"

    schema = Schema(query=Query)
    assert schema is not None


def test_objecttype_meta_arguments():
    class MyInterface(Interface):
        foo = String()

    class MyType(ObjectType, interfaces=[MyInterface]):
        bar = String()

    assert MyType._meta.interfaces == [MyInterface]
    assert list(MyType._meta.fields.keys()) == ["foo", "bar"]


def test_objecttype_type_name():
    class MyObjectType(ObjectType, name="FooType"):
        pass

    assert MyObjectType._meta.name == "FooType"
