from django.contrib import sitemaps
from django.contrib.sitemaps.views import sitemap
from django.http import HttpRequest, HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import render
from django.urls import path
from django.urls import reverse

from guenthner_xyz import settings


def default_render(request: HttpRequest, template_name: str, context) -> HttpResponse:
    return render(request, template_name, {**get_default_context(request), **context})


def plain_redirect(to: str, permanent: bool = False) -> HttpResponse:
    if permanent:
        return HttpResponsePermanentRedirect(to)
    else:
        return HttpResponseRedirect(to)


def _get_parent_paths(request: HttpRequest) -> list:
    path_components = request.path.strip("/").split("/")

    cumulative_path = request.get_host()
    output = [{"name": "root",
               "path": cumulative_path}]

    for component in path_components:
        if component.strip() == "": continue
        cumulative_path += "/" + component
        output.append({"name": component,
                       "path": cumulative_path})

    return output


def get_default_context(request: HttpRequest) -> HttpResponse:
    if settings.DEBUG:
        schost = "http://localhost:8000"
    elif request is None:
        schost = "https://guenthner.xyz"
    else:
        schost = f"https://{request.get_host()}"

    response = {"schost": schost,
                "website_version": "2025.9.5",
                "author": "J. Günthner"}

    if request is not None:
        response["parent_paths"] = _get_parent_paths(request)

    return response


class MySitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def __init__(self, *items):
        self.my_items = items

    def items(self):
        return self.my_items

    def location(self, item):
        return reverse(item)

    @classmethod
    def with_path(cls, route: str, *items):
        return path(route, sitemap, {"sitemaps": {"main": cls(*items), }})
