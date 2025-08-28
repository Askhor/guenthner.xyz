# Create your views here.
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
    raise Http404


def creations(request: HttpRequest):
    raise Http404
