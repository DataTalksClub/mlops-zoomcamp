import inspect
from collections.abc import Mapping
from functools import partial

from .argument import Argument, to_arguments
from .mountedtype import MountedType
from .resolver import default_resolver
from .structures import NonNull
from .unmountedtype import UnmountedType
from .utils import get_type
from ..utils.deprecated import warn_deprecation

base_type = type


def source_resolver(source, root, info, **args):
    resolved = default_resolver(source, None, root, info, **args)
    if inspect.isfunction(resolved) or inspect.ismethod(resolved):
        return resolved()
    return resolved


class Field(MountedType):
    """
    Makes a field available on an ObjectType in the GraphQL schema. Any type can be mounted as a
    Field:

    - Object Type
    - Scalar Type
    - Enum
    - Interface
    - Union

    All class attributes of ``graphene.ObjectType`` are implicitly mounted as Field using the below
    arguments.

    .. code:: python

        class Person(ObjectType):
            first_name = graphene.String(required=True)                # implicitly mounted as Field
            last_name = graphene.Field(String, description='Surname')  # explicitly mounted as Field

    args:
        type (class for a graphene.UnmountedType): Must be a class (not an instance) of an
            unmounted graphene type (ex. scalar or object) which is used for the type of this
            field in the GraphQL schema.
        args (optional, Dict[str, graphene.Argument]): Arguments that can be input to the field.
            Prefer to use ``**extra_args``, unless you use an argument name that clashes with one
            of the Field arguments presented here (see :ref:`example<ResolverParamGraphQLArguments>`).
        resolver (optional, Callable): A function to get the value for a Field from the parent
            value object. If not set, the default resolver method for the schema is used.
        source (optional, str): attribute name to resolve for this field from the parent value
            object. Alternative to resolver (cannot set both source and resolver).
        deprecation_reason (optional, str): Setting this value indicates that the field is
            depreciated and may provide instruction or reason on how for clients to proceed.
        required (optional, bool): indicates this field as not null in the graphql schema. Same behavior as
            graphene.NonNull. Default False.
        name (optional, str): the name of the GraphQL field (must be unique in a type). Defaults to attribute
            name.
        description (optional, str): the description of the GraphQL field in the schema.
        default_value (optional, Any): Default value to resolve if none set from schema.
        **extra_args (optional, Dict[str, Union[graphene.Argument, graphene.UnmountedType]): any
            additional arguments to mount on the field.
    """

    def __init__(
        self,
        type_,
        args=None,
        resolver=None,
        source=None,
        deprecation_reason=None,
        name=None,
        description=None,
        required=False,
        _creation_counter=None,
        default_value=None,
        **extra_args,
    ):
        super(Field, self).__init__(_creation_counter=_creation_counter)
        assert not args or isinstance(
            args, Mapping
        ), f'Arguments in a field have to be a mapping, received "{args}".'
        assert not (
            source and resolver
        ), "A Field cannot have a source and a resolver in at the same time."
        assert not callable(
            default_value
        ), f'The default value can not be a function but received "{base_type(default_value)}".'

        if required:
            type_ = NonNull(type_)

        # Check if name is actually an argument of the field
        if isinstance(name, (Argument, UnmountedType)):
            extra_args["name"] = name
            name = None

        # Check if source is actually an argument of the field
        if isinstance(source, (Argument, UnmountedType)):
            extra_args["source"] = source
            source = None

        self.name = name
        self._type = type_
        self.args = to_arguments(args or {}, extra_args)
        if source:
            resolver = partial(source_resolver, source)
        self.resolver = resolver
        self.deprecation_reason = deprecation_reason
        self.description = description
        self.default_value = default_value

    @property
    def type(self):
        return get_type(self._type)

    get_resolver = None

    def wrap_resolve(self, parent_resolver):
        """
        Wraps a function resolver, using the ObjectType resolve_{FIELD_NAME}
        (parent_resolver) if the Field definition has no resolver.
        """
        if self.get_resolver is not None:
            warn_deprecation(
                "The get_resolver method is being deprecated, please rename it to wrap_resolve."
            )
            return self.get_resolver(parent_resolver)

        return self.resolver or parent_resolver

    def wrap_subscribe(self, parent_subscribe):
        """
        Wraps a function subscribe, using the ObjectType subscribe_{FIELD_NAME}
        (parent_subscribe) if the Field definition has no subscribe.
        """
        return parent_subscribe
