import datetime
import hashlib
import json
import logging
import os
import shutil
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpRequest, HttpResponse, FileResponse, JsonResponse, \
    HttpResponseServerError
from django.utils import timezone
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.http import require_http_methods, condition, require_safe
from django.views.decorators.vary import vary_on_headers

from general import default_render, exception_to_response, UserError, get_mime_type
from guenthner_xyz import settings
from private.icons import img_file_icon
from private.models import FilePacket, PermissionsRule
from template_tags import base64e

log = logging.getLogger("my")

fs_root = settings.FFS_FS_ROOT
file_packet_cache = settings.FFS_FILE_PACKET_CACHE


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
            if request.method == "HEAD":
                return HttpResponse(status=404, content_type="text/plain; charset=utf-8")
            return HttpResponse(f"File {path} does not exist", status=404,
                                content_type="text/plain; charset=utf-8")
        return func(request, path)

    return wrapper


def check_path(request: HttpRequest, path: Path):
    if path.is_absolute():
        raise UserError("Path must not be absolute and it really looks like that")


def check_permissions(request: HttpRequest, path: Path):
    for rule in PermissionsRule.objects.all():
        if not rule.user_allowed(path, str(request.user)):
            return HttpResponse(f"You are not allowed to view this location.\n"
                                f"You have been blocked by the rule:\n"
                                f"{rule}", status=403, content_type="text/plain; charset=utf-8")

    return None


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


@never_cache
@require_http_methods(["GET"])
@require_path_exists
@condition(etag_func=get_path_etag, last_modified_func=get_path_last_mod)
def api_raw(request: HttpRequest, path: Path):
    full_path = fs_root / path

    if full_path.is_file():
        return FileResponse(open(full_path, "rb"), content_type=get_mime_type(full_path))
    else:
        files = list(full_path.iterdir())
        files.sort()
        files = [*filter(lambda f: not f.is_file(), files),
                 *filter(lambda f: f.is_file(), files)]
        files = {p.name: str(p.relative_to(fs_root)) for p in files}

        return JsonResponse(files)


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
        title_msg = "Directory"
        files = list(full_path.iterdir())
        files.sort()
        extra_context = {
            # "files": [f.relative_to(fs_root) for f in files if f.is_file()],
            # "folders": [f.relative_to(fs_root) for f in files if not f.is_file()],
            "net_block_size": settings.FFS_NET_BLOCK_SIZE}

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


@never_cache
@require_safe
@require_path_exists
@condition(etag_func=get_path_etag, last_modified_func=get_path_last_mod)
def api_info(request: HttpRequest, path: Path):
    if request.method == "HEAD":
        return HttpResponse(status=200)

    full_path = fs_root / path

    mime = get_mime_type(full_path)

    return JsonResponse({
        "path": str(path),
        "name": path.name,
        "size": full_path.stat().st_size,
        "mime": mime,
        "ascii key": base64e(path.name)
    })


@require_http_methods(["POST"])
@require_path_exists
def api_move(request: HttpRequest, src: Path):
    dst = request.body.decode('utf-8')

    if (r := check_permissions(request, dst)) is not None:
        return r

    full_src = fs_root / src
    full_dst = fs_root / dst

    if full_dst.exists():
        return HttpResponse(f"The file at {dst} already exists", status=400)

    shutil.move(full_src, full_dst)

    return HttpResponse(status=200)


@require_http_methods(["POST"])
def api_new(request: HttpRequest, path: Path):
    full_path = fs_root / path

    if full_path.exists():
        return HttpResponse(f"The file at {path} already exists", status=400)
    else:
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.touch()
        return HttpResponse(status=201)


@require_http_methods(["POST"])
def api_mkdir(request: HttpRequest, path: Path):
    full_path = fs_root / path

    if full_path.exists():
        return HttpResponse(f"The file at {path} already exists", status=400)
    else:
        full_path.mkdir(parents=True)
        return HttpResponse(status=201)


class api_class:
    @classmethod
    def dispatch(cls, request: HttpRequest, *args):
        match request.method:
            case "HEAD":
                return cls.get_or_head(request, *args, False)
            case "GET":
                return cls.get_or_head(request, *args, True)
            case "POST":
                return cls.post(request, *args)
            case _:
                log.error("Well, I forgot something again")
                return HttpResponse(status=500)


class FileHasher:
    def __init__(self, path: Path, buffer_size: int = 2 ** 16):
        self.path = path
        self.buffer_size = buffer_size

    def __enter__(self):
        self.buffer = bytearray(self.buffer_size)
        self.memory_view = memoryview(self.buffer)
        self.fp = open(self.path, "rb", buffering=0)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fp.close()

    def hash(self, start, length, debug=False):
        if debug:
            hsh = []
        else:
            hsh = hashlib.sha256()
        self.fp.seek(start, os.SEEK_SET)

        while n := self.fp.readinto(self.memory_view):
            memory = self.memory_view[:min(length, n)]
            if debug:
                hsh.append(memory.tobytes().decode())
            else:
                hsh.update(memory)
            length -= n

        if debug:
            return hsh
        else:
            return hsh.hexdigest()


class api_file_ledger(api_class):
    @classmethod
    def get_or_head(cls, request: HttpRequest, path: Path, is_get: bool):
        full_path = fs_root / path

        if not full_path.is_file():
            content = None
            if is_get:
                content = f"The file at {path} is a folder"

            return HttpResponse(status=400, content_type="text/plain; charset=utf-8", content=content)

        if not is_get:
            return HttpResponse(status=200)

        size = full_path.stat().st_size
        hashes = {}

        with FileHasher(full_path) as hasher:
            for offset in range(0, size, settings.FFS_NET_BLOCK_SIZE):
                hsh = hasher.hash(offset, settings.FFS_NET_BLOCK_SIZE)
                hashes[hsh] = FilePacket.status_for(hsh)

        return JsonResponse(status=200, data={"hashes": hashes})

    @classmethod
    def post_status_response(cls, packet_info, success):
        return JsonResponse(status=200 if success else 202, data=packet_info)

    @classmethod
    def post(cls, request: HttpRequest, path: Path):
        full_path = fs_root / path

        if full_path.exists():
            return HttpResponse(status=400, content_type="text/plain; charset=utf-8",
                                content=f"The file at {path} already exists")

        # Client sent wrong body:
        try:
            data = json.loads(request.body.decode())
            hashes = data["hashes"]
        except json.JSONDecodeError:
            return HttpResponse(status=400, content_type="text/plain; charset=utf-8",
                                content="The request was not valid JSON")
        except (KeyError, TypeError):
            return HttpResponse(status=400, content_type="text/plain; charset=utf-8",
                                content="The request did not contain the hashes key (or something related)")

        full_path.parent.mkdir(parents=True, exist_ok=True)
        if len(hashes) == 0:
            full_path.touch()
            return HttpResponse(status=200)

        missing = []
        packet_info = {}

        for hsh in hashes:
            status = FilePacket.status_for(hsh)
            if status != FilePacket.STORED:
                missing.append(hsh)
            packet_info[hsh] = status

        if len(missing) > 0:
            return cls.post_status_response(packet_info, False)

        packets = [FilePacket.objects.get(hsh=hsh) for hsh in hashes]
        files = [p.file for p in packets]

        try:
            with open(full_path, "wb") as dst:
                for f in files:
                    with open(file_packet_cache / f, "rb") as src:
                        shutil.copyfileobj(src, dst)
        except Exception as e:
            full_path.unlink(missing_ok=True)
            raise e

        return cls.post_status_response(packet_info, True)

    @staticmethod
    @never_cache
    @require_http_methods(["GET", "POST", "HEAD"])
    @condition(etag_func=get_path_etag, last_modified_func=get_path_last_mod)
    def call(request: HttpRequest, path: Path):
        cls = api_file_ledger
        return cls.dispatch(request, path)


class api_file_packet(api_class):
    @classmethod
    def file_for_file_packet(cls, hsh: str):
        hsh = str(hsh)
        a = hsh[:2]
        b = hsh[2:]
        return Path(a) / b

    @classmethod
    def get_or_head(cls, request: HttpRequest, hsh: str, is_get: bool):
        content = None

        headers = {
            "X-File-Packet-Status": FilePacket.PENDING,
        }

        try:
            packet = FilePacket.objects.get(hsh=hsh)
            headers["X-File-Packet-Status"] = packet.status

            if packet.status == packet.STORED:
                file = file_packet_cache / packet.file
                if not file.exists() or not file.is_file():
                    if is_get:
                        content = "Internal error while reading file packet"
                    return HttpResponse(status=500,
                                        content_type="text/plain;charset=utf-8", content=content, headers=headers)

                packet.save()
                if is_get:
                    return FileResponse(open(file, "rb"), content_type="application/octet-stream", headers=headers)
                else:
                    return HttpResponse(status=200, headers=headers)
            else:
                raise RuntimeError()
        except (FilePacket.DoesNotExist, RuntimeError):
            content = f"File packet for hash {hsh} does not exist"
            return HttpResponse(status=404, content=content, content_type="text/plain;charset=utf-8", headers=headers)

    @classmethod
    def delete_old(cls, max_age=48):
        to_delete = FilePacket.objects.filter(
            last_used__lt=timezone.now() - datetime.timedelta(hours=max_age))

        if len(to_delete) > 0:
            log.info(f"Deleting {len(to_delete)} old file packets")

        for p in to_delete:
            if p.status == FilePacket.STORED:
                file = file_packet_cache / p.file
                if file.exists():
                    file.unlink()
                else:
                    log.error(f"File packet for hash {p.hsh} is missing during automatic cleanup")
            p.delete()

    @classmethod
    def post(cls, request: HttpRequest, hsh: str):
        def pre_return(_packet: FilePacket):
            _packet.save()
            cls.delete_old()

        hsh = str(hsh)
        packet, _ = FilePacket.objects.get_or_create(hsh=hsh)

        if packet.status == FilePacket.STORED:
            pre_return(packet)
            return HttpResponse(status=400, content=f"File Packet with hash {hsh} was already uploaded",
                                content_type="text/plain;charset=utf-8",
                                headers={"X-File-Packet-Status": packet.status})

        if packet.status == FilePacket.NEW:
            packet.file = cls.file_for_file_packet(hsh)

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
            pre_return(packet)
            content = f"Actual file hash:\n{check_hash} ({len(check_hash)})\ndoes not match specified hash:\n{hsh} ({len(str(hsh))})\n"
            if file.stat().st_size < 100:
                content += f"What you uploaded: {file.read_text()}\n"
            return HttpResponse(status=400,
                                content=content,
                                content_type="text/plain;charset=utf-8",
                                headers={"X-File-Packet-Status": packet.status})

        packet.status = FilePacket.STORED
        pre_return(packet)
        return HttpResponse(status=200, headers={"X-File-Packet-Status": packet.status})

    @staticmethod
    @require_http_methods(["GET", "POST", "HEAD"])
    @vary_on_headers("X-File-Packet-Status")
    @condition(etag_func=get_path_etag, last_modified_func=get_path_last_mod)
    def call(request: HttpRequest, hsh: str):
        cls = api_file_packet
        return cls.dispatch(request, hsh)


@login_required
@permission_required("private.ffs")
@cache_control(max_age=60 * 60)
@exception_to_response(UserError, 400)
def view_api(request: HttpRequest, api: str, path: Path = Path("")):
    valid_apis = ["raw", "files", "info", "icon", "file-packet", "file-ledger", "move", "new", "mkdir"]

    if api not in valid_apis:
        raise UserError(f"The requested API does not exist: {api}, the only options are {valid_apis}")

    path = Path(path)
    check_path(request, path)

    if (r := check_permissions(request, path)) is not None:
        return r

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
            return api_file_packet.call(request, path)
        case "file-ledger":
            return api_file_ledger.call(request, path)
        case "move":
            return api_move(request, path)
        case "new":
            return api_new(request, path)
        case "mkdir":
            return api_mkdir(request, path)

    return HttpResponseServerError("Did not configure my stuff correctly")
