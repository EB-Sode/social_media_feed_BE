from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    """
    AbstractUser extension to include additional fields.
    """
    bio = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    profile_image = models.URLField(max_length=500, blank=True, null=True)
    cover_image = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.username
    
    def following_count(self):
        return self.following.count()
    
    def followers_count(self):
        return self.followers.count()
    