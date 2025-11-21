
"""
Follow-related GraphQL definitions.
We only need mutations in many cases because following a user is an action.
If you want read endpoints (followers/following lists), you can add those in Query later.
"""

import graphene
from apps.follows.models import Follow
from graphene_django import DjangoObjectType

class FollowType(DjangoObjectType):
    """GraphQL type for Follow model."""
    class Meta:
        model = Follow
        fields = ("id", "follower", "following", "created_at")

class FollowMutation(graphene.ObjectType):
    from .mutations import FollowUserMutation, UnfollowUserMutation

    follow_user = FollowUserMutation.Field()
    unfollow_user = UnfollowUserMutation.Field()
