from django.contrib import admin
from .models import Photo

from .models import Photo


class PhotoAdmin(admin.ModelAdmin):
    fieldsets =[
        (None, {"fields": ["user", "description", "image"]}),
        ("Likes and Dislikes", {"fields": ["likes", "dislikes"]}),
    ]
    list_display = ["description", "image", "likes", "dislikes", "created_at", "updated_at"]

admin.site.register(Photo, PhotoAdmin)
