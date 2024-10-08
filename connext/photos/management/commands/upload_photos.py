import os
from pathlib import Path
import random

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from photos.models import Photo

class Command(BaseCommand):
    help = "Upload photos to S3"

    def handle(self, *args, **options):
        names_dir = Path("/Users/mattsthilaire/Downloads/first-names.txt")
        img_dir = Path("/Users/mattsthilaire/Downloads/tiny-imagenet-200/train/n09428293/images")
        
        with open(names_dir, "r") as f:
            names = [name.strip() for name in f.readlines()]
            
        for img in os.listdir(img_dir):
            
            name = random.choice(names)
            
            try:
                user = User.objects.get(username=name) if User.objects.filter(username=name).exists() else User.objects.create_user(username=name, password="password")
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User with name {name} does not exist"))
                return

            filepath = img_dir / img
            with open(filepath, "rb") as f:
                photo = Photo(
                    user=user,
                    description=f"Uploaded photo: {img}",
                    image=ImageFile(f, name=img)
                )
                photo.save()
                self.stdout.write(self.style.SUCCESS(f"Successfully uploaded {img}"))

            self.stdout.write(self.style.SUCCESS("Bulk upload completed"))