import graphene
import social.schema as social_schema
import user.schema as user_schema
from graphene import AbstractType, Mutation, ObjectType, relay


class Mutation(user_schema.Mutation, social_schema.Mutation, ObjectType):
    pass


class Query(user_schema.Query, social_schema.Query, ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
