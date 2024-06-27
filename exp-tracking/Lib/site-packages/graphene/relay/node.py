from functools import partial
from inspect import isclass

from ..types import Field, Interface, ObjectType
from ..types.interface import InterfaceOptions
from ..types.utils import get_type
from .id_type import BaseGlobalIDType, DefaultGlobalIDType


def is_node(objecttype):
    """
    Check if the given objecttype has Node as an interface
    """
    if not isclass(objecttype):
        return False

    if not issubclass(objecttype, ObjectType):
        return False

    return any(issubclass(i, Node) for i in objecttype._meta.interfaces)


class GlobalID(Field):
    def __init__(
        self,
        node=None,
        parent_type=None,
        required=True,
        global_id_type=DefaultGlobalIDType,
        *args,
        **kwargs,
    ):
        super(GlobalID, self).__init__(
            global_id_type.graphene_type, required=required, *args, **kwargs
        )
        self.node = node or Node
        self.parent_type_name = parent_type._meta.name if parent_type else None

    @staticmethod
    def id_resolver(parent_resolver, node, root, info, parent_type_name=None, **args):
        type_id = parent_resolver(root, info, **args)
        parent_type_name = parent_type_name or info.parent_type.name
        return node.to_global_id(parent_type_name, type_id)  # root._meta.name

    def wrap_resolve(self, parent_resolver):
        return partial(
            self.id_resolver,
            parent_resolver,
            self.node,
            parent_type_name=self.parent_type_name,
        )


class NodeField(Field):
    def __init__(self, node, type_=False, **kwargs):
        assert issubclass(node, Node), "NodeField can only operate in Nodes"
        self.node_type = node
        self.field_type = type_
        global_id_type = node._meta.global_id_type

        super(NodeField, self).__init__(
            # If we don't specify a type, the field type will be the node interface
            type_ or node,
            id=global_id_type.graphene_type(
                required=True, description="The ID of the object"
            ),
            **kwargs,
        )

    def wrap_resolve(self, parent_resolver):
        return partial(self.node_type.node_resolver, get_type(self.field_type))


class AbstractNode(Interface):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, global_id_type=DefaultGlobalIDType, **options):
        assert issubclass(
            global_id_type, BaseGlobalIDType
        ), "Custom ID type need to be implemented as a subclass of BaseGlobalIDType."
        _meta = InterfaceOptions(cls)
        _meta.global_id_type = global_id_type
        _meta.fields = {
            "id": GlobalID(
                cls, global_id_type=global_id_type, description="The ID of the object"
            )
        }
        super(AbstractNode, cls).__init_subclass_with_meta__(_meta=_meta, **options)

    @classmethod
    def resolve_global_id(cls, info, global_id):
        return cls._meta.global_id_type.resolve_global_id(info, global_id)


class Node(AbstractNode):
    """An object with an ID"""

    @classmethod
    def Field(cls, *args, **kwargs):  # noqa: N802
        return NodeField(cls, *args, **kwargs)

    @classmethod
    def node_resolver(cls, only_type, root, info, id):
        return cls.get_node_from_global_id(info, id, only_type=only_type)

    @classmethod
    def get_node_from_global_id(cls, info, global_id, only_type=None):
        _type, _id = cls.resolve_global_id(info, global_id)

        graphene_type = info.schema.get_type(_type)
        if graphene_type is None:
            raise Exception(f'Relay Node "{_type}" not found in schema')

        graphene_type = graphene_type.graphene_type

        if only_type:
            assert (
                graphene_type == only_type
            ), f"Must receive a {only_type._meta.name} id."

        # We make sure the ObjectType implements the "Node" interface
        if cls not in graphene_type._meta.interfaces:
            raise Exception(
                f'ObjectType "{_type}" does not implement the "{cls}" interface.'
            )

        get_node = getattr(graphene_type, "get_node", None)
        if get_node:
            return get_node(info, _id)

    @classmethod
    def to_global_id(cls, type_, id):
        return cls._meta.global_id_type.to_global_id(type_, id)
