from django.core.management.base import BaseCommand
from apps.notifications.models import Notification

class Command(BaseCommand):
    help = "Fix invalid notification_type values that break GraphQL enums."

    def handle(self, *args, **options):
        mapping = {
            "liked": "like",
            "commented": "comment",
            "followed": "follow",
            "FOLLOW": "follow",
            "LIKE": "like",
            "COMMENT": "comment",
        }

        total = 0
        for old, new in mapping.items():
            updated = Notification.objects.filter(notification_type=old).update(notification_type=new)
            total += updated

        self.stdout.write(self.style.SUCCESS(f"✅ Fixed {total} notification rows"))
