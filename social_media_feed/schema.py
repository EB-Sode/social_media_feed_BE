"""
Root GraphQL schema that stitches together app-level Query & Mutation classes.
This file is used by Graphene to expose a single /graphql endpoint.
"""

import graphene

from apps.users.schema import UserQuery, UserMutation
from apps.posts.schema import PostQuery, PostMutation
from apps.follows.schema import FollowMutation
from apps.notifications.schema import NotificationQuery, NotificationMutation


class Query(
    UserQuery,            # brings in user-related read queries (users, me)
    PostQuery,            # brings in post-related read queries (posts, post, feed)
    NotificationQuery,    # brings in notification read queries
    graphene.ObjectType
):
    """Aggregated Query for the whole service."""
    pass


class Mutation(
    UserMutation,         # user mutations (signup, login, update)
    PostMutation,         # post mutations (create/update/delete/like/comment)
    FollowMutation,       # follow/unfollow
    NotificationMutation, # mark notifications read
    graphene.ObjectType
):
    """Aggregated Mutation for the whole service."""
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
