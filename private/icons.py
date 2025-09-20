import logging
import subprocess
from pathlib import Path

from django.conf import settings

log = logging.getLogger("my")

fs_root = settings.FFS_FS_ROOT
img_icon_root = settings.FFS_IMAGE_ICONS


def get_icon_file(path: Path):
    return img_icon_root / f"{path}.jpg"


def create_icon(path: Path):
    full_path = fs_root / path
    icon_file = get_icon_file(path)
    icon_file.parent.mkdir(parents=True, exist_ok=True)
    cmd = f'convert -resize 32x32! "{full_path}" "{icon_file}"'
    output = subprocess.run(cmd,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    if not icon_file.exists():
        msg = (f"Could not create image icon:\n"
               f"Image path: {full_path}\n"
               f"Icon path: {icon_file}\n"
               f"Stdout:\n{output.stdout.decode()}\n"
               f"Stderr:\n{output.stderr.decode()}\n"
               f"Full command: {cmd}")

        log.error(msg)
        raise RuntimeError(msg)


def img_file_icon(path: Path) -> Path:
    icon_file = get_icon_file(path)

    if not icon_file.exists():
        create_icon(path)

    return icon_file
