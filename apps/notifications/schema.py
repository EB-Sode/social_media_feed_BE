# apps/notifications/schema.py
"""
Notification types and read queries + mutation to mark as read.
Notifications are generated elsewhere (e.g., in services or signals when likes/comments/follows happen).
"""

import graphene
from graphene_django import DjangoObjectType
from .models import Notification


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        fields = (
            "id",
            "recipient",
            "sender",
            "notification_type",
            "post",
            "message",
            "is_read",
            "created_at",
        )


class NotificationQuery(graphene.ObjectType):
    notifications = graphene.List(NotificationType, limit=graphene.Int(), unread_only=graphene.Boolean())
    unread_notifications = graphene.List(NotificationType)

    def resolve_notifications(self, info, limit=None, unread_only=False):
        user = info.context.user
        if user.is_anonymous:
            return []

        qs = Notification.objects.filter(recipient=user)
        if unread_only:
            qs = qs.filter(is_read=False)
        if limit:
            qs = qs[:limit]
        return qs

    def resolve_unread_notifications(self, info):
        user = info.context.user
        if user.is_anonymous:
            return []
        return Notification.objects.filter(recipient=user, is_read=False)


class NotificationMutation(graphene.ObjectType):
    from .mutations import MarkNotificationAsReadMutation
    
    mark_as_read = MarkNotificationAsReadMutation.Field()
