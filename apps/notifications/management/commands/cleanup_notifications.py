from django.core.management.base import BaseCommand
from django.db.models import Count
from apps.notifications.models import Notification


class Command(BaseCommand):
    help = "Remove duplicate like/follow notifications (keeps newest per event)."

    def handle(self, *args, **options):
        self.stdout.write("🔍 Searching for duplicate notifications...")

        dupes = (
            Notification.objects
            .filter(notification_type__in=["like", "follow"])
            .values("recipient_id", "sender_id", "notification_type", "post_id")
            .annotate(c=Count("id"))
            .filter(c__gt=1)
        )

        total_deleted = 0

        for d in dupes:
            qs = Notification.objects.filter(
                recipient_id=d["recipient_id"],
                sender_id=d["sender_id"],
                notification_type=d["notification_type"],
                post_id=d["post_id"],
            ).order_by("-created_at", "-id")

            ids = list(qs.values_list("id", flat=True))

            if len(ids) > 1:
                to_delete = ids[1:]  # keep newest, delete rest
                deleted_count, _ = Notification.objects.filter(id__in=to_delete).delete()
                total_deleted += deleted_count

        self.stdout.write(self.style.SUCCESS(
            f"✅ Cleanup complete. Deleted {total_deleted} duplicate notifications."
        ))