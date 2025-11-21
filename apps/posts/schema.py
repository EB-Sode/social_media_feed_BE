# apps/posts/schema.py
"""
Post-related GraphQL types and read queries.
- PostType exposes post data and computed fields (likes_count, comments_count)
- CommentType for post comments
- Queries: posts (all), post(id), feed (posts from followed users)
"""

import graphene
from graphene_django import DjangoObjectType
from .models import Post, Comment
from django.shortcuts import get_object_or_404
from .services import get_user_feed  # implement feed algorithm here

class PostType(DjangoObjectType):
    likes_count = graphene.Int()
    comments_count = graphene.Int()

    class Meta:
        model = Post
        fields = ("id", "content", "image", "author", "created_at", "likes_count", "comments_count")

    def resolve_likes_count(self, info):
        # quick computed field for convenience in the client
        return self.likes.count()

    def resolve_comments_count(self, info):
        return self.comments.count()


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = ("id", "post", "author", "content", "created_at")



class PostQuery(graphene.ObjectType):
    posts = graphene.List(
        PostType,
        limit=graphene.Int(default_value=20),
        offset=graphene.Int(default_value=0),
        query=graphene.String(description="Optional search query to filter posts by content"),
    )
    post = graphene.Field(PostType, id=graphene.Int(required=True))
    feed = graphene.List(
        PostType,
        limit=graphene.Int(default_value=20),
        offset=graphene.Int(default_value=0),
    )

    def resolve_posts(self, info, limit, offset, query=None):
        """
        Returns paginated posts.
        If `query` is provided, it filters posts by content containing the query string.
        """
        qs = Post.objects.all().order_by('-created_at')

        if query:
            qs = qs.filter(content__icontains=query)

        return qs[offset: offset + limit]

    def resolve_post(self, info, id):
        return get_object_or_404(Post, pk=id)

    def resolve_feed(self, info, limit, offset):
        """
        Returns paginated feed for the current user.
        Example: feed(limit: 10, offset: 20)
        """
        user = info.context.user
        if user.is_anonymous:
            return []
        return get_user_feed(user, limit=limit, offset=offset)

class PostMutation(graphene.ObjectType):
    from .mutations import (
    CreatePostMutation,
    UpdatePostMutation,
    DeletePostMutation,
    LikePostMutation,
    CreateCommentMutation,
)
    create_post = CreatePostMutation.Field()
    update_post = UpdatePostMutation.Field()
    delete_post = DeletePostMutation.Field()
    like_post = LikePostMutation.Field()
    create_comment = CreateCommentMutation.Field()
