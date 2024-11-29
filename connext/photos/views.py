import base64
import json
import requests
import io
import string

from django.conf import settings
from django.db.models import Case, F, IntegerField, Q, When
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_not_required, login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from .models import Photo
from django.contrib.auth.models import User

from .utils.search_utils import tokenize

@login_not_required
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
    user_id = User.objects.get(username=photo.user).id # get User ID for linking user page
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
        "user_id": user_id,
        "caption": caption,
    }
    return render(request, "photos/photo.html", context)

def user_photos(request, user_id):
    user = get_user_model()
    user = get_object_or_404(user, pk=user_id)
    user_photos = Photo.objects.filter(user_id=user_id).order_by("-created_at")
    context = {
        "photos": user_photos,
        "user": user,
    }
    return render(request, "photos/user.html", context)

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
        headers={"Authorization": api_key},
        timeout=settings.TIMEOUT)
    
    if resp.status_code == 200:
        return resp.json()["output"]["caption"]
    else:
        return "Failed to generate caption"
    
def search(request):
    query = request.GET.get("query")
    query_tokens = tokenize(query)
    
    method = "fusion"
    if method == "tfidf":
        resp = requests.post(
            settings.TFIDF_TEXT_SEARCH_URL,
            data=json.dumps({"query": query, "topk": settings.TOPK}),
            timeout=settings.TIMEOUT
        )

        top_images = json.loads(resp.text)["top_ids"]
        
        preserved_order = Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(top_images)],
            output_field=IntegerField()
            )
        photos = Photo.objects.filter(pk__in=top_images).order_by(preserved_order)

    elif method == "semantic":
        resp = requests.post(
            settings.SEMANTIC_EMBEDDING_URL,
            headers={"Authorization": settings.RUNDPOD_API_KEY},
            data=json.dumps({"input": {"text": query, "topk": settings.TOPK}}),
            timeout=settings.TIMEOUT
        )

        embedding = json.loads(resp.text)["output"]["embedding"]

        resp = requests.post(
            settings.SEMANTIC_TEXT_SEARCH_URL,
            data=json.dumps({"query": embedding, "topk": settings.TOPK}),
            timeout=settings.TIMEOUT
        )

        top_images = json.loads(resp.text)["ordered_ids"]

        preserved_order = Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(top_images)],
            output_field=IntegerField()
            )
        photos = Photo.objects.filter(pk__in=top_images).order_by(preserved_order)

    elif method == "fusion":
        tfidf_resp = requests.post(
            settings.TFIDF_TEXT_SEARCH_URL,
            data=json.dumps({"query": query, "topk": settings.TOPK}),
            timeout=settings.TIMEOUT
        )

        embedding_resp = requests.post(
            settings.SEMANTIC_EMBEDDING_URL,
            headers={"Authorization": settings.RUNDPOD_API_KEY},
            data=json.dumps({"input": {"text": query, "topk": settings.TOPK}}),
            timeout=settings.TIMEOUT
        )

        embedding = json.loads(embedding_resp.text)["output"]["embedding"]

        semantic_resp = requests.post(
            settings.SEMANTIC_TEXT_SEARCH_URL,
            data=json.dumps({"query": embedding, "topk": settings.TOPK}),
            timeout=settings.TIMEOUT
        )

        data = {"rankers": {
            "tfidf": json.loads(tfidf_resp.text)["top_ids"],
            "semantic": json.loads(semantic_resp.text)["ordered_ids"]
            },
            "topk": settings.TOPK
        }

        reranker_resp = requests.post(
            settings.RERANKER_URL,
            data=json.dumps(data),
            timeout=settings.TIMEOUT
        )

        top_images = json.loads(reranker_resp.text)["ranked_idx"]
        
        preserved_order = Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(top_images)],
            output_field=IntegerField()
            )
        photos = Photo.objects.filter(pk__in=top_images).order_by(preserved_order)
    
    else:
        query_filters = Q()
        
        if query:
            for token in query_tokens:
                query_filters |= Q(description__icontains=token)
            photos = Photo.objects.filter(query_filters).distinct()[:settings.TOPK]
        else:
            photos = Photo.objects.none()
            
    context = {
        "photos": photos,
        "query": query,
    }
    
    return render(request, "photos/search.html", context)