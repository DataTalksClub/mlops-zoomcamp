from typing import Any, Callable, NamedTuple, Optional, Union

from graphql_relay.utils.base64 import base64, unbase64

from graphql import (
    GraphQLArgument,
    GraphQLNonNull,
    GraphQLID,
    GraphQLField,
    GraphQLInterfaceType,
    GraphQLList,
    GraphQLResolveInfo,
    GraphQLTypeResolver,
)

__all__ = [
    "from_global_id",
    "global_id_field",
    "node_definitions",
    "to_global_id",
    "GraphQLNodeDefinitions",
    "ResolvedGlobalId",
]


class GraphQLNodeDefinitions(NamedTuple):

    node_interface: GraphQLInterfaceType
    node_field: GraphQLField
    nodes_field: GraphQLField


def node_definitions(
    fetch_by_id: Callable[[str, GraphQLResolveInfo], Any],
    type_resolver: Optional[GraphQLTypeResolver] = None,
) -> GraphQLNodeDefinitions:
    """
    Given a function to map from an ID to an underlying object, and a function
    to map from an underlying object to the concrete GraphQLObjectType it
    corresponds to, constructs a `Node` interface that objects can implement,
    and a field object to be used as a `node` root field.

    If the type_resolver is omitted, object resolution on the interface will be
    handled with the `is_type_of` method on object types, as with any GraphQL
    interface without a provided `resolve_type` method.
    """
    node_interface = GraphQLInterfaceType(
        "Node",
        description="An object with an ID",
        fields=lambda: {
            "id": GraphQLField(
                GraphQLNonNull(GraphQLID), description="The id of the object."
            )
        },
        resolve_type=type_resolver,
    )

    # noinspection PyShadowingBuiltins
    node_field = GraphQLField(
        node_interface,
        description="Fetches an object given its ID",
        args={
            "id": GraphQLArgument(
                GraphQLNonNull(GraphQLID), description="The ID of an object"
            )
        },
        resolve=lambda _obj, info, id: fetch_by_id(id, info),
    )

    nodes_field = GraphQLField(
        GraphQLNonNull(GraphQLList(node_interface)),
        description="Fetches objects given their IDs",
        args={
            "ids": GraphQLArgument(
                GraphQLNonNull(GraphQLList(GraphQLNonNull(GraphQLID))),
                description="The IDs of objects",
            )
        },
        resolve=lambda _obj, info, ids: [fetch_by_id(id_, info) for id_ in ids],
    )

    return GraphQLNodeDefinitions(node_interface, node_field, nodes_field)


class ResolvedGlobalId(NamedTuple):

    type: str
    id: str


def to_global_id(type_: str, id_: Union[str, int]) -> str:
    """
    Takes a type name and an ID specific to that type name, and returns a
    "global ID" that is unique among all types.
    """
    return base64(f"{type_}:{GraphQLID.serialize(id_)}")


def from_global_id(global_id: str) -> ResolvedGlobalId:
    """
    Takes the "global ID" created by to_global_id, and returns the type name and ID
    used to create it.
    """
    global_id = unbase64(global_id)
    if ":" not in global_id:
        return ResolvedGlobalId("", global_id)
    return ResolvedGlobalId(*global_id.split(":", 1))


def global_id_field(
    type_name: Optional[str] = None,
    id_fetcher: Optional[Callable[[Any, GraphQLResolveInfo], str]] = None,
) -> GraphQLField:
    """
    Creates the configuration for an id field on a node, using `to_global_id` to
    construct the ID from the provided typename. The type-specific ID is fetched
    by calling id_fetcher on the object, or if not provided, by accessing the `id`
    attribute of the object, or the `id` if the object is a dict.
    """

    def resolve(obj: Any, info: GraphQLResolveInfo, **_args: Any) -> str:
        type_ = type_name or info.parent_type.name
        id_ = (
            id_fetcher(obj, info)
            if id_fetcher
            else (obj["id"] if isinstance(obj, dict) else obj.id)
        )
        return to_global_id(type_, id_)

    return GraphQLField(
        GraphQLNonNull(GraphQLID), description="The ID of an object", resolve=resolve
    )
