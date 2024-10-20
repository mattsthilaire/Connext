from contextlib import AbstractContextManager
from typing import Any
from django.test import Client, TestCase
from django.urls import reverse

from .models import Photo
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models import F

from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

class PhotoModelTests(TestCase):

    def test_photo_creation(self):
        user = User.objects.create(username="testuser", password="testpassword")
        photo = Photo.objects.create(user=user, description="Test Photo")
        self.assertEqual(photo.user, user)
        self.assertEqual(photo.description, "Test Photo")

    def test_photo_likes_and_dislikes(self):
        user = User.objects.create(username="testuser", password="testpassword")
        photo = Photo.objects.create(user=user, description="Test Photo")
        self.assertEqual(photo.likes, 0)
        self.assertEqual(photo.dislikes, 0)

    def test_photo_str_representation(self):
        user = User.objects.create(username="testuser", password="testpassword")
        
    @patch("storages.backends.s3boto3.S3Boto3Storage.save")
    def test_photo_upload(self, mock_save):
        mock_save.return_value = "users/1/photos/test_image.jpg"
        
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        photo = Photo.objects.create(user_id=1, description="Test Photo", image=image)
        
        self.assertTrue(mock_save.called)
        self.assertEqual(photo.image.name, "users/1/photos/test_image.jpg")
        
class PhotoViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.photo = Photo.objects.create(user=self.user, description="Test Photo")
        self.url = reverse("photos:photo", args=[self.photo.id])

    def test_photo_like_increment(self):
        # Ensure the photo starts with 0 likes
        print(self.photo.likes)
        self.assertEqual(self.photo.likes, 0)

        # Simulate a POST request to like the photo
        response = self.client.post(self.url, {"action": "like"})

        # Check that the response is a redirect (as per your view logic)
        self.assertEqual(response.status_code, 302)

        # Refresh the photo instance from the database
        self.photo.refresh_from_db()

        # Check that the likes have been incremented
        self.assertEqual(self.photo.likes, 1)

    def test_photo_dislike_increment(self):
        # Ensure the photo starts with 0 likes
        self.assertEqual(self.photo.likes, 0)

        # Simulate a POST request to like the photo
        response = self.client.post(self.url, {"action": "dislike"})

        # Check that the response is a redirect (as per your view logic)
        self.assertEqual(response.status_code, 302)

        # Refresh the photo instance from the database
        self.photo.refresh_from_db()

        # Check that the likes have been incremented
        self.assertEqual(self.photo.dislikes, 1)
        
    def test_user_page(self):
        url = reverse("photos:user", args=[self.user.id])
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        self.assertTemplateUsed(response=response, template_name="photos/user.html")
        
        photos_in_context = response.context["photos"]
        self.assertEqual(set(photos_in_context),
                         set(Photo.objects.filter(user=self.user)))
        