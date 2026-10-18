import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from tkinterdnd2 import DND_FILES

from pdf_manager_service import split_pdf_pages



class SplitTabMixin:
    """Split tab application behavior."""

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

    def choose_split_source(self):
        """Open the file picker to select a PDF to split.

        Ouvre le sélecteur pour choisir le PDF à découper.
        """
        file_path = filedialog.askopenfilename(
            title=self.t("select_pdf"),
            filetypes=[(self.t("files_filter"), "*.pdf"), (self.t("all_files"), "*.*")],
        )
        if file_path:
            self.load_split_source(file_path)

    def load_split_source(self, file_path):
        def source_loaded(_page_count):
            self.split_source_var.set(file_path)
            self.split_status_var.set(self.t("status_selected_pdf", name=os.path.basename(file_path)))
            if not self.split_output_dir_var.get().strip():
                self.split_output_dir_var.set(os.path.dirname(file_path))

        self.run_with_loading(
            self.t("select_pdf"),
            lambda: self.read_pdf_page_count(file_path),
            source_loaded,
            lambda error: messagebox.showerror(
                self.t("app_error"),
                self.t("split_fail", error=error),
            ),
        )

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

        self.load_split_source(dropped_file)
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

        def split():
            return split_pdf_pages(pdf_path, output_dir=output_dir)

        def split_complete(created_files):
            self.split_status_var.set(self.t("status_generated", count=len(created_files), path=output_dir))
            messagebox.showinfo(
                self.t("split_success"),
                self.t("split_success_details", count=len(created_files), path=output_dir),
            )

        self.run_with_loading(
            self.t("split_button"),
            split,
            split_complete,
            lambda error: messagebox.showerror(
                self.t("app_error"),
                self.t("split_fail", error=error),
            ),
        )
