# apps/posts/services.py

"""
Business logic for Posts, Likes, Comments.
This layer ensures that GraphQL remains thin and clean.
"""

from django.db.models import Q, Count
from .models import Post, Like, Comment
from apps.notifications.tasks import send_notification_task, send_notification_email


def get_user_feed(user, limit=20, offset=0):
    """
    Advanced feed algorithm with pagination.

    Feed rankings:
    - Newest posts first
    - Then posts with high engagement
    - Then relevance based on follow relationships

    Parameters:
        limit: number of posts to return
        offset: number of posts to skip (for pagination)
    """

    following_ids = user.following.values_list("followed_id", flat=True)

    # Base feed query
    queryset = Post.objects.filter(
        Q(author__id__in=following_ids) | Q(author=user)
    )

    # Rank posts (simple scoring for now)
    queryset = queryset.annotate(
        score=(
            3 * Count("likes") +        # likes weigh more
            2 * Count("comments") +     # comments also important
            1                           # freshness default weight
        )
    ).order_by("-score", "-created_at")

    # Apply pagination
    return queryset[offset : offset + limit]



def toggle_like(post, user):
    """
    Like or unlike a post.
    If the user already liked the post → unlike it.
    Otherwise → like it.
    """

    like_obj = Like.objects.filter(post=post, user=user).first()

    if like_obj:
        like_obj.delete()
        return False  # Now unliked

    Like.objects.create(post=post, user=user)
    return True  # Now liked


def create_comment(post, user, content):
    """
    Create a new comment on a post.
    """
    return Comment.objects.create(
        post=post,
        user=user,
        content=content
    )


def like_post(user, post):
    if post.likes.filter(user=user).exists():
        return False

    Like.objects.create(user=user, post=post)

    send_notification_task.delay(
        post.author.id,
        f"{user.username} liked your post."
    )

    return True

def add_comment(post, user, text):
    comment = Comment.objects.create(
        post=post,
        user=user,
        text=text
    )

    # Send email to the post owner
    subject = "New Comment on Your Post"
    message = f"{user.username} commented: {text}"
    recipient = post.user.email

    send_notification_email.delay(subject, message, recipient)

    return comment
