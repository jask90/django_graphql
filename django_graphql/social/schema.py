import graphene
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from graphql import GraphQLError
from graphql_auth import mutations
from user.types import UserType

from social.models import Follow, Idea
from social.types import FollowType, IdeaType


class CreateIdea(graphene.Mutation):
    success = graphene.Boolean(default_value=True)
    errors = graphene.String()
    idea = graphene.Field(IdeaType)

    class Arguments:
        text = graphene.String(required=True)
        visibility = graphene.String(required=True)

    @staticmethod
    def mutate(root, info, **kwargs):
        if not info.context.user or info.context.user.is_anonymous:
            return CreateIdea(idea=None, errors="User not found", success=False)

        text = kwargs.get('text', None)
        visibility = kwargs.get('visibility', None)

        if not text:
            return CreateIdea(idea=None, errors="Text is required", success=False)

        if len(text) > 140:
            return CreateIdea(idea=None, errors="The text is too long, the maximum length is 140 characters", success=False)

        if not visibility:
            return CreateIdea(idea=None, errors="Visibility is required", success=False)

        if not any(visibility in option for option in Idea.VISIBILITY_CHOICES):
            return CreateIdea(idea=None, errors="Invalid visibility data", success=False)

        try:
            idea_instance = Idea(
                user=info.context.user,
                text=text,
                visibility=visibility
            )
            idea_instance.save()
        except Exception as e:
            return CreateIdea(idea=None, errors=e, success=False)

        return CreateIdea(idea=idea_instance, errors=False, success=True)


class UpdateIdeaVisibility(graphene.Mutation):
    success = graphene.Boolean(default_value=True)
    errors = graphene.String()
    idea = graphene.Field(IdeaType)

    class Arguments:
        id = graphene.ID(required=True)
        visibility = graphene.String(required=True)

    @staticmethod
    def mutate(root, info, **kwargs):
        if not info.context.user or info.context.user.is_anonymous:
            return UpdateIdeaVisibility(idea=None, errors="User not found", success=False)

        idea_id = kwargs.get('id')
        visibility = kwargs.get('visibility')

        if not visibility:
            return UpdateIdeaVisibility(idea=None, errors="Visibility is required", success=False)

        if not any(visibility in option for option in Idea.VISIBILITY_CHOICES):
            return UpdateIdeaVisibility(idea=None, errors="Invalid visibility data", success=False)

        try:
            idea_instance = Idea.objects.get(
                id=idea_id,
                user=info.context.user,
            )
        except:
            return UpdateIdeaVisibility(idea=None, errors="Idea not found", success=False)
        idea_instance.visibility = visibility
        idea_instance.save()

        return UpdateIdeaVisibility(idea=idea_instance, errors=False, success=True)


class DeleteIdea(graphene.Mutation):
    success = graphene.Boolean(default_value=True)
    errors = graphene.String()
    idea = graphene.Field(IdeaType)

    class Arguments:
        id = graphene.ID(required=True)

    @staticmethod
    def mutate(root, info, **kwargs):
        if not info.context.user or info.context.user.is_anonymous:
            return DeleteIdea(idea=None, errors="You must be logged in", success=False)

        idea_id = kwargs.get('id')

        try:
            idea_instance = Idea.objects.get(
                id=idea_id,
                user=info.context.user,
            )
            idea_instance.delete()
        except:
            return DeleteIdea(idea=None, errors="Idea not found", success=False)

        return DeleteIdea(idea=None, errors=False, success=True)


class FollowUser(graphene.Mutation):
    success = graphene.Boolean(default_value=True)
    errors = graphene.String()
    follow = graphene.Field(FollowType)

    class Arguments:
        email = graphene.String(required=True)

    @staticmethod
    def mutate(root, info, **kwargs):
        if not info.context.user or info.context.user.is_anonymous:
            return FollowUser(follow=None, errors="You must be logged in", success=False)

        email = kwargs.get('email', None)
        if not email:
            return FollowUser(follow=None, errors="Invalid email", success=False)

        try:
            user = User.objects.get(email=email)
        except:
            return FollowUser(follow=None, errors="User not found", success=False)
        
        if user == info.context.user:
            return FollowUser(follow=None, errors="You cant follow yourself", success=False)

        try:
            follow_instance = Follow.objects.create(
                user=user,
                follower=info.context.user,
                status='pending',
            )
        except:
            return FollowUser(follow=None, errors="Internal Server Error", success=False)

        return FollowUser(follow=follow_instance, errors=False, success=True)


class ChangeFollowStatus(graphene.Mutation):
    success = graphene.Boolean(default_value=True)
    errors = graphene.String()
    follow = graphene.Field(FollowType)

    class Arguments:
        id = graphene.ID(required=True)
        action = graphene.String(required=True)

    @staticmethod
    def mutate(root, info, **kwargs):
        if not info.context.user or info.context.user.is_anonymous:
            return ChangeFollowStatus(follow=None, errors="You must be logged in", success=False)

        follow_id = kwargs.get('id', None)
        action = kwargs.get('action', None)

        try:
            follow_instance = Follow.objects.get(id=follow_id, user=info.context.user, status='pending')
        except:
            return ChangeFollowStatus(follow=None, errors="Follow request not found", success=False)

        if not id or action not in ['accept', 'refuse']:
            return ChangeFollowStatus(follow=None, errors="Invalid action", success=False)

        try:
            result = False
            if action == 'accept':
                result = follow_instance.accept(user=info.context.user)
            elif action == 'refuse':
                result = follow_instance.refuse(user=info.context.user)

            if not result:
                return ChangeFollowStatus(follow=None, errors="Action rejected", success=False)
        except:
            return ChangeFollowStatus(follow=None, errors="Internal Server Error", success=False)

        return ChangeFollowStatus(follow=follow_instance, errors=False, success=True)


class UnfollowUser(graphene.Mutation):
    success = graphene.Boolean(default_value=True)
    errors = graphene.String()

    class Arguments:
        email = graphene.String(required=True)

    @staticmethod
    def mutate(root, info, **kwargs):
        if not info.context.user or info.context.user.is_anonymous:
            return UnfollowUser(errors="You must be logged in", success=False)

        email = kwargs.get('email', None)
        if not email:
            return UnfollowUser(errors="Invalid email", success=False)

        try:
            user = User.objects.get(email=email)
        except:
            return UnfollowUser(errors="User not found", success=False)

        try:
            Follow.objects.get(
                user=user,
                follower=info.context.user,
            ).delete()
        except Follow.DoesNotExist:
            return UnfollowUser(errors="Follow does not exist", success=True)
        except:
            return UnfollowUser(errors="Internal Server Error", success=False)

        return UnfollowUser(errors=False, success=True)


class DeleteFollower(graphene.Mutation):
    success = graphene.Boolean(default_value=True)
    errors = graphene.String()

    class Arguments:
        email = graphene.String(required=True)

    @staticmethod
    def mutate(root, info, **kwargs):
        if not info.context.user or info.context.user.is_anonymous:
            return DeleteFollower(errors="You must be logged in", success=False)

        email = kwargs.get('email', None)
        if not email:
            return DeleteFollower(errors="Invalid email", success=False)

        try:
            user = User.objects.get(email=email)
        except:
            return DeleteFollower(errors="User not found", success=False)

        try:
            Follow.objects.get(
                user=info.context.user,
                follower=user,
            ).delete()
        except Follow.DoesNotExist:
            return DeleteFollower(errors="Follow does not exist", success=True)
        except:
            return DeleteFollower(errors="Internal Server Error", success=False)

        return DeleteFollower(errors=False, success=True)


class Query(graphene.ObjectType):
    list_own_ideas = graphene.List(IdeaType)
    list_follow_requests = graphene.List(FollowType)
    list_followed = graphene.List(UserType)
    list_followers = graphene.List(UserType)
    list_user_ideas = graphene.List(IdeaType, email=graphene.String(required=True))
    timeline = graphene.List(IdeaType)

    def resolve_list_own_ideas(self, info, **kwargs):
        if not info.context.user or info.context.user.is_anonymous:
            return GraphQLError("You must be logged in")

        ideas = Idea.objects.filter(user=info.context.user).order_by('-created')

        return ideas

    def resolve_list_follow_requests(self, info, **kwargs):
        if not info.context.user or info.context.user.is_anonymous:
            return GraphQLError("You must be logged in")

        follow = Follow.objects.filter(user=info.context.user, status='pending').order_by('-created')

        return follow

    def resolve_list_followed(self, info, **kwargs):
        if not info.context.user or info.context.user.is_anonymous:
            return GraphQLError("You must be logged in")

        users_ids = Follow.objects.filter(follower=info.context.user, status='accepted').values_list('user__id', flat=True)
        users = User.objects.filter(id__in=users_ids).distinct().order_by('username')

        return users

    def resolve_list_followers(self, info, **kwargs):
        if not info.context.user or info.context.user.is_anonymous:
            return GraphQLError("You must be logged in")

        followers_ids = Follow.objects.filter(user=info.context.user, status='accepted').values_list('follower__id', flat=True)
        users = User.objects.filter(id__in=followers_ids).distinct().order_by('username')

        return users

    def resolve_list_user_ideas(self, info, email):
        if not info.context.user or info.context.user.is_anonymous:
            return GraphQLError("You must be logged in")

        if not email:
            return GraphQLError("Invalid email")

        try:
            user = User.objects.get(email=email)
        except:
            return GraphQLError("User not found")

        visibilities = ['public',]
        if Follow.objects.filter(user=user, follower=info.context.user, status='accepted').exists():
            visibilities.append('protected')

        ideas = Idea.objects.filter(user=user, visibility__in=visibilities).order_by('-created')

        return ideas

    def resolve_timeline(self, info, **kwargs):
        if not info.context.user or info.context.user.is_anonymous:
            return GraphQLError("You must be logged in")

        users_i_follow = Follow.objects.filter(follower=info.context.user, status='accepted').values_list('user__id', flat=True)

        visibilities = ['public', 'protected']
        ideas = Idea.objects.filter(Q(user=info.context.user) | (Q(user__id__in=users_i_follow) & Q(visibility__in=visibilities))).order_by('-created')

        return ideas


class Mutation(graphene.ObjectType):
    create_idea = CreateIdea.Field()
    update_idea_visibility = UpdateIdeaVisibility.Field()
    delete_idea = DeleteIdea.Field()
    follow_user = FollowUser.Field()
    unfollow_user = UnfollowUser.Field()
    change_follow_status = ChangeFollowStatus.Field()
    delete_follower = DeleteFollower.Field()
