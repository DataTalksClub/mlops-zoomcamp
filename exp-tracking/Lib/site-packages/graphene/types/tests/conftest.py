import pytest
from graphql import Undefined

from graphene.types.inputobjecttype import set_input_object_type_default_value


@pytest.fixture()
def set_default_input_object_type_to_undefined():
    """This fixture is used to change the default value of optional inputs in InputObjectTypes for specific tests"""
    set_input_object_type_default_value(Undefined)
    yield
    set_input_object_type_default_value(None)
