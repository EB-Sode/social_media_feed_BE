from django.db import models
from django.conf import settings

# Create your models here.
class Follow(models.Model):
    """
    A relationship where one user follows another.
    """

    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="following",   
        on_delete=models.CASCADE,
    )
    followed = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="followers",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "followed")

    def __str__(self):
        return f"{self.follower.username} → {self.followed.username}"
