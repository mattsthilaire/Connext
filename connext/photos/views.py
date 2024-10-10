import base64
import requests
import io

from django.conf import settings
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_not_required, login_required
from django.utils.decorators import method_decorator
from .models import Photo

#@login_not_required
class IndexView(generic.ListView):
    template_name = "photos/index.html"
    context_object_name = "photos"
    
    def get_queryset(self):
        return Photo.objects.order_by("-created_at").all()[:500]

#@method_decorator(
#  login_required(login_url="/photos/photos", redirect_field_name="redirect_to"), 
#    name="dispatch"
#)
class DetailView(generic.DetailView):
    model = Photo
    template_name = "photos/photo.html"
    context_object_name = "photo"

def photo(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)
    caption = None
    
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "like":
            photo.likes = F("likes") + 1
        elif action == "dislike":
            photo.dislikes = F("dislikes") + 1
        elif action == "generate_caption":
            caption = generate_caption(photo.image.url)
        
        photo.save()
        
        if action in ["like", "dislike"]:
            return HttpResponseRedirect(reverse("photos:photo", args=(photo.id,)))
    
    context = {
        "photo": photo,
        "caption": caption,
    }
    return render(request, "photos/photo.html", context)

def generate_caption(image_url):
    
    api_url = settings.RUNPOD_IMAGE_CAPTIONING_URL
    api_key = settings.RUNDPOD_API_KEY
    
    resp = requests.get(image_url)
    if resp.status_code != 200:
        return "Failed to fetch image"
    
    encoded_string = base64.b64encode(resp.content).decode("utf-8")
        
    resp = requests.post(
        api_url, 
        json={"input": {"image": encoded_string}},
        headers={"Authorization": api_key},)
    
    if resp.status_code == 200:
        return resp.json()["output"]["caption"]
    else:
        return "Failed to generate caption"