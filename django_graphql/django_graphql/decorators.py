import functools

from graphql import GraphQLError


def graphql_login_required(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        user = args[1].context.user
        if not user or user.is_anonymous:
            return GraphQLError("You must be logged in")
        return func(*args, **kwargs)
    return inner
