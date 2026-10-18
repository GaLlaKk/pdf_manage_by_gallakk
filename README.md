# PDF Manager by GaLlaKk

A lightweight, efficient Python utility designed to simplify PDF file operations, including merging, splitting, compressing, and extracting pages.

---

## 🛠️ Features

- **Merge PDFs**: Combine multiple PDF files into a single document seamlessly.
- **Split & Extract**: Extract specific pages or split large PDFs into individual files.
- **PDF Compression**: Reduce PDF file sizes while maintaining reasonable document quality.
- **Loading feedback**: See an animated progress window while PDFs are loaded, merged, split, or compressed.
- **Page Operations**: Rotate or reorder pages inside your PDF files.

---

## 🚀 Getting Started

### Downloads

For each version released with a `v*` tag, GitHub Actions builds standalone packages for Windows, Linux, and macOS. Download the package for your system from the **Assets** section of that version's [GitHub Releases](https://github.com/GaLlaKk/pdf_manage_by_gallakk/releases) page; Python does not need to be installed.

On macOS, the first launch may require approval in **System Settings → Privacy & Security**, because the application is not signed or notarized. Linux packages target the architecture shown in the package name and require a graphical desktop with Tk support.

To publish a release, push a version tag, for example:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The same workflow can also be started manually from the repository's **Actions** tab; manual builds are available as workflow artifacts.

### Running from source

The standalone downloads above do not require Python. To run the source code directly, install Python 3.10 or higher and the dependencies:

```bash
python --version
