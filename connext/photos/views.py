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
        return Photo.objects.order_by("-created_at").all()

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
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "like":
            photo.likes = F("likes") + 1
        elif action == "dislike":
            photo.dislikes = F("dislikes") + 1
        photo.save()
        return HttpResponseRedirect(reverse("photos:photo", args=(photo.id,)))
    
    context = {
        "photo": photo,
    }
    return render(request, "photos/photo.html", context)
