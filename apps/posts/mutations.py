"""
Mutations for posts: create, update, delete; like/unlike; commenting.
Each mutation returns the changed object for convenience.
"""

import graphene
from graphene_file_upload.scalars import Upload
from django.shortcuts import get_object_or_404
from .services import create_comment
from .models import Post, Comment, Like
from .types import PostType, CommentType
from django.contrib.auth import get_user_model
import cloudinary.uploader

User = get_user_model()


class CreatePostMutation(graphene.Mutation):
    """
    Create a post. Accepts content and optional image upload.
    """
    post = graphene.Field(PostType)

    class Arguments:
        content = graphene.String(required=False)
        image = Upload(required=False)

    def mutate(self, info, content, image=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        post = Post.objects.create(author=user, content=content)
        if image:
            # Upload to Cloudinary
            uploaded = cloudinary.uploader.upload(image)
            post.image = uploaded.get("secure_url")  # ✅ store URL in DB

            post.save()
        return CreatePostMutation(post=post)


class UpdatePostMutation(graphene.Mutation):
    """
    Update a post owned by the current user.
    """
    post = graphene.Field(PostType)

    class Arguments:
        post_id = graphene.ID(required=True) 
        content = graphene.String(required=False)
        image = Upload(required=False)

    def mutate(self, info, post_id, content=None, image=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        post = get_object_or_404(Post, pk=int(post_id))
        if post.author != user:
            raise Exception("You don't have permission to edit this post")

        if content is not None:
            post.content = content
        if image is not None:
            uploaded = cloudinary.uploader.upload(image)
            post.image = uploaded.get("secure_url")
        post.save()
        return UpdatePostMutation(post=post)


class DeleteAllUserPosts(graphene.Mutation):
    success = graphene.Boolean()
    deleted_count = graphene.Int()

    class Arguments:
        user_id = graphene.ID(required=True)

    def mutate(self, info, user_id):
        current_user = info.context.user

        if current_user.is_anonymous:
            raise Exception("Authentication required")

        # Only allow self or admin
        if str(current_user.id) != str(user_id) and not current_user.is_staff:
            raise Exception("You are not allowed to delete these posts")

        deleted_count, _ = Post.objects.filter(author_id=user_id).delete()

        return DeleteAllUserPosts(
            success=True,
            deleted_count=deleted_count
        )

class DeletePostMutation(graphene.Mutation):
    """
    Delete a post owned by the current user.
    """
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        post_id = graphene.ID(required=True) 

    def mutate(self, info, post_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        post = get_object_or_404(Post, pk=int(post_id))
        if post.author != user:
            raise Exception("You don't have permission to delete this post")

        post.delete()
        return DeletePostMutation(success=True)


class LikePostMutation(graphene.Mutation):
    """
    Toggles a like for the current user on a post.
    Returns the post and success status.
    """
    success = graphene.Boolean() 
    post = graphene.Field(PostType)
    message = graphene.String()

    class Arguments:
        post_id = graphene.ID(required=True)

    def mutate(self, info, post_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        post = get_object_or_404(Post, pk=int(post_id))
        
        # Toggle like
        like, created = Like.objects.get_or_create(user=user, post=post)
        
        if not created:
            # Already liked -> unlike
            like.delete()
            message = "Post unliked"
        else:
            message = "Post liked"
            
            # Create notification for post author
            if post.author != user:
                from apps.notifications.models import Notification
                Notification.objects.create(
                    recipient=post.author,
                    sender=user,
                    notification_type='like',
                    post=post,
                    message=f"{user.username} liked your post"
                )

        return LikePostMutation(
            success=True,
            post=post,
            message=message
        )


class CreateCommentMutation(graphene.Mutation):
    comment = graphene.Field(CommentType)
    success = graphene.Boolean()

    class Arguments:
        post_id = graphene.ID(required=True)
        content = graphene.String(required=True)

    def mutate(self, info, post_id, content):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        post = get_object_or_404(Post, pk=int(post_id))
        
        # ✅ Use service function
        comment = create_comment(post, user, content)
        
        return CreateCommentMutation(comment=comment, success=True)


class UpdateCommentMutation(graphene.Mutation):
    """
    Update a comment owned by the current user.
    """
    comment = graphene.Field(CommentType)
    success = graphene.Boolean()

    class Arguments:
        comment_id = graphene.ID(required=True)
        content = graphene.String(required=True)

    def mutate(self, info, comment_id, content):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        comment = get_object_or_404(Comment, pk=int(comment_id))
        if comment.author != user:
            raise Exception("You don't have permission to edit this comment")

        comment.content = content
        comment.save()
        return UpdateCommentMutation(comment=comment, success=True)


class DeleteCommentMutation(graphene.Mutation):
    """
    Delete a comment owned by the current user.
    """
    success = graphene.Boolean()

    class Arguments:
        comment_id = graphene.ID(required=True)

    def mutate(self, info, comment_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        comment = get_object_or_404(Comment, pk=int(comment_id))
        if comment.author != user:
            raise Exception("You don't have permission to delete this comment")

        comment.delete()
        return DeleteCommentMutation(success=True)