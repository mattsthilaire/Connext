from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
import boto3

@receiver(post_save, sender=User)
def create_user_folder(sender, instance, created, **kwargs):
    if created:
        s3_client = boto3.client("s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Create user folder
        user_folder = f"users/{instance.id}/"
        s3_client.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=user_folder)
        
        # Create photos subfolder
        photos_folder = f"{user_folder}photos/"
        s3_client.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=photos_folder)
        