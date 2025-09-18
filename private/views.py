import datetime
import hashlib
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpRequest, HttpResponse, FileResponse, JsonResponse, \
    HttpResponseServerError
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, condition
from django.views.decorators.vary import vary_on_headers
from magic.compat import detect_from_filename

from general import default_render, exception_to_response, UserError
from private.icons import img_file_icon
from private.models import Setting
from template_tags import base64e

fs_root = Path(Setting.objects.get(name='fs_root').value)


@cache_control(max_age=settings.CACHE_MIDDLEWARE_SECONDS)
@condition(etag_func=lambda request: str(request.user))
@login_required
@permission_required("private.ffs")
def view_index(request: HttpRequest):
    return default_render(request, "private/index.html", {
        "title": "FFS"
    })


def require_path_exists(func):
    def wrapper(request: HttpRequest, path: Path):
        if not (fs_root / path).exists():
            return HttpResponse(f"File {path} does not exist", status=404,
                                content_type="text/plain; charset=utf-8")
        return func(request, path)

    return wrapper


def check_path(request: HttpRequest, path: Path):
    if path.is_absolute():
        raise UserError("Path must not be absolute and it really looks like that")


def check_permissions(request: HttpRequest, path: Path):
    pass


def get_path_last_mod(request, path: Path):
    full_path = fs_root / path
    if not full_path.exists():
        return None
    return datetime.datetime.fromtimestamp(full_path.stat().st_mtime)


def get_path_etag(request, path: Path):
    full_path = fs_root / path

    if not full_path.exists():
        return None

    hsh = hashlib.sha256()

    if full_path.is_file():
        hsh.update(str(full_path.stat().st_mtime).encode())
        hsh.update(str(full_path.stat().st_size).encode())
    else:
        for f in full_path.iterdir():
            hsh.update(f.name.encode())

    return hsh.hexdigest()


@require_http_methods(["GET"])
@require_path_exists
@cache_control(max_age=settings.CACHE_MIDDLEWARE_SECONDS)
@condition(etag_func=get_path_etag, last_modified_func=get_path_last_mod)
def api_raw(request: HttpRequest, path: Path):
    full_path = fs_root / path

    if full_path.is_file():
        return FileResponse(open(full_path, "rb"))
    else:
        return JsonResponse({p.name: str(p.relative_to(fs_root)) for p in sorted(full_path.iterdir())})


@require_http_methods(["GET"])
@condition(etag_func=get_path_etag, last_modified_func=get_path_last_mod)
def api_files(request: HttpRequest, path: Path):
    full_path = fs_root / path
    extra_context = {}

    if not full_path.exists():
        template_name = "file_404"
        title_msg = "does not exist"
    elif full_path.is_file():
        return api_raw(request, path)
    else:
        template_name = "files"
        title_msg = "Files"
        files = list(full_path.iterdir())
        files.sort()
        extra_context = {"files": [f.relative_to(fs_root) for f in files if f.is_file()],
                         "folders": [f.relative_to(fs_root) for f in files if not f.is_file()]}

    return default_render(request, f"private/{template_name}.html", {
        "title": f"{path}: {title_msg}", **extra_context,
        "path": path,
    })


@require_http_methods(["GET"])
@require_path_exists
@condition(etag_func=get_path_etag, last_modified_func=get_path_last_mod)
def api_icon(request: HttpRequest, path: Path):
    try:
        return FileResponse(open(img_file_icon(path), "rb"))
    except RuntimeError:
        return HttpResponse(status=500)


@require_http_methods(["GET"])
@require_path_exists
@condition(etag_func=get_path_etag, last_modified_func=get_path_last_mod)
def api_info(request: HttpRequest, path: Path):
    full_path = fs_root / path

    try:
        mime = detect_from_filename(full_path).mime_type
    except Exception:
        # Sometimes the function just fails
        mime = "text/plain;charset=utf-8"

    return JsonResponse({
        "path": str(path),
        "name": path.name,
        "size": full_path.stat().st_size,
        "mime": mime,
        "ascii key": base64e(path.name)
    })


# file_packet:
# - hash
# - content (binary)
# - path
# - name
#
# function get_file_packet(hash) -> file_packet
# js:
# - Get from local cache
# - Send request
# py:
# - Get from fs
# - Wait for request

@require_http_methods(["GET", "POST"])
@vary_on_headers("X-File-Packet-Hash")
@csrf_exempt
@require_path_exists
@condition(etag_func=get_path_etag, last_modified_func=get_path_last_mod)
def api_file_packet(request: HttpRequest, path: Path):
    return HttpResponse("Ho!")

    match request.method:
        case "GET":
            pass
        case "PUT":
            pass
        case _:
            raise RuntimeError()


@login_required
@permission_required("private.ffs")
@cache_control(max_age=settings.CACHE_MIDDLEWARE_SECONDS)
@exception_to_response(UserError, 400)
def view_api(request: HttpRequest, api: str, path: Path = Path("")):
    valid_apis = ["raw", "files", "info", "icon", "file_packet"]

    if api not in valid_apis:
        raise UserError(f"The requested API does not exist: {api}, the only options are {valid_apis}")

    path = Path(path)
    check_path(request, path)
    check_permissions(request, path)

    match api:
        case "raw":
            return api_raw(request, path)
        case "files":
            return api_files(request, path)
        case "info":
            return api_info(request, path)
        case "icon":
            return api_icon(request, path)
        case "file_packet":
            return api_file_packet(request, path)

    return HttpResponseServerError("Did not configure my stuff correctly")
