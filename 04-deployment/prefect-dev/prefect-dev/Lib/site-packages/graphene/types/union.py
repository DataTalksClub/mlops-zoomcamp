from typing import TYPE_CHECKING

from .base import BaseOptions, BaseType
from .unmountedtype import UnmountedType

# For static type checking with type checker
if TYPE_CHECKING:
    from .objecttype import ObjectType  # NOQA
    from typing import Iterable, Type  # NOQA


class UnionOptions(BaseOptions):
    types = ()  # type: Iterable[Type[ObjectType]]


class Union(UnmountedType, BaseType):
    """
    Union Type Definition

    When a field can return one of a heterogeneous set of types, a Union type
    is used to describe what types are possible as well as providing a function
    to determine which type is actually used when the field is resolved.

    The schema in this example can take a search text and return any of the GraphQL object types
    indicated: Human, Droid or Starship.

    Ambiguous return types can be resolved on each ObjectType through ``Meta.possible_types``
    attribute or ``is_type_of`` method. Or by implementing ``resolve_type`` class method on the
    Union.

    .. code:: python

        from graphene import Union, ObjectType, List

        class SearchResult(Union):
            class Meta:
                types = (Human, Droid, Starship)

        class Query(ObjectType):
            search = List(SearchResult.Field(
                search_text=String(description='Value to search for'))
            )

    Meta:
        types (Iterable[graphene.ObjectType]): Required. Collection of types that may be returned
            by this Union for the graphQL schema.
        name (optional, str): the name of the GraphQL type (must be unique in schema). Defaults to class
            name.
        description (optional, str): the description of the GraphQL type in the schema. Defaults to class
            docstring.
    """

    @classmethod
    def __init_subclass_with_meta__(cls, types=None, **options):
        assert (
            isinstance(types, (list, tuple)) and len(types) > 0
        ), f"Must provide types for Union {cls.__name__}."

        _meta = UnionOptions(cls)
        _meta.types = types
        super(Union, cls).__init_subclass_with_meta__(_meta=_meta, **options)

    @classmethod
    def get_type(cls):
        """
        This function is called when the unmounted type (Union instance)
        is mounted (as a Field, InputField or Argument)
        """
        return cls

    @classmethod
    def resolve_type(cls, instance, info):
        from .objecttype import ObjectType  # NOQA

        if isinstance(instance, ObjectType):
            return type(instance)
