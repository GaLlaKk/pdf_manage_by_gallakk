# PDF Manager by GaLlaKk

A Python desktop application for merging, splitting, compressing, rotating, and reordering PDF pages.

PDF Manager runs locally: you can manage your PDFs without uploading or sharing private documents with an online service.

## Read this in another language

[English](README.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Português](README.pt.md) · [中文](README.zh.md) · [日本語](README.ja.md) · [Русский](README.ru.md) · [العربية](README.ar.md) · [한국어](README.ko.md) · [हिन्दी](README.hi.md)

## Features

- Merge multiple PDFs into one document.
- Split a PDF into individual pages.
- Compress PDFs in lossless or balanced mode.
- Rotate and reorder pages before saving.
- Display progress while long-running operations are in progress.

## Downloads

For each version released with a `v*` tag, GitHub Actions builds standalone packages for Windows, Linux, and macOS. Download the package for your system from the **Assets** section of that version's [GitHub Releases](https://github.com/GaLlaKk/pdf_manage_by_gallakk/releases) page; Python does not need to be installed.

The application version is displayed in the window title. The application icon is included in the Windows executable and macOS app bundle, and is also used in the application window, loading dialog, and taskbar.

On macOS, the first launch may require approval in **System Settings → Privacy & Security**, because the application is not signed or notarized. Linux packages target the architecture shown in the package name and require a graphical desktop with Tk support.

## Versioning and releases

`pdf_manager_version.py` is the single source of the application's displayed version. Update `__version__` there for a release, then create and push a matching `v`-prefixed Git tag. For example, for version `1.0.0`:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The same workflow can be started manually from the repository's **Actions** tab; those builds are available as workflow artifacts.

## Running from source

Install Python 3.10 or higher and the application dependencies, then launch the app:

```bash
python -m pip install -r requirements.txt
python pdf_manager.py
```

To run the tests:

```bash
python -m pip install -r requirements-build.txt
python -m pytest -q
```

## Project layout

- `pdf_manager.py`: application entry point and main-window orchestration.
- `pdf_manager_ui/`: UI behavior grouped by merge, split, compression, and preview.
- `assets/icons/`: application icon source files.
- `scripts/`: standalone build and release packaging scripts.
- `tests/`: application and PDF-service tests.
- `pdf_manager_version.py`: displayed application version.
