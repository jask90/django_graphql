from graphene_django.types import DjangoObjectType

from social.models import Idea, Follow


class IdeaType(DjangoObjectType):
    class Meta:
        model = Idea


class FollowType(DjangoObjectType):
    class Meta:
        model = Follow
