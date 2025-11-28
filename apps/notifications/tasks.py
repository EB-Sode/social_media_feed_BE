from celery import shared_task
from django.contrib.auth import get_user_model
from .models import Notification
from django.core.mail import send_mail

User = get_user_model()

@shared_task
def send_notification_task(user_id, message):
    """
    Celery background task to create a notification for a user.
    Ideal for async events (likes, follows, new posts)
    """

    try:
        user = User.objects.get(id=user_id)
        Notification.objects.create(user=user, message=message)
        return True
    except User.DoesNotExist:
        return False


@shared_task
def send_notification_email(subject, message, recipient):
    """
    Sends an email notification asynchronously using Celery.
    This keeps the request fast while heavy tasks run in the background.
    """
    send_mail(
        subject,
        message,
        None,
        [recipient],
        fail_silently=False,
    )
    return "Email Sent"