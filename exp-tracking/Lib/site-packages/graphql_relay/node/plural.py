from typing import Any, Callable, List, Optional

from graphql import (
    GraphQLArgument,
    GraphQLField,
    GraphQLInputType,
    GraphQLOutputType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLResolveInfo,
    get_nullable_type,
)

__all__ = ["plural_identifying_root_field"]


def plural_identifying_root_field(
    arg_name: str,
    input_type: GraphQLInputType,
    output_type: GraphQLOutputType,
    resolve_single_input: Callable[[GraphQLResolveInfo, str], Any],
    description: Optional[str] = None,
) -> GraphQLField:
    def resolve(_obj: Any, info: GraphQLResolveInfo, **args: Any) -> List:
        inputs = args[arg_name]
        return [resolve_single_input(info, input_) for input_ in inputs]

    return GraphQLField(
        GraphQLList(output_type),
        description=description,
        args={
            arg_name: GraphQLArgument(
                GraphQLNonNull(
                    GraphQLList(
                        GraphQLNonNull(get_nullable_type(input_type))  # type: ignore
                    )
                )
            )
        },
        resolve=resolve,
    )
