# apps/notifications/tasks.py

from celery import shared_task
from django.core.mail import send_mail


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_notification_email(self, subject, message, recipient_email):
    """
    Sends an email notification asynchronously using Celery.
    Retries a few times if sending fails.
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=None,  # uses DEFAULT_FROM_EMAIL if configured
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        return "Email Sent"
    except Exception as exc:
        # retry transient failures
        raise self.retry(exc=exc)