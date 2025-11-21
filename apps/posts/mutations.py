# apps/posts/mutations.py
"""
Mutations for posts: create, update, delete; like/unlike; commenting.
Each mutation returns the changed object for convenience.
"""

import graphene
from graphene_file_upload.scalars import Upload
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db import IntegrityError

from .models import Post, Comment, Like
from django.contrib.auth import get_user_model

User = get_user_model()


class CreatePostMutation(graphene.Mutation):
    """
    Create a post. Accepts content and optional image upload.
    """
    post = graphene.Field(lambda: graphene.NonNull(lambda: PostType))

    class Arguments:
        content = graphene.String(required=True)
        image = Upload(required=False)

    def mutate(self, info, content, image=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        post = Post.objects.create(author=user, content=content)
        if image:
            post.image = image
            post.save()
        return CreatePostMutation(post=post)


class UpdatePostMutation(graphene.Mutation):
    """
    Update a post owned by the current user.
    """
    post = graphene.Field(lambda: graphene.NonNull(lambda: PostType))

    class Arguments:
        post_id = graphene.Int(required=True)
        content = graphene.String(required=False)
        image = Upload(required=False)

    def mutate(self, info, post_id, content=None, image=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        post = get_object_or_404(Post, pk=post_id)
        if post.author != user:
            raise Exception("You don't have permission to edit this post")

        if content is not None:
            post.content = content
        if image is not None:
            post.image = image
        post.save()
        return UpdatePostMutation(post=post)


class DeletePostMutation(graphene.Mutation):
    """
    Delete a post owned by the current user.
    """
    success = graphene.Boolean()

    class Arguments:
        post_id = graphene.Int(required=True)

    def mutate(self, info, post_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        post = get_object_or_404(Post, pk=post_id)
        if post.author != user:
            raise Exception("You don't have permission to delete this post")

        post.delete()
        return DeletePostMutation(success=True)


class LikePostMutation(graphene.Mutation):
    """
    Toggles a like for the current user on a post.
    Returns the post (so client can refresh like count).
    """
    post = graphene.Field(lambda: graphene.NonNull(lambda: PostType))

    class Arguments:
        post_id = graphene.Int(required=True)

    def mutate(self, info, post_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        post = get_object_or_404(Post, pk=post_id)
        # Try to create like; if exists, remove it (toggle)
        try:
            like, created = Like.objects.get_or_create(user=user, post=post)
            if not created:
                # Already liked -> unlike
                like.delete()
        except IntegrityError:
            # Unique constraint race guard
            Like.objects.filter(user=user, post=post).delete()

        return LikePostMutation(post=post)


class CreateCommentMutation(graphene.Mutation):
    """
    Add a comment to a post.
    """
    comment = graphene.Field(lambda: graphene.NonNull(lambda: CommentType))

    class Arguments:
        post_id = graphene.Int(required=True)
        content = graphene.String(required=True)

    def mutate(self, info, post_id, content):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        post = get_object_or_404(Post, pk=post_id)
        comment = Comment.objects.create(post=post, author=user, content=content)
        return CreateCommentMutation(comment=comment)


# Local imports to avoid circular import issues in the same file
from .schema import PostType, CommentType
