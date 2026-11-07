"""Export the interface translations as Android string resources.

Exporte les traductions de l'interface en ressources de chaînes Android.

Usage:
    python scripts/export_android_strings.py [output_dir]

Writes res/values/strings.xml (English, default) and res/values-<lang>/strings.xml.
Named placeholders such as {path} become positional ones (%1$s) following their
order of first appearance in the English string.
"""

import argparse
import os
import re
import sys
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from pdf_manager_translations import LANG_ORDER, TRANSLATIONS  # noqa: E402

DEFAULT_LANG = "en"
DEFAULT_OUTPUT = os.path.join(ROOT, "docs", "android-handoff", "res")
RENAMED_KEYS = {"label": "language_name"}
PLACEHOLDER = re.compile(r"\{(\w+)\}")


def android_key(key):
    return RENAMED_KEYS.get(key, key)


def android_directory(lang):
    return "values" if lang == DEFAULT_LANG else f"values-{lang}"


def placeholder_order(key):
    """Return {name: index} using the English string as the reference."""
    names = []
    for name in PLACEHOLDER.findall(TRANSLATIONS[DEFAULT_LANG][key]):
        if name not in names:
            names.append(name)
    return {name: index for index, name in enumerate(names, start=1)}


def android_value(key, text):
    order = placeholder_order(key)
    if order:
        text = text.replace("%", "%%")
    text = PLACEHOLDER.sub(lambda m: f"%{order[m.group(1)]}$s", text)
    text = escape(text)
    text = text.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')
    text = text.replace("\n", "\\n")
    if text.startswith(("@", "?")):
        text = "\\" + text
    return text


def render(lang):
    lines = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>"]
    for key, text in TRANSLATIONS[lang].items():
        lines.append(f'    <string name="{android_key(key)}">{android_value(key, text)}</string>')
    lines.append("</resources>")
    return "\n".join(lines) + "\n"


def export(output_dir):
    written = []
    for lang in LANG_ORDER:
        directory = os.path.join(output_dir, android_directory(lang))
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, "strings.xml")
        with open(path, "w", encoding="utf-8", newline="\n") as output_file:
            output_file.write(render(lang))
        written.append(path)
    return written


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("output_dir", nargs="?", default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    for path in export(args.output_dir):
        print(path)


if __name__ == "__main__":
    main()
