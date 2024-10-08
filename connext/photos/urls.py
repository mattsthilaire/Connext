from django.urls import path

from . import views

app_name = "photos"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:photo_id>/photo/', views.photo, name='photo'),
]
