from typing import Any, Dict, List, NamedTuple, Optional, Union

from graphql import (
    get_named_type,
    resolve_thunk,
    GraphQLArgument,
    GraphQLArgumentMap,
    GraphQLBoolean,
    GraphQLField,
    GraphQLFieldResolver,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLString,
    ThunkMapping,
)

from graphql import GraphQLNamedOutputType

try:
    from typing import Protocol
except ImportError:  # Python < 3.8
    from typing_extensions import Protocol  # type: ignore

__all__ = [
    "backward_connection_args",
    "connection_args",
    "connection_definitions",
    "forward_connection_args",
    "page_info_type",
    "Connection",
    "ConnectionArguments",
    "ConnectionConstructor",
    "ConnectionCursor",
    "ConnectionType",
    "Edge",
    "EdgeConstructor",
    "EdgeType",
    "GraphQLConnectionDefinitions",
    "PageInfo",
    "PageInfoConstructor",
    "PageInfoType",
]


# Returns a GraphQLArgumentMap appropriate to include on a field
# whose return type is a connection type with forward pagination.
forward_connection_args: GraphQLArgumentMap = {
    "after": GraphQLArgument(
        GraphQLString,
        description="Returns the items in the list"
        " that come after the specified cursor.",
    ),
    "first": GraphQLArgument(
        GraphQLInt,
        description="Returns the first n items from the list.",
    ),
}

# Returns a GraphQLArgumentMap appropriate to include on a field
# whose return type is a connection type with backward pagination.
backward_connection_args: GraphQLArgumentMap = {
    "before": GraphQLArgument(
        GraphQLString,
        description="Returns the items in the list"
        " that come before the specified cursor.",
    ),
    "last": GraphQLArgument(
        GraphQLInt, description="Returns the last n items from the list."
    ),
}

# Returns a GraphQLArgumentMap appropriate to include on a field
# whose return type is a connection type with bidirectional pagination.
connection_args = {**forward_connection_args, **backward_connection_args}


class GraphQLConnectionDefinitions(NamedTuple):
    edge_type: GraphQLObjectType
    connection_type: GraphQLObjectType


"""A type alias for cursors in this implementation."""
ConnectionCursor = str


"""A type describing the arguments a connection field receives in GraphQL.

The following kinds of arguments are expected (all optional):

    before: ConnectionCursor
    after: ConnectionCursor
    first: int
    last: int
"""
ConnectionArguments = Dict[str, Any]


def connection_definitions(
    node_type: Union[GraphQLNamedOutputType, GraphQLNonNull[GraphQLNamedOutputType]],
    name: Optional[str] = None,
    resolve_node: Optional[GraphQLFieldResolver] = None,
    resolve_cursor: Optional[GraphQLFieldResolver] = None,
    edge_fields: Optional[ThunkMapping[GraphQLField]] = None,
    connection_fields: Optional[ThunkMapping[GraphQLField]] = None,
) -> GraphQLConnectionDefinitions:
    """Return GraphQLObjectTypes for a connection with the given name.

    The nodes of the returned object types will be of the specified type.
    """
    name = name or get_named_type(node_type).name

    edge_type = GraphQLObjectType(
        name + "Edge",
        description="An edge in a connection.",
        fields=lambda: {
            "node": GraphQLField(
                node_type,
                resolve=resolve_node,
                description="The item at the end of the edge",
            ),
            "cursor": GraphQLField(
                GraphQLNonNull(GraphQLString),
                resolve=resolve_cursor,
                description="A cursor for use in pagination",
            ),
            **resolve_thunk(edge_fields or {}),
        },
    )

    connection_type = GraphQLObjectType(
        name + "Connection",
        description="A connection to a list of items.",
        fields=lambda: {
            "pageInfo": GraphQLField(
                GraphQLNonNull(page_info_type),
                description="Information to aid in pagination.",
            ),
            "edges": GraphQLField(
                GraphQLList(edge_type), description="A list of edges."
            ),
            **resolve_thunk(connection_fields or {}),
        },
    )

    return GraphQLConnectionDefinitions(edge_type, connection_type)


class PageInfoType(Protocol):
    @property
    def startCursor(self) -> Optional[ConnectionCursor]:
        ...

    def endCursor(self) -> Optional[ConnectionCursor]:
        ...

    def hasPreviousPage(self) -> bool:
        ...

    def hasNextPage(self) -> bool:
        ...


class PageInfoConstructor(Protocol):
    def __call__(
        self,
        *,
        startCursor: Optional[ConnectionCursor],
        endCursor: Optional[ConnectionCursor],
        hasPreviousPage: bool,
        hasNextPage: bool,
    ) -> PageInfoType:
        ...


class PageInfo(NamedTuple):
    """A type designed to be exposed as `PageInfo` over GraphQL."""

    startCursor: Optional[ConnectionCursor]
    endCursor: Optional[ConnectionCursor]
    hasPreviousPage: bool
    hasNextPage: bool


class EdgeType(Protocol):
    @property
    def node(self) -> Any:
        ...

    @property
    def cursor(self) -> ConnectionCursor:
        ...


class EdgeConstructor(Protocol):
    def __call__(self, *, node: Any, cursor: ConnectionCursor) -> EdgeType:
        ...


class Edge(NamedTuple):
    """A type designed to be exposed as a `Edge` over GraphQL."""

    node: Any
    cursor: ConnectionCursor


class ConnectionType(Protocol):
    @property
    def edges(self) -> List[EdgeType]:
        ...

    @property
    def pageInfo(self) -> PageInfoType:
        ...


class ConnectionConstructor(Protocol):
    def __call__(
        self,
        *,
        edges: List[EdgeType],
        pageInfo: PageInfoType,
    ) -> ConnectionType:
        ...


class Connection(NamedTuple):
    """A type designed to be exposed as a `Connection` over GraphQL."""

    edges: List[Edge]
    pageInfo: PageInfo


# The common page info type used by all connections.
page_info_type = GraphQLObjectType(
    "PageInfo",
    description="Information about pagination in a connection.",
    fields=lambda: {
        "hasNextPage": GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description="When paginating forwards, are there more items?",
        ),
        "hasPreviousPage": GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description="When paginating backwards, are there more items?",
        ),
        "startCursor": GraphQLField(
            GraphQLString,
            description="When paginating backwards, the cursor to continue.",
        ),
        "endCursor": GraphQLField(
            GraphQLString,
            description="When paginating forwards, the cursor to continue.",
        ),
    },
)
