from django.urls import path

from . import views

app_name = "movies"
urlpatterns = [
    path("", views.search, name="search"),
    path("film/<int:pk>/", views.film_detail, name="film_detail"),
    path("actor/<int:pk>/", views.actor_detail, name="actor_detail"),
]
