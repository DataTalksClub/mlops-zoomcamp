from graphql.error import GraphQLError

from graphene.types.schema import Schema


def default_format_error(error):
    if isinstance(error, GraphQLError):
        return error.formatted
    return {"message": str(error)}


def format_execution_result(execution_result, format_error):
    if execution_result:
        response = {}
        if execution_result.errors:
            response["errors"] = [format_error(e) for e in execution_result.errors]
        response["data"] = execution_result.data
        return response


class Client:
    def __init__(self, schema, format_error=None, **execute_options):
        assert isinstance(schema, Schema)
        self.schema = schema
        self.execute_options = execute_options
        self.format_error = format_error or default_format_error

    def format_result(self, result):
        return format_execution_result(result, self.format_error)

    def execute(self, *args, **kwargs):
        executed = self.schema.execute(*args, **dict(self.execute_options, **kwargs))
        return self.format_result(executed)

    async def execute_async(self, *args, **kwargs):
        executed = await self.schema.execute_async(
            *args, **dict(self.execute_options, **kwargs)
        )
        return self.format_result(executed)
