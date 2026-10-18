# ============================================================
# PDF merging and splitting - GaLlaKk
# Fusion et division de PDF - GaLlaKk
# PDF file management application using Tkinter
# Application de gestion de fichiers PDF avec Tkinter
# ============================================================

import locale
import os
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pymupdf
from tkinterdnd2 import DND_FILES, TkinterDnD

try:
    from .pdf_manager_service import compress_pdf, merge_pdfs, split_pdf_pages
except ImportError:
    from pdf_manager_service import compress_pdf, merge_pdfs, split_pdf_pages


try:
    from .pdf_manager_translations import LANG_ORDER, TRANSLATIONS
except ImportError:
    from pdf_manager_translations import LANG_ORDER, TRANSLATIONS


def detect_system_language():
    """Detect the interface language from the system locale.

    Détermine la langue de l'interface à partir des paramètres régionaux.
    """
    try:
        default_locale = locale.getdefaultlocale()[0] or ""
    except Exception:
        default_locale = ""

    if not default_locale:
        return "fr"

    short_code = default_locale.lower().split("_")[0]
    return short_code if short_code in TRANSLATIONS else "fr"


class PdfManagerApp:
    """Main window for the PDF file management application.

    Fenêtre principale de l'application de gestion des fichiers PDF.
    """

    def __init__(self, root):
        """Initialize the window, tabs, and interface components.

        Initialise la fenêtre, ses onglets et les composants de l'interface.
        """
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
        self.compress_source_var = tk.StringVar(value="")
        self.compress_output_var = tk.StringVar(value="")
        self.compress_mode_var = tk.StringVar(value="lossless")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.merge_tab = tk.Frame(self.notebook, padx=10, pady=10)
        self.split_tab = tk.Frame(self.notebook, padx=10, pady=10)
        self.compress_tab = tk.Frame(self.notebook, padx=10, pady=10)

        self.notebook.add(self.merge_tab, text=self.t("merge_tab"))
        self.notebook.add(self.split_tab, text=self.t("split_tab"))
        self.notebook.add(self.compress_tab, text=self.t("compress_tab"))

        self.build_merge_tab()
        self.build_split_tab()
        self.build_compress_tab()
        self.apply_language()

    def t(self, key, **kwargs):
        """Return translated text for the active language, formatted with parameters.

        Renvoie le texte traduit pour la langue active, avec ses paramètres.
        """
        text = self.translations.get(self.current_lang, self.translations["fr"]).get(key, key)
        try:
            return text.format(**kwargs)
        except Exception:
            return text

    def on_language_change(self, event=None):
        """Apply the language selected in the drop-down list.

        Applique la langue choisie dans la liste déroulante.
        """
        selected_label = self.language_combo.get()
        selected_lang = next((code for code in LANG_ORDER if self.translations[code]["label"] == selected_label), self.current_lang)
        if selected_lang != self.current_lang:
            self.current_lang = selected_lang
            self.apply_language()

    def apply_language(self):
        """Refresh visible text after a language change.

        Actualise les textes visibles après un changement de langue.
        """
        self.root.title(self.t("app_title"))
        self.language_label.config(text=self.t("language"))
        self.notebook.tab(0, text=self.t("merge_tab"))
        self.notebook.tab(1, text=self.t("split_tab"))
        self.notebook.tab(2, text=self.t("compress_tab"))

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

        self.compress_title_label.config(text=self.t("compress_title"))
        self.compress_input_label.config(text=self.t("compress_input_label"))
        self.compress_choose_file_button.config(text=self.t("browse"))
        self.compress_output_label.config(text=self.t("compress_output_label"))
        self.compress_choose_output_button.config(text=self.t("choose"))
        self.compress_mode_label.config(text=self.t("compress_mode_label"))
        self.compress_lossless_radio.config(text=self.t("compress_lossless"))
        self.compress_balanced_radio.config(text=self.t("compress_balanced"))
        self.compress_info_label.config(text=self.t("compress_info"))
        self.compress_button.config(text=self.t("compress_button"))

        self.update_preview()

    def build_merge_tab(self):
        """Build the merge tab controls, file list, and preview.

        Crée les commandes, la liste de fichiers et l'aperçu de fusion.
        """
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
        """Build the split tab fields and controls.

        Crée les champs et commandes de l'onglet de découpage.
        """
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

    def build_compress_tab(self):
        """Build the PDF compression tab and its quality options.

        Crée l'onglet de compression PDF et ses options de qualité.
        """
        self.compress_title_label = tk.Label(
            self.compress_tab,
            text=self.t("compress_title"),
            font=("Segoe UI", 11, "bold"),
            anchor="w",
            padx=15,
            pady=12,
        )
        self.compress_title_label.pack(fill="x")

        input_frame = tk.Frame(self.compress_tab, padx=15, pady=5)
        input_frame.pack(fill="x")
        self.compress_input_label = tk.Label(input_frame, text=self.t("compress_input_label"), width=16, anchor="w")
        self.compress_input_label.pack(side="left")
        self.compress_source_entry = tk.Entry(input_frame, textvariable=self.compress_source_var, width=60)
        self.compress_source_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.compress_choose_file_button = ttk.Button(
            input_frame,
            text=self.t("browse"),
            command=self.choose_compress_source,
        )
        self.compress_choose_file_button.pack(side="left")

        output_frame = tk.Frame(self.compress_tab, padx=15, pady=5)
        output_frame.pack(fill="x")
        self.compress_output_label = tk.Label(output_frame, text=self.t("compress_output_label"), width=16, anchor="w")
        self.compress_output_label.pack(side="left")
        self.compress_output_entry = tk.Entry(output_frame, textvariable=self.compress_output_var, width=60)
        self.compress_output_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.compress_choose_output_button = ttk.Button(
            output_frame,
            text=self.t("choose"),
            command=self.choose_compress_output,
        )
        self.compress_choose_output_button.pack(side="left")

        self.compress_mode_label = tk.Label(
            self.compress_tab,
            text=self.t("compress_mode_label"),
            font=("Segoe UI", 10, "bold"),
            anchor="w",
            padx=15,
            pady=10,
        )
        self.compress_mode_label.pack(fill="x")
        mode_frame = tk.Frame(self.compress_tab, padx=15)
        mode_frame.pack(fill="x")
        self.compress_lossless_radio = tk.Radiobutton(
            mode_frame,
            text=self.t("compress_lossless"),
            variable=self.compress_mode_var,
            value="lossless",
        )
        self.compress_lossless_radio.pack(anchor="w")
        self.compress_balanced_radio = tk.Radiobutton(
            mode_frame,
            text=self.t("compress_balanced"),
            variable=self.compress_mode_var,
            value="balanced",
        )
        self.compress_balanced_radio.pack(anchor="w")

        self.compress_info_label = tk.Label(
            self.compress_tab,
            text=self.t("compress_info"),
            justify="left",
            wraplength=760,
            fg="#444444",
            padx=15,
            pady=12,
            anchor="w",
        )
        self.compress_info_label.pack(fill="x")

        buttons_frame = tk.Frame(self.compress_tab, padx=15, pady=10)
        buttons_frame.pack(fill="x")
        self.compress_button = tk.Button(
            buttons_frame,
            text=self.t("compress_button"),
            command=self.compress_selected_pdf,
            width=18,
        )
        self.compress_button.pack(side="right")

    def choose_compress_source(self):
        """Select the PDF to compress and suggest a separate output path.

        Sélectionne le PDF à compresser et propose un chemin de sortie distinct.
        """
        file_path = filedialog.askopenfilename(
            title=self.t("compress_choose_file"),
            filetypes=[(self.t("files_filter"), "*.pdf"), (self.t("all_files"), "*.*")],
        )
        if file_path:
            self.compress_source_var.set(file_path)
            base_name, extension = os.path.splitext(file_path)
            self.compress_output_var.set(f"{base_name}_compressed{extension}")

    def choose_compress_output(self):
        """Choose where to save the compressed PDF.

        Choisit l'emplacement d'enregistrement du PDF compressé.
        """
        source_path = self.compress_source_var.get().strip()
        initial_dir = os.path.dirname(source_path) if source_path else os.getcwd()
        default_name = os.path.basename(self.compress_output_var.get().strip()) or "compressed.pdf"
        output_path = filedialog.asksaveasfilename(
            title=self.t("compress_save_pdf"),
            initialdir=initial_dir,
            initialfile=default_name,
            defaultextension=".pdf",
            filetypes=[(self.t("files_filter"), "*.pdf")],
        )
        if output_path:
            self.compress_output_var.set(output_path)

    def compress_selected_pdf(self):
        """Compress the selected PDF and report file sizes or errors.

        Compresse le PDF sélectionné et affiche les tailles ou les erreurs.
        """
        source_path = self.compress_source_var.get().strip()
        if not source_path:
            messagebox.showwarning(self.t("no_selection"), self.t("compress_select_pdf"))
            return
        if not source_path.lower().endswith(".pdf") or not os.path.isfile(source_path):
            messagebox.showerror(self.t("invalid_pdf"), self.t("not_a_pdf"))
            return

        output_path = self.compress_output_var.get().strip()
        if not output_path:
            base_name, extension = os.path.splitext(source_path)
            output_path = f"{base_name}_compressed{extension}"
            self.compress_output_var.set(output_path)

        try:
            compress_pdf(source_path, output_path, mode=self.compress_mode_var.get())
            input_size = os.path.getsize(source_path)
            output_size = os.path.getsize(output_path)
            messagebox.showinfo(
                self.t("compress_success"),
                self.t(
                    "compress_success_details",
                    input_size=f"{input_size:,}",
                    output_size=f"{output_size:,}",
                    path=output_path,
                ),
            )
        except Exception as exc:
            messagebox.showerror(self.t("app_error"), self.t("compress_fail", error=exc))

    def choose_split_source(self):
        """Open the file picker to select a PDF to split.

        Ouvre le sélecteur pour choisir le PDF à découper.
        """
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
        """Handle a PDF dropped into the source file field.

        Traite le dépôt d'un PDF dans le champ du fichier source.
        """
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
        """Open the folder picker for the split output pages.

        Ouvre le sélecteur du dossier où enregistrer les pages.
        """
        directory = filedialog.askdirectory(title=self.t("choose_output_dir"))
        if directory:
            self.split_output_dir_var.set(directory)

    def on_split_output_drop(self, event):
        """Set the output folder from a dropped path.

        Définit le dossier de sortie à partir d'un chemin déposé.
        """
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
        """Split the selected PDF and report the result or any error.

        Découpe le PDF sélectionné et affiche le résultat ou l'erreur.
        """
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
        """Add PDFs selected in the file picker to the list.

        Ajoute à la liste les PDF choisis dans le sélecteur de fichiers.
        """
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
        """Add PDFs found in the selected folder to the list.

        Ajoute à la liste les PDF trouvés dans le dossier choisi.
        """
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
        """Clear the list placeholder before the first file is selected.

        Efface le texte indicatif de la liste avant la première sélection.
        """
        if self.selected_files:
            return
        self.file_listbox.delete(0, tk.END)

    def on_listbox_select(self, event=None):
        """Update the active file and preview after a selection.

        Met à jour le fichier actif et son aperçu après une sélection.
        """
        selected_indexes = self.file_listbox.curselection()
        if selected_indexes:
            self.current_index = selected_indexes[0]
        elif self.selected_files:
            self.current_index = 0
        self.preview_page_index = 0
        self.refresh_buttons()
        self.update_preview()

    def get_pdf_page_count(self, pdf_path):
        """Return the PDF page count, or zero if the file is inaccessible.

        Renvoie le nombre de pages du PDF, ou zéro s'il est inaccessible.
        """
        if not pdf_path or not os.path.isfile(pdf_path):
            return 0
        try:
            with pymupdf.open(pdf_path) as doc:
                return doc.page_count
        except Exception:
            return 0

    def render_pdf_thumbnail(self, pdf_path, page_number=0):
        """Render the requested page as a temporary preview image.

        Génère une image temporaire de la page demandée pour l'aperçu.
        """
        if not pdf_path or not os.path.isfile(pdf_path):
            return None

        try:
            with pymupdf.open(pdf_path) as doc:
                if doc.page_count == 0:
                    return None
                page_index = max(0, min(int(page_number), doc.page_count - 1))
                page = doc[page_index]
                pix = page.get_pixmap(matrix=pymupdf.Matrix(1.8, 1.8), alpha=False)

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
        """Go to the next page in the active PDF preview.

        Passe à la page suivante dans l'aperçu du PDF actif.
        """
        if not self.selected_files:
            return
        pdf_path = self.selected_files[self.current_index]
        page_count = self.get_pdf_page_count(pdf_path)
        if page_count <= 1:
            return
        self.preview_page_index = min(page_count - 1, self.preview_page_index + 1)
        self.update_preview()

    def previous_preview_page(self):
        """Go to the previous page in the active PDF preview.

        Revient à la page précédente dans l'aperçu du PDF actif.
        """
        if not self.selected_files:
            return
        if self.preview_page_index <= 0:
            return
        self.preview_page_index -= 1
        self.update_preview()

    def update_preview(self):
        """Refresh the preview image, page number, and navigation controls.

        Actualise l'image, le numéro de page et les commandes de navigation.
        """
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
        """Add PDF files dropped into the merge area to the list.

        Ajoute à la liste les fichiers PDF déposés dans la zone de fusion.
        """
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
        """Move the selected file up by one position.

        Déplace le fichier sélectionné d'une position vers le début.
        """
        if not self.selected_files or self.current_index <= 0:
            return
        index = self.current_index
        self.selected_files[index], self.selected_files[index - 1] = self.selected_files[index - 1], self.selected_files[index]
        self.current_index = index - 1
        self.refresh_list()
        self.file_listbox.selection_set(self.current_index)
        self.refresh_buttons()

    def move_down(self):
        """Move the selected file down by one position.

        Déplace le fichier sélectionné d'une position vers la fin.
        """
        if not self.selected_files or self.current_index >= len(self.selected_files) - 1:
            return
        index = self.current_index
        self.selected_files[index], self.selected_files[index + 1] = self.selected_files[index + 1], self.selected_files[index]
        self.current_index = index + 1
        self.refresh_list()
        self.file_listbox.selection_set(self.current_index)
        self.refresh_buttons()

    def remove_selected(self):
        """Remove the currently selected files from the list.

        Retire de la liste les fichiers actuellement sélectionnés.
        """
        selected_indexes = list(self.file_listbox.curselection())
        if not selected_indexes:
            return
        for index in sorted(selected_indexes, reverse=True):
            del self.selected_files[index]
        self.refresh_list()

    def refresh_buttons(self):
        """Update button states based on file selection and order.

        Actualise l'état des boutons selon la sélection et l'ordre des fichiers.
        """
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
        """Rebuild the displayed list and refresh controls and preview.

        Reconstruit la liste affichée et actualise les commandes et l'aperçu.
        """
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
        """Open the save dialog for the merged PDF.

        Ouvre le sélecteur du chemin de sortie du PDF fusionné.
        """
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
        """Merge the selected PDFs and report the result or any error.

        Fusionne les PDF sélectionnés et affiche le résultat ou l'erreur.
        """
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
