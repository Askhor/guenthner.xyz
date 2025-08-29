from django.urls import path

from . import views

app_name = "root"
urlpatterns = [
    path("", views.index, name="index"),
    path("404.html", views.error404),
    path("math", views.math, name="math"),
    path("pretty", views.pretty, name="pretty"),
    path("memes", views.memes, name="memes"),
    path("creations", views.creations, name="creations"),
]
