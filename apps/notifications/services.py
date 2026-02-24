from .models import Notification
from .tasks import send_notification_email


def create_notification(recipient, actor, verb, post=None, message=""):
    """
    Create a notification (sync DB write) and optionally trigger async email.

    verb should match your model choices:
      "like" | "comment" | "follow" | "mention"
    """
    verb = (verb or "mention").lower()

    notif = Notification.objects.create(
        recipient=recipient,
        sender=actor,
        notification_type=verb,
        post=post,
        message=message or default_message(verb),
    )

    # Email async (optional)
    recipient_email = getattr(recipient, "email", None)
    if recipient_email:
        send_notification_email.delay(
            subject=email_subject_for(verb),
            message=email_body_for(notif, actor=actor, verb=verb, post=post),
            recipient_email=recipient_email,
        )

    return notif


def default_message(verb: str) -> str:
    return {
        "like": "liked your post",
        "comment": "commented on your post",
        "follow": "started following you",
        "mention": "mentioned you",
    }.get(verb, verb)


def email_subject_for(verb: str) -> str:
    return {
        "like": "New like",
        "comment": "New comment",
        "follow": "New follower",
        "mention": "New mention",
    }.get(verb, "New notification")


def email_body_for(notif: Notification, actor, verb: str, post=None) -> str:
    """
    Keep email content simple and safe.
    You can expand this later to include links, richer formatting, etc.
    """
    actor_name = getattr(actor, "username", "Someone")
    base = f"{actor_name} {notif.message}."

    if post is not None:
        # optional snippet
        content = getattr(post, "content", "") or ""
        snippet = (content[:80] + "...") if len(content) > 80 else content
        if snippet:
            base += f"\n\nPost: {snippet}"

    return base


def mark_all_as_read(user):
    return Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)