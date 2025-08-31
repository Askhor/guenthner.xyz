# Create your views here.
import os
from pathlib import Path

from django.http import HttpRequest, Http404

from general import default_render


def index(request: HttpRequest):
    return default_render(request, "root/index.html", {
        "title": "Günthner's Webpage"
    })


def math(request: HttpRequest):
    raise Http404


def pretty(request: HttpRequest):
    raise Http404


def memes(request: HttpRequest):
    return default_render(request, "root/memes.html", {
        "title": "Memes",
        "images": os.listdir(Path("/") / "var" / "www" / "guenthner.xyz" / "images" / "memes"),
    })


def creations(request: HttpRequest):
    return default_render(request, "root/creations.html", {
        "title": "Creations"
    })


def cowsay(request: HttpRequest):
    return default_render(request, "root/creations/cowsay.html", {
        "title": "Cowsay",
        "output": "hi, there!"
    })


def chat(request: HttpRequest):
    return default_render(request, "root/creations/chat.html", {
        "title": "Chat"
    })
