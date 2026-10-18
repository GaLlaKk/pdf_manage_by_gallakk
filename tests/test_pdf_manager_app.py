import os

from pdf_manager import PdfManagerApp, resource_path
from pdf_manager_translations import TRANSLATIONS
from pdf_manager_version import __version__


def test_window_title_displays_application_version():
    app = object.__new__(PdfManagerApp)
    app.current_lang = "en"
    app.translations = TRANSLATIONS

    assert app.window_title() == f"{TRANSLATIONS['en']['app_title']} v{__version__}"


def test_source_icon_is_found_in_dedicated_asset_directory():
    assert os.path.isfile(
        resource_path(os.path.join("assets", "icons", "pdf_manager_logo_256x256.ico"))
    )
