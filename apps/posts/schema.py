"""
Post-related GraphQL types and read queries.
- PostType exposes post data and computed fields (likes_count, comments_count)
- CommentType for post comments
- Queries: posts (all), post(id), feed (posts from followed users)
"""

import graphene
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .types import PostType, CommentType, LikeType, UserStatsType
from .models import Post, Comment, Like
from .services import get_user_feed,  get_trending_posts, get_user_stats


User = get_user_model()

class PostQuery(graphene.ObjectType):
    # Get all posts (with pagination and search)
    posts = graphene.List(
        PostType,
        limit=graphene.Int(default_value=20),
        offset=graphene.Int(default_value=0),
        query=graphene.String(description="Optional search query to filter posts by content"),
    )
    
    # Get single post by ID
    post = graphene.Field(PostType, id=graphene.ID(required=True))  # ✅ Changed to ID
    
    # Get personalized feed
    feed = graphene.List(
        PostType,
        limit=graphene.Int(default_value=20),
        offset=graphene.Int(default_value=0),
    )
    
    # Get posts by specific user
    user_posts = graphene.List(
        PostType, 
        user_id=graphene.ID(required=True),
        limit=graphene.Int(default_value=20),
        offset=graphene.Int(default_value=0),
    )
    
    # Get comments on a post
    comments = graphene.List(
        CommentType, 
        post_id=graphene.ID(required=True)
    )
    
    # Get likes on a post
    likes = graphene.List(
        LikeType, 
        post_id=graphene.ID(required=True)
    )

    # Get trending posts
    trending_posts = graphene.List(PostType, limit=graphene.Int(default_value=10))
    user_stats = graphene.Field(
        UserStatsType,
        user_id=graphene.ID(required=True)
    )

    def resolve_posts(self, info, limit, offset, query=None):
        """
        Returns paginated posts.
        If `query` is provided, it filters posts by content containing the query string.
        """
        qs = Post.objects.select_related('author').prefetch_related('likes', 'comments').all()

        if query:
            qs = qs.filter(content__icontains=query)

        return qs[offset: offset + limit]

    def resolve_post(self, info, id):
        """Get single post by ID."""
        return get_object_or_404(Post, pk=int(id))  # ✅ Convert ID to int

    def resolve_feed(self, info, limit, offset):
        """
        Returns paginated feed for the current user.
        Shows posts from users they follow.
        """
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")
        return get_user_feed(user, limit=limit, offset=offset)
    
    def resolve_user_posts(self, info, user_id, limit, offset):
        """Get posts by a specific user."""
        return Post.objects.filter(
            author_id=int(user_id)
        ).select_related('author').prefetch_related('likes', 'comments')[offset:offset + limit]
    
    def resolve_comments(self, info, post_id):
        """Get all comments on a post."""
        return Comment.objects.filter(
            post_id=int(post_id)
        ).select_related('author').order_by('created_at')
    
    def resolve_likes(self, info, post_id):
        """Get all likes on a post."""
        return Like.objects.filter(
            post_id=int(post_id)
        ).select_related('user').order_by('-created_at')

    
    def resolve_trending_posts(self, info, limit):
        """Get trending posts from last 24 hours."""
        return get_trending_posts(limit=limit)
    
    def resolve_user_stats(self, info, user_id):
        """Get user statistics."""
        user = User.objects.get(pk=int(user_id))
        return get_user_stats(user)

class PostMutation(graphene.ObjectType):
    from .mutations import (
        CreatePostMutation,
        UpdatePostMutation,
        DeletePostMutation,
        LikePostMutation,
        CreateCommentMutation,
        UpdateCommentMutation,
        DeleteCommentMutation,  
    )
    
    create_post = CreatePostMutation.Field()
    update_post = UpdatePostMutation.Field()
    delete_post = DeletePostMutation.Field()
    like_post = LikePostMutation.Field()
    create_comment = CreateCommentMutation.Field()
    update_comment = UpdateCommentMutation.Field()
    delete_comment = DeleteCommentMutation.Field()