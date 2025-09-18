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
from private.models import Setting, FilePacket
from template_tags import base64e

try:
    fs_root = Path(Setting.objects.get(name='fs_root').value)
    file_packet_cache = Path(Setting.objects.get(name='file_packet_cache').value)
except Setting.DoesNotExist:
    pass


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

def file_for_file_packet(hsh: str):
    hsh = str(hsh)
    l = len(hsh)
    a = hsh[:l // 2]
    b = hsh[l // 2:]
    return Path(a) / b


def api_file_packet_get_or_head(request: HttpRequest, hsh: str, is_get: bool):
    content = None

    headers = {
        "X-File-Packet-Status": FilePacket.OUTSTANDING,
    }

    try:
        packet = FilePacket.objects.get(hsh=hsh)
        headers["X-File-Packet-Status"] = packet.status

        if packet.status == packet.STORED:
            file = file_packet_cache / packet.file
            if not file.exists():
                if is_get:
                    content = "Internal error while reading file packet"
                return HttpResponse(status=500,
                                    content_type="text/plain;charset=utf-8", content=content, headers=headers)

            if is_get:
                return FileResponse(open(file, "rb"), content_type="application/octet-stream", headers=headers)
            else:
                return HttpResponse(status=200, headers=headers)
        else:
            raise RuntimeError()
    except (FilePacket.DoesNotExist, RuntimeError):
        content = f"File packet for hash {hsh} does not exist"
        return HttpResponse(status=404, content=content, content_type="text/plain;charset=utf-8", headers=headers)


def api_file_packet_post(request: HttpRequest, hsh: str):
    hsh = str(hsh)
    packet, _ = FilePacket.objects.get_or_create(hsh=hsh)

    if packet.status == FilePacket.STORED:
        return HttpResponse(status=400, content=f"File Packet with hash {hsh} was already uploaded",
                            content_type="text/plain;charset=utf-8", headers={"X-File-Packet-Status": packet.status})

    if packet.status == FilePacket.NEW:
        packet.file = file_for_file_packet(hsh)

    packet.status = FilePacket.FAILED
    file = file_packet_cache / packet.file
    file.parent.mkdir(parents=True, exist_ok=True)
    file.touch(exist_ok=True)

    CHUNK_SIZE = 64 * 1024

    with open(file, "wb") as fp:
        while True:
            data = request.read(CHUNK_SIZE)
            if len(data) == 0:
                break

            fp.write(data)

    with open(file, "rb") as fp:
        check_hash = hashlib.file_digest(fp, "sha256").hexdigest()

    if check_hash != hsh:
        packet.save()
        return HttpResponse(status=400,
                            content=f"Actual file hash:\n{check_hash} ({len(check_hash)})\ndoes not match specified hash:\n{hsh} ({len(str(hsh))})\n",
                            content_type="text/plain;charset=utf-8")

    packet.status = FilePacket.STORED
    packet.save()
    return HttpResponse(status=200)


@require_http_methods(["GET", "POST", "HEAD"])
@vary_on_headers("X-File-Packet-Hash")
@csrf_exempt
@condition(etag_func=get_path_etag, last_modified_func=get_path_last_mod)
def api_file_packet(request: HttpRequest, hsh: str):
    match request.method:
        case "HEAD":
            return api_file_packet_get_or_head(request, hsh, False)
        case "GET":
            return api_file_packet_get_or_head(request, hsh, True)
        case "POST":
            return api_file_packet_post(request, hsh)
        case _:
            return HttpResponse(status=500)


@login_required
@permission_required("private.ffs")
@cache_control(max_age=settings.CACHE_MIDDLEWARE_SECONDS)
@exception_to_response(UserError, 400)
def view_api(request: HttpRequest, api: str, path: Path = Path("")):
    valid_apis = ["raw", "files", "info", "icon", "file-packet"]

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
        case "file-packet":
            return api_file_packet(request, path)

    return HttpResponseServerError("Did not configure my stuff correctly")
