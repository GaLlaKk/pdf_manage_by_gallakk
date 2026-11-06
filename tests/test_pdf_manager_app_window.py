import tkinter as tk

import pymupdf
import pytest
from tkinterdnd2 import TkinterDnD

import pdf_manager
from pdf_manager import PdfManagerApp, detect_system_language
from pdf_manager_translations import LANG_ORDER, TRANSLATIONS


@pytest.fixture(scope="module")
def app():
    # A single interpreter is shared: worker threads are unreliable across several Tk roots.
    try:
        root = TkinterDnD.Tk()
    except tk.TclError:
        pytest.skip("No display available")
    root.withdraw()
    application = PdfManagerApp(root)
    yield application
    root.destroy()


def run_until(app, condition, timeout_ms=5000):
    """Run the Tk main loop, which worker threads need to schedule callbacks."""
    waited = 0

    def check():
        nonlocal waited
        if condition() or waited >= timeout_ms:
            app.root.quit()
        else:
            waited += 20
            app.root.after(20, check)

    app.root.after(20, check)
    app.root.mainloop()
    assert condition()


def test_every_language_can_be_applied(app):
    for code in LANG_ORDER:
        app.current_lang = code
        app.apply_language()
        assert app.root.title() == app.window_title()
    app.current_lang = "en"
    app.apply_language()


def test_translation_falls_back_to_key_and_ignores_bad_format(app):
    app.current_lang = "en"
    assert app.t("missing_key") == "missing_key"
    assert app.t("app_title", unused="x") == TRANSLATIONS["en"]["app_title"]


def test_run_with_loading_calls_success_with_result(app):
    results = []

    app.run_with_loading("test", lambda: 42, results.append, results.append)
    run_until(app, lambda: results)

    assert results == [42]
    assert app.loading_window is None
    assert app._busy is False


def test_run_with_loading_reports_errors(app):
    errors = []

    def fail():
        raise ValueError("boom")

    app.run_with_loading("test", fail, lambda _: errors.append("ok"), errors.append)
    run_until(app, lambda: errors)

    assert isinstance(errors[0], ValueError)
    assert app._busy is False


def test_run_with_loading_ignores_reentrant_calls(app):
    app._busy = True
    calls = []

    app.run_with_loading("test", lambda: calls.append("task"), calls.append, calls.append)

    app._busy = False
    assert calls == []


def test_read_pdf_page_count(app, tmp_path):
    source = tmp_path / "three.pdf"
    document = pymupdf.open()
    for _ in range(3):
        document.new_page()
    document.save(source)
    document.close()

    assert app.read_pdf_page_count(str(source)) == 3


@pytest.mark.parametrize(
    ("locale_value", "expected"),
    [
        (("en_US", "UTF-8"), "en"),
        (("fr-FR", "UTF-8"), "fr"),
        ((None, None), "fr"),
        (("xx_XX", "UTF-8"), "fr"),
    ],
)
def test_detect_system_language(monkeypatch, locale_value, expected):
    monkeypatch.setattr(pdf_manager.locale, "getlocale", lambda: locale_value)

    assert detect_system_language() == expected
