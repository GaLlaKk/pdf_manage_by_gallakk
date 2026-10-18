import argparse
import platform
import subprocess
import zipfile
from pathlib import Path


def archive_executable(executable, archive_path, arcname):
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        info = zipfile.ZipInfo(arcname)
        info.external_attr = executable.stat().st_mode << 16
        archive.writestr(info, executable.read_bytes())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist", type=Path, default=Path("dist"))
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    parser.add_argument("--platform", required=True, choices=("windows", "linux", "macos"))
    parser.add_argument("--architecture", default=platform.machine())
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    architecture = args.architecture.lower().replace("amd64", "x64").replace("x86_64", "x64")
    archive_path = args.output / f"PDFManager-{args.platform}-{architecture}.zip"

    if args.platform == "macos":
        app_bundle = args.dist / "PDFManager.app"
        if not app_bundle.is_dir():
            parser.error(f"macOS application bundle not found: {app_bundle}")
        subprocess.run(
            [
                "ditto",
                "-c",
                "-k",
                "--sequesterRsrc",
                "--keepParent",
                str(app_bundle),
                str(archive_path),
            ],
            check=True,
        )
    else:
        executable_name = "PDFManager.exe" if args.platform == "windows" else "PDFManager"
        executable = args.dist / executable_name
        if not executable.is_file():
            parser.error(f"application executable not found: {executable}")
        archive_executable(executable, archive_path, executable_name)

    print(f"Created {archive_path}")


if __name__ == "__main__":
    main()
