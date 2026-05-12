# Create your views here.
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from movies.models import Actor, Film
from movies.normalize import normalize

PAGE_SIZE = 50


def search(request: HttpRequest) -> HttpResponse:
    q = request.GET.get("q", "").strip()
    films, actors = [], []
    if q:
        q_norm = normalize(q)
        films = Film.objects.filter(title_normalized__icontains=q_norm)[:PAGE_SIZE]
        actors = Actor.objects.filter(name_normalized__icontains=q_norm)[:PAGE_SIZE]
    return render(request, "movies/search.html", {"films": films, "actors": actors, "q": q})


def film_detail(request: HttpRequest, pk: int) -> HttpResponse:
    film = get_object_or_404(Film, pk=pk)
    return render(request, "movies/film_detail.html", {"film": film})


def actor_detail(request: HttpRequest, pk: int) -> HttpResponse:
    actor = get_object_or_404(Actor, pk=pk)
    return render(request, "movies/actor_detail.html", {"actor": actor})
