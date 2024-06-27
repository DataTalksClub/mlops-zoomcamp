from graphql import Undefined

from .mountedtype import MountedType
from .structures import NonNull
from .utils import get_type


class InputField(MountedType):
    """
    Makes a field available on an ObjectType in the GraphQL schema. Any type can be mounted as a
    Input Field except Interface and Union:

    - Object Type
    - Scalar Type
    - Enum

    Input object types also can't have arguments on their input fields, unlike regular ``graphene.Field``.

    All class attributes of ``graphene.InputObjectType`` are implicitly mounted as InputField
    using the below arguments.

    .. code:: python

        from graphene import InputObjectType, String, InputField

        class Person(InputObjectType):
            # implicitly mounted as Input Field
            first_name = String(required=True)
            # explicitly mounted as Input Field
            last_name = InputField(String, description="Surname")

    args:
        type (class for a graphene.UnmountedType): Must be a class (not an instance) of an
            unmounted graphene type (ex. scalar or object) which is used for the type of this
            field in the GraphQL schema.
        name (optional, str): Name of the GraphQL input field (must be unique in a type).
            Defaults to attribute name.
        default_value (optional, Any): Default value to use as input if none set in user operation (
            query, mutation, etc.).
        deprecation_reason (optional, str): Setting this value indicates that the field is
            depreciated and may provide instruction or reason on how for clients to proceed.
        description (optional, str): Description of the GraphQL field in the schema.
        required (optional, bool): Indicates this input field as not null in the graphql schema.
            Raises a validation error if argument not provided. Same behavior as graphene.NonNull.
            Default False.
        **extra_args (optional, Dict): Not used.
    """

    def __init__(
        self,
        type_,
        name=None,
        default_value=Undefined,
        deprecation_reason=None,
        description=None,
        required=False,
        _creation_counter=None,
        **extra_args,
    ):
        super(InputField, self).__init__(_creation_counter=_creation_counter)
        self.name = name
        if required:
            assert (
                deprecation_reason is None
            ), f"InputField {name} is required, cannot deprecate it."
            type_ = NonNull(type_)
        self._type = type_
        self.deprecation_reason = deprecation_reason
        self.default_value = default_value
        self.description = description

    @property
    def type(self):
        return get_type(self._type)
