import os

import pytest

import pdf_manager_ui.compress as compress_module
from pdf_manager_translations import TRANSLATIONS
from pdf_manager_ui.compress import CompressionTabMixin


class FakeVariable:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class FakeApp(CompressionTabMixin):
    def __init__(self, source="", output="", mode="lossless"):
        self.compress_source_var = FakeVariable(source)
        self.compress_output_var = FakeVariable(output)
        self.compress_mode_var = FakeVariable(mode)
        self.loading_calls = []

    def t(self, key, **kwargs):
        return TRANSLATIONS["en"][key].format(**kwargs)

    def read_pdf_page_count(self, path):
        return 1

    def run_with_loading(self, action, task, on_success, on_error):
        self.loading_calls.append(action)
        try:
            result = task()
        except Exception as error:
            on_error(error)
        else:
            on_success(result)


@pytest.fixture
def messages(monkeypatch):
    recorded = []
    for name in ("showinfo", "showwarning", "showerror"):
        monkeypatch.setattr(
            compress_module.messagebox,
            name,
            lambda title, message, name=name: recorded.append((name, title, message)),
        )
    return recorded


def test_compress_without_source_warns(messages):
    app = FakeApp()

    app.compress_selected_pdf()

    assert [kind for kind, *_ in messages] == ["showwarning"]
    assert app.loading_calls == []


def test_compress_rejects_non_pdf_source(tmp_path, messages):
    source = tmp_path / "notes.txt"
    source.write_text("text")
    app = FakeApp(source=str(source))

    app.compress_selected_pdf()

    assert [kind for kind, *_ in messages] == ["showerror"]
    assert app.loading_calls == []


def test_compress_suggests_output_and_reports_sizes(tmp_path, messages, monkeypatch):
    source = tmp_path / "report.pdf"
    source.write_bytes(b"source")

    def fake_compress(source_path, output_path, mode):
        assert mode == "balanced"
        with open(output_path, "wb") as output:
            output.write(b"out")

    monkeypatch.setattr(compress_module, "compress_pdf", fake_compress)
    app = FakeApp(source=str(source), mode="balanced")

    app.compress_selected_pdf()

    expected_output = str(tmp_path / "report_compressed.pdf")
    assert app.compress_output_var.get() == expected_output
    assert os.path.exists(expected_output)
    kind, _title, message = messages[0]
    assert kind == "showinfo"
    assert expected_output in message
    assert source.read_bytes() == b"source"


def test_compress_failure_is_reported(tmp_path, messages, monkeypatch):
    source = tmp_path / "report.pdf"
    source.write_bytes(b"source")

    def failing_compress(source_path, output_path, mode):
        raise ValueError("boom")

    monkeypatch.setattr(compress_module, "compress_pdf", failing_compress)
    app = FakeApp(source=str(source))

    app.compress_selected_pdf()

    kind, _title, message = messages[0]
    assert kind == "showerror"
    assert "boom" in message
