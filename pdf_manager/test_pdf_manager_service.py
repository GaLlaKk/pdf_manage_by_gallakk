import os

from pypdf import PdfWriter

from pdf_manager.pdf_manager_service import split_pdf_pages


def _create_pdf(path, page_count):
    writer = PdfWriter()
    for _ in range(page_count):
        writer.add_blank_page(width=100, height=200)
    with open(path, "wb") as fh:
        writer.write(fh)
    writer.close()


def test_split_pdf_pages_names_for_single_digit_count(tmp_path):
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


def test_split_pdf_pages_names_for_double_digit_count(tmp_path):
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
