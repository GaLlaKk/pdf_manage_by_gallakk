# ============================================================
# Service métier PDF - GaLlaKk
# Logique de fusion, découpe et validation des fichiers PDF
# ============================================================

import os

from pypdf import PdfReader, PdfWriter


def _format_page_number(page_number, total_pages):
    """Calcule le format de numérotation selon le nombre total de pages."""
    if total_pages <= 0:
        return str(page_number)
    width = len(str(total_pages))
    return str(page_number).zfill(width)


def split_pdf_pages(pdf_file, output_dir=None):
    """Découpe un PDF en un fichier par page avec un nom de type {nomfichier}_{numero}.pdf."""
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
    """Fusionne plusieurs fichiers PDF dans l'ordre de sélection."""
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


def is_pdf_file(path):
    """Retourne True si le chemin correspond à un fichier PDF."""
    return isinstance(path, str) and path.lower().endswith(".pdf") and os.path.isfile(path)
