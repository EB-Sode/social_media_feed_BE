"""
Follow-related GraphQL definitions.
Queries for reading follow data and mutations for follow actions.
"""

import graphene
from django.contrib.auth import get_user_model
from .types import FollowType, FollowStatsType
from .models import Follow

User = get_user_model()


class FollowQuery(graphene.ObjectType):
    """
    Read operations for follows.
    """
    # Get all followers of a user
    followers = graphene.List(
        FollowType, 
        user_id=graphene.ID(required=True)
    )
    
    # Get all users a user is following
    following = graphene.List(
        FollowType, 
        user_id=graphene.ID(required=True)
    )
    
    # Get follow stats for a user
    follow_stats = graphene.Field(
        FollowStatsType,
        user_id=graphene.ID(required=True)
    )
    
    # Check if current user follows another user
    is_following = graphene.Boolean(
        user_id=graphene.ID(required=True)
    )
    
    def resolve_followers(self, info, user_id):
        """Get all followers of a specific user."""
        return Follow.objects.filter(followed_id=int(user_id)).select_related('follower', 'followed')
    
    def resolve_following(self, info, user_id):
        """Get all users that a specific user is following."""
        return Follow.objects.filter(follower_id=int(user_id)).select_related('follower', 'followed')
    
    def resolve_follow_stats(self, info, user_id):
        """Get follow statistics for a user."""
        current_user = info.context.user
        target_user_id = int(user_id)
        
        followers_count = Follow.objects.filter(followed_id=target_user_id).count()
        following_count = Follow.objects.filter(follower_id=target_user_id).count()
        
        is_following = False
        is_followed_by = False
        
        if not current_user.is_anonymous:
            is_following = Follow.objects.filter(
                follower=current_user,
                followed_id=target_user_id
            ).exists()
            
            is_followed_by = Follow.objects.filter(
                follower_id=target_user_id,
                followed=current_user
            ).exists()
        
        return {
            'followers_count': followers_count,
            'following_count': following_count,
            'is_following': is_following,
            'is_followed_by': is_followed_by
        }
    
    def resolve_is_following(self, info, user_id):
        """Check if current user is following another user."""
        current_user = info.context.user
        if current_user.is_anonymous:
            return False
        
        return Follow.objects.filter(
            follower=current_user,
            followed_id=int(user_id)
        ).exists()


class FollowMutation(graphene.ObjectType):
    """
    Write operations for follows.
    """
    from .mutations import FollowUserMutation, UnfollowUserMutation

    follow_user = FollowUserMutation.Field()
    unfollow_user = UnfollowUserMutation.Field()