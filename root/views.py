from pathlib import Path

from django.http import HttpRequest, Http404

from general import default_render
from general.cowsay import run_cowsay


def index(request: HttpRequest):
    return default_render(request, "root/index.html", {
        "title": "Günthner's Webpage"
    })


def math(request: HttpRequest):
    raise Http404


def pretty(request: HttpRequest):
    return default_render(request, "root/pretty/pretty.html", {
        "title": "Pretty Stuff I made"
    })


def words(request: HttpRequest):
    return default_render(request, "root/pretty/words.html", {
        "title": "Pretty Words I wrote"
    })


def pictures(request: HttpRequest):
    return default_render(request, "root/pretty/pictures.html", {
        "title": "Pretty Pictures I made",
        "images": {"Sunlight.png": "A pretty abstract pictures with the theme sunlight",
                   "Sunlight - Pixelated.png": "The previous picture, but more pixelated",
                   "Blurry Sundown.png": "A blurry sundown recorded above a highway in Augsburg",
                   "Blurrier Sundown.png": "A blurrier version of the previous image"}
    })

def memes(request: HttpRequest):
    return default_render(request, "root/memes.html", {
        "title": "Memes",
        "images": os.listdir(Path("/") / "var" / "www" / "guenthner.xyz" / "images" / "memes"),
    })

def creations(request: HttpRequest):
    return default_render(request, "root/creations/creations.html", {
        "title": "Creations"
    })

def cowsay(request: HttpRequest):
    return default_render(request, "root/creations/cowsay.html", {
        "title": "Cowsay",
        "output": run_cowsay()
    })

def chat(request: HttpRequest):
    return default_render(request, "root/creations/chat.html", {
        "title": "Chat"
    })
