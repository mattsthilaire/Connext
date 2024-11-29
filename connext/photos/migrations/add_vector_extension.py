from django.db import migrations
from pgvector.django import VectorExtension

class Migration(migrations.Migration):
    dependencies = [
        ("photos", "0004_alter_photo_image"),  # Replace with your last migration
    ]
    operations = [
        VectorExtension()
    ]