from pathlib import Path

from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpRequest

from general import default_render


@login_required
@permission_required("private.ffs")
def view_index(request: HttpRequest):
    return default_render(request, "private/index.html", {
        "title": "FFS"
    })


@login_required
@permission_required("private.ffs")
def view_api(request: HttpRequest, endpoint: str, path: Path):
    pass
