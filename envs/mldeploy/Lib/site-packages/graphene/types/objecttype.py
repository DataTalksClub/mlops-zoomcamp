from typing import TYPE_CHECKING

from .base import BaseOptions, BaseType, BaseTypeMeta
from .field import Field
from .interface import Interface
from .utils import yank_fields_from_attrs

try:
    from dataclasses import make_dataclass, field
except ImportError:
    from ..pyutils.dataclasses import make_dataclass, field  # type: ignore
# For static type checking with type checker
if TYPE_CHECKING:
    from typing import Dict, Iterable, Type  # NOQA


class ObjectTypeOptions(BaseOptions):
    fields = None  # type: Dict[str, Field]
    interfaces = ()  # type: Iterable[Type[Interface]]


class ObjectTypeMeta(BaseTypeMeta):
    def __new__(cls, name_, bases, namespace, **options):
        # Note: it's safe to pass options as keyword arguments as they are still type-checked by ObjectTypeOptions.

        # We create this type, to then overload it with the dataclass attrs
        class InterObjectType:
            pass

        base_cls = super().__new__(
            cls, name_, (InterObjectType,) + bases, namespace, **options
        )
        if base_cls._meta:
            fields = [
                (
                    key,
                    "typing.Any",
                    field(
                        default=field_value.default_value
                        if isinstance(field_value, Field)
                        else None
                    ),
                )
                for key, field_value in base_cls._meta.fields.items()
            ]
            dataclass = make_dataclass(name_, fields, bases=())
            InterObjectType.__init__ = dataclass.__init__
            InterObjectType.__eq__ = dataclass.__eq__
            InterObjectType.__repr__ = dataclass.__repr__
        return base_cls


class ObjectType(BaseType, metaclass=ObjectTypeMeta):
    """
    Object Type Definition

    Almost all of the GraphQL types you define will be object types. Object types
    have a name, but most importantly describe their fields.

    The name of the type defined by an _ObjectType_ defaults to the class name. The type
    description defaults to the class docstring. This can be overridden by adding attributes
    to a Meta inner class.

    The class attributes of an _ObjectType_ are mounted as instances of ``graphene.Field``.

    Methods starting with ``resolve_<field_name>`` are bound as resolvers of the matching Field
    name. If no resolver is provided, the default resolver is used.

    Ambiguous types with Interface and Union can be determined through ``is_type_of`` method and
    ``Meta.possible_types`` attribute.

    .. code:: python

        from graphene import ObjectType, String, Field

        class Person(ObjectType):
            class Meta:
                description = 'A human'

            # implicitly mounted as Field
            first_name = String()
            # explicitly mounted as Field
            last_name = Field(String)

            def resolve_last_name(parent, info):
                return last_name

    ObjectType must be mounted using ``graphene.Field``.

    .. code:: python

        from graphene import ObjectType, Field

        class Query(ObjectType):

            person = Field(Person, description="My favorite person")

    Meta class options (optional):
        name (str): Name of the GraphQL type (must be unique in schema). Defaults to class
            name.
        description (str): Description of the GraphQL type in the schema. Defaults to class
            docstring.
        interfaces (Iterable[graphene.Interface]): GraphQL interfaces to extend with this object.
            all fields from interface will be included in this object's schema.
        possible_types (Iterable[class]): Used to test parent value object via isinstance to see if
            this type can be used to resolve an ambiguous type (interface, union).
        default_resolver (any Callable resolver): Override the default resolver for this
            type. Defaults to graphene default resolver which returns an attribute or dictionary
            key with the same name as the field.
        fields (Dict[str, graphene.Field]): Dictionary of field name to Field. Not recommended to
            use (prefer class attributes).

    An _ObjectType_ can be used as a simple value object by creating an instance of the class.

    .. code:: python

        p = Person(first_name='Bob', last_name='Roberts')
        assert p.first_name == 'Bob'

    Args:
        *args (List[Any]): Positional values to use for Field values of value object
        **kwargs (Dict[str: Any]): Keyword arguments to use for Field values of value object
    """

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        interfaces=(),
        possible_types=(),
        default_resolver=None,
        _meta=None,
        **options,
    ):
        if not _meta:
            _meta = ObjectTypeOptions(cls)
        fields = {}

        for interface in interfaces:
            assert issubclass(
                interface, Interface
            ), f'All interfaces of {cls.__name__} must be a subclass of Interface. Received "{interface}".'
            fields.update(interface._meta.fields)
        for base in reversed(cls.__mro__):
            fields.update(yank_fields_from_attrs(base.__dict__, _as=Field))
        assert not (possible_types and cls.is_type_of), (
            f"{cls.__name__}.Meta.possible_types will cause type collision with {cls.__name__}.is_type_of. "
            "Please use one or other."
        )

        if _meta.fields:
            _meta.fields.update(fields)
        else:
            _meta.fields = fields
        if not _meta.interfaces:
            _meta.interfaces = interfaces
        _meta.possible_types = possible_types
        _meta.default_resolver = default_resolver

        super(ObjectType, cls).__init_subclass_with_meta__(_meta=_meta, **options)

    is_type_of = None
