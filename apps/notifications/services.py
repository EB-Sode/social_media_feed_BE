# apps/notifications/services.py

from .models import Notification
from .tasks import send_notification_email

DEDUPED_TYPES = {"like", "follow"}


def create_notification(recipient, actor, verb, post=None, message=""):
    verb = (verb or "mention").lower()
    msg = message or default_message(verb)

    if verb in DEDUPED_TYPES:
        notif, created = Notification.objects.get_or_create(
            recipient=recipient,
            sender=actor,
            notification_type=verb,
            post=post,
            defaults={"message": msg},
        )

        # Optional: normalize message if it differs (prevents mixed formats)
        if notif.message != msg:
            notif.message = msg
            notif.save(update_fields=["message"])

    else:
        notif = Notification.objects.create(
            recipient=recipient,
            sender=actor,
            notification_type=verb,
            post=post,
            message=msg,
        )
        created = True  # ✅ important

    # Only email when it was actually created
    if created and getattr(recipient, "email", None):
        send_notification_email.delay(
            email_subject_for(verb),
            email_body_for(notif, actor=actor, verb=verb, post=post),
            recipient.email,
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
    actor_name = getattr(actor, "username", "Someone")
    base = f"{actor_name} {notif.message}."

    if post is not None:
        content = getattr(post, "content", "") or ""
        snippet = (content[:80] + "...") if len(content) > 80 else content
        if snippet:
            base += f"\n\nPost: {snippet}"

    return base


def mark_all_as_read(user):
    return Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)