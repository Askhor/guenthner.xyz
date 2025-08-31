from django.urls import path, include

from . import views

app_name = "root"

creations_urls = [path("", views.creations, name="creations"),
                  path("chat", views.chat, name="chat"),
                  path("cowsay", views.cowsay, name="cowsay")]

pretty_urls = [path("", views.pretty, name="pretty"),
               path("words", views.words, name="words"),
               path("pictures", views.pictures, name="pictures"), ]

urlpatterns = [
    path("", views.index, name="index"),
    path("math/", views.math, name="math"),
    path("pretty/", include(pretty_urls)),
    path("memes", views.memes, name="memes"),
    path("creations/", include(creations_urls)),
]
