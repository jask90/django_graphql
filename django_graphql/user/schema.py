import graphene
from django.contrib.auth.models import User
from graphql import GraphQLError
from graphql_auth import mutations
from graphql_auth.schema import MeQuery

from user.types import UserType


# We create this class to avoid user verification, since it is not necessary in this case
class RegisterUser(mutations.Register):

    @classmethod
    def mutate(cls, *args, **kwargs):
        try:
            email = kwargs.get("email")
    
            res = super().mutate(*args, **kwargs)
            user = User.objects.filter(email=email).first()
            if user:
                user.status.verified = True
                user.status.save()

            return res
        except Exception:
            raise Exception(res.errors)


class AuthMutation(graphene.ObjectType):
    register = RegisterUser.Field()
    token_auth = mutations.ObtainJSONWebToken.Field()
    verify_account = mutations.VerifyAccount.Field()
    password_change = mutations.PasswordChange.Field()


class Query(AuthMutation, graphene.ObjectType):
    viewer = graphene.Field(UserType)
    search_users = graphene.List(UserType, username=graphene.String(required=True))

    def resolve_viewer(self, info, **kwargs):
        return info.context.user

    def resolve_search_users(self, info, username):
        if not info.context.user or info.context.user.is_anonymous:
            return GraphQLError("You must be logged in")

        if not username:
            return GraphQLError("Invalid username")

        users = User.objects.filter(username__icontains=username)

        return users


class Mutation(AuthMutation, graphene.ObjectType):
    pass
