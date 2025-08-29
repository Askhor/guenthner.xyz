from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def default_render(request: HttpRequest, template_name: str, context) -> HttpResponse:
    return render(request, template_name, {**get_default_context(request), **context})


def _get_parent_paths(request: HttpRequest) -> list:
    path_components = request.path.strip("/").split("/")

    cumulative_path = "https://" + request.get_host()
    output = [{"name": "root",
               "path": cumulative_path}]

    for component in path_components:
        if component.strip() == "": continue
        cumulative_path += "/" + component
        output.append({"name": component,
                       "path": cumulative_path})

    return output


def get_default_context(request: HttpRequest):
    return {
        "parent_paths": _get_parent_paths(request),
    }
