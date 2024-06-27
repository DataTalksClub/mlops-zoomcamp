class Context:
    """
    Context can be used to make a convenient container for attributes to provide
    for execution for resolvers of a GraphQL operation like a query.

    .. code:: python

        from graphene import Context

        context = Context(loaders=build_dataloaders(), request=my_web_request)
        schema.execute('{ hello(name: "world") }', context=context)

        def resolve_hello(parent, info, name):
            info.context.request  # value set in Context
            info.context.loaders  # value set in Context
            # ...

    args:
        **params (Dict[str, Any]): values to make available on Context instance as attributes.

    """

    def __init__(self, **params):
        for key, value in params.items():
            setattr(self, key, value)
