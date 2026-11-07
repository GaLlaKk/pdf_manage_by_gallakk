import ast
import socket
from pathlib import Path

import pytest
from pypdf import PdfWriter

from pdf_manager_service import compress_pdf, merge_pdfs, rotate_pdf_pages, split_pdf_pages

ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN_MODULES = {
    "socket", "ssl", "http", "urllib", "urllib3", "requests", "httpx", "aiohttp",
    "ftplib", "smtplib", "telnetlib", "xmlrpc", "webbrowser",
}


def _application_sources():
    sources = [ROOT / "pdf_manager.py", *ROOT.glob("pdf_manager_*.py")]
    sources += (ROOT / "pdf_manager_ui").glob("*.py")
    return sorted(set(sources))


def test_application_modules_do_not_import_network_libraries():
    offenders = []
    for path in _application_sources():
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            offenders += [
                f"{path.name}: {name}"
                for name in names
                if name.split(".")[0] in FORBIDDEN_MODULES
            ]
    assert offenders == []


def test_pdf_operations_open_no_network_connection(tmp_path, monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("Network access attempted during a PDF operation")

    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(socket, "getaddrinfo", blocked)

    source = tmp_path / "source.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.add_blank_page(width=200, height=200)
    with open(source, "wb") as handle:
        writer.write(handle)

    merge_pdfs([str(source), str(source)], str(tmp_path / "merged.pdf"))
    assert len(split_pdf_pages(str(source), str(tmp_path / "split"))) == 2
    rotate_pdf_pages(str(source), str(tmp_path / "rotated.pdf"), {0: 90})
    compress_pdf(str(source), str(tmp_path / "compressed.pdf"))
    compress_pdf(str(source), str(tmp_path / "balanced.pdf"), mode="balanced")
