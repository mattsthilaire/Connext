from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from .storage import UserS3Storage
import boto3

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/users/<user_id>/photos/<filename>
    return f"users/{instance.user.id}/photos/{filename}"

class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    image = models.ImageField(upload_to=user_directory_path, storage=UserS3Storage)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

    def __str__(self):
        return self.description