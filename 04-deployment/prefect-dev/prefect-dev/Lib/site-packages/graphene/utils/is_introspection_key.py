def is_introspection_key(key):
    # from: https://spec.graphql.org/June2018/#sec-Schema
    # > All types and directives defined within a schema must not have a name which
    # > begins with "__" (two underscores), as this is used exclusively
    # > by GraphQL’s introspection system.
    return str(key).startswith("__")
