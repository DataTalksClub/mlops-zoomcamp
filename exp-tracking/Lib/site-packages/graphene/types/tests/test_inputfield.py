from functools import partial

from pytest import raises

from ..inputfield import InputField
from ..structures import NonNull
from .utils import MyLazyType


def test_inputfield_required():
    MyType = object()
    field = InputField(MyType, required=True)
    assert isinstance(field.type, NonNull)
    assert field.type.of_type == MyType


def test_inputfield_deprecated():
    MyType = object()
    deprecation_reason = "deprecated"
    field = InputField(MyType, required=False, deprecation_reason=deprecation_reason)
    assert isinstance(field.type, type(MyType))
    assert field.deprecation_reason == deprecation_reason


def test_inputfield_required_deprecated():
    MyType = object()
    with raises(AssertionError) as exc_info:
        InputField(MyType, name="input", required=True, deprecation_reason="deprecated")

    assert str(exc_info.value) == "InputField input is required, cannot deprecate it."


def test_inputfield_with_lazy_type():
    MyType = object()
    field = InputField(lambda: MyType)
    assert field.type == MyType


def test_inputfield_with_lazy_partial_type():
    MyType = object()
    field = InputField(partial(lambda: MyType))
    assert field.type == MyType


def test_inputfield_with_string_type():
    field = InputField("graphene.types.tests.utils.MyLazyType")
    assert field.type == MyLazyType
