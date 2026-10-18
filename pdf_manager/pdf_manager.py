# ============================================================
# Fusion et division de PDF - GaLlaKk
# Application de gestion de fichiers PDF via interface Tkinter
# ============================================================

import locale
import os
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import fitz
from tkinterdnd2 import DND_FILES, TkinterDnD

try:
    from .pdf_manager_service import merge_pdfs, split_pdf_pages
except ImportError:
    from pdf_manager_service import merge_pdfs, split_pdf_pages


LANG_ORDER = ["fr", "en", "de", "es", "pt"]
TRANSLATIONS = {
    "fr": {
        "label": "Français",
        "app_title": "PDF Manager by GaLlaKk",
        "language": "Langue",
        "merge_tab": "Fusionner",
        "split_tab": "Diviser",
        "merge_title": "Sélectionnez les fichiers PDF à fusionner :",
        "signature": "GaLlaKk",
        "open_pdf": "Ouvrir PDF",
        "add_folder": "Ajouter un dossier",
        "remove_selection": "Retirer la sélection",
        "move_up": "Monter",
        "move_down": "Descendre",
        "merge": "Fusionner",
        "drop_files_hint": "Glissez ici vos fichiers PDF",
        "preview_title": "Aperçu du PDF",
        "output_file_label": "Fichier de sortie :",
        "choose": "Choisir",
        "split_title": "Sélectionnez un PDF à découper :",
        "pdf_file_label": "Fichier PDF :",
        "browse": "Parcourir",
        "output_dir_label": "Dossier de sortie :",
        "split_help": "Le nom des fichiers générés sera de la forme : nomfichier_1.pdf, nomfichier_02.pdf, nomfichier_123.pdf selon le nombre total de pages.",
        "split_button": "Diviser",
        "status_no_pdf": "Aucun PDF sélectionné.",
        "status_selected_pdf": "PDF sélectionné : {name}",
        "status_generated": "{count} fichiers générés dans : {path}",
        "page_label": "Page {current} / {total}",
        "no_pdf_selected_preview": "Aucun PDF sélectionné\nAjoutez un fichier pour voir l'aperçu",
        "preview_unavailable": "Prévisualisation indisponible\n{name}",
        "preview_not_available": "Aperçu non disponible\n{name}",
        "drop_pdf_only": "Glissez uniquement des fichiers PDF.",
        "pdf_required": "PDF requis",
        "pdf_valid_required": "Veuillez déposer un fichier PDF valide.",
        "invalid_pdf": "Fichier invalide",
        "not_a_pdf": "Le fichier sélectionné n'est pas un PDF.",
        "select_pdf": "Sélectionner le PDF à découper",
        "save_merge": "Enregistrer le PDF fusionné",
        "no_selection": "Aucune sélection",
        "select_a_pdf": "Veuillez sélectionner au moins un fichier PDF.",
        "select_folder_title": "Sélectionner un dossier contenant des PDF",
        "choose_output_dir": "Choisir le dossier de destination",
        "split_success": "Découpage réussi",
        "split_success_details": "{count} fichiers PDF individuels ont été créés dans :\n{path}",
        "success_merge": "Fusion réussie",
        "merge_success_details": "Le fichier PDF a bien été créé :\n{path}",
        "merge_fail": "La fusion a échoué :\n{error}",
        "split_fail": "Le découpage a échoué :\n{error}",
        "app_error": "Erreur",
        "select_pdf_to_split": "Veuillez sélectionner un fichier PDF à diviser.",
        "files_filter": "Fichiers PDF",
        "all_files": "Tous les fichiers",
        "select_pdf_files": "Sélectionner les fichiers PDF",
        "select_pdf_to_merge": "Veuillez sélectionner au moins un fichier PDF.",
        "select_split_pdf": "Veuillez sélectionner un fichier PDF à diviser.",
    },
    "en": {
        "label": "English",
        "app_title": "PDF Manager by GaLlaKk",
        "language": "Language",
        "merge_tab": "Merge",
        "split_tab": "Split",
        "merge_title": "Select the PDF files to merge:",
        "signature": "GaLlaKk",
        "open_pdf": "Open PDF",
        "add_folder": "Add folder",
        "remove_selection": "Remove selection",
        "move_up": "Move up",
        "move_down": "Move down",
        "merge": "Merge",
        "drop_files_hint": "Drag your PDF files here",
        "preview_title": "PDF preview",
        "output_file_label": "Output file:",
        "choose": "Choose",
        "split_title": "Select a PDF to split:",
        "pdf_file_label": "PDF file:",
        "browse": "Browse",
        "output_dir_label": "Output folder:",
        "split_help": "Generated file names will look like: document_1.pdf, document_02.pdf, document_123.pdf according to the total number of pages.",
        "split_button": "Split",
        "status_no_pdf": "No PDF selected.",
        "status_selected_pdf": "Selected PDF: {name}",
        "status_generated": "{count} files generated in: {path}",
        "page_label": "Page {current} / {total}",
        "no_pdf_selected_preview": "No PDF selected\nAdd a file to preview it",
        "preview_unavailable": "Preview unavailable\n{name}",
        "preview_not_available": "Preview not available\n{name}",
        "drop_pdf_only": "Only PDF files can be dropped here.",
        "pdf_required": "PDF required",
        "pdf_valid_required": "Please drop a valid PDF file.",
        "invalid_pdf": "Invalid file",
        "not_a_pdf": "The selected file is not a PDF.",
        "select_pdf": "Select the PDF to split",
        "save_merge": "Save merged PDF",
        "no_selection": "No selection",
        "select_a_pdf": "Please select at least one PDF file.",
        "select_folder_title": "Select a folder containing PDFs",
        "choose_output_dir": "Choose destination folder",
        "split_success": "Split successful",
        "split_success_details": "{count} individual PDF files were created in:\n{path}",
        "success_merge": "Merge successful",
        "merge_success_details": "The PDF file was created successfully:\n{path}",
        "merge_fail": "Merging failed:\n{error}",
        "split_fail": "Splitting failed:\n{error}",
        "app_error": "Error",
        "select_pdf_to_split": "Please select a PDF file to split.",
        "files_filter": "PDF files",
        "all_files": "All files",
        "select_pdf_files": "Select PDF files",
        "select_pdf_to_merge": "Please select at least one PDF file.",
        "select_split_pdf": "Please select a PDF file to split.",
    },
    "de": {
        "label": "Deutsch",
        "app_title": "PDF Manager by GaLlaKk",
        "language": "Sprache",
        "merge_tab": "Zusammenführen",
        "split_tab": "Teilen",
        "merge_title": "Wählen Sie die zu zusammenführenden PDF-Dateien aus:",
        "signature": "GaLlaKk",
        "open_pdf": "PDF öffnen",
        "add_folder": "Ordner hinzufügen",
        "remove_selection": "Auswahl entfernen",
        "move_up": "Nach oben",
        "move_down": "Nach unten",
        "merge": "Zusammenführen",
        "drop_files_hint": "Ziehen Sie Ihre PDF-Dateien hierher",
        "preview_title": "PDF-Vorschau",
        "output_file_label": "Ausgabedatei:",
        "choose": "Auswählen",
        "split_title": "Wählen Sie eine PDF-Datei zum Teilen aus:",
        "pdf_file_label": "PDF-Datei:",
        "browse": "Durchsuchen",
        "output_dir_label": "Ausgabeordner:",
        "split_help": "Die Dateinamen sehen so aus: dokument_1.pdf, dokument_02.pdf, dokument_123.pdf entsprechend der Gesamtseitenzahl.",
        "split_button": "Teilen",
        "status_no_pdf": "Keine PDF ausgewählt.",
        "status_selected_pdf": "Ausgewählte PDF: {name}",
        "status_generated": "{count} Dateien in {path} erstellt",
        "page_label": "Seite {current} / {total}",
        "no_pdf_selected_preview": "Keine PDF ausgewählt\nDatei hinzufügen, um Vorschau zu sehen",
        "preview_unavailable": "Vorschau nicht verfügbar\n{name}",
        "preview_not_available": "Vorschau nicht verfügbar\n{name}",
        "drop_pdf_only": "Nur PDF-Dateien können hier abgelegt werden.",
        "pdf_required": "PDF erforderlich",
        "pdf_valid_required": "Bitte ziehen Sie eine gültige PDF-Datei herein.",
        "invalid_pdf": "Ungültige Datei",
        "not_a_pdf": "Die ausgewählte Datei ist keine PDF.",
        "select_pdf": "PDF-Datei zum Teilen auswählen",
        "save_merge": "Zusammengeführte PDF speichern",
        "no_selection": "Keine Auswahl",
        "select_a_pdf": "Bitte wählen Sie mindestens eine PDF-Datei aus.",
        "select_folder_title": "Ordner mit PDFs auswählen",
        "choose_output_dir": "Zielordner auswählen",
        "split_success": "Teilen erfolgreich",
        "split_success_details": "{count} einzelne PDF-Dateien wurden erstellt in:\n{path}",
        "success_merge": "Zusammenführen erfolgreich",
        "merge_success_details": "Die PDF-Datei wurde erstellt:\n{path}",
        "merge_fail": "Zusammenführen fehlgeschlagen:\n{error}",
        "split_fail": "Teilen fehlgeschlagen:\n{error}",
        "app_error": "Fehler",
        "select_pdf_to_split": "Bitte wählen Sie eine PDF-Datei zum Teilen aus.",
        "files_filter": "PDF-Dateien",
        "all_files": "Alle Dateien",
        "select_pdf_files": "PDF-Dateien auswählen",
        "select_pdf_to_merge": "Bitte wählen Sie mindestens eine PDF-Datei aus.",
        "select_split_pdf": "Bitte wählen Sie eine PDF-Datei zum Teilen aus.",
    },
    "es": {
        "label": "Español",
        "app_title": "PDF Manager by GaLlaKk",
        "language": "Idioma",
        "merge_tab": "Fusionar",
        "split_tab": "Dividir",
        "merge_title": "Seleccione los archivos PDF para fusionar:",
        "signature": "GaLlaKk",
        "open_pdf": "Abrir PDF",
        "add_folder": "Añadir carpeta",
        "remove_selection": "Quitar selección",
        "move_up": "Subir",
        "move_down": "Bajar",
        "merge": "Fusionar",
        "drop_files_hint": "Arrastre aquí sus archivos PDF",
        "preview_title": "Vista previa del PDF",
        "output_file_label": "Archivo de salida:",
        "choose": "Elegir",
        "split_title": "Seleccione un PDF para dividir:",
        "pdf_file_label": "Archivo PDF:",
        "browse": "Examinar",
        "output_dir_label": "Carpeta de salida:",
        "split_help": "Los nombres generados tendrán este formato: documento_1.pdf, documento_02.pdf, documento_123.pdf según el número total de páginas.",
        "split_button": "Dividir",
        "status_no_pdf": "No hay PDF seleccionado.",
        "status_selected_pdf": "PDF seleccionado: {name}",
        "status_generated": "{count} archivos generados en: {path}",
        "page_label": "Página {current} / {total}",
        "no_pdf_selected_preview": "No hay PDF seleccionado\nAñada un archivo para ver la vista previa",
        "preview_unavailable": "Vista previa no disponible\n{name}",
        "preview_not_available": "Vista previa no disponible\n{name}",
        "drop_pdf_only": "Solo se permiten archivos PDF.",
        "pdf_required": "Se requiere PDF",
        "pdf_valid_required": "Por favor, arrastre un archivo PDF válido.",
        "invalid_pdf": "Archivo no válido",
        "not_a_pdf": "El archivo seleccionado no es un PDF.",
        "select_pdf": "Seleccionar PDF para dividir",
        "save_merge": "Guardar PDF fusionado",
        "no_selection": "Sin selección",
        "select_a_pdf": "Seleccione al menos un archivo PDF.",
        "select_folder_title": "Seleccionar una carpeta que contenga PDFs",
        "choose_output_dir": "Elegir carpeta de destino",
        "split_success": "División correcta",
        "split_success_details": "{count} archivos PDF individuales se crearon en:\n{path}",
        "success_merge": "Fusión correcta",
        "merge_success_details": "El archivo PDF se creó correctamente:\n{path}",
        "merge_fail": "La fusión falló:\n{error}",
        "split_fail": "La división falló:\n{error}",
        "app_error": "Error",
        "select_pdf_to_split": "Seleccione un archivo PDF para dividir.",
        "files_filter": "Archivos PDF",
        "all_files": "Todos los archivos",
        "select_pdf_files": "Seleccionar archivos PDF",
        "select_pdf_to_merge": "Seleccione al menos un archivo PDF.",
        "select_split_pdf": "Seleccione un archivo PDF para dividir.",
    },
    "pt": {
        "label": "Português",
        "app_title": "PDF Manager by GaLlaKk",
        "language": "Idioma",
        "merge_tab": "Mesclar",
        "split_tab": "Dividir",
        "merge_title": "Selecione os arquivos PDF para mesclar:",
        "signature": "GaLlaKk",
        "open_pdf": "Abrir PDF",
        "add_folder": "Adicionar pasta",
        "remove_selection": "Remover seleção",
        "move_up": "Subir",
        "move_down": "Descer",
        "merge": "Mesclar",
        "drop_files_hint": "Arraste seus arquivos PDF aqui",
        "preview_title": "Pré-visualização do PDF",
        "output_file_label": "Arquivo de saída:",
        "choose": "Escolher",
        "split_title": "Selecione um PDF para dividir:",
        "pdf_file_label": "Arquivo PDF:",
        "browse": "Procurar",
        "output_dir_label": "Pasta de saída:",
        "split_help": "Os nomes gerados terão este formato: documento_1.pdf, documento_02.pdf, documento_123.pdf de acordo com o número total de páginas.",
        "split_button": "Dividir",
        "status_no_pdf": "Nenhum PDF selecionado.",
        "status_selected_pdf": "PDF selecionado: {name}",
        "status_generated": "{count} arquivos gerados em: {path}",
        "page_label": "Página {current} / {total}",
        "no_pdf_selected_preview": "Nenhum PDF selecionado\nAdicione um arquivo para ver a pré-visualização",
        "preview_unavailable": "Pré-visualização indisponível\n{name}",
        "preview_not_available": "Pré-visualização indisponível\n{name}",
        "drop_pdf_only": "Apenas arquivos PDF podem ser arrastados aqui.",
        "pdf_required": "PDF necessário",
        "pdf_valid_required": "Por favor, arraste um PDF válido.",
        "invalid_pdf": "Arquivo inválido",
        "not_a_pdf": "O arquivo selecionado não é um PDF.",
        "select_pdf": "Selecionar PDF para dividir",
        "save_merge": "Salvar PDF mesclado",
        "no_selection": "Nenhuma seleção",
        "select_a_pdf": "Selecione pelo menos um arquivo PDF.",
        "select_folder_title": "Selecionar uma pasta com PDFs",
        "choose_output_dir": "Escolher pasta de destino",
        "split_success": "Divisão concluída",
        "split_success_details": "{count} arquivos PDF individuais foram criados em:\n{path}",
        "success_merge": "Mesclagem concluída",
        "merge_success_details": "O arquivo PDF foi criado com sucesso:\n{path}",
        "merge_fail": "A mesclagem falhou:\n{error}",
        "split_fail": "A divisão falhou:\n{error}",
        "app_error": "Erro",
        "select_pdf_to_split": "Selecione um arquivo PDF para dividir.",
        "files_filter": "Arquivos PDF",
        "all_files": "Todos os arquivos",
        "select_pdf_files": "Selecionar arquivos PDF",
        "select_pdf_to_merge": "Selecione pelo menos um arquivo PDF.",
        "select_split_pdf": "Selecione um arquivo PDF para dividir.",
    },
}


def detect_system_language():
    try:
        default_locale = locale.getdefaultlocale()[0] or ""
    except Exception:
        default_locale = ""

    if not default_locale:
        return "fr"

    short_code = default_locale.lower().split("_")[0]
    return short_code if short_code in TRANSLATIONS else "fr"


class PdfManagerApp:
    def __init__(self, root):
        self.root = root
        self.current_lang = detect_system_language()
        self.translations = TRANSLATIONS
        self.root.title(self.t("app_title"))
        self.root.geometry("1030x560")
        self.root.minsize(860, 430)

        self.selected_files = []
        self.current_index = 0
        self.preview_page_index = 0

        self.language_frame = tk.Frame(root, padx=10)
        self.language_frame.pack(fill="x", pady=(8, 0))
        self.language_label = tk.Label(self.language_frame, text=self.t("language"), anchor="e")
        language_values = [self.translations[code]["label"] for code in LANG_ORDER]
        self.language_var = tk.StringVar(value=self.translations[self.current_lang]["label"])
        self.language_combo = ttk.Combobox(
            self.language_frame,
            textvariable=self.language_var,
            values=language_values,
            state="readonly",
            width=14,
        )
        self.language_combo.pack(side="right", padx=(0, 10))
        self.language_label.pack(side="right", padx=(0, 5))
        self.language_combo.bind("<<ComboboxSelected>>", self.on_language_change)

        self.split_source_var = tk.StringVar(value="")
        self.split_output_dir_var = tk.StringVar(value="")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.merge_tab = tk.Frame(self.notebook, padx=10, pady=10)
        self.split_tab = tk.Frame(self.notebook, padx=10, pady=10)

        self.notebook.add(self.merge_tab, text=self.t("merge_tab"))
        self.notebook.add(self.split_tab, text=self.t("split_tab"))

        self.build_merge_tab()
        self.build_split_tab()
        self.apply_language()

    def t(self, key, **kwargs):
        text = self.translations.get(self.current_lang, self.translations["fr"]).get(key, key)
        try:
            return text.format(**kwargs)
        except Exception:
            return text

    def on_language_change(self, event=None):
        selected_label = self.language_combo.get()
        selected_lang = next((code for code in LANG_ORDER if self.translations[code]["label"] == selected_label), self.current_lang)
        if selected_lang != self.current_lang:
            self.current_lang = selected_lang
            self.apply_language()

    def apply_language(self):
        self.root.title(self.t("app_title"))
        self.language_label.config(text=self.t("language"))
        self.notebook.tab(0, text=self.t("merge_tab"))
        self.notebook.tab(1, text=self.t("split_tab"))

        self.merge_title_label.config(text=self.t("merge_title"))
        self.signature_label.config(text=self.t("signature"))
        self.open_button.config(text=self.t("open_pdf"))
        self.folder_button.config(text=self.t("add_folder"))
        self.remove_button.config(text=self.t("remove_selection"))
        self.up_button.config(text=self.t("move_up"))
        self.down_button.config(text=self.t("move_down"))
        self.preview_title_label.config(text=self.t("preview_title"))
        self.output_label.config(text=self.t("output_file_label"))
        self.choose_output_button.config(text=self.t("choose"))
        self.merge_button.config(text=self.t("merge"))

        self.split_title_label.config(text=self.t("split_title"))
        self.pdf_file_label.config(text=self.t("pdf_file_label"))
        self.browse_source_button.config(text=self.t("browse"))
        self.output_dir_label.config(text=self.t("output_dir_label"))
        self.choose_output_dir_button.config(text=self.t("choose"))
        self.split_info_label.config(text=self.t("split_help"))
        self.split_button.config(text=self.t("split_button"))
        self.split_status_var.set(self.t("status_no_pdf"))

        self.update_preview()

    def build_merge_tab(self):
        self.merge_title_label = tk.Label(
            self.merge_tab,
            text=self.t("merge_title"),
            font=("Segoe UI", 11, "bold"),
            anchor="w",
            padx=15,
            pady=10,
        )
        self.merge_title_label.pack(fill="x")

        self.signature_label = tk.Label(
            self.merge_tab,
            text=self.t("signature"),
            font=("Segoe UI", 8),
            fg="#666666",
            anchor="e",
            padx=15,
            pady=5,
        )
        self.signature_label.pack(fill="x")

        frame_actions = tk.Frame(self.merge_tab, padx=15, pady=5)
        frame_actions.pack(fill="x")

        self.open_button = tk.Button(frame_actions, text=self.t("open_pdf"), command=self.select_files, width=18, state=tk.NORMAL)
        self.open_button.pack(side="left")

        self.folder_button = tk.Button(frame_actions, text=self.t("add_folder"), command=self.select_folder, width=18, state=tk.NORMAL)
        self.folder_button.pack(side="left", padx=10)

        self.remove_button = tk.Button(frame_actions, text=self.t("remove_selection"), command=self.remove_selected, width=18, state=tk.NORMAL)
        self.remove_button.pack(side="left")

        self.up_button = tk.Button(frame_actions, text=self.t("move_up"), command=self.move_up, width=10, state=tk.DISABLED)
        self.up_button.pack(side="left", padx=10)

        self.down_button = tk.Button(frame_actions, text=self.t("move_down"), command=self.move_down, width=10, state=tk.DISABLED)
        self.down_button.pack(side="left")

        content_frame = tk.Frame(self.merge_tab, padx=15, pady=8)
        content_frame.pack(fill="both", expand=True)

        left_frame = tk.Frame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True)

        self.file_listbox = tk.Listbox(left_frame, selectmode=tk.SINGLE, height=14, font=("Segoe UI", 10))
        self.file_listbox.pack(fill="both", expand=True)
        self.file_listbox.config(bg="#f7f7f7")
        self.file_listbox.drop_target_register(DND_FILES)
        self.file_listbox.dnd_bind('<<Drop>>', self.on_drop)
        self.file_listbox.bind("<Button-1>", self.clear_placeholder)
        self.file_listbox.bind("<ButtonRelease-1>", self.on_listbox_select)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

        right_frame = tk.Frame(content_frame, width=300, padx=10)
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)

        self.preview_title_label = tk.Label(right_frame, text=self.t("preview_title"), font=("Segoe UI", 10, "bold"), anchor="w")
        self.preview_title_label.pack(fill="x", pady=6)

        self.preview_nav = tk.Frame(right_frame)
        self.preview_nav.pack(fill="x", pady=6)

        self.prev_page_button = tk.Button(self.preview_nav, text="←", width=5, command=self.previous_preview_page, state=tk.DISABLED)
        self.prev_page_button.pack(side="left")

        self.preview_page_var = tk.StringVar(value=self.t("page_label", current=1, total=1))
        self.preview_page_label = tk.Label(self.preview_nav, textvariable=self.preview_page_var, font=("Segoe UI", 9), anchor="center")
        self.preview_page_label.pack(side="left", expand=True, fill="x")

        self.next_page_button = tk.Button(self.preview_nav, text="→", width=5, command=self.next_preview_page, state=tk.DISABLED)
        self.next_page_button.pack(side="right")

        self.preview_label = tk.Label(
            right_frame,
            text=self.t("no_pdf_selected_preview"),
            bg="#f5f5f5",
            relief="solid",
            bd=1,
            anchor="center",
            justify="center",
            compound="center",
            font=("Segoe UI", 9),
        )
        self.preview_label.pack(fill="both", expand=True)
        self.preview_label.image = None
        self.preview_temp_path = None

        output_frame = tk.Frame(self.merge_tab, padx=15, pady=5)
        output_frame.pack(fill="x")

        self.output_label = tk.Label(output_frame, text=self.t("output_file_label"), anchor="w", width=16)
        self.output_label.pack(side="left")
        self.output_var = tk.StringVar(value="")
        self.output_entry = tk.Entry(output_frame, textvariable=self.output_var, width=60)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.choose_output_button = ttk.Button(output_frame, text=self.t("choose"), command=self.choose_output_file)
        self.choose_output_button.pack(side="left")

        buttons_frame = tk.Frame(self.merge_tab, padx=15, pady=10)
        buttons_frame.pack(fill="x")

        self.merge_button = tk.Button(buttons_frame, text=self.t("merge"), command=self.merge_selected_files, width=18, state=tk.DISABLED)
        self.merge_button.pack(side="right")

        self.refresh_list()

    def build_split_tab(self):
        self.split_title_label = tk.Label(
            self.split_tab,
            text=self.t("split_title"),
            font=("Segoe UI", 11, "bold"),
            anchor="w",
            padx=15,
            pady=12,
        )
        self.split_title_label.pack(fill="x")

        file_frame = tk.Frame(self.split_tab, padx=15, pady=5)
        file_frame.pack(fill="x")
        self.pdf_file_label = tk.Label(file_frame, text=self.t("pdf_file_label"), width=16, anchor="w")
        self.pdf_file_label.pack(side="left")
        self.split_source_entry = tk.Entry(file_frame, textvariable=self.split_source_var, width=60)
        self.split_source_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.split_source_entry.drop_target_register(DND_FILES)
        self.split_source_entry.dnd_bind('<<Drop>>', self.on_split_drop)
        self.browse_source_button = ttk.Button(file_frame, text=self.t("browse"), command=self.choose_split_source)
        self.browse_source_button.pack(side="left")

        output_dir_frame = tk.Frame(self.split_tab, padx=15, pady=5)
        output_dir_frame.pack(fill="x")
        self.output_dir_label = tk.Label(output_dir_frame, text=self.t("output_dir_label"), width=16, anchor="w")
        self.output_dir_label.pack(side="left")
        self.split_output_entry = tk.Entry(output_dir_frame, textvariable=self.split_output_dir_var, width=60)
        self.split_output_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.split_output_entry.drop_target_register(DND_FILES)
        self.split_output_entry.dnd_bind('<<Drop>>', self.on_split_output_drop)
        self.choose_output_dir_button = ttk.Button(output_dir_frame, text=self.t("choose"), command=self.choose_split_output_dir)
        self.choose_output_dir_button.pack(side="left")

        info_frame = tk.Frame(self.split_tab, padx=15, pady=5)
        info_frame.pack(fill="x")
        self.split_info_label = tk.Label(
            info_frame,
            text=self.t("split_help"),
            justify="left",
            wraplength=700,
            fg="#444444",
        )
        self.split_info_label.pack(anchor="w")

        buttons_frame = tk.Frame(self.split_tab, padx=15, pady=10)
        buttons_frame.pack(fill="x")
        self.split_button = tk.Button(buttons_frame, text=self.t("split_button"), command=self.split_selected_pdf, width=18)
        self.split_button.pack(side="right")

        self.split_status_var = tk.StringVar(value=self.t("status_no_pdf"))
        tk.Label(self.split_tab, textvariable=self.split_status_var, fg="#333333", padx=15, pady=5, anchor="w").pack(fill="x")

    def choose_split_source(self):
        file_path = filedialog.askopenfilename(
            title=self.t("select_pdf"),
            filetypes=[(self.t("files_filter"), "*.pdf"), (self.t("all_files"), "*.*")],
        )
        if file_path:
            self.split_source_var.set(file_path)
            self.split_status_var.set(self.t("status_selected_pdf", name=os.path.basename(file_path)))
            if not self.split_output_dir_var.get().strip():
                self.split_output_dir_var.set(os.path.dirname(file_path))

    def on_split_drop(self, event):
        try:
            paths = self.split_source_entry.tk.splitlist(event.data)
        except Exception:
            paths = []

        if not paths:
            return ""

        dropped_file = paths[0]
        if not dropped_file.lower().endswith(".pdf"):
            messagebox.showwarning(self.t("pdf_required"), self.t("pdf_valid_required"))
            return ""

        self.split_source_var.set(dropped_file)
        self.split_status_var.set(self.t("status_selected_pdf", name=os.path.basename(dropped_file)))
        if not self.split_output_dir_var.get().strip():
            self.split_output_dir_var.set(os.path.dirname(dropped_file))
        return ""

    def choose_split_output_dir(self):
        directory = filedialog.askdirectory(title=self.t("choose_output_dir"))
        if directory:
            self.split_output_dir_var.set(directory)

    def on_split_output_drop(self, event):
        try:
            paths = self.split_output_entry.tk.splitlist(event.data)
        except Exception:
            paths = []

        if not paths:
            return ""

        dropped_path = paths[0]
        if os.path.isdir(dropped_path):
            self.split_output_dir_var.set(dropped_path)
        else:
            self.split_output_dir_var.set(os.path.dirname(dropped_path))
        return ""

    def split_selected_pdf(self):
        pdf_path = self.split_source_var.get().strip()
        if not pdf_path:
            messagebox.showwarning(self.t("no_selection"), self.t("select_pdf_to_split"))
            return

        if not pdf_path.lower().endswith(".pdf"):
            messagebox.showerror(self.t("invalid_pdf"), self.t("not_a_pdf"))
            return

        output_dir = self.split_output_dir_var.get().strip()
        if not output_dir:
            output_dir = os.path.dirname(pdf_path)

        try:
            created_files = split_pdf_pages(pdf_path, output_dir=output_dir)
            self.split_status_var.set(self.t("status_generated", count=len(created_files), path=output_dir))
            messagebox.showinfo(
                self.t("split_success"),
                self.t("split_success_details", count=len(created_files), path=output_dir),
            )
        except Exception as exc:
            messagebox.showerror(self.t("app_error"), self.t("split_fail", error=exc))

    def select_files(self):
        files = filedialog.askopenfilenames(
            title=self.t("select_pdf_files"),
            filetypes=[(self.t("all_files"), "*.*"), (self.t("files_filter"), "*.pdf")],
        )
        if not files:
            return

        pdf_files = []
        for file_path in files:
            if file_path.lower().endswith(".pdf"):
                pdf_files.append(file_path)

        if not pdf_files:
            messagebox.showwarning(self.t("no_selection"), self.t("select_a_pdf"))
            return

        for file_path in pdf_files:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)

        self.refresh_list()
        self.file_listbox.selection_clear(0, tk.END)

    def select_folder(self):
        folder_path = filedialog.askdirectory(title=self.t("select_folder_title"))
        if not folder_path:
            return

        pdf_files = []
        for file_name in sorted(os.listdir(folder_path)):
            full_path = os.path.join(folder_path, file_name)
            if os.path.isfile(full_path) and full_path.lower().endswith(".pdf"):
                pdf_files.append(full_path)

        for file_path in pdf_files:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)

        self.refresh_list()
        self.file_listbox.selection_clear(0, tk.END)

    def clear_placeholder(self, event=None):
        if self.selected_files:
            return
        self.file_listbox.delete(0, tk.END)

    def on_listbox_select(self, event=None):
        selected_indexes = self.file_listbox.curselection()
        if selected_indexes:
            self.current_index = selected_indexes[0]
        elif self.selected_files:
            self.current_index = 0
        self.preview_page_index = 0
        self.refresh_buttons()
        self.update_preview()

    def get_pdf_page_count(self, pdf_path):
        if not pdf_path or not os.path.isfile(pdf_path):
            return 0
        try:
            with fitz.open(pdf_path) as doc:
                return doc.page_count
        except Exception:
            return 0

    def render_pdf_thumbnail(self, pdf_path, page_number=0):
        if not pdf_path or not os.path.isfile(pdf_path):
            return None

        try:
            with fitz.open(pdf_path) as doc:
                if doc.page_count == 0:
                    return None
                page_index = max(0, min(int(page_number), doc.page_count - 1))
                page = doc[page_index]
                pix = page.get_pixmap(matrix=fitz.Matrix(1.8, 1.8), alpha=False)

                if self.preview_temp_path and os.path.exists(self.preview_temp_path):
                    os.remove(self.preview_temp_path)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                    temp_path = temp_file.name
                pix.save(temp_path)
                self.preview_temp_path = temp_path
                return temp_path
        except Exception:
            return None

    def next_preview_page(self):
        if not self.selected_files:
            return
        pdf_path = self.selected_files[self.current_index]
        page_count = self.get_pdf_page_count(pdf_path)
        if page_count <= 1:
            return
        self.preview_page_index = min(page_count - 1, self.preview_page_index + 1)
        self.update_preview()

    def previous_preview_page(self):
        if not self.selected_files:
            return
        if self.preview_page_index <= 0:
            return
        self.preview_page_index -= 1
        self.update_preview()

    def update_preview(self):
        if not self.selected_files:
            self.preview_page_index = 0
            self.preview_page_var.set(self.t("page_label", current=1, total=1))
            self.prev_page_button.config(state=tk.DISABLED)
            self.next_page_button.config(state=tk.DISABLED)
            self.preview_label.config(text=self.t("no_pdf_selected_preview"), image="")
            self.preview_label.image = None
            return

        if self.current_index >= len(self.selected_files):
            self.current_index = len(self.selected_files) - 1

        current_path = self.selected_files[self.current_index]
        page_count = self.get_pdf_page_count(current_path)
        if page_count <= 0:
            self.preview_page_index = 0
            self.preview_page_var.set(self.t("page_label", current=1, total=1))
            self.prev_page_button.config(state=tk.DISABLED)
            self.next_page_button.config(state=tk.DISABLED)
            self.preview_label.config(text=self.t("preview_unavailable", name=os.path.basename(current_path)), image="")
            self.preview_label.image = None
            return

        if self.preview_page_index >= page_count:
            self.preview_page_index = page_count - 1

        self.preview_page_var.set(self.t("page_label", current=self.preview_page_index + 1, total=page_count))
        self.prev_page_button.config(state=tk.NORMAL if page_count > 1 and self.preview_page_index > 0 else tk.DISABLED)
        self.next_page_button.config(state=tk.NORMAL if page_count > 1 and self.preview_page_index < page_count - 1 else tk.DISABLED)

        preview_path = self.render_pdf_thumbnail(current_path, self.preview_page_index)

        if not preview_path:
            self.preview_label.config(text=self.t("preview_unavailable", name=os.path.basename(current_path)), image="")
            self.preview_label.image = None
            return

        try:
            photo = tk.PhotoImage(file=preview_path)
            max_width = 260
            max_height = 340
            width = photo.width()
            height = photo.height()
            scale = max(1, int(max(width / max_width, height / max_height)))
            if scale > 1:
                photo = photo.subsample(scale)
            self.preview_label.config(text="", image=photo, compound="center")
            self.preview_label.image = photo
        except Exception:
            self.preview_label.config(text=self.t("preview_not_available", name=os.path.basename(current_path)), image="")
            self.preview_label.image = None

    def on_drop(self, event):
        file_paths = []
        try:
            file_paths = self.file_listbox.tk.splitlist(event.data)
        except Exception:
            file_paths = []

        pdf_files = []
        for file_path in file_paths:
            if file_path.lower().endswith(".pdf"):
                pdf_files.append(file_path)

        if not pdf_files:
            messagebox.showwarning(self.t("pdf_required"), self.t("drop_pdf_only"))
            return ""

        for file_path in pdf_files:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)

        self.refresh_list()
        self.file_listbox.selection_clear(0, tk.END)
        return ""

    def move_up(self):
        if not self.selected_files or self.current_index <= 0:
            return
        index = self.current_index
        self.selected_files[index], self.selected_files[index - 1] = self.selected_files[index - 1], self.selected_files[index]
        self.current_index = index - 1
        self.refresh_list()
        self.file_listbox.selection_set(self.current_index)
        self.refresh_buttons()

    def move_down(self):
        if not self.selected_files or self.current_index >= len(self.selected_files) - 1:
            return
        index = self.current_index
        self.selected_files[index], self.selected_files[index + 1] = self.selected_files[index + 1], self.selected_files[index]
        self.current_index = index + 1
        self.refresh_list()
        self.file_listbox.selection_set(self.current_index)
        self.refresh_buttons()

    def remove_selected(self):
        selected_indexes = list(self.file_listbox.curselection())
        if not selected_indexes:
            return
        for index in sorted(selected_indexes, reverse=True):
            del self.selected_files[index]
        self.refresh_list()

    def refresh_buttons(self):
        has_files = bool(self.selected_files)
        self.merge_button.config(state=tk.NORMAL if has_files else tk.DISABLED)
        self.remove_button.config(state=tk.NORMAL if has_files else tk.DISABLED)

        if not has_files:
            self.up_button.config(state=tk.DISABLED)
            self.down_button.config(state=tk.DISABLED)
            return

        index = self.current_index if self.current_index < len(self.selected_files) else len(self.selected_files) - 1
        self.up_button.config(state=tk.NORMAL if index > 0 and len(self.selected_files) > 1 else tk.DISABLED)
        self.down_button.config(state=tk.NORMAL if index < len(self.selected_files) - 1 and len(self.selected_files) > 1 else tk.DISABLED)

    def refresh_list(self):
        self.file_listbox.delete(0, tk.END)
        if not self.selected_files:
            self.file_listbox.insert(tk.END, self.t("drop_files_hint"))
            self.file_listbox.config(bg="#f7f7f7")
            self.file_listbox.selection_clear(0, tk.END)
            self.current_index = 0
        else:
            for file_path in self.selected_files:
                self.file_listbox.insert(tk.END, os.path.basename(file_path))
            self.file_listbox.config(bg="white")
            if self.current_index >= len(self.selected_files):
                self.current_index = len(self.selected_files) - 1
            self.file_listbox.selection_set(self.current_index)
        self.refresh_buttons()
        self.update_preview()

    def choose_output_file(self):
        default_name = "fusion.pdf"
        if self.selected_files:
            default_name = os.path.splitext(os.path.basename(self.selected_files[0]))[0] + "_fusion.pdf"

        output_path = filedialog.asksaveasfilename(
            title=self.t("save_merge"),
            defaultextension=".pdf",
            filetypes=[(self.t("files_filter"), "*.pdf")],
            initialfile=default_name,
        )

        if output_path:
            self.output_var.set(output_path)

    def merge_selected_files(self):
        if not self.selected_files:
            messagebox.showwarning(self.t("no_selection"), self.t("select_a_pdf"))
            return

        output_path = self.output_var.get().strip()
        if not output_path:
            output_path = os.path.join(
                os.path.dirname(self.selected_files[0]),
                "fusion.pdf",
            )

        if not output_path.lower().endswith(".pdf"):
            output_path += ".pdf"

        try:
            merge_pdfs(self.selected_files, output_path)
            messagebox.showinfo(
                self.t("success_merge"),
                self.t("merge_success_details", path=output_path),
            )
        except Exception as exc:
            messagebox.showerror(self.t("app_error"), self.t("merge_fail", error=exc))


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PdfManagerApp(root)
    root.mainloop()
