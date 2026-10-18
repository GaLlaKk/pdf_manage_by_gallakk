# ============================================================
# PDF processing service - GaLlaKk
# Service métier PDF - GaLlaKk
# PDF merging, splitting, and validation logic
# Logique de fusion, découpe et validation des fichiers PDF
# ============================================================

import os
import tempfile

import pymupdf
from pypdf import PdfReader, PdfWriter


def _format_page_number(page_number, total_pages):
    """Format a page number based on the total number of pages.

    Calcule le format de numérotation selon le nombre total de pages.
    """
    if total_pages <= 0:
        return str(page_number)
    width = len(str(total_pages))
    return str(page_number).zfill(width)


def split_pdf_pages(pdf_file, output_dir=None):
    """Split a PDF into one file per page, named {filename}_{number}.pdf.

    Découpe un PDF en un fichier par page avec un nom de type {nomfichier}_{numero}.pdf.
    """
    if not is_pdf_file(pdf_file):
        raise ValueError(f"Le fichier PDF est introuvable ou invalide : {pdf_file}")

    input_path = os.path.abspath(pdf_file)
    destination_dir = os.path.abspath(output_dir) if output_dir else os.path.dirname(input_path)
    os.makedirs(destination_dir, exist_ok=True)

    try:
        with open(input_path, "rb") as source_file:
            reader = PdfReader(source_file)
            if len(reader.pages) == 0:
                raise ValueError(f"Le PDF est vide : {input_path}")

            base_name = os.path.splitext(os.path.basename(input_path))[0]
            created_files = []

            for page_number, page in enumerate(reader.pages, start=1):
                writer = PdfWriter()
                writer.add_page(page)
                output_path = os.path.join(destination_dir, f"{base_name}_{_format_page_number(page_number, len(reader.pages))}.pdf")
                with open(output_path, "wb") as output_file:
                    writer.write(output_file)
                writer.close()
                created_files.append(output_path)

            return created_files
    except Exception:
        raise


def merge_pdfs(pdf_files, output_path):
    """Merge PDF files in the order they were selected.

    Fusionne plusieurs fichiers PDF dans l'ordre de sélection.
    """
    if not pdf_files:
        raise ValueError("Aucun fichier PDF sélectionné.")

    output_path = os.path.abspath(output_path)
    output_dir = os.path.dirname(output_path) or os.getcwd()
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    writer = PdfWriter()
    try:
        for pdf_file in pdf_files:
            if not os.path.isfile(pdf_file):
                raise FileNotFoundError(f"Fichier introuvable : {pdf_file}")
            writer.append(pdf_file)

        writer.write(output_path)
    finally:
        writer.close()


def compress_pdf(pdf_file, output_path, mode="lossless"):
    """Compress a PDF without changing its source file.

    Compresse un PDF sans modifier le fichier source.
    """
    if mode not in {"lossless", "balanced"}:
        raise ValueError(f"Unsupported compression mode: {mode}")
    if not is_pdf_file(pdf_file):
        raise ValueError(f"The PDF file is missing or invalid: {pdf_file}")
    if not isinstance(output_path, str) or not output_path.lower().endswith(".pdf"):
        raise ValueError("The output path must have a .pdf extension.")

    input_path = os.path.abspath(pdf_file)
    destination_path = os.path.abspath(output_path)
    if os.path.normcase(input_path) == os.path.normcase(destination_path):
        raise ValueError("The output file must be different from the source file.")

    output_dir = os.path.dirname(destination_path)
    os.makedirs(output_dir, exist_ok=True)
    temporary_fd, temporary_path = tempfile.mkstemp(
        prefix=".pdf-compress-",
        suffix=".pdf",
        dir=output_dir,
    )
    os.close(temporary_fd)

    try:
        with pymupdf.open(input_path) as document:
            if mode == "balanced":
                document.rewrite_images(
                    dpi_threshold=200,
                    dpi_target=150,
                    quality=65,
                    lossy=True,
                    lossless=True,
                    bitonal=False,
                )
            document.save(
                temporary_path,
                garbage=4,
                clean=True,
                deflate=True,
                deflate_images=True,
                deflate_fonts=True,
            )
        os.replace(temporary_path, destination_path)
    finally:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)

    return destination_path


def is_pdf_file(path):
    """Return whether the path points to an existing PDF file.

    Retourne True si le chemin correspond à un fichier PDF.
    """
    return isinstance(path, str) and path.lower().endswith(".pdf") and os.path.isfile(path)
