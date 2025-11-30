"""
Mark notifications as read/unread.
Notifications are created by your business logic (e.g., in post/follow handlers).
"""

import graphene
from django.shortcuts import get_object_or_404
from .models import Notification


class MarkNotificationAsReadMutation(graphene.Mutation):
    success = graphene.Boolean()
    notification = graphene.Field(lambda: graphene.NonNull(lambda: NotificationType))

    class Arguments:
        notification_id = graphene.Int(required=True)

    def mutate(self, info, notification_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        notification = get_object_or_404(Notification, pk=notification_id)
        if notification.recipient != user:
            raise Exception("You don't have permission to modify this notification")

        notification.is_read = True
        notification.save()
        return MarkNotificationAsReadMutation(success=True, notification=notification)


class MarkAllNotificationsAsReadMutation(graphene.Mutation):
    success = graphene.Boolean()
    count = graphene.Int()  # Number of notifications marked as read
    notifications = graphene.List(lambda: NotificationType)  # All notifications

    def mutate(self, info):
        # Mark all notifications as read
        notifications = Notification.objects.all()
        updated_count = notifications.update(is_read=True)
        
        return MarkAllNotificationsAsReadMutation(
            success=True,
            count=updated_count,
            notifications=notifications
        )

# Local import
from .schema import NotificationType
