from django.urls import path, re_path

from . import views

app_name = "root"
urlpatterns = [
    path("", views.index, name="index"),
    re_path("^/?404([.]html)?$", views.error404),
    path("math", views.math, name="math"),
    path("pretty", views.pretty, name="pretty"),
    path("memes", views.memes, name="memes"),
    path("creations", views.creations, name="creations"),
]
