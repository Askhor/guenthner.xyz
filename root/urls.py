from django.urls import path, include

from . import views

app_name = "root"

creations_urls = [path("", views.view_creations, name="creations"),
                  path("chat", views.view_chat, name="chat"),
                  path("cowsay", views.view_cowsay, name="cowsay"),
                  path("convolutions", views.view_convolutions, name="convolutions"),]

pretty_urls = [path("", views.view_pretty, name="pretty"),
               path("words", views.view_words, name="words"),
               path("pictures", views.view_pictures, name="pictures"), ]

math_urls = [path("", views.view_math, name="math"),
             path("paper", views.view_paper, name="paper"),
             path("mandelbrot", views.view_mandelbrot, name="mandelbrot"),
             path("eratosthenes", views.view_eratosthenes, name="eratosthenes")]

urlpatterns = [
    path("", views.view_index, name="index"),
    path("math/", include(math_urls)),
    path("pretty/", include(pretty_urls)),
    path("memes", views.view_memes, name="memes"),
    path("creations/", include(creations_urls)),
]
