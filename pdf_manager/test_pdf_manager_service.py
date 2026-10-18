# ============================================================
# Tests for PDF splitting and generated file naming - GaLlaKk
# Tests de découpage des PDF et de nommage des fichiers générés - GaLlaKk
# ============================================================
import os
import string

import pymupdf
import pytest
from pypdf import PdfWriter

from pdf_manager.pdf_manager_service import compress_pdf, split_pdf_pages
from pdf_manager.pdf_manager_translations import LANG_ORDER, TRANSLATIONS


def _create_pdf(path, page_count):
    """Create a test PDF with the requested number of pages.

    Crée un PDF de test contenant le nombre de pages demandé.
    """
    writer = PdfWriter()
    for _ in range(page_count):
        writer.add_blank_page(width=100, height=200)
    with open(path, "wb") as fh:
        writer.write(fh)
    writer.close()


def _create_image_pdf(path):
    """Create a test PDF containing a high-resolution image.

    Crée un PDF de test contenant une image haute résolution.
    """
    document = pymupdf.open()
    page = document.new_page(width=200, height=200)
    pixmap = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 600, 600), 0)
    pixmap.samples_mv[:] = bytes((index * 73 + 19) % 256 for index in range(len(pixmap.samples_mv)))
    page.insert_image(page.rect, pixmap=pixmap)
    page.insert_text((20, 30), "Compression test")
    document.save(path)
    document.close()


def test_split_pdf_pages_names_for_single_digit_count(tmp_path):
    """Check that page numbers are not zero-padded for PDFs with fewer than ten pages.

    Vérifie que les pages d'un PDF de moins de dix pages ne sont pas complétées par zéro.
    """
    source = tmp_path / "rapport.pdf"
    _create_pdf(source, 9)

    output_dir = tmp_path / "sortie"
    created = split_pdf_pages(str(source), output_dir=str(output_dir))

    assert created == [
        str(output_dir / "rapport_1.pdf"),
        str(output_dir / "rapport_2.pdf"),
        str(output_dir / "rapport_3.pdf"),
        str(output_dir / "rapport_4.pdf"),
        str(output_dir / "rapport_5.pdf"),
        str(output_dir / "rapport_6.pdf"),
        str(output_dir / "rapport_7.pdf"),
        str(output_dir / "rapport_8.pdf"),
        str(output_dir / "rapport_9.pdf"),
    ]
    assert all(os.path.isfile(path) for path in created)


def test_compress_pdf_lossless_preserves_source_and_pages(tmp_path):
    """Check lossless compression creates a separate, readable PDF.

    Vérifie que la compression sans perte crée un PDF distinct et lisible.
    """
    source = tmp_path / "source.pdf"
    _create_pdf(source, 2)
    original_bytes = source.read_bytes()
    output = tmp_path / "compressed.pdf"

    assert compress_pdf(str(source), str(output), mode="lossless") == str(output)
    assert source.read_bytes() == original_bytes
    with pymupdf.open(output) as document:
        assert document.page_count == 2


def test_compress_pdf_balanced_reduces_high_resolution_image(tmp_path):
    """Check balanced compression reduces a high-resolution image PDF.

    Vérifie que la compression équilibrée réduit un PDF avec une image haute résolution.
    """
    source = tmp_path / "image.pdf"
    _create_image_pdf(source)
    output = tmp_path / "image_compressed.pdf"

    compress_pdf(str(source), str(output), mode="balanced")

    assert output.stat().st_size < source.stat().st_size
    with pymupdf.open(output) as document:
        assert document.page_count == 1


def test_compress_pdf_rejects_overwriting_source(tmp_path):
    """Check compression refuses to overwrite the source PDF.

    Vérifie que la compression refuse d'écraser le PDF source.
    """
    source = tmp_path / "source.pdf"
    _create_pdf(source, 1)
    original_bytes = source.read_bytes()

    with pytest.raises(ValueError, match="different from the source"):
        compress_pdf(str(source), str(source))

    assert source.read_bytes() == original_bytes


def test_compress_pdf_rejects_unknown_mode(tmp_path):
    """Check compression rejects unknown modes.

    Vérifie que la compression refuse les modes inconnus.
    """
    source = tmp_path / "source.pdf"
    _create_pdf(source, 1)

    with pytest.raises(ValueError, match="Unsupported compression mode"):
        compress_pdf(str(source), str(tmp_path / "output.pdf"), mode="unknown")


def test_all_languages_have_matching_translation_keys_and_placeholders():
    """Check every language has complete strings with matching format placeholders.

    Vérifie que chaque langue contient toutes les chaînes et les mêmes paramètres.
    """
    expected_keys = set(TRANSLATIONS["fr"])
    formatter = string.Formatter()

    assert set(TRANSLATIONS) == set(LANG_ORDER)
    for language in LANG_ORDER:
        assert set(TRANSLATIONS[language]) == expected_keys
        for key in expected_keys:
            expected_fields = {
                field_name
                for _, field_name, _, _ in formatter.parse(TRANSLATIONS["fr"][key])
                if field_name
            }
            actual_fields = {
                field_name
                for _, field_name, _, _ in formatter.parse(TRANSLATIONS[language][key])
                if field_name
            }
            assert actual_fields == expected_fields, f"{language}.{key}"


def test_split_pdf_pages_names_for_double_digit_count(tmp_path):
    """Check that page numbers are zero-padded for PDFs with ten or more pages.

    Vérifie que les numéros sont complétés par zéro lorsque le PDF a dix pages ou plus.
    """
    source = tmp_path / "rapport.pdf"
    _create_pdf(source, 10)

    output_dir = tmp_path / "sortie"
    created = split_pdf_pages(str(source), output_dir=str(output_dir))

    assert created == [
        str(output_dir / "rapport_01.pdf"),
        str(output_dir / "rapport_02.pdf"),
        str(output_dir / "rapport_03.pdf"),
        str(output_dir / "rapport_04.pdf"),
        str(output_dir / "rapport_05.pdf"),
        str(output_dir / "rapport_06.pdf"),
        str(output_dir / "rapport_07.pdf"),
        str(output_dir / "rapport_08.pdf"),
        str(output_dir / "rapport_09.pdf"),
        str(output_dir / "rapport_10.pdf"),
    ]
    assert all(os.path.isfile(path) for path in created)
