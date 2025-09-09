from django.http import HttpRequest
from django.shortcuts import render

from general import default_render


def view_index(request: HttpRequest):
    return default_render(request, "dev/index.html", {})