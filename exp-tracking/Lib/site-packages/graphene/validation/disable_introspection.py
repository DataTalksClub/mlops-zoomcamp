from graphql import GraphQLError
from graphql.language import FieldNode
from graphql.validation import ValidationRule

from ..utils.is_introspection_key import is_introspection_key


class DisableIntrospection(ValidationRule):
    def enter_field(self, node: FieldNode, *_args):
        field_name = node.name.value
        if is_introspection_key(field_name):
            self.report_error(
                GraphQLError(
                    f"Cannot query '{field_name}': introspection is disabled.", node
                )
            )
