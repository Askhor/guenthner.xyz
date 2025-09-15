import math
import os
from datetime import datetime, UTC
from functools import reduce
from pathlib import Path

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.views.decorators.cache import never_cache, cache_control
from django.views.decorators.http import condition

from general import default_render
from general.cowsay import run_cowsay
from root.models import ChatMessage

server_root = Path("/var/www/guenthner.xyz")


@cache_control(max_age=settings.CACHE_MIDDLEWARE_SECONDS)
@condition(etag_func=lambda *a, **kw: "A")
def view_index(request: HttpRequest):
    return default_render(request, "root/index.html", {
        "title": "Günthner's Webpage",
        "semester": int(math.ceil((datetime.now() - datetime(2024, 4, 1)).total_seconds() / (6 * 30 * 24 * 60 * 60))),
    })


@cache_control(max_age=settings.CACHE_MIDDLEWARE_SECONDS)
@condition(etag_func=lambda *a, **kw: "A")
def view_pretty(request: HttpRequest):
    return default_render(request, "root/pretty/pretty.html", {
        "title": "Pretty Stuff I made"
    })


@cache_control(max_age=settings.CACHE_MIDDLEWARE_SECONDS)
@condition(etag_func=lambda *a, **kw: "A")
def view_words(request: HttpRequest):
    return default_render(request, "root/pretty/words.html", {
        "title": "Pretty Words I wrote",
        "docs": os.listdir(server_root / "documents" / "stories"),
    })


@cache_control(max_age=settings.CACHE_MIDDLEWARE_SECONDS)
@condition(etag_func=lambda *a, **kw: "A")
def view_pictures(request: HttpRequest):
    return default_render(request, "root/pretty/pictures.html", {
        "title": "Pretty Pictures I made",
        "images": {"Sunlight.png": "A pretty abstract pictures with the theme sunlight",
                   "Sunlight - Pixelated.png": "The previous picture, but more pixelated",
                   "Blurry Sundown.png": "A blurry sundown recorded above a highway in Augsburg",
                   "Blurrier Sundown.png": "A blurrier version of the previous image"}
    })


@cache_control(max_age=settings.CACHE_MIDDLEWARE_SECONDS)
@condition(etag_func=lambda *a, **kw: "A")
def view_memes(request: HttpRequest):
    return default_render(request, "root/memes.html", {
        "title": "Memes",
        "images": os.listdir(server_root / "images" / "memes"),
    })


@cache_control(max_age=settings.CACHE_MIDDLEWARE_SECONDS)
@condition(etag_func=lambda *a, **kw: "A")
def view_creations(request: HttpRequest):
    return default_render(request, "root/creations/creations.html", {
        "title": "Creations"
    })


@never_cache
def view_cowsay(request: HttpRequest):
    return default_render(request, "root/creations/cowsay.html", {
        "title": "Cowsay",
        "output": run_cowsay()
    })


@never_cache
def view_chat(request: HttpRequest):
    error_msg = None
    messages = ChatMessage.objects.all()

    if request.method == "POST":
        if request.POST["message"] is None:
            error_msg = "No message received by server"
        elif request.POST["message"].strip() == "":
            error_msg = "Empty message"
        elif len(messages) > 0:
            last_msg_time = reduce(max, [m.time for m in messages])
            delta = (datetime.now(tz=UTC) - last_msg_time).total_seconds()
            if delta < 10:
                error_msg = "Wait at least 10 seconds between messages"

        if error_msg is None:
            ChatMessage.objects.create(user=request.user if request.user.is_authenticated else None,
                                       message=request.POST["message"], )

        if request.POST.get("FROM_JS", False):
            return HttpResponse(error_msg, status=200 if error_msg is None else 400)

    return default_render(request, "root/creations/chat.html", {
        "title": "Chat",
        "messages": messages,
        "error_msg": error_msg})


@cache_control(max_age=settings.CACHE_MIDDLEWARE_SECONDS)
@condition(etag_func=lambda *a, **kw: "A")
def view_math(request: HttpRequest):
    return default_render(request, "root/math/math.html", {
        "title": "The Math-Corner"
    })


@cache_control(max_age=settings.CACHE_MIDDLEWARE_SECONDS)
@condition(etag_func=lambda *a, **kw: "A")
def view_paper(request: HttpRequest):
    return default_render(request, "root/math/paper.html", {
        "title": "Paper"
    })


@cache_control(max_age=settings.CACHE_MIDDLEWARE_SECONDS)
@condition(etag_func=lambda *a, **kw: "A")
def view_mandelbrot(request: HttpRequest):
    return default_render(request, "root/math/mandelbrot.html", {
        "title": "Mandelbrot"
    })


@cache_control(max_age=settings.CACHE_MIDDLEWARE_SECONDS)
@condition(etag_func=lambda *a, **kw: "A")
def view_eratosthenes(request: HttpRequest):
    return default_render(request, "root/math/eratosthenes.html", {
        "title": "Eratosthenes"
    })
