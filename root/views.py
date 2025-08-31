from pathlib import Path
from subprocess import run
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
