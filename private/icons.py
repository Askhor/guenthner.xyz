import subprocess
from pathlib import Path

from private.models import Setting

fs_root = Path(Setting.objects.get(name='fs_root').value)
img_icon_root = Path(Setting.objects.get(name='img_icon_root').value)


def get_icon_file(path: Path):
    return img_icon_root / f"{path}.jpg"


def create_icon(path: Path):
    full_path = fs_root / path
    icon_file = get_icon_file(path)
    icon_file.parent.mkdir(parents=True, exist_ok=True)
    output = subprocess.run(["convert", "-resize", "32x32!", str(full_path), str(icon_file)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    if not icon_file.exists():
        raise ValueError(f"Could not create image icon:\nStdout:\n{output.stdout.decode()}\nStderr:\n{output.stderr.decode()}")


def img_file_icon(path: Path) -> Path:
    icon_file = get_icon_file(path)

    if not icon_file.exists():
        create_icon(path)

    return icon_file
