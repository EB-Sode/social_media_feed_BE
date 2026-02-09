"""
GraphQL types and queries for users.
This file defines:
 - UserType: GraphQL representation of the CustomUser model
 - UserQuery: read endpoints (users list, me)
 - UserMutation: fields that register mutations implemented in mutations.py
"""

import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from django.db.models import Q

from apps.users.mutations import DeleteAllUsersMutation
from .types import UserType


User = get_user_model()

class UserQuery(graphene.ObjectType):
    users = graphene.List(UserType) 
    user = graphene.Field(UserType, user_id=graphene.ID(required=True)) 
    search_users = graphene.List(UserType, query=graphene.String(required=True))
    me = graphene.Field(UserType)

    def resolve_users(self, info, **kwargs):
        # Return all users
        return User.objects.all()
    
    def resolve_user(self, info, user_id, **kwargs):
        try:
            return User.objects.get(pk=int(user_id))
        except User.DoesNotExist:
            return None
        
    def resolve_search_users(self, info, query, **kwargs):
        # Search by username or bio
        return User.objects.filter(
            Q(username__icontains=query) | Q(bio__icontains=query)
        )

    def resolve_me(self, info, **kwargs):
        user = info.context.user
        return None if user.is_anonymous else user


class UserMutation(graphene.ObjectType):
    from .mutations import SignUpMutation, LoginMutation, UpdateProfileMutation, RefreshTokenMutation, DeleteAllUsersMutation
    signup = SignUpMutation.Field()
    login = LoginMutation.Field()
    update_profile = UpdateProfileMutation.Field()
    refresh_token = RefreshTokenMutation.Field()
    delete_all_users = DeleteAllUsersMutation.Field()



