from django.urls import path, include

from . import views

app_name = "root"

creations_urls = [path("", views.creations, name="creations"),
                  path("chat", views.chat, name="chat"),
                  path("cowsay", views.cowsay, name="cowsay")]

urlpatterns = [
    path("", views.index, name="index"),
    path("math/", views.math, name="math"),
    path("pretty/", views.pretty, name="pretty"),
    path("memes", views.memes, name="memes"),
    path("creations/", include(creations_urls)),
]
