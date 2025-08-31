import os
from pathlib import Path

from django.http import HttpRequest

from general import default_render
from general.cowsay import run_cowsay

server_root = Path("/var/www/guenthner.xyz")


def view_index(request: HttpRequest):
    return default_render(request, "root/index.html", {
        "title": "Günthner's Webpage"
    })


def view_pretty(request: HttpRequest):
    return default_render(request, "root/pretty/pretty.html", {
        "title": "Pretty Stuff I made"
    })


def view_words(request: HttpRequest):
    return default_render(request, "root/pretty/words.html", {
        "title": "Pretty Words I wrote",
        "docs": os.listdir(server_root / "documents" / "stories2"),
    })


def view_pictures(request: HttpRequest):
    return default_render(request, "root/pretty/pictures.html", {
        "title": "Pretty Pictures I made",
        "images": {"Sunlight.png": "A pretty abstract pictures with the theme sunlight",
                   "Sunlight - Pixelated.png": "The previous picture, but more pixelated",
                   "Blurry Sundown.png": "A blurry sundown recorded above a highway in Augsburg",
                   "Blurrier Sundown.png": "A blurrier version of the previous image"}
    })


def view_memes(request: HttpRequest):
    return default_render(request, "root/memes.html", {
        "title": "Memes",
        "images": os.listdir(server_root / "images" / "memes"),
    })


def view_creations(request: HttpRequest):
    return default_render(request, "root/creations/creations.html", {
        "title": "Creations"
    })


def view_cowsay(request: HttpRequest):
    return default_render(request, "root/creations/cowsay.html", {
        "title": "Cowsay",
        "output": run_cowsay()
    })


def view_chat(request: HttpRequest):
    return default_render(request, "root/creations/chat.html", {
        "title": "Chat"
    })


def view_math(request: HttpRequest):
    return default_render(request, "root/math/math.html", {
        "title": "The Math-Corner"
    })


def view_paper(request: HttpRequest):
    return default_render(request, "root/math/paper.html", {
        "title": "Paper"
    })


def view_mandelbrot(request: HttpRequest):
    return default_render(request, "root/math/mandelbrot.html", {
        "title": "Mandelbrot"
    })


def view_eratosthenes(request: HttpRequest):
    return default_render(request, "root/math/eratosthenes.html", {
        "title": "Eratosthenes"
    })
