import re
import xml.etree.ElementTree as ET

from pdf_manager_translations import LANG_ORDER, TRANSLATIONS
from scripts import export_android_strings as exporter


def test_every_language_is_exported_with_all_keys(tmp_path):
    exporter.export(str(tmp_path))

    for lang in LANG_ORDER:
        path = tmp_path / exporter.android_directory(lang) / "strings.xml"
        names = {node.get("name") for node in ET.parse(path).getroot()}
        assert names == {exporter.android_key(key) for key in TRANSLATIONS[lang]}


def test_placeholders_become_positional_and_consistent():
    for lang in LANG_ORDER:
        for key, text in TRANSLATIONS[lang].items():
            value = exporter.android_value(key, text)
            assert "{" not in value
            expected = len(exporter.placeholder_order(key))
            used = {int(n) for n in re.findall(r"%(\d)\$s", value)}
            assert used == set(range(1, expected + 1))


def test_special_characters_are_escaped():
    assert exporter.android_value("page_label", "l'a & b\n") == "l\\'a &amp; b\\n"
