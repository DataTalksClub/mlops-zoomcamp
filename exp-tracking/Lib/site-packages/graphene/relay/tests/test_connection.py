import re

from pytest import raises

from ...types import Argument, Field, Int, List, NonNull, ObjectType, Schema, String
from ..connection import (
    Connection,
    ConnectionField,
    PageInfo,
    ConnectionOptions,
    get_edge_class,
)
from ..node import Node


class MyObject(ObjectType):
    class Meta:
        interfaces = [Node]

    field = String()


def test_connection():
    class MyObjectConnection(Connection):
        extra = String()

        class Meta:
            node = MyObject

        class Edge:
            other = String()

    assert MyObjectConnection._meta.name == "MyObjectConnection"
    fields = MyObjectConnection._meta.fields
    assert list(fields) == ["page_info", "edges", "extra"]
    edge_field = fields["edges"]
    pageinfo_field = fields["page_info"]

    assert isinstance(edge_field, Field)
    assert isinstance(edge_field.type, NonNull)
    assert isinstance(edge_field.type.of_type, List)
    assert edge_field.type.of_type.of_type == MyObjectConnection.Edge

    assert isinstance(pageinfo_field, Field)
    assert isinstance(pageinfo_field.type, NonNull)
    assert pageinfo_field.type.of_type == PageInfo


def test_connection_inherit_abstracttype():
    class BaseConnection:
        extra = String()

    class MyObjectConnection(BaseConnection, Connection):
        class Meta:
            node = MyObject

    assert MyObjectConnection._meta.name == "MyObjectConnection"
    fields = MyObjectConnection._meta.fields
    assert list(fields) == ["page_info", "edges", "extra"]


def test_connection_extra_abstract_fields():
    class ConnectionWithNodes(Connection):
        class Meta:
            abstract = True

        @classmethod
        def __init_subclass_with_meta__(cls, node=None, name=None, **options):
            _meta = ConnectionOptions(cls)

            _meta.fields = {
                "nodes": Field(
                    NonNull(List(node)),
                    description="Contains all the nodes in this connection.",
                ),
            }

            return super(ConnectionWithNodes, cls).__init_subclass_with_meta__(
                node=node, name=name, _meta=_meta, **options
            )

    class MyObjectConnection(ConnectionWithNodes):
        class Meta:
            node = MyObject

        class Edge:
            other = String()

    assert MyObjectConnection._meta.name == "MyObjectConnection"
    fields = MyObjectConnection._meta.fields
    assert list(fields) == ["nodes", "page_info", "edges"]
    edge_field = fields["edges"]
    pageinfo_field = fields["page_info"]
    nodes_field = fields["nodes"]

    assert isinstance(edge_field, Field)
    assert isinstance(edge_field.type, NonNull)
    assert isinstance(edge_field.type.of_type, List)
    assert edge_field.type.of_type.of_type == MyObjectConnection.Edge

    assert isinstance(pageinfo_field, Field)
    assert isinstance(pageinfo_field.type, NonNull)
    assert pageinfo_field.type.of_type == PageInfo

    assert isinstance(nodes_field, Field)
    assert isinstance(nodes_field.type, NonNull)
    assert isinstance(nodes_field.type.of_type, List)
    assert nodes_field.type.of_type.of_type == MyObject


def test_connection_override_fields():
    class ConnectionWithNodes(Connection):
        class Meta:
            abstract = True

        @classmethod
        def __init_subclass_with_meta__(cls, node=None, name=None, **options):
            _meta = ConnectionOptions(cls)
            base_name = (
                re.sub("Connection$", "", name or cls.__name__) or node._meta.name
            )

            edge_class = get_edge_class(cls, node, base_name)

            _meta.fields = {
                "page_info": Field(
                    NonNull(
                        PageInfo,
                        name="pageInfo",
                        required=True,
                        description="Pagination data for this connection.",
                    )
                ),
                "edges": Field(
                    NonNull(List(NonNull(edge_class))),
                    description="Contains the nodes in this connection.",
                ),
            }

            return super(ConnectionWithNodes, cls).__init_subclass_with_meta__(
                node=node, name=name, _meta=_meta, **options
            )

    class MyObjectConnection(ConnectionWithNodes):
        class Meta:
            node = MyObject

    assert MyObjectConnection._meta.name == "MyObjectConnection"
    fields = MyObjectConnection._meta.fields
    assert list(fields) == ["page_info", "edges"]
    edge_field = fields["edges"]
    pageinfo_field = fields["page_info"]

    assert isinstance(edge_field, Field)
    assert isinstance(edge_field.type, NonNull)
    assert isinstance(edge_field.type.of_type, List)
    assert isinstance(edge_field.type.of_type.of_type, NonNull)

    assert edge_field.type.of_type.of_type.of_type.__name__ == "MyObjectEdge"

    # This page info is NonNull
    assert isinstance(pageinfo_field, Field)
    assert isinstance(edge_field.type, NonNull)
    assert pageinfo_field.type.of_type == PageInfo


def test_connection_name():
    custom_name = "MyObjectCustomNameConnection"

    class BaseConnection:
        extra = String()

    class MyObjectConnection(BaseConnection, Connection):
        class Meta:
            node = MyObject
            name = custom_name

    assert MyObjectConnection._meta.name == custom_name


def test_edge():
    class MyObjectConnection(Connection):
        class Meta:
            node = MyObject

        class Edge:
            other = String()

    Edge = MyObjectConnection.Edge
    assert Edge._meta.name == "MyObjectEdge"
    edge_fields = Edge._meta.fields
    assert list(edge_fields) == ["node", "cursor", "other"]

    assert isinstance(edge_fields["node"], Field)
    assert edge_fields["node"].type == MyObject

    assert isinstance(edge_fields["other"], Field)
    assert edge_fields["other"].type == String


def test_edge_with_bases():
    class BaseEdge:
        extra = String()

    class MyObjectConnection(Connection):
        class Meta:
            node = MyObject

        class Edge(BaseEdge):
            other = String()

    Edge = MyObjectConnection.Edge
    assert Edge._meta.name == "MyObjectEdge"
    edge_fields = Edge._meta.fields
    assert list(edge_fields) == ["node", "cursor", "extra", "other"]

    assert isinstance(edge_fields["node"], Field)
    assert edge_fields["node"].type == MyObject

    assert isinstance(edge_fields["other"], Field)
    assert edge_fields["other"].type == String


def test_edge_with_nonnull_node():
    class MyObjectConnection(Connection):
        class Meta:
            node = NonNull(MyObject)

    edge_fields = MyObjectConnection.Edge._meta.fields
    assert isinstance(edge_fields["node"], Field)
    assert isinstance(edge_fields["node"].type, NonNull)
    assert edge_fields["node"].type.of_type == MyObject


def test_pageinfo():
    assert PageInfo._meta.name == "PageInfo"
    fields = PageInfo._meta.fields
    assert list(fields) == [
        "has_next_page",
        "has_previous_page",
        "start_cursor",
        "end_cursor",
    ]


def test_connectionfield():
    class MyObjectConnection(Connection):
        class Meta:
            node = MyObject

    field = ConnectionField(MyObjectConnection)
    assert field.args == {
        "before": Argument(String),
        "after": Argument(String),
        "first": Argument(Int),
        "last": Argument(Int),
    }


def test_connectionfield_node_deprecated():
    field = ConnectionField(MyObject)
    with raises(Exception) as exc_info:
        field.type

    assert "ConnectionFields now need a explicit ConnectionType for Nodes." in str(
        exc_info.value
    )


def test_connectionfield_custom_args():
    class MyObjectConnection(Connection):
        class Meta:
            node = MyObject

    field = ConnectionField(
        MyObjectConnection, before=String(required=True), extra=String()
    )
    assert field.args == {
        "before": Argument(NonNull(String)),
        "after": Argument(String),
        "first": Argument(Int),
        "last": Argument(Int),
        "extra": Argument(String),
    }


def test_connectionfield_required():
    class MyObjectConnection(Connection):
        class Meta:
            node = MyObject

    class Query(ObjectType):
        test_connection = ConnectionField(MyObjectConnection, required=True)

        def resolve_test_connection(root, info, **args):
            return []

    schema = Schema(query=Query)
    executed = schema.execute("{ testConnection { edges { cursor } } }")
    assert not executed.errors
    assert executed.data == {"testConnection": {"edges": []}}


def test_connectionfield_strict_types():
    class MyObjectConnection(Connection):
        class Meta:
            node = MyObject
            strict_types = True

    connection_field = ConnectionField(MyObjectConnection)
    edges_field_type = connection_field.type._meta.fields["edges"].type
    assert isinstance(edges_field_type, NonNull)

    edges_list_element_type = edges_field_type.of_type.of_type
    assert isinstance(edges_list_element_type, NonNull)

    node_field = edges_list_element_type.of_type._meta.fields["node"]
    assert isinstance(node_field.type, NonNull)
