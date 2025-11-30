"""
Root GraphQL schema that stitches together app-level Query & Mutation classes.
This file is used by Graphene to expose a single /graphql endpoint.
"""

import graphene

from apps.users.schema import UserQuery, UserMutation
from apps.posts.schema import PostQuery, PostMutation
from apps.follows.schema import FollowMutation, FollowQuery
from apps.notifications.schema import NotificationQuery, NotificationMutation



class Query(
    UserQuery,         
    PostQuery,            
    NotificationQuery,  
    FollowQuery,
    graphene.ObjectType
):
    """Aggregated Query for the whole service."""
    pass


class Mutation(
    UserMutation,       
    PostMutation,       
    FollowMutation, 
    NotificationMutation,
    graphene.ObjectType
):
    """Aggregated Mutation for the whole service."""
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)

