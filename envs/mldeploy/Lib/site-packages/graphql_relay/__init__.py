"""The graphql_relay package"""

# The graphql-relay and graphql-relay-js version info
from .version import version, version_info, version_js, version_info_js

# Types and helpers for creating connection types in the schema
from .connection.connection import (
    backward_connection_args,
    connection_args,
    connection_definitions,
    forward_connection_args,
    page_info_type,
    Connection,
    ConnectionArguments,
    ConnectionConstructor,
    ConnectionCursor,
    ConnectionType,
    Edge,
    EdgeConstructor,
    EdgeType,
    GraphQLConnectionDefinitions,
    PageInfo,
    PageInfoConstructor,
    PageInfoType,
)

# Helpers for creating connections from arrays
from .connection.array_connection import (
    connection_from_array,
    connection_from_array_slice,
    cursor_for_object_in_connection,
    cursor_to_offset,
    get_offset_with_default,
    offset_to_cursor,
    SizedSliceable,
)

# Helper for creating mutations with client mutation IDs
from .mutation.mutation import (
    mutation_with_client_mutation_id,
    MutationFn,
    MutationFnWithoutArgs,
    NullResult,
)

# Helper for creating node definitions
from .node.node import node_definitions, GraphQLNodeDefinitions

#  Helper for creating plural identifying root fields
from .node.plural import plural_identifying_root_field

# Utilities for creating global IDs in systems that don't have them
from .node.node import from_global_id, global_id_field, to_global_id, ResolvedGlobalId

__version__ = version
__version_info__ = version_info
__version_js__ = version_js
__version_info_js__ = version_info_js

__all__ = [
    "backward_connection_args",
    "Connection",
    "ConnectionArguments",
    "ConnectionConstructor",
    "ConnectionCursor",
    "ConnectionType",
    "connection_args",
    "connection_from_array",
    "connection_from_array_slice",
    "connection_definitions",
    "cursor_for_object_in_connection",
    "cursor_to_offset",
    "Edge",
    "EdgeConstructor",
    "EdgeType",
    "forward_connection_args",
    "from_global_id",
    "get_offset_with_default",
    "global_id_field",
    "GraphQLConnectionDefinitions",
    "GraphQLNodeDefinitions",
    "MutationFn",
    "MutationFnWithoutArgs",
    "mutation_with_client_mutation_id",
    "node_definitions",
    "NullResult",
    "offset_to_cursor",
    "PageInfo",
    "PageInfoConstructor",
    "PageInfoType",
    "page_info_type",
    "plural_identifying_root_field",
    "ResolvedGlobalId",
    "SizedSliceable",
    "to_global_id",
    "version",
    "version_info",
    "version_js",
    "version_info_js",
]
