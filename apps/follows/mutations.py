from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import graphene
from .types import FollowType
from .services import follow_user, unfollow_user
from apps.notifications.services import create_notification

User = get_user_model()


class FollowUserMutation(graphene.Mutation):
    success = graphene.Boolean()
    follow = graphene.Field(lambda: FollowType)

    class Arguments:
        user_id = graphene.ID(required=True)

    def mutate(self, info, user_id):
        follower = info.context.user
        if follower.is_anonymous:
            raise Exception("Authentication required")

        followed = get_object_or_404(User, pk=int(user_id))
        
        try:
            follow_obj, created = follow_user(follower, followed)
        except ValidationError as e:
            raise Exception(str(e))
        
        if not created:
            raise Exception("You are already following this user")

        # Create notification
        if follower != followed:
            create_notification(
                recipient=followed,
                actor=follower,
                verb="follow",
                message="started following you",
            )

        return FollowUserMutation(success=True, follow=follow_obj)


class UnfollowUserMutation(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        user_id = graphene.ID(required=True)

    def mutate(self, info, user_id):
        follower = info.context.user
        if follower.is_anonymous:
            raise Exception("Authentication required")

        followed = get_object_or_404(User, pk=int(user_id))

        # Use the service function
        success = unfollow_user(follower, followed)
        
        if not success:
            raise Exception("You are not following this user")

        return UnfollowUserMutation(success=True)

