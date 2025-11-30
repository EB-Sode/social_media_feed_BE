import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from .models import Follow

User = get_user_model()


class FollowType(DjangoObjectType):
    """GraphQL type for Follow model."""
    
    class Meta:
        model = Follow
        fields = ("id", "follower", "followed", "created_at")


class FollowStatsType(graphene.ObjectType):
    """
    Follow statistics for a user.
    """
    followers_count = graphene.Int()
    following_count = graphene.Int()
    is_following = graphene.Boolean()
    is_followed_by = graphene.Boolean()
    
    def resolve_followers_count(self, info):
        """Number of users following this user."""
        return self.get('followers_count', 0)
    
    def resolve_following_count(self, info):
        """Number of users this user is following."""
        return self.get('following_count', 0)
    
    def resolve_is_following(self, info):
        """Whether the current user is following this user."""
        return self.get('is_following', False)
    
    def resolve_is_followed_by(self, info):
        """Whether this user is following the current user."""
        return self.get('is_followed_by', False)


class UserWithFollowInfoType(graphene.ObjectType):
    """
    User type with follow information.
    Useful for search results or user lists.
    """
    id = graphene.ID()
    username = graphene.String()
    email = graphene.String()
    bio = graphene.String()
    profile_image = graphene.String()
    created_at = graphene.DateTime()
    
    # Follow stats
    followers_count = graphene.Int()
    following_count = graphene.Int()
    is_following = graphene.Boolean()
    
    def resolve_followers_count(self, info):
        """Count of followers for this user."""
        return Follow.objects.filter(followed=self).count()
    
    def resolve_following_count(self, info):
        """Count of users this user is following."""
        return Follow.objects.filter(follower=self).count()
    
    def resolve_is_following(self, info):
        """Whether the current user is following this user."""
        current_user = info.context.user
        if current_user.is_anonymous:
            return False
        return Follow.objects.filter(
            follower=current_user, 
            followed=self
        ).exists()