
"""
Services for the users app.
These functions contain BUSINESS LOGIC that should not live in GraphQL mutations.
GraphQL is only for receiving requests and returning responses.

This keeps your code clean, testable, and reusable.
"""

from django.contrib.auth import get_user_model
from django.db.models import Q

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
        .order_by("-date_joined")[:limit]  # Suggest newest users first
    )

    return suggestions
