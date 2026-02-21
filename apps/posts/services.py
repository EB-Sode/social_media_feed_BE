"""
Business logic for Posts, Likes, Comments.
This layer ensures that GraphQL remains thin and clean.
"""

from django.db.models import Q, Count, F
from django.utils import timezone
from datetime import timedelta
from .models import Post, Like, Comment
from apps.follows.models import Follow
from apps.notifications.models import Notification
from apps.notifications.tasks import send_notification_email


def get_user_feed(user, limit=20, offset=0):
    """
    Advanced feed algorithm with pagination.

    Feed rankings:
    - Posts from followed users + own posts
    - Sorted by engagement score and recency
    - Recent posts (last 7 days) get bonus points

    Parameters:
        user: Current user requesting feed
        limit: Number of posts to return
        offset: Number of posts to skip (for pagination)
    """
    # Get IDs of users the current user follows
    following_ids = Follow.objects.filter(
        follower=user
    ).values_list('followed_id', flat=True)

    # Get recent cutoff (posts from last 7 days get recency bonus)
    recent_cutoff = timezone.now() - timedelta(days=7)

    # Base feed query: posts from followed users + own posts
    queryset = Post.objects.filter(
        Q(author_id__in=following_ids) | Q(author=user)
    ).select_related('author').prefetch_related('likes', 'comments')

    # Annotate with engagement score
    queryset = queryset.annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True),
    ).annotate(
        # Calculate engagement score
        engagement_score=(
            F('likes_count') * 3 +      # Likes weigh most
            F('comments_count') * 2     # Comments also important
        )
    ).order_by('-created_at', '-engagement_score', '-likes_count', '-comments_count')

    # Apply pagination
    return queryset[offset:offset + limit]


def toggle_like(post, user):
    """
    Like or unlike a post.
    If the user already liked the post → unlike it and return False.
    Otherwise → like it, create notification, and return True.
    
    Returns:
        bool: True if liked, False if unliked
    """
    like_obj = Like.objects.filter(post=post, user=user).first()

    if like_obj:
        # Unlike
        like_obj.delete()
        return False

    # Like
    Like.objects.create(post=post, user=user)
    
    # Create notification (don't notify yourself)
    if post.author != user:
        Notification.objects.create(
            recipient=post.author,
            sender=user,
            notification_type='like',
            post=post,
            message=f"{user.username} liked your post"
        )
        
        try:
            send_notification_email.delay(
                subject="New Like on Your Post",
                message=f"{user.username} liked your post: {post.content[:50]}...",
                recipient_email=post.author.email
            )
        except Exception as e:
            print(f"Failed to send email notification: {e}")
    
    return True


def create_comment(post, user, content):
    """
    Create a new comment on a post.
    Creates notification for post author and sends email.
    
    Parameters:
        post: Post object to comment on
        user: User creating the comment
        content: Comment text content
        
    Returns:
        Comment: Created comment object
    """
    # Create comment
    comment = Comment.objects.create(
        post=post,
        author=user,
        content=content
    )
    
    # Create notification (don't notify yourself)
    if post.author != user:
        Notification.objects.create(
            recipient=post.author,
            sender=user,
            notification_type='comment',
            post=post,
            message=f"{user.username} commented on your post"
        )
        
        # Optional: Send email notification (async)
        try:
            send_notification_email.delay(
                subject="New Comment on Your Post",
                message=f"{user.username} commented: {content[:100]}...",
                recipient_email=post.author.email
            )
        except Exception as e:
            print(f"Failed to send email notification: {e}")
    
    return comment


def get_post_with_engagement(post_id):
    """
    Get a single post with engagement metrics pre-calculated.
    Useful for detail views.
    """
    return Post.objects.annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True),
    ).get(pk=post_id)


def get_trending_posts(limit=10):
    """
    Get trending posts based on recent engagement.
    Posts from the last 24 hours with high engagement.
    """
    cutoff = timezone.now() - timedelta(hours=24)
    
    return Post.objects.filter(
        created_at__gte=cutoff
    ).annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True),
        engagement_score=(
            F('likes_count') * 3 + F('comments_count') * 2
        )
    ).filter(
        engagement_score__gt=0
    ).order_by('-engagement_score')[:limit]


def get_user_stats(user):
    """
    Get aggregated statistics for a user.
    
    Returns:
        dict: User statistics including posts, likes, comments counts
    """
    return {
        'posts_count': Post.objects.filter(author=user).count(),
        'total_likes_received': Like.objects.filter(post__author=user).count(),
        'total_comments_received': Comment.objects.filter(post__author=user).count(),
        'followers_count': Follow.objects.filter(followed=user).count(),
        'following_count': Follow.objects.filter(follower=user).count(),
    }