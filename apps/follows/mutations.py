# apps/follows/mutations.py
"""
Follow and unfollow mutations.
Use the Follow model (follower -> followed).
The mutations return a simple success boolean and optionally the Follow object.
"""

import graphene
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from .models import Follow

User = get_user_model()


class FollowUserMutation(graphene.Mutation):
    success = graphene.Boolean()
    # follow = graphene.Field(lambda: graphene.NonNull(lambda: FollowType))
    follow = graphene.Field(lambda: FollowType)

    class Arguments:
        user_id = graphene.Int(required=True)  # ID of the user to follow

    def mutate(self, info, user_id):
        follower = info.context.user
        if follower.is_anonymous:
            raise Exception("Authentication required")

        followed = get_object_or_404(User, pk=user_id)
        if follower == followed:
            raise Exception("You cannot follow yourself")

        try:
            follow = Follow.objects.create(follower=follower, followed=followed)
        except IntegrityError:
            # already following
            follow = Follow.objects.get(follower=follower, followed=followed)

        return FollowUserMutation(success=True, follow=follow)


class UnfollowUserMutation(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        user_id = graphene.Int(required=True)

    def mutate(self, info, user_id):
        follower = info.context.user
        if follower.is_anonymous:
            raise Exception("Authentication required")

        followed = get_object_or_404(User, pk=user_id)
        Follow.objects.filter(follower=follower, followed=followed).delete()
        return UnfollowUserMutation(success=True)


# Local import to reference the GraphQL type for Follow
from .schema import FollowType
