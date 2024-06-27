from collections.abc import Mapping
from inspect import iscoroutinefunction
from typing import Any, Callable, Dict, Optional

from graphql import (
    resolve_thunk,
    GraphQLArgument,
    GraphQLField,
    GraphQLFieldMap,
    GraphQLInputField,
    GraphQLInputFieldMap,
    GraphQLInputObjectType,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLResolveInfo,
    GraphQLString,
    ThunkMapping,
)
from graphql.pyutils import AwaitableOrValue

__all__ = [
    "mutation_with_client_mutation_id",
    "MutationFn",
    "MutationFnWithoutArgs",
    "NullResult",
]

# Note: Contrary to the Javascript implementation of MutationFn,
# the context is passed as part of the GraphQLResolveInfo and any arguments
# are passed individually as keyword arguments.
MutationFnWithoutArgs = Callable[[GraphQLResolveInfo], AwaitableOrValue[Any]]
# Unfortunately there is currently no syntax to indicate optional or keyword
# arguments in Python, so we also allow any other Callable as a workaround:
MutationFn = Callable[..., AwaitableOrValue[Any]]


class NullResult:
    def __init__(self, clientMutationId: Optional[str] = None) -> None:
        self.clientMutationId = clientMutationId


def mutation_with_client_mutation_id(
    name: str,
    input_fields: ThunkMapping[GraphQLInputField],
    output_fields: ThunkMapping[GraphQLField],
    mutate_and_get_payload: MutationFn,
    description: Optional[str] = None,
    deprecation_reason: Optional[str] = None,
    extensions: Optional[Dict[str, Any]] = None,
) -> GraphQLField:
    """
    Returns a GraphQLFieldConfig for the specified mutation.

    The input_fields and output_fields should not include `clientMutationId`,
    as this will be provided automatically.

    An input object will be created containing the input fields, and an
    object will be created containing the output fields.

    mutate_and_get_payload will receive a GraphQLResolveInfo as first argument,
    and the input fields as keyword arguments, and it should return an object
    (or a dict) with an attribute (or a key) for each output field.
    It may return synchronously or asynchronously.
    """

    def augmented_input_fields() -> GraphQLInputFieldMap:
        return dict(
            resolve_thunk(input_fields),
            clientMutationId=GraphQLInputField(GraphQLString),
        )

    def augmented_output_fields() -> GraphQLFieldMap:
        return dict(
            resolve_thunk(output_fields),
            clientMutationId=GraphQLField(GraphQLString),
        )

    output_type = GraphQLObjectType(name + "Payload", fields=augmented_output_fields)

    input_type = GraphQLInputObjectType(name + "Input", fields=augmented_input_fields)

    if iscoroutinefunction(mutate_and_get_payload):

        # noinspection PyShadowingBuiltins
        async def resolve(_root: Any, info: GraphQLResolveInfo, input: Dict) -> Any:
            payload = await mutate_and_get_payload(info, **input)
            clientMutationId = input.get("clientMutationId")
            if payload is None:
                return NullResult(clientMutationId)
            if isinstance(payload, Mapping):
                payload["clientMutationId"] = clientMutationId  # type: ignore
            else:
                payload.clientMutationId = clientMutationId
            return payload

    else:

        # noinspection PyShadowingBuiltins
        def resolve(  # type: ignore
            _root: Any, info: GraphQLResolveInfo, input: Dict
        ) -> Any:
            payload = mutate_and_get_payload(info, **input)
            clientMutationId = input.get("clientMutationId")
            if payload is None:
                return NullResult(clientMutationId)
            if isinstance(payload, Mapping):
                payload["clientMutationId"] = clientMutationId  # type: ignore
            else:
                payload.clientMutationId = clientMutationId  # type: ignore
            return payload

    return GraphQLField(
        output_type,
        description=description,
        deprecation_reason=deprecation_reason,
        args={"input": GraphQLArgument(GraphQLNonNull(input_type))},
        resolve=resolve,
        extensions=extensions,
    )
