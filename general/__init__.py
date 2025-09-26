import logging
import time
from pathlib import Path

import magic
from django.contrib import sitemaps
from django.contrib.sitemaps.views import sitemap
from django.http import HttpRequest, HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import render
from django.urls import path
from django.urls import reverse

from guenthner_xyz import settings

log = logging.getLogger("my")


def default_render(request: HttpRequest, template_name: str, context) -> HttpResponse:
    return render(request, template_name, {**get_default_context(request), **context})


def plain_redirect(to: str, permanent: bool = False) -> HttpResponse:
    if permanent:
        return HttpResponsePermanentRedirect(to)
    else:
        return HttpResponseRedirect(to)


def _get_parent_paths(request: HttpRequest) -> list:
    path_components = request.path.strip("/").split("/")

    cumulative_path = ""
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


def exception_to_response(exception, status: int):
    def wrapper1(func):
        def wrapper2(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception as e:
                return HttpResponse(str(e), status=status, content_type="text/plain; charset=utf-8")

        return wrapper2

    return wrapper1


class UserError(Exception):
    pass


class DebugTimer:
    def __init__(self):
        self.start = time.time()

    def log(self, message):
        now = time.time()
        delta = now - self.start
        log.info(f"{message:20} at {delta:5.2f} seconds")


def log_call(func):
    def func_wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        log.info(f"{func.__name__} with {args} and {kwargs} returned {result}")
        return result

    return func_wrapper


def overwrite_result(mapping):
    def wrapper(func):
        def func_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if result in mapping:
                return mapping[result]
            return result

        return func_wrapper

    return wrapper


@overwrite_result({"audio/x-hx-aac-adts": "audio/aac"})
def get_mime_type(p: Path):
    if p.is_dir():
        return "inode/directory"

    try:
        return magic.from_file(p, mime=True)
    except Exception as e:
        # Sometimes the function just fails
        log.error(f"Could not determine mime type of {p}; reason: {e}")
        return "text/plain;charset=utf-8"
