from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import render


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
    schost = "https://guenthner.xyz" if settings.DEBUG or request is None else f"https://{request.get_host()}"

    response = {"schost": schost,
                "website_version": "2025.9.4"}

    if request is not None:
        response["parent_paths"] = _get_parent_paths(request)

    return response
