# apps/notifications/services.py

"""
Services for creating social notifications.
This can later be replaced with Celery tasks for async processing.
"""

from .models import Notification


def create_notification(recipient, actor, verb, target=None):
    """
    Create a notification.
    Examples:
        - actor liked your post
        - actor started following you
        - actor commented on your post

    verb = "liked", "followed", "commented"
    target = post or user object
    """

    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=verb,
        target_object=target
    )


def mark_all_as_read(user):
    """
    Mark all unread notifications for a user as read.
    """
    return Notification.objects.filter(
        recipient=user,
        read=False
    ).update(read=True)
