from typing import TYPE_CHECKING

from .base import BaseOptions, BaseType
from .field import Field
from .utils import yank_fields_from_attrs

# For static type checking with type checker
if TYPE_CHECKING:
    from typing import Dict, Iterable, Type  # NOQA


class InterfaceOptions(BaseOptions):
    fields = None  # type: Dict[str, Field]
    interfaces = ()  # type: Iterable[Type[Interface]]


class Interface(BaseType):
    """
    Interface Type Definition

    When a field can return one of a heterogeneous set of types, a Interface type
    is used to describe what types are possible, what fields are in common across
    all types, as well as a function to determine which type is actually used
    when the field is resolved.

    .. code:: python

        from graphene import Interface, String

        class HasAddress(Interface):
            class Meta:
                description = "Address fields"

            address1 = String()
            address2 = String()

    If a field returns an Interface Type, the ambiguous type of the object can be determined using
    ``resolve_type`` on Interface and an ObjectType with ``Meta.possible_types`` or ``is_type_of``.

    Meta:
        name (str): Name of the GraphQL type (must be unique in schema). Defaults to class
            name.
        description (str): Description of the GraphQL type in the schema. Defaults to class
            docstring.
        fields (Dict[str, graphene.Field]): Dictionary of field name to Field. Not recommended to
            use (prefer class attributes).
    """

    @classmethod
    def __init_subclass_with_meta__(cls, _meta=None, interfaces=(), **options):
        if not _meta:
            _meta = InterfaceOptions(cls)

        fields = {}
        for base in reversed(cls.__mro__):
            fields.update(yank_fields_from_attrs(base.__dict__, _as=Field))

        if _meta.fields:
            _meta.fields.update(fields)
        else:
            _meta.fields = fields

        if not _meta.interfaces:
            _meta.interfaces = interfaces

        super(Interface, cls).__init_subclass_with_meta__(_meta=_meta, **options)

    @classmethod
    def resolve_type(cls, instance, info):
        from .objecttype import ObjectType

        if isinstance(instance, ObjectType):
            return type(instance)

    def __init__(self, *args, **kwargs):
        raise Exception("An Interface cannot be initialized")
