import os
import platform
import struct
import subprocess
from pathlib import Path

from PIL import Image
from PyInstaller.__main__ import run


ROOT = Path(__file__).resolve().parent.parent
ICON_ASSET_DIRECTORY = ROOT / "assets" / "icons"
SOURCE_ICON = ICON_ASSET_DIRECTORY / "pdf_manager_logo_256x256.ico"
ICON_SIZES = (16, 32, 48, 64, 128, 256)
ICON_DIRECTORY = ROOT / ".build_icons"


def largest_icon_frame(icon_path):
    with Image.open(icon_path) as icon:
        frame_count = getattr(icon, "n_frames", 1)
        largest_frame = max(
            range(frame_count),
            key=lambda frame: icon_size(icon, frame),
        )
        icon.seek(largest_frame)
        return icon.convert("RGBA")


def icon_size(icon, frame):
    icon.seek(frame)
    return icon.width * icon.height


def load_icon(size):
    icon_path = ICON_ASSET_DIRECTORY / f"pdf_manager_logo_{size}x{size}.ico"
    if icon_path.is_file():
        return largest_icon_frame(icon_path)
    with largest_icon_frame(SOURCE_ICON) as source_image:
        return source_image.resize((size, size), Image.Resampling.LANCZOS)


def create_windows_icon():
    icon_path = ICON_DIRECTORY / "PDFManager.ico"
    directory_entries = []
    image_data = []
    offset = 6 + 16 * len(ICON_SIZES)

    for size in ICON_SIZES:
        source_path = ICON_ASSET_DIRECTORY / f"pdf_manager_logo_{size}x{size}.ico"
        data = source_path.read_bytes()
        reserved, image_type, count = struct.unpack_from("<HHH", data)
        if reserved != 0 or image_type != 1 or count != 1:
            raise ValueError(f"Expected a single-image ICO file: {source_path}")
        entry = bytearray(data[6:22])
        image_length, = struct.unpack_from("<I", entry, 8)
        image_offset, = struct.unpack_from("<I", entry, 12)
        image = data[image_offset:image_offset + image_length]
        struct.pack_into("<I", entry, 12, offset)
        directory_entries.append(entry)
        image_data.append(image)
        offset += len(image)

    with icon_path.open("wb") as output:
        output.write(struct.pack("<HHH", 0, 1, len(ICON_SIZES)))
        for entry in directory_entries:
            output.write(entry)
        for image in image_data:
            output.write(image)
    return icon_path


def create_macos_icon():
    iconset = ICON_DIRECTORY / "PDFManager.iconset"
    iconset.mkdir(parents=True, exist_ok=True)
    sizes = (16, 32, 128, 256, 512)
    for size in sizes:
        load_icon(size).save(iconset / f"icon_{size}x{size}.png")
        load_icon(size * 2).save(iconset / f"icon_{size}x{size}@2x.png")

    icon_path = ICON_DIRECTORY / "PDFManager.icns"
    subprocess.run(
        ["iconutil", "-c", "icns", str(iconset), "-o", str(icon_path)],
        check=True,
    )
    return icon_path


def main():
    if not SOURCE_ICON.is_file():
        raise FileNotFoundError(f"Application icon not found: {SOURCE_ICON}")

    ICON_DIRECTORY.mkdir(parents=True, exist_ok=True)
    if platform.system() == "Darwin":
        build_icon = create_macos_icon()
    elif platform.system() == "Windows":
        build_icon = create_windows_icon()
    else:
        with largest_icon_frame(SOURCE_ICON) as image:
            build_icon = ICON_DIRECTORY / "PDFManager.png"
            image.save(build_icon, format="PNG")

    arguments = [
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name",
        "PDFManager",
        "--icon",
        str(build_icon),
        "--add-data",
        f"{SOURCE_ICON}{os.pathsep}assets/icons",
        "--collect-all",
        "tkinterdnd2",
        "--collect-all",
        "pymupdf",
        "--collect-all",
        "PIL",
    ]
    if platform.system() == "Windows":
        arguments.extend(
            ["--add-data", f"{build_icon}{os.pathsep}PDFManager.ico"]
        )
    arguments.append(str(ROOT / "pdf_manager.py"))
    run(arguments)


if __name__ == "__main__":
    main()
