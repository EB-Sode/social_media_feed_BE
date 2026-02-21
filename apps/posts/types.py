import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from .models import Post, Comment, Like

User = get_user_model()


class PostType(DjangoObjectType):
    """GraphQL type for Post model."""
    
    likes_count = graphene.Int()
    comments_count = graphene.Int()
    is_liked_by_user = graphene.Boolean()
    image_url = graphene.String()
    
    class Meta:
        model = Post
        fields = ("id", "author", "content", "created_at", "updated_at")

    def resolve_likes_count(self, info):
        """Count of likes on this post."""
        return self.likes.count()
    
    def resolve_image_url(self, info):
        return self.image or None

    def resolve_comments_count(self, info):
        """Count of comments on this post."""
        return self.comments.count()

    def resolve_is_liked_by_user(self, info):
        """Check if current user has liked this post."""
        user = info.context.user
        if user.is_anonymous:
            return False
        return self.likes.filter(user=user).exists()


class CommentType(DjangoObjectType):
    """GraphQL type for Comment model."""
    
    class Meta:
        model = Comment
        fields = ("id", "post", "author", "content", "created_at", "updated_at")


class LikeType(DjangoObjectType):
    """GraphQL type for Like model."""
    
    class Meta:
        model = Like
        fields = ("id", "user", "post", "created_at")


class PostWithEngagementType(graphene.ObjectType):
    """
    Post with additional engagement metrics.
    Useful for feed views where you need more context.
    """
    id = graphene.ID()
    author = graphene.Field(lambda: graphene.String())  # or UserType if imported
    content = graphene.String()
    image = graphene.String()
    created_at = graphene.DateTime()
    
    # Engagement metrics
    likes_count = graphene.Int()
    comments_count = graphene.Int()
    is_liked_by_user = graphene.Boolean()
    
    # Recent interactions
    recent_likes = graphene.List(LikeType)
    recent_comments = graphene.List(CommentType)
    
    def resolve_author(self, info):
        """Resolve author username."""
        return self.author.username
    
    def resolve_likes_count(self, info):
        """Count of likes."""
        return self.likes.count()
    
    def resolve_comments_count(self, info):
        """Count of comments."""
        return self.comments.count()
    
    def resolve_is_liked_by_user(self, info):
        """Check if current user liked this post."""
        user = info.context.user
        if user.is_anonymous:
            return False
        return self.likes.filter(user=user).exists()
    
    def resolve_recent_likes(self, info):
        """Get last 5 likes."""
        return self.likes.select_related('user').order_by('-created_at')[:5]
    
    def resolve_recent_comments(self, info):
        """Get last 3 comments."""
        return self.comments.select_related('author').order_by('-created_at')[:3]


class PostStatsType(graphene.ObjectType):
    """
    Statistics for a post.
    """
    post_id = graphene.ID()
    likes_count = graphene.Int()
    comments_count = graphene.Int()
    is_liked_by_user = graphene.Boolean()
    
    def resolve_likes_count(self, info):
        return self.get('likes_count', 0)
    
    def resolve_comments_count(self, info):
        return self.get('comments_count', 0)
    
    def resolve_is_liked_by_user(self, info):
        return self.get('is_liked_by_user', False)


class CommentWithRepliesType(graphene.ObjectType):
    """
    Comment type with nested replies support (for future use).
    """
    id = graphene.ID()
    post_id = graphene.ID()
    author = graphene.Field(lambda: graphene.String())
    content = graphene.String()
    created_at = graphene.DateTime()
    replies_count = graphene.Int()
    
    def resolve_author(self, info):
        return self.author.username
    
    def resolve_replies_count(self, info):
        # If you add reply functionality later
        return 0
    
class UserStatsType(graphene.ObjectType):
    """
    Docstring for UserStatsType for user engagement statistics.
    """
    user_id = graphene.ID()
    posts_count = graphene.Int()
    total_likes_received = graphene.Int()
    total_comments_received = graphene.Int()
    
    def resolve_posts_count(self, info):
        return self.get('posts_count', 0)
    
    def resolve_total_likes_received(self, info):
        return self.get('total_likes_received', 0)
    
    def resolve_total_comments_received(self, info):
        return self.get('total_comments_received', 0)