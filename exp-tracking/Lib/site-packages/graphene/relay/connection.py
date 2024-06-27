import re
from collections.abc import Iterable
from functools import partial
from typing import Type

from graphql_relay import connection_from_array

from ..types import Boolean, Enum, Int, Interface, List, NonNull, Scalar, String, Union
from ..types.field import Field
from ..types.objecttype import ObjectType, ObjectTypeOptions
from ..utils.thenables import maybe_thenable
from .node import is_node, AbstractNode


def get_edge_class(
    connection_class: Type["Connection"],
    _node: Type[AbstractNode],
    base_name: str,
    strict_types: bool = False,
):
    edge_class = getattr(connection_class, "Edge", None)

    class EdgeBase:
        node = Field(
            NonNull(_node) if strict_types else _node,
            description="The item at the end of the edge",
        )
        cursor = String(required=True, description="A cursor for use in pagination")

    class EdgeMeta:
        description = f"A Relay edge containing a `{base_name}` and its cursor."

    edge_name = f"{base_name}Edge"

    edge_bases = [edge_class, EdgeBase] if edge_class else [EdgeBase]
    if not isinstance(edge_class, ObjectType):
        edge_bases = [*edge_bases, ObjectType]

    return type(edge_name, tuple(edge_bases), {"Meta": EdgeMeta})


class PageInfo(ObjectType):
    class Meta:
        description = (
            "The Relay compliant `PageInfo` type, containing data necessary to"
            " paginate this connection."
        )

    has_next_page = Boolean(
        required=True,
        name="hasNextPage",
        description="When paginating forwards, are there more items?",
    )

    has_previous_page = Boolean(
        required=True,
        name="hasPreviousPage",
        description="When paginating backwards, are there more items?",
    )

    start_cursor = String(
        name="startCursor",
        description="When paginating backwards, the cursor to continue.",
    )

    end_cursor = String(
        name="endCursor",
        description="When paginating forwards, the cursor to continue.",
    )


# noinspection PyPep8Naming
def page_info_adapter(startCursor, endCursor, hasPreviousPage, hasNextPage):
    """Adapter for creating PageInfo instances"""
    return PageInfo(
        start_cursor=startCursor,
        end_cursor=endCursor,
        has_previous_page=hasPreviousPage,
        has_next_page=hasNextPage,
    )


class ConnectionOptions(ObjectTypeOptions):
    node = None


class Connection(ObjectType):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls, node=None, name=None, strict_types=False, _meta=None, **options
    ):
        if not _meta:
            _meta = ConnectionOptions(cls)
        assert node, f"You have to provide a node in {cls.__name__}.Meta"
        assert isinstance(node, NonNull) or issubclass(
            node, (Scalar, Enum, ObjectType, Interface, Union, NonNull)
        ), f'Received incompatible node "{node}" for Connection {cls.__name__}.'

        base_name = re.sub("Connection$", "", name or cls.__name__) or node._meta.name
        if not name:
            name = f"{base_name}Connection"

        options["name"] = name

        _meta.node = node

        if not _meta.fields:
            _meta.fields = {}

        if "page_info" not in _meta.fields:
            _meta.fields["page_info"] = Field(
                PageInfo,
                name="pageInfo",
                required=True,
                description="Pagination data for this connection.",
            )

        if "edges" not in _meta.fields:
            edge_class = get_edge_class(cls, node, base_name, strict_types)  # type: ignore
            cls.Edge = edge_class
            _meta.fields["edges"] = Field(
                NonNull(List(NonNull(edge_class) if strict_types else edge_class)),
                description="Contains the nodes in this connection.",
            )

        return super(Connection, cls).__init_subclass_with_meta__(
            _meta=_meta, **options
        )


# noinspection PyPep8Naming
def connection_adapter(cls, edges, pageInfo):
    """Adapter for creating Connection instances"""
    return cls(edges=edges, page_info=pageInfo)


class IterableConnectionField(Field):
    def __init__(self, type_, *args, **kwargs):
        kwargs.setdefault("before", String())
        kwargs.setdefault("after", String())
        kwargs.setdefault("first", Int())
        kwargs.setdefault("last", Int())
        super(IterableConnectionField, self).__init__(type_, *args, **kwargs)

    @property
    def type(self):
        type_ = super(IterableConnectionField, self).type
        connection_type = type_
        if isinstance(type_, NonNull):
            connection_type = type_.of_type

        if is_node(connection_type):
            raise Exception(
                "ConnectionFields now need a explicit ConnectionType for Nodes.\n"
                "Read more: https://github.com/graphql-python/graphene/blob/v2.0.0/UPGRADE-v2.0.md#node-connections"
            )

        assert issubclass(
            connection_type, Connection
        ), f'{self.__class__.__name__} type has to be a subclass of Connection. Received "{connection_type}".'
        return type_

    @classmethod
    def resolve_connection(cls, connection_type, args, resolved):
        if isinstance(resolved, connection_type):
            return resolved

        assert isinstance(resolved, Iterable), (
            f"Resolved value from the connection field has to be an iterable or instance of {connection_type}. "
            f'Received "{resolved}"'
        )
        connection = connection_from_array(
            resolved,
            args,
            connection_type=partial(connection_adapter, connection_type),
            edge_type=connection_type.Edge,
            page_info_type=page_info_adapter,
        )
        connection.iterable = resolved
        return connection

    @classmethod
    def connection_resolver(cls, resolver, connection_type, root, info, **args):
        resolved = resolver(root, info, **args)

        if isinstance(connection_type, NonNull):
            connection_type = connection_type.of_type

        on_resolve = partial(cls.resolve_connection, connection_type, args)
        return maybe_thenable(resolved, on_resolve)

    def wrap_resolve(self, parent_resolver):
        resolver = super(IterableConnectionField, self).wrap_resolve(parent_resolver)
        return partial(self.connection_resolver, resolver, self.type)


ConnectionField = IterableConnectionField
