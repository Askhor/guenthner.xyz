from django.http import HttpRequest

from general import default_render


def error404(request: HttpRequest):
    return default_render(request, "root/404", {
        "title": "404 Page"
    })
