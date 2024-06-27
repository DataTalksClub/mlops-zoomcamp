from graphql_relay import from_global_id, to_global_id

from ..types import ID, UUID
from ..types.base import BaseType

from typing import Type


class BaseGlobalIDType:
    """
    Base class that define the required attributes/method for a type.
    """

    graphene_type = ID  # type: Type[BaseType]

    @classmethod
    def resolve_global_id(cls, info, global_id):
        # return _type, _id
        raise NotImplementedError

    @classmethod
    def to_global_id(cls, _type, _id):
        # return _id
        raise NotImplementedError


class DefaultGlobalIDType(BaseGlobalIDType):
    """
    Default global ID type: base64 encoded version of "<node type name>: <node id>".
    """

    graphene_type = ID

    @classmethod
    def resolve_global_id(cls, info, global_id):
        try:
            _type, _id = from_global_id(global_id)
            if not _type:
                raise ValueError("Invalid Global ID")
            return _type, _id
        except Exception as e:
            raise Exception(
                f'Unable to parse global ID "{global_id}". '
                'Make sure it is a base64 encoded string in the format: "TypeName:id". '
                f"Exception message: {e}"
            )

    @classmethod
    def to_global_id(cls, _type, _id):
        return to_global_id(_type, _id)


class SimpleGlobalIDType(BaseGlobalIDType):
    """
    Simple global ID type: simply the id of the object.
    To be used carefully as the user is responsible for ensuring that the IDs are indeed global
    (otherwise it could cause request caching issues).
    """

    graphene_type = ID

    @classmethod
    def resolve_global_id(cls, info, global_id):
        _type = info.return_type.graphene_type._meta.name
        return _type, global_id

    @classmethod
    def to_global_id(cls, _type, _id):
        return _id


class UUIDGlobalIDType(BaseGlobalIDType):
    """
    UUID global ID type.
    By definition UUID are global so they are used as they are.
    """

    graphene_type = UUID

    @classmethod
    def resolve_global_id(cls, info, global_id):
        _type = info.return_type.graphene_type._meta.name
        return _type, global_id

    @classmethod
    def to_global_id(cls, _type, _id):
        return _id
