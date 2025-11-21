"""
Services for managing follow/unfollow logic.
This layer contains the actual business rules.
Mutations should NEVER directly manipulate the database.
"""

from django.core.exceptions import ValidationError
from .models import Follow


def follow_user(follower, followed):
    """
    Handle the logic for following a user.
    - Prevent users from following themselves.
    - Prevent duplicate follow records.
    """

    if follower == followed:
        raise ValidationError("You cannot follow yourself.")

    follow_obj, created = Follow.objects.get_or_create(
        follower=follower,
        followed=followed
    )

    return follow_obj, created


def unfollow_user(follower, followed):
    """
    Logic for UNFOLLOWING a user.
    - If follow relationship exists → delete it.
    - If not → return False.
    """
    try:
        follow_obj = Follow.objects.get(
            follower=follower,
            followed=followed
        )
        follow_obj.delete()
        return True

    except Follow.DoesNotExist:
        return False
