import json
from pathlib import Path

from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from general import default_render


@login_required
@permission_required("root.admin")
def view_index(request: HttpRequest):
    return default_render(request, "dev/index.html", {
        "title": "Dev Stuff",
    })


@login_required
@permission_required("root.admin")
def view_log(request: HttpRequest, service: str, name: str):
    file = Path("/var/log") / service / f"{name}.log"

    try:
        content = file.read_text(encoding="utf-8")
    except (FileNotFoundError, IOError) as e:
        content = f"Could not read file {file}:\n{e}"

    return HttpResponse(content, content_type="text/plain; charset=utf-8")


@csrf_exempt
def view_headers(request: HttpRequest):
    params = {}

    for key in request.GET.keys():
        params[key] = request.GET[key]
    for key in request.POST.keys():
        params[key] = request.POST[key]


    if params["pwd"] != "fml as it sucks!":
        raise PermissionDenied

    result = ""

    for name, value in request.headers.items():
        result += f"{name}: {value}\n"

    return HttpResponse(result, content_type="text/plain; charset=utf-8")
