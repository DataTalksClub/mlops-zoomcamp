# This is a Python port of https://github.com/stems/graphql-depth-limit
# which is licensed under the terms of the MIT license, reproduced below.
#
# -----------
#
# MIT License
#
# Copyright (c) 2017 Stem
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

try:
    from re import Pattern
except ImportError:
    # backwards compatibility for v3.6
    from typing import Pattern
from typing import Callable, Dict, List, Optional, Union, Tuple

from graphql import GraphQLError
from graphql.validation import ValidationContext, ValidationRule
from graphql.language import (
    DefinitionNode,
    FieldNode,
    FragmentDefinitionNode,
    FragmentSpreadNode,
    InlineFragmentNode,
    Node,
    OperationDefinitionNode,
)

from ..utils.is_introspection_key import is_introspection_key


IgnoreType = Union[Callable[[str], bool], Pattern, str]


def depth_limit_validator(
    max_depth: int,
    ignore: Optional[List[IgnoreType]] = None,
    callback: Optional[Callable[[Dict[str, int]], None]] = None,
):
    class DepthLimitValidator(ValidationRule):
        def __init__(self, validation_context: ValidationContext):
            document = validation_context.document
            definitions = document.definitions

            fragments = get_fragments(definitions)
            queries = get_queries_and_mutations(definitions)
            query_depths = {}

            for name in queries:
                query_depths[name] = determine_depth(
                    node=queries[name],
                    fragments=fragments,
                    depth_so_far=0,
                    max_depth=max_depth,
                    context=validation_context,
                    operation_name=name,
                    ignore=ignore,
                )
            if callable(callback):
                callback(query_depths)
            super().__init__(validation_context)

    return DepthLimitValidator


def get_fragments(
    definitions: Tuple[DefinitionNode, ...],
) -> Dict[str, FragmentDefinitionNode]:
    fragments = {}
    for definition in definitions:
        if isinstance(definition, FragmentDefinitionNode):
            fragments[definition.name.value] = definition
    return fragments


# This will actually get both queries and mutations.
# We can basically treat those the same
def get_queries_and_mutations(
    definitions: Tuple[DefinitionNode, ...],
) -> Dict[str, OperationDefinitionNode]:
    operations = {}

    for definition in definitions:
        if isinstance(definition, OperationDefinitionNode):
            operation = definition.name.value if definition.name else "anonymous"
            operations[operation] = definition
    return operations


def determine_depth(
    node: Node,
    fragments: Dict[str, FragmentDefinitionNode],
    depth_so_far: int,
    max_depth: int,
    context: ValidationContext,
    operation_name: str,
    ignore: Optional[List[IgnoreType]] = None,
) -> int:
    if depth_so_far > max_depth:
        context.report_error(
            GraphQLError(
                f"'{operation_name}' exceeds maximum operation depth of {max_depth}.",
                [node],
            )
        )
        return depth_so_far
    if isinstance(node, FieldNode):
        should_ignore = is_introspection_key(node.name.value) or is_ignored(
            node, ignore
        )

        if should_ignore or not node.selection_set:
            return 0
        return 1 + max(
            map(
                lambda selection: determine_depth(
                    node=selection,
                    fragments=fragments,
                    depth_so_far=depth_so_far + 1,
                    max_depth=max_depth,
                    context=context,
                    operation_name=operation_name,
                    ignore=ignore,
                ),
                node.selection_set.selections,
            )
        )
    elif isinstance(node, FragmentSpreadNode):
        return determine_depth(
            node=fragments[node.name.value],
            fragments=fragments,
            depth_so_far=depth_so_far,
            max_depth=max_depth,
            context=context,
            operation_name=operation_name,
            ignore=ignore,
        )
    elif isinstance(
        node, (InlineFragmentNode, FragmentDefinitionNode, OperationDefinitionNode)
    ):
        return max(
            map(
                lambda selection: determine_depth(
                    node=selection,
                    fragments=fragments,
                    depth_so_far=depth_so_far,
                    max_depth=max_depth,
                    context=context,
                    operation_name=operation_name,
                    ignore=ignore,
                ),
                node.selection_set.selections,
            )
        )
    else:
        raise Exception(
            f"Depth crawler cannot handle: {node.kind}."
        )  # pragma: no cover


def is_ignored(node: FieldNode, ignore: Optional[List[IgnoreType]] = None) -> bool:
    if ignore is None:
        return False
    for rule in ignore:
        field_name = node.name.value
        if isinstance(rule, str):
            if field_name == rule:
                return True
        elif isinstance(rule, Pattern):
            if rule.match(field_name):
                return True
        elif callable(rule):
            if rule(field_name):
                return True
        else:
            raise ValueError(f"Invalid ignore option: {rule}.")
    return False
