from pathlib import Path

from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse

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


def view_headers(request: HttpRequest):
    if request.GET is None or request.GET.get("pwd", default="") != "fml as it sucks!":
        raise PermissionDenied

    result = ""

    for name, value in request.headers.items():
        result += f"{name}: {value}\n"

    return HttpResponse(result, content_type="text/plain; charset=utf-8")
