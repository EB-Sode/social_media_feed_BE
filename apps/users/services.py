
"""
Services for the users app.
These functions contain BUSINESS LOGIC that should not live in GraphQL mutations.
GraphQL is only for receiving requests and returning responses.

This keeps your code clean, testable, and reusable.
"""

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings
from apps.notifications.tasks import send_notification_task
from jwt.exceptions import ExpiredSignatureError, DecodeError
import jwt

User = get_user_model()


def suggest_users_to_follow(current_user, limit=5):
    """
    Suggest users that the current user does NOT already follow.
    - Excludes themselves.
    - Excludes already-followed users.
    - Returns a list of suggested users.
    """

    followed_ids = current_user.following.values_list("followed_id", flat=True)

    suggestions = (
        User.objects.exclude(id=current_user.id)
        .exclude(id__in=followed_ids)
        .order_by("-date_joined")[:limit]
    )
    

    return suggestions

def follow_user(follower, target_user):
    """
    Handles the logic of following another user.
    - Creates follow relationship
    - Sends notification via Celery
    """
    if follower.id == target_user.id:
        raise ValueError("You cannot follow yourself.")

    # Prevent double-following
    if follower.following.filter(followed=target_user).exists():
        return False  # Already following

    # Create follow record
    follower.following.create(followed=target_user)

    # Trigger async notification
    send_notification_task.delay(
        target_user.id,
        f"{follower.username} started following you."
    )

    return True


def get_user_from_token(token: str):
    """
    Decode a JWT and return the user.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if not user_id:
            return None
        user = User.objects.get(id=user_id)
        return user
    except (ExpiredSignatureError, DecodeError, User.DoesNotExist):
        return None